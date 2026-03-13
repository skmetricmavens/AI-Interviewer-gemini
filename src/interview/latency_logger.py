"""Pipeline latency logger for measuring real-time performance.

Logs time deltas between key pipeline events:
- user_stopped → llm_start (STT + context processing)
- llm_start → tts_started (LLM generation + TTS synthesis)
- user_stopped → tts_started (total end-to-end latency)
"""

from __future__ import annotations

import logging
import time

from pipecat.frames.frames import (
    Frame,
    LLMFullResponseStartFrame,
    TTSStartedFrame,
    UserStoppedSpeakingFrame,
)
from pipecat.processors.frame_processor import FrameDirection, FrameProcessor

logger = logging.getLogger("ai_interviewer.latency")


class LatencyLogger(FrameProcessor):
    """Measures and logs latency between pipeline events."""

    def __init__(self) -> None:
        super().__init__()
        self._timestamps: dict[str, float] = {}
        self._logger = logger

    def _record(self, event_name: str) -> None:
        """Record current time for an event."""
        self._timestamps[event_name] = time.perf_counter()

    def _elapsed(self, start_event: str, end_event: str) -> float | None:
        """Return seconds between two recorded events, or None if missing."""
        start = self._timestamps.get(start_event)
        end = self._timestamps.get(end_event)
        if start is None or end is None:
            return None
        return end - start

    async def process_frame(self, frame: Frame, direction: FrameDirection) -> None:
        """Track timestamps for key frames and log latencies."""
        await super().process_frame(frame, direction)

        if isinstance(frame, UserStoppedSpeakingFrame):
            self._record("user_stopped")

        elif isinstance(frame, LLMFullResponseStartFrame):
            self._record("llm_start")
            delta = self._elapsed("user_stopped", "llm_start")
            if delta is not None:
                self._logger.info("STT→LLM: %.0fms", delta * 1000)

        elif isinstance(frame, TTSStartedFrame):
            self._record("tts_started")
            llm_tts = self._elapsed("llm_start", "tts_started")
            total = self._elapsed("user_stopped", "tts_started")
            if llm_tts is not None:
                self._logger.info("LLM→TTS: %.0fms", llm_tts * 1000)
            if total is not None:
                self._logger.info("Total latency: %.0fms", total * 1000)

        await self.push_frame(frame, direction)
