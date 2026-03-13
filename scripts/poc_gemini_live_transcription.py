"""POC 3: Transcription quality + multi-turn context + echo suppression.

Uses POC 1's pipeline (TEXT + ElevenLabs) and validates:
1. Input transcription quality (user speech → text)
2. Multi-turn context maintenance (bot references prior answers)
3. Echo suppressor integration with GeminiLive's TranscriptionFrame

Pipeline:
  Mic → LocalAudioTransport → MicMuter → GeminiLiveLLMService(TEXT)
    → EchoSuppressor → ElevenLabsTTSService → Speaker

Success criteria:
  - User speech accurately transcribed (logged for review)
  - Bot maintains context across 3+ turns (references prior answers)
  - EchoSuppressor correctly identifies bot speech echoes
  - Transcriptions are complete sentences (not fragments)

Usage:
  python scripts/poc_gemini_live_transcription.py
"""

from __future__ import annotations

import asyncio
import logging
import os
import sys
import time

import certifi
from dotenv import load_dotenv
from pipecat.frames.frames import (
    BotStartedSpeakingFrame,
    BotStoppedSpeakingFrame,
    Frame,
    LLMFullResponseEndFrame,
    LLMFullResponseStartFrame,
    TranscriptionFrame,
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

# Add project root to path so we can import src modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.interview.echo_suppressor import EchoSuppressor
from src.interview.mic_muter import MicMuter

# Fix SSL for macOS Python
os.environ.setdefault("SSL_CERT_FILE", certifi.where())

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
logger = logging.getLogger("poc.gemini_live_transcription")

AUDIO_SAMPLE_RATE = 24000


class TranscriptionLogger(FrameProcessor):
    """Logs all transcription events and tracks conversation turns."""

    def __init__(self) -> None:
        super().__init__()
        self._turn_count = 0
        self._user_turns: list[str] = []
        self._bot_turns: list[str] = []
        self._current_bot_text: list[str] = []
        self._user_stopped_at: float | None = None

    async def process_frame(self, frame: Frame, direction: FrameDirection) -> None:
        await super().process_frame(frame, direction)

        if isinstance(frame, UserStoppedSpeakingFrame):
            self._user_stopped_at = time.perf_counter()

        elif isinstance(frame, TranscriptionFrame):
            self._turn_count += 1
            self._user_turns.append(frame.text)
            logger.info(
                "=== USER TURN %d === %r",
                self._turn_count,
                frame.text,
            )
            # Check completeness
            text = frame.text.strip()
            if text and text[-1] in ".?!":
                logger.info("  [OK] Ends with punctuation — likely complete sentence")
            else:
                logger.warning("  [WARN] No terminal punctuation — may be fragment: %r", text)

        elif isinstance(frame, LLMFullResponseStartFrame):
            self._current_bot_text = []
            if self._user_stopped_at:
                delta = (time.perf_counter() - self._user_stopped_at) * 1000
                logger.info("  Latency (user→LLM): %.0fms", delta)

        elif isinstance(frame, TTSTextFrame):
            self._current_bot_text.append(frame.text)

        elif isinstance(frame, LLMFullResponseEndFrame):
            full_response = "".join(self._current_bot_text)
            self._bot_turns.append(full_response)
            logger.info(
                "=== BOT TURN %d === %r",
                len(self._bot_turns),
                full_response[:120],
            )
            # Check if bot references prior context
            if len(self._bot_turns) >= 2:
                self._check_context_maintenance()

        elif isinstance(frame, TTSStartedFrame):
            if self._user_stopped_at:
                total = (time.perf_counter() - self._user_stopped_at) * 1000
                logger.info("  Total latency: %.0fms", total)

        elif isinstance(frame, BotStartedSpeakingFrame):
            logger.info("  [Bot speaking — echo suppressor should activate]")

        elif isinstance(frame, BotStoppedSpeakingFrame):
            logger.info("  [Bot stopped — trailing window active]")

        await self.push_frame(frame, direction)

    def _check_context_maintenance(self) -> None:
        """Heuristic check: does the bot seem to reference prior conversation?"""
        latest = self._bot_turns[-1].lower()
        # Look for pronouns/references that suggest context awareness
        context_markers = [
            "you mentioned",
            "earlier",
            "as you said",
            "that",
            "this",
            "your",
            "you",
            "we",
            "our",
        ]
        found = [m for m in context_markers if m in latest]
        if found:
            logger.info(
                "  [OK] Context markers found: %s — bot likely maintains context",
                found[:3],
            )
        else:
            logger.info("  [INFO] No explicit context markers — check manually")

    def print_summary(self) -> None:
        """Print conversation summary for review."""
        logger.info("\n" + "=" * 60)
        logger.info("=== CONVERSATION SUMMARY ===")
        logger.info("=" * 60)
        logger.info("Total user turns: %d", len(self._user_turns))
        logger.info("Total bot turns: %d", len(self._bot_turns))
        for i, (user, bot) in enumerate(zip(self._user_turns, self._bot_turns), 1):
            logger.info("\n--- Turn %d ---", i)
            logger.info("  User: %s", user)
            logger.info("  Bot:  %s", bot[:150])
        # Any remaining user turns without bot responses
        for i, user in enumerate(
            self._user_turns[len(self._bot_turns) :],
            len(self._bot_turns) + 1,
        ):
            logger.info("\n--- Turn %d (no response) ---", i)
            logger.info("  User: %s", user)


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

    # GeminiLive in TEXT mode
    gemini = GeminiLiveLLMService(
        api_key=google_api_key,
        model="gemini-2.5-flash-native-audio-preview-12-2025",
        system_instruction=(
            "You are conducting a short interview about the person's work and interests. "
            "Ask follow-up questions that reference what they said before. "
            "Keep responses under 2 sentences. Be warm and curious. "
            "After each answer, ask a follow-up that builds on their response."
        ),
        params=InputParams(
            modalities=GeminiModalities.TEXT,
            temperature=0.7,
        ),
    )

    # Echo suppressor — reuse production settings
    echo_suppressor = EchoSuppressor(
        threshold=0.6,
        window_secs=8.0,
        min_length=1,
        trailing_secs=1.5,
    )

    # Mic muter — prevents VAD echo
    mic_muter = MicMuter(trailing_secs=1.5)

    # ElevenLabs TTS
    tts = ElevenLabsTTSService(
        api_key=elevenlabs_api_key,
        voice_id=elevenlabs_voice_id,
        model="eleven_turbo_v2_5",
    )

    # Transcription logger
    transcript_logger = TranscriptionLogger()

    # Pipeline: mic → mic_muter → GeminiLive(TEXT) → echo_sup → transcript_log → TTS → speaker
    pipeline = Pipeline(
        processors=[
            transport.input(),
            mic_muter,
            gemini,
            echo_suppressor,
            transcript_logger,
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

    logger.info("=== POC 3: Transcription + Context + Echo Suppression ===")
    logger.info("Have a 3+ turn conversation. The bot will interview you.")
    logger.info("Watch for:")
    logger.info("  - Transcription quality (complete sentences?)")
    logger.info("  - Context maintenance (bot references prior answers?)")
    logger.info("  - Echo suppression (bot speech not echoed back?)")
    logger.info("Press Ctrl+C to stop and see summary.")

    runner = PipelineRunner(handle_sigint=True)
    try:
        await runner.run(task)
    except KeyboardInterrupt:
        pass
    finally:
        transcript_logger.print_summary()


if __name__ == "__main__":
    asyncio.run(main())
