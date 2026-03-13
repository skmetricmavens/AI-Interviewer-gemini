"""POC 2: Gemini Live AUDIO mode (native voice) — baseline latency.

Validates Gemini Live native audio mode and measures baseline latency
for comparison with TEXT + ElevenLabs (POC 1).

Pipeline:
  Mic → LocalAudioTransport → GeminiLiveLLMService(AUDIO, voice="Kore") → Speaker

Success criteria:
  - Bot responds with Gemini native voice
  - Latency measured for comparison with POC 1
  - Output transcription captured

Usage:
  python scripts/poc_gemini_live_audio_native.py
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
    TranscriptionFrame,
    TTSStartedFrame,
    TTSStoppedFrame,
    TTSTextFrame,
    UserStoppedSpeakingFrame,
)
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.frame_processor import FrameDirection, FrameProcessor
from pipecat.services.google.gemini_live.llm import (
    GeminiLiveLLMService,
    GeminiModalities,
    InputParams,
)
from pipecat.transports.local.audio import LocalAudioTransport, LocalAudioTransportParams

# Fix SSL for macOS Python
os.environ.setdefault("SSL_CERT_FILE", certifi.where())

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
logger = logging.getLogger("poc.gemini_live_audio")

# GeminiLive native audio uses 24kHz
AUDIO_SAMPLE_RATE = 24000


class NativeAudioTracker(FrameProcessor):
    """Tracks latency and transcription for native audio mode."""

    def __init__(self) -> None:
        super().__init__()
        self._user_stopped_at: float | None = None
        self._latencies: list[float] = []

    async def process_frame(self, frame: Frame, direction: FrameDirection) -> None:
        await super().process_frame(frame, direction)

        if isinstance(frame, UserStoppedSpeakingFrame):
            self._user_stopped_at = time.perf_counter()
            logger.info(">>> User stopped speaking")

        elif isinstance(frame, LLMFullResponseStartFrame):
            if self._user_stopped_at:
                delta = (time.perf_counter() - self._user_stopped_at) * 1000
                logger.info(">>> User→LLM response start: %.0fms", delta)

        elif isinstance(frame, TTSStartedFrame):
            if self._user_stopped_at:
                total = (time.perf_counter() - self._user_stopped_at) * 1000
                self._latencies.append(total)
                logger.info(">>> Total latency (native audio): %.0fms", total)
                avg = sum(self._latencies) / len(self._latencies)
                logger.info(">>> Avg latency so far: %.0fms", avg)

        elif isinstance(frame, TTSStoppedFrame):
            logger.info(">>> Bot finished speaking")

        elif isinstance(frame, TranscriptionFrame):
            logger.info(">>> User transcription: %r", frame.text)

        elif isinstance(frame, TTSTextFrame):
            logger.info(">>> Bot output transcript: %r", frame.text[:80])

        await self.push_frame(frame, direction)


async def main() -> None:
    load_dotenv()

    google_api_key = os.environ["GOOGLE_API_KEY"]

    # Local audio I/O
    transport = LocalAudioTransport(
        LocalAudioTransportParams(
            audio_in_enabled=True,
            audio_in_sample_rate=AUDIO_SAMPLE_RATE,
            audio_out_enabled=True,
            audio_out_sample_rate=AUDIO_SAMPLE_RATE,
        )
    )

    # GeminiLive in AUDIO mode — native STT + LLM + native TTS
    gemini = GeminiLiveLLMService(
        api_key=google_api_key,
        model="gemini-2.5-flash-native-audio-preview-12-2025",
        voice_id="Kore",
        system_instruction=(
            "You are a helpful assistant. Keep responses short — under 2 sentences. "
            "Be conversational and friendly."
        ),
        params=InputParams(
            modalities=GeminiModalities.AUDIO,
            temperature=0.7,
        ),
    )

    # Tracking
    tracker = NativeAudioTracker()

    # Pipeline: mic → GeminiLive(AUDIO) → tracker → speaker
    pipeline = Pipeline(
        processors=[
            transport.input(),
            gemini,
            tracker,
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

    logger.info("=== POC 2: Gemini Live AUDIO (Native Voice) ===")
    logger.info("Speak into your microphone. The bot should respond with Gemini's native voice.")
    logger.info("This measures baseline latency for comparison with POC 1 (TEXT + ElevenLabs).")
    logger.info("Press Ctrl+C to stop.")

    runner = PipelineRunner(handle_sigint=True)
    await runner.run(task)


if __name__ == "__main__":
    asyncio.run(main())
