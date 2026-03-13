"""POC 1: Gemini Live TEXT mode + ElevenLabs TTS Pipeline.

Validates that GeminiLiveLLMService in TEXT mode can pipe text to
ElevenLabsTTSService through Pipecat's pipeline.

Pipeline:
  Mic → LocalAudioTransport → GeminiLiveLLMService(TEXT)
    → ElevenLabsTTSService → Speaker

Success criteria:
  - Audio response plays through ElevenLabs voice
  - No frame type errors between GeminiLive TEXT output and ElevenLabs input
  - End-to-end latency measured (speech in → speech out)

Usage:
  python scripts/poc_gemini_live_text_elevenlabs.py
"""

from __future__ import annotations

import asyncio
import logging
import os
import time

import certifi
from dotenv import load_dotenv
from pipecat.frames.frames import (
    Frame,
    LLMFullResponseStartFrame,
    TTSStartedFrame,
    TTSTextFrame,
    UserStoppedSpeakingFrame,
)
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.frame_processor import FrameDirection, FrameProcessor
from pipecat.services.elevenlabs.tts import ElevenLabsTTSService
from pipecat.services.google.gemini_live.llm import (
    GeminiLiveLLMService,
    GeminiModalities,
    InputParams,
)
from pipecat.transports.local.audio import LocalAudioTransport, LocalAudioTransportParams

# Fix SSL for macOS Python
os.environ.setdefault("SSL_CERT_FILE", certifi.where())

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
logger = logging.getLogger("poc.gemini_live_text")

# Audio settings — GeminiLive uses 24kHz for both input and output
AUDIO_SAMPLE_RATE = 24000


class LatencyTracker(FrameProcessor):
    """Measures end-to-end latency between key pipeline events."""

    def __init__(self) -> None:
        super().__init__()
        self._user_stopped_at: float | None = None
        self._llm_started_at: float | None = None

    async def process_frame(self, frame: Frame, direction: FrameDirection) -> None:
        await super().process_frame(frame, direction)

        if isinstance(frame, UserStoppedSpeakingFrame):
            self._user_stopped_at = time.perf_counter()
            logger.info(">>> User stopped speaking")

        elif isinstance(frame, LLMFullResponseStartFrame):
            self._llm_started_at = time.perf_counter()
            if self._user_stopped_at:
                delta = (self._llm_started_at - self._user_stopped_at) * 1000
                logger.info(">>> STT→LLM: %.0fms", delta)

        elif isinstance(frame, TTSStartedFrame):
            now = time.perf_counter()
            if self._llm_started_at:
                delta = (now - self._llm_started_at) * 1000
                logger.info(">>> LLM→TTS: %.0fms", delta)
            if self._user_stopped_at:
                total = (now - self._user_stopped_at) * 1000
                logger.info(">>> Total latency: %.0fms", total)

        elif isinstance(frame, TTSTextFrame):
            logger.info(">>> TTS text: %r", frame.text[:80])

        await self.push_frame(frame, direction)


class FrameDebugger(FrameProcessor):
    """Logs all frame types passing through for debugging compatibility."""

    def __init__(self, name: str) -> None:
        super().__init__()
        self._name = name

    async def process_frame(self, frame: Frame, direction: FrameDirection) -> None:
        await super().process_frame(frame, direction)
        frame_type = type(frame).__name__
        # Only log interesting frames (skip audio frames to avoid spam)
        if "Audio" not in frame_type:
            logger.debug("[%s] %s: %s", self._name, direction, frame_type)
        await self.push_frame(frame, direction)


async def main() -> None:
    load_dotenv()

    google_api_key = os.environ["GOOGLE_API_KEY"]
    elevenlabs_api_key = os.environ["ELEVENLABS_API_KEY"]
    elevenlabs_voice_id = os.environ["ELEVENLABS_VOICE_ID"]

    # Local audio I/O
    transport = LocalAudioTransport(
        LocalAudioTransportParams(
            audio_in_enabled=True,
            audio_in_sample_rate=AUDIO_SAMPLE_RATE,
            audio_out_enabled=True,
            audio_out_sample_rate=AUDIO_SAMPLE_RATE,
        )
    )

    # GeminiLive in TEXT mode — native STT + LLM, text output only
    gemini = GeminiLiveLLMService(
        api_key=google_api_key,
        model="gemini-2.5-flash-native-audio-preview-12-2025",
        system_instruction=(
            "You are a helpful assistant. Keep responses short — under 2 sentences. "
            "Be conversational and friendly."
        ),
        params=InputParams(
            modalities=GeminiModalities.TEXT,
            temperature=0.7,
        ),
    )

    # ElevenLabs TTS
    tts = ElevenLabsTTSService(
        api_key=elevenlabs_api_key,
        voice_id=elevenlabs_voice_id,
        model="eleven_turbo_v2_5",
    )

    # Latency + debug tracking
    latency = LatencyTracker()
    debug_pre_tts = FrameDebugger("pre-tts")

    # Pipeline: mic → GeminiLive(TEXT) → debug → latency → TTS → speaker
    pipeline = Pipeline(
        processors=[
            transport.input(),
            gemini,
            debug_pre_tts,
            latency,
            tts,
            transport.output(),
        ]
    )

    task = PipelineTask(
        pipeline=pipeline,
        params=PipelineParams(
            audio_in_sample_rate=AUDIO_SAMPLE_RATE,
            audio_out_sample_rate=AUDIO_SAMPLE_RATE,
        ),
    )

    logger.info("=== POC 1: Gemini Live TEXT + ElevenLabs ===")
    logger.info("Speak into your microphone. The bot should respond with ElevenLabs voice.")
    logger.info("Press Ctrl+C to stop.")

    runner = PipelineRunner(handle_sigint=True)
    await runner.run(task)


if __name__ == "__main__":
    asyncio.run(main())
