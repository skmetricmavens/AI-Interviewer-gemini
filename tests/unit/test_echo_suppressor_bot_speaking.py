"""Tests for EchoSuppressor bot-speaking-state suppression.

These tests cover the enhanced EchoSuppressor that tracks bot speaking state
via BotStartedSpeakingFrame / BotStoppedSpeakingFrame and suppresses ALL
transcriptions while the bot is speaking plus a configurable trailing window.
"""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, patch

import pytest

from pipecat.frames.frames import (
    BotStartedSpeakingFrame,
    BotStoppedSpeakingFrame,
    Frame,
    TranscriptionFrame,
    TTSTextFrame,
)
from pipecat.processors.frame_processor import FrameDirection

from src.interview.echo_suppressor import EchoSuppressor


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _transcription(text: str = "Hello from user") -> TranscriptionFrame:
    """Create a TranscriptionFrame with required fields."""
    return TranscriptionFrame(text=text, user_id="user", timestamp="ts")


def _tts(text: str = "Bot says hello") -> TTSTextFrame:
    """Create a TTSTextFrame."""
    return TTSTextFrame(text=text, aggregated_by="SENTENCE")


# ---------------------------------------------------------------------------
# Init tests for new trailing_secs parameter
# ---------------------------------------------------------------------------

class TestBotSpeakingInit:
    """Verify new constructor parameter and initial state."""

    def test_default_trailing_secs(self) -> None:
        es = EchoSuppressor()
        assert es._trailing_secs == 1.5

    def test_custom_trailing_secs(self) -> None:
        es = EchoSuppressor(trailing_secs=2.0)
        assert es._trailing_secs == 2.0

    def test_bot_speaking_initially_false(self) -> None:
        es = EchoSuppressor()
        assert es._bot_speaking is False

    def test_bot_stopped_time_initially_none_or_zero(self) -> None:
        """The timestamp for when the bot stopped should start at 0 or None."""
        es = EchoSuppressor()
        # Accept either 0.0 or None as valid initial state
        assert es._bot_stopped_at is None or es._bot_stopped_at == 0.0


# ---------------------------------------------------------------------------
# Bot speaking state tracking (pure logic)
# ---------------------------------------------------------------------------

class TestBotSpeakingStateTracking:
    """Verify bot speaking state is tracked via frame processing."""

    @pytest.mark.asyncio
    async def test_bot_started_speaking_sets_flag(self) -> None:
        es = EchoSuppressor()
        es.push_frame = AsyncMock()  # type: ignore[method-assign]

        frame = BotStartedSpeakingFrame()
        await es.process_frame(frame, FrameDirection.DOWNSTREAM)

        assert es._bot_speaking is True

    @pytest.mark.asyncio
    async def test_bot_stopped_speaking_clears_flag(self) -> None:
        es = EchoSuppressor()
        es.push_frame = AsyncMock()  # type: ignore[method-assign]

        # Start speaking first
        await es.process_frame(BotStartedSpeakingFrame(), FrameDirection.DOWNSTREAM)
        assert es._bot_speaking is True

        # Then stop
        await es.process_frame(BotStoppedSpeakingFrame(), FrameDirection.DOWNSTREAM)
        assert es._bot_speaking is False

    @pytest.mark.asyncio
    async def test_bot_stopped_records_timestamp(self) -> None:
        es = EchoSuppressor()
        es.push_frame = AsyncMock()  # type: ignore[method-assign]

        await es.process_frame(BotStartedSpeakingFrame(), FrameDirection.DOWNSTREAM)
        await es.process_frame(BotStoppedSpeakingFrame(), FrameDirection.DOWNSTREAM)

        assert es._bot_stopped_at is not None
        assert isinstance(es._bot_stopped_at, float)
        assert es._bot_stopped_at > 0

    @pytest.mark.asyncio
    async def test_start_and_stop_frames_are_forwarded(self) -> None:
        """BotStarted/StoppedSpeakingFrames must be pushed downstream, not consumed."""
        es = EchoSuppressor()
        es.push_frame = AsyncMock()  # type: ignore[method-assign]

        start_frame = BotStartedSpeakingFrame()
        stop_frame = BotStoppedSpeakingFrame()

        await es.process_frame(start_frame, FrameDirection.DOWNSTREAM)
        await es.process_frame(stop_frame, FrameDirection.DOWNSTREAM)

        # Both frames should be pushed downstream
        pushed_frames = [call.args[0] for call in es.push_frame.call_args_list]
        assert start_frame in pushed_frames
        assert stop_frame in pushed_frames


# ---------------------------------------------------------------------------
# Suppression while bot is speaking
# ---------------------------------------------------------------------------

class TestSuppressionWhileBotSpeaking:
    """Transcriptions must be suppressed while bot is actively speaking."""

    @pytest.mark.asyncio
    async def test_transcription_suppressed_while_bot_speaking(self) -> None:
        es = EchoSuppressor()
        es.push_frame = AsyncMock()  # type: ignore[method-assign]

        # Bot starts speaking
        await es.process_frame(BotStartedSpeakingFrame(), FrameDirection.DOWNSTREAM)

        # Transcription arrives while bot is speaking
        tf = _transcription("Some echoed text from the bot")
        await es.process_frame(tf, FrameDirection.DOWNSTREAM)

        # The transcription should NOT appear in pushed frames
        pushed_frames = [call.args[0] for call in es.push_frame.call_args_list]
        assert tf not in pushed_frames

    @pytest.mark.asyncio
    async def test_multiple_transcriptions_suppressed_while_bot_speaking(self) -> None:
        es = EchoSuppressor()
        es.push_frame = AsyncMock()  # type: ignore[method-assign]

        await es.process_frame(BotStartedSpeakingFrame(), FrameDirection.DOWNSTREAM)

        transcriptions = [
            _transcription("First echo fragment"),
            _transcription("Second echo fragment"),
            _transcription("Third echo fragment"),
        ]
        for tf in transcriptions:
            await es.process_frame(tf, FrameDirection.DOWNSTREAM)

        pushed_frames = [call.args[0] for call in es.push_frame.call_args_list]
        for tf in transcriptions:
            assert tf not in pushed_frames

    @pytest.mark.asyncio
    async def test_non_transcription_frames_pass_while_bot_speaking(self) -> None:
        """Only TranscriptionFrames should be suppressed, other frames pass through."""
        es = EchoSuppressor()
        es.push_frame = AsyncMock()  # type: ignore[method-assign]

        await es.process_frame(BotStartedSpeakingFrame(), FrameDirection.DOWNSTREAM)

        # A TTS frame or other frame should still pass
        tts = _tts("Bot speaking text")
        await es.process_frame(tts, FrameDirection.DOWNSTREAM)

        pushed_frames = [call.args[0] for call in es.push_frame.call_args_list]
        assert tts in pushed_frames


# ---------------------------------------------------------------------------
# Trailing window suppression
# ---------------------------------------------------------------------------

class TestTrailingWindowSuppression:
    """Transcriptions within the trailing window after bot stops should be suppressed."""

    @pytest.mark.asyncio
    async def test_transcription_suppressed_during_trailing_window(self) -> None:
        """Right after bot stops, transcriptions should still be suppressed."""
        es = EchoSuppressor(trailing_secs=1.5)
        es.push_frame = AsyncMock()  # type: ignore[method-assign]

        # Bot speaks then stops
        await es.process_frame(BotStartedSpeakingFrame(), FrameDirection.DOWNSTREAM)
        await es.process_frame(BotStoppedSpeakingFrame(), FrameDirection.DOWNSTREAM)

        # Immediately after stop -- within trailing window
        tf = _transcription("Echo during trailing window")
        await es.process_frame(tf, FrameDirection.DOWNSTREAM)

        pushed_frames = [call.args[0] for call in es.push_frame.call_args_list]
        assert tf not in pushed_frames

    @pytest.mark.asyncio
    async def test_transcription_allowed_after_trailing_window_expires(self) -> None:
        """After trailing window expires, transcriptions should pass through."""
        es = EchoSuppressor(trailing_secs=1.5)
        es.push_frame = AsyncMock()  # type: ignore[method-assign]

        # Bot speaks then stops
        await es.process_frame(BotStartedSpeakingFrame(), FrameDirection.DOWNSTREAM)

        # Simulate bot stopped at a known time, then advance past trailing window
        with patch("time.perf_counter") as mock_time:
            mock_time.return_value = 100.0
            await es.process_frame(BotStoppedSpeakingFrame(), FrameDirection.DOWNSTREAM)

            # Now advance time past the trailing window
            mock_time.return_value = 102.0  # 2.0 seconds later, > 1.5 trailing
            tf = _transcription("Real user speech after trailing window")
            await es.process_frame(tf, FrameDirection.DOWNSTREAM)

        pushed_frames = [call.args[0] for call in es.push_frame.call_args_list]
        assert tf in pushed_frames

    @pytest.mark.asyncio
    async def test_transcription_suppressed_just_before_trailing_expires(self) -> None:
        """Transcription arriving just before trailing window expires is suppressed."""
        es = EchoSuppressor(trailing_secs=1.5)
        es.push_frame = AsyncMock()  # type: ignore[method-assign]

        await es.process_frame(BotStartedSpeakingFrame(), FrameDirection.DOWNSTREAM)

        with patch("time.perf_counter") as mock_time:
            mock_time.return_value = 100.0
            await es.process_frame(BotStoppedSpeakingFrame(), FrameDirection.DOWNSTREAM)

            # 1.4 seconds later -- just inside trailing window
            mock_time.return_value = 101.4
            tf = _transcription("Still within trailing window")
            await es.process_frame(tf, FrameDirection.DOWNSTREAM)

        pushed_frames = [call.args[0] for call in es.push_frame.call_args_list]
        assert tf not in pushed_frames

    @pytest.mark.asyncio
    async def test_custom_trailing_window_duration(self) -> None:
        """A custom trailing_secs value should be respected."""
        es = EchoSuppressor(trailing_secs=3.0)
        es.push_frame = AsyncMock()  # type: ignore[method-assign]

        await es.process_frame(BotStartedSpeakingFrame(), FrameDirection.DOWNSTREAM)

        with patch("time.perf_counter") as mock_time:
            mock_time.return_value = 100.0
            await es.process_frame(BotStoppedSpeakingFrame(), FrameDirection.DOWNSTREAM)

            # 2.5 seconds later -- inside 3.0 trailing window
            mock_time.return_value = 102.5
            tf_suppressed = _transcription("Should be suppressed")
            await es.process_frame(tf_suppressed, FrameDirection.DOWNSTREAM)

            # 3.5 seconds later -- outside 3.0 trailing window
            mock_time.return_value = 103.5
            tf_allowed = _transcription("Should pass through")
            await es.process_frame(tf_allowed, FrameDirection.DOWNSTREAM)

        pushed_frames = [call.args[0] for call in es.push_frame.call_args_list]
        assert tf_suppressed not in pushed_frames
        assert tf_allowed in pushed_frames


# ---------------------------------------------------------------------------
# Multiple start/stop cycles
# ---------------------------------------------------------------------------

class TestMultipleStartStopCycles:
    """Verify correct behavior across multiple bot speaking cycles."""

    @pytest.mark.asyncio
    async def test_second_speaking_cycle_suppresses(self) -> None:
        """A second bot speaking cycle should also suppress transcriptions."""
        es = EchoSuppressor(trailing_secs=1.5)
        es.push_frame = AsyncMock()  # type: ignore[method-assign]

        with patch("time.perf_counter") as mock_time:
            # First cycle
            mock_time.return_value = 100.0
            await es.process_frame(BotStartedSpeakingFrame(), FrameDirection.DOWNSTREAM)
            mock_time.return_value = 105.0
            await es.process_frame(BotStoppedSpeakingFrame(), FrameDirection.DOWNSTREAM)

            # Allow trailing to expire
            mock_time.return_value = 107.0
            tf_between = _transcription("User speaks between cycles")
            await es.process_frame(tf_between, FrameDirection.DOWNSTREAM)

            # Second cycle
            mock_time.return_value = 110.0
            await es.process_frame(BotStartedSpeakingFrame(), FrameDirection.DOWNSTREAM)

            mock_time.return_value = 111.0
            tf_during_second = _transcription("Echo during second cycle")
            await es.process_frame(tf_during_second, FrameDirection.DOWNSTREAM)

        pushed_frames = [call.args[0] for call in es.push_frame.call_args_list]
        assert tf_between in pushed_frames
        assert tf_during_second not in pushed_frames

    @pytest.mark.asyncio
    async def test_new_start_resets_trailing_window(self) -> None:
        """If bot starts speaking again during trailing window, the state resets."""
        es = EchoSuppressor(trailing_secs=1.5)
        es.push_frame = AsyncMock()  # type: ignore[method-assign]

        with patch("time.perf_counter") as mock_time:
            # First cycle: start and stop
            mock_time.return_value = 100.0
            await es.process_frame(BotStartedSpeakingFrame(), FrameDirection.DOWNSTREAM)
            mock_time.return_value = 103.0
            await es.process_frame(BotStoppedSpeakingFrame(), FrameDirection.DOWNSTREAM)

            # During trailing window, bot starts speaking again
            mock_time.return_value = 103.5
            await es.process_frame(BotStartedSpeakingFrame(), FrameDirection.DOWNSTREAM)
            assert es._bot_speaking is True

            # Transcription during second speaking period should be suppressed
            mock_time.return_value = 104.0
            tf = _transcription("Echo during restart")
            await es.process_frame(tf, FrameDirection.DOWNSTREAM)

            # Stop again
            mock_time.return_value = 106.0
            await es.process_frame(BotStoppedSpeakingFrame(), FrameDirection.DOWNSTREAM)

            # After new trailing window expires, transcriptions should pass
            mock_time.return_value = 108.0
            tf_after = _transcription("User speech after second cycle")
            await es.process_frame(tf_after, FrameDirection.DOWNSTREAM)

        pushed_frames = [call.args[0] for call in es.push_frame.call_args_list]
        assert tf not in pushed_frames
        assert tf_after in pushed_frames


# ---------------------------------------------------------------------------
# Text-similarity fallback still works
# ---------------------------------------------------------------------------

class TestTextSimilarityFallbackStillWorks:
    """Text-similarity echo detection must still work when bot is NOT speaking."""

    @pytest.mark.asyncio
    async def test_text_similarity_suppresses_when_bot_not_speaking(self) -> None:
        """Even when bot is not speaking, text-similarity should catch echoes."""
        es = EchoSuppressor(trailing_secs=0.0)  # No trailing window
        es.push_frame = AsyncMock()  # type: ignore[method-assign]

        # Record a bot utterance via TTS frame
        tts = _tts("That is a really fascinating insight you have there")
        await es.process_frame(tts, FrameDirection.DOWNSTREAM)

        # A transcription that matches the bot utterance by text similarity
        # (bot is NOT in speaking state -- no BotStartedSpeakingFrame sent)
        with patch("time.perf_counter") as mock_time:
            mock_time.return_value = 100.0
            # Re-record with known timestamp for the similarity window
            es._bot_utterances.clear()
            es._bot_utterances.append(
                ("that is a really fascinating insight you have there", 99.5)
            )

            tf = _transcription("That is a really fascinating insight you have there")
            await es.process_frame(tf, FrameDirection.DOWNSTREAM)

        pushed_frames = [call.args[0] for call in es.push_frame.call_args_list]
        assert tf not in pushed_frames

    @pytest.mark.asyncio
    async def test_non_matching_text_passes_when_bot_not_speaking(self) -> None:
        """User speech that does not match bot text should pass through normally."""
        es = EchoSuppressor(trailing_secs=0.0)
        es.push_frame = AsyncMock()  # type: ignore[method-assign]

        tts = _tts("What do you think about machine learning?")
        await es.process_frame(tts, FrameDirection.DOWNSTREAM)

        tf = _transcription("I have been working on this project for three years")
        await es.process_frame(tf, FrameDirection.DOWNSTREAM)

        pushed_frames = [call.args[0] for call in es.push_frame.call_args_list]
        assert tf in pushed_frames


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

class TestBotSpeakingEdgeCases:
    """Edge cases for bot-speaking-state suppression."""

    @pytest.mark.asyncio
    async def test_stop_without_start_does_not_crash(self) -> None:
        """Receiving BotStoppedSpeakingFrame without a prior start should not error."""
        es = EchoSuppressor()
        es.push_frame = AsyncMock()  # type: ignore[method-assign]

        # Should not raise
        await es.process_frame(BotStoppedSpeakingFrame(), FrameDirection.DOWNSTREAM)
        assert es._bot_speaking is False

    @pytest.mark.asyncio
    async def test_double_start_does_not_crash(self) -> None:
        """Receiving two BotStartedSpeakingFrames in a row should be handled."""
        es = EchoSuppressor()
        es.push_frame = AsyncMock()  # type: ignore[method-assign]

        await es.process_frame(BotStartedSpeakingFrame(), FrameDirection.DOWNSTREAM)
        await es.process_frame(BotStartedSpeakingFrame(), FrameDirection.DOWNSTREAM)
        assert es._bot_speaking is True

    @pytest.mark.asyncio
    async def test_trailing_secs_zero_disables_trailing_window(self) -> None:
        """With trailing_secs=0, transcription should pass immediately after stop."""
        es = EchoSuppressor(trailing_secs=0.0)
        es.push_frame = AsyncMock()  # type: ignore[method-assign]

        await es.process_frame(BotStartedSpeakingFrame(), FrameDirection.DOWNSTREAM)

        with patch("time.perf_counter") as mock_time:
            mock_time.return_value = 100.0
            await es.process_frame(BotStoppedSpeakingFrame(), FrameDirection.DOWNSTREAM)

            # Immediately after stop with trailing=0, should pass
            mock_time.return_value = 100.001
            tf = _transcription("User speaks right away")
            await es.process_frame(tf, FrameDirection.DOWNSTREAM)

        pushed_frames = [call.args[0] for call in es.push_frame.call_args_list]
        assert tf in pushed_frames
