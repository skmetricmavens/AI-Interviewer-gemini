"""Mic muter — drops audio input frames while the bot is speaking.

Without this, the speaker output is picked up by the microphone and VAD
detects it as user speech, triggering constant interruptions. By dropping
InputAudioRawFrame while the bot is speaking (plus a trailing window),
VAD never sees the echo audio and interruptions are prevented.
"""

from __future__ import annotations

import logging
import time

from pipecat.frames.frames import (
    BotStartedSpeakingFrame,
    BotStoppedSpeakingFrame,
    Frame,
    InputAudioRawFrame,
)
from pipecat.processors.frame_processor import FrameDirection, FrameProcessor

logger = logging.getLogger("ai_interviewer.mic_muter")


class MicMuter(FrameProcessor):
    """Drops audio input frames while the bot is speaking.

    Tracks bot speaking state via BotStartedSpeakingFrame and
    BotStoppedSpeakingFrame. Drops all InputAudioRawFrame instances
    while the bot is speaking plus a configurable trailing window
    after it stops, preventing VAD from triggering on echo audio.
    """

    def __init__(self, *, trailing_secs: float = 1.5) -> None:
        super().__init__()
        self._trailing_secs = trailing_secs
        self._bot_speaking: bool = False
        self._bot_stopped_at: float | None = None

    def _in_trailing_window(self) -> bool:
        """Check if we're within the trailing mute window after bot stopped."""
        if self._bot_stopped_at is None or self._trailing_secs <= 0:
            return False
        return (time.perf_counter() - self._bot_stopped_at) < self._trailing_secs

    async def process_frame(self, frame: Frame, direction: FrameDirection) -> None:
        """Track bot speaking state and mute mic input during bot speech."""
        await super().process_frame(frame, direction)

        if isinstance(frame, BotStartedSpeakingFrame):
            self._bot_speaking = True
            self._bot_stopped_at = None
            logger.debug("Mic muted — bot started speaking")
        elif isinstance(frame, BotStoppedSpeakingFrame):
            self._bot_speaking = False
            self._bot_stopped_at = time.perf_counter()
            logger.debug("Mic unmuting — bot stopped (trailing %.1fs)", self._trailing_secs)
        elif isinstance(frame, InputAudioRawFrame):
            if self._bot_speaking or self._in_trailing_window():
                return  # Drop — mute mic during bot speech + trailing

        await self.push_frame(frame, direction)
