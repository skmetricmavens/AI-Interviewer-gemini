"""Interstitial filler system for natural conversation pacing.

Plays short filler phrases (e.g., "Hmm, interesting...") when the LLM
takes longer than a threshold to respond, filling the awkward silence.
"""

from __future__ import annotations

import asyncio
import random

from pipecat.frames.frames import (
    Frame,
    LLMFullResponseStartFrame,
    TTSTextFrame,
    UserStoppedSpeakingFrame,
)
from pipecat.processors.frame_processor import FrameDirection, FrameProcessor

FILLER_PHRASES: dict[str, list[str]] = {
    "en": [
        "Hmm, interesting...",
        "Right...",
        "Got it...",
        "Let me think...",
        "Good point...",
    ],
    "nl": [
        "Even kijken...",
        "Helder...",
        "Hm-hm...",
        "Goed punt...",
        "Eens kijken...",
    ],
}


def get_random_filler(language: str) -> str:
    """Return a random filler phrase for the given language.

    Unknown languages default to English.
    """
    phrases = FILLER_PHRASES.get(language, FILLER_PHRASES["en"])
    return random.choice(phrases)


class FillerProcessor(FrameProcessor):
    """Injects a filler phrase when LLM response is slow.

    Listens for UserStoppedSpeakingFrame, starts a timer. If no
    LLMFullResponseStartFrame arrives within timeout_secs, pushes
    a TTSTextFrame with a random filler phrase.
    """

    def __init__(self, *, language: str, timeout_secs: float = 0.4) -> None:
        super().__init__()
        self.language = language
        self.timeout_secs = timeout_secs
        self._llm_responded = asyncio.Event()
        self._timer_task: asyncio.Task[None] | None = None

    async def process_frame(self, frame: Frame, direction: FrameDirection) -> None:
        """Process frames, injecting fillers on slow LLM responses."""
        await super().process_frame(frame, direction)

        if isinstance(frame, UserStoppedSpeakingFrame):
            self._llm_responded.clear()
            if self._timer_task and not self._timer_task.done():
                self._timer_task.cancel()
            self._timer_task = self.get_event_loop().create_task(self._wait_and_fill())

        elif isinstance(frame, LLMFullResponseStartFrame):
            self._llm_responded.set()

        await self.push_frame(frame, direction)

    async def _wait_and_fill(self) -> None:
        """Wait for LLM response; inject filler if it takes too long."""
        try:
            await asyncio.wait_for(
                self._llm_responded.wait(),
                timeout=self.timeout_secs,
            )
        except asyncio.TimeoutError:
            filler = get_random_filler(self.language)
            await self.push_frame(TTSTextFrame(text=filler, aggregated_by="SENTENCE"))

    async def cleanup(self) -> None:
        """Cancel any pending timer on cleanup."""
        await super().cleanup()
        if self._timer_task and not self._timer_task.done():
            self._timer_task.cancel()
