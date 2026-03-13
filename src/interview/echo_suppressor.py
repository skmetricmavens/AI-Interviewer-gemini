"""Echo suppression for preventing bot speech from being transcribed as user input.

Without headphones, the microphone picks up the bot's TTS output. The STT
then transcribes it as "user" speech, creating a feedback loop. This processor
tracks recent bot utterances and drops incoming transcriptions that match.
"""

from __future__ import annotations

import logging
import time
from collections import deque
from difflib import SequenceMatcher

from pipecat.frames.frames import (
    BotStartedSpeakingFrame,
    BotStoppedSpeakingFrame,
    Frame,
    TranscriptionFrame,
    TTSTextFrame,
)
from pipecat.processors.frame_processor import FrameDirection, FrameProcessor

logger = logging.getLogger("ai_interviewer.echo")


class EchoSuppressor(FrameProcessor):
    """Drops transcription frames that match recent bot speech.

    Tracks bot utterances (via TTSTextFrame) and compares incoming
    TranscriptionFrame text using fuzzy string similarity. Frames
    above the similarity threshold within the time window are dropped.
    """

    def __init__(
        self,
        *,
        threshold: float = 0.6,
        window_secs: float = 8.0,
        min_length: int = 1,
        trailing_secs: float = 1.5,
    ) -> None:
        super().__init__()
        self._threshold = threshold
        self._window_secs = window_secs
        self._min_length = min_length
        self._trailing_secs = trailing_secs
        self._bot_utterances: deque[tuple[str, float]] = deque(maxlen=10)
        self._bot_speaking: bool = False
        self._bot_stopped_at: float | None = None

    def record_bot_utterance(self, text: str) -> None:
        """Store a bot utterance with current timestamp for echo comparison."""
        self._bot_utterances.append((text.lower(), time.perf_counter()))

    def is_echo(self, text: str) -> bool:
        """Check if text is likely an echo of recent bot speech."""
        stripped = text.strip()
        if not stripped:
            return False

        words = stripped.split()
        if len(words) < self._min_length:
            return False

        now = time.perf_counter()
        normalized = stripped.lower()

        for bot_text, ts in self._bot_utterances:
            if now - ts > self._window_secs:
                continue

            ratio = SequenceMatcher(None, normalized, bot_text).ratio()
            if ratio >= self._threshold:
                logger.info(
                    "Echo suppressed (%.0f%%): %r",
                    ratio * 100,
                    stripped[:60],
                )
                return True

            # Check if user text is a substring/fragment of bot speech
            if len(normalized) < len(bot_text):
                sub_ratio = SequenceMatcher(
                    None, normalized, bot_text[: len(normalized) + 10]
                ).ratio()
                if sub_ratio >= self._threshold:
                    logger.info(
                        "Echo suppressed (partial %.0f%%): %r",
                        sub_ratio * 100,
                        stripped[:60],
                    )
                    return True

        return False

    def _in_trailing_window(self) -> bool:
        """Check if we're within the trailing suppression window after bot stopped."""
        if self._bot_stopped_at is None or self._trailing_secs <= 0:
            return False
        return (time.perf_counter() - self._bot_stopped_at) < self._trailing_secs

    async def process_frame(self, frame: Frame, direction: FrameDirection) -> None:
        """Track bot speaking state and suppress echoed transcriptions."""
        await super().process_frame(frame, direction)

        if isinstance(frame, BotStartedSpeakingFrame):
            self._bot_speaking = True
            self._bot_stopped_at = None
        elif isinstance(frame, BotStoppedSpeakingFrame):
            self._bot_speaking = False
            self._bot_stopped_at = time.perf_counter()
        elif isinstance(frame, TTSTextFrame):
            self.record_bot_utterance(frame.text)
        elif isinstance(frame, TranscriptionFrame):
            if self._bot_speaking:
                logger.info("Echo suppressed (bot speaking): %r", frame.text[:60])
                return  # Drop — bot is actively speaking
            if self._in_trailing_window():
                logger.info("Echo suppressed (trailing window): %r", frame.text[:60])
                return  # Drop — within trailing window after bot stopped
            if self.is_echo(frame.text):
                return  # Drop — text similarity match

        await self.push_frame(frame, direction)
