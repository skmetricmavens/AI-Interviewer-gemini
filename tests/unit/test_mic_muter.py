"""Tests for MicMuter — drops audio input while bot is speaking."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from pipecat.frames.frames import (
    BotStartedSpeakingFrame,
    BotStoppedSpeakingFrame,
    InputAudioRawFrame,
    TranscriptionFrame,
)
from pipecat.processors.frame_processor import FrameDirection

from src.interview.mic_muter import MicMuter


def _audio_frame() -> InputAudioRawFrame:
    """Create a minimal InputAudioRawFrame."""
    return InputAudioRawFrame(audio=b"\x00" * 320, sample_rate=16000, num_channels=1)


class TestMicMuterInit:
    """Verify constructor and initial state."""

    def test_default_trailing_secs(self) -> None:
        m = MicMuter()
        assert m._trailing_secs == 1.5

    def test_custom_trailing_secs(self) -> None:
        m = MicMuter(trailing_secs=2.0)
        assert m._trailing_secs == 2.0

    def test_bot_speaking_initially_false(self) -> None:
        m = MicMuter()
        assert m._bot_speaking is False


class TestMicMuteDuringBotSpeech:
    """Audio input must be dropped while bot is speaking."""

    @pytest.mark.asyncio
    async def test_audio_dropped_while_bot_speaking(self) -> None:
        m = MicMuter()
        m.push_frame = AsyncMock()  # type: ignore[method-assign]

        await m.process_frame(BotStartedSpeakingFrame(), FrameDirection.DOWNSTREAM)

        audio = _audio_frame()
        await m.process_frame(audio, FrameDirection.DOWNSTREAM)

        pushed = [call.args[0] for call in m.push_frame.call_args_list]
        assert audio not in pushed

    @pytest.mark.asyncio
    async def test_audio_passes_when_bot_not_speaking(self) -> None:
        m = MicMuter(trailing_secs=0.0)
        m.push_frame = AsyncMock()  # type: ignore[method-assign]

        audio = _audio_frame()
        await m.process_frame(audio, FrameDirection.DOWNSTREAM)

        pushed = [call.args[0] for call in m.push_frame.call_args_list]
        assert audio in pushed

    @pytest.mark.asyncio
    async def test_non_audio_frames_pass_while_bot_speaking(self) -> None:
        """TranscriptionFrames and other frames should pass through."""
        m = MicMuter()
        m.push_frame = AsyncMock()  # type: ignore[method-assign]

        await m.process_frame(BotStartedSpeakingFrame(), FrameDirection.DOWNSTREAM)

        tf = TranscriptionFrame(text="hello", user_id="u", timestamp="ts")
        await m.process_frame(tf, FrameDirection.DOWNSTREAM)

        pushed = [call.args[0] for call in m.push_frame.call_args_list]
        assert tf in pushed

    @pytest.mark.asyncio
    async def test_bot_speaking_frames_forwarded(self) -> None:
        m = MicMuter()
        m.push_frame = AsyncMock()  # type: ignore[method-assign]

        start = BotStartedSpeakingFrame()
        stop = BotStoppedSpeakingFrame()
        await m.process_frame(start, FrameDirection.DOWNSTREAM)
        await m.process_frame(stop, FrameDirection.DOWNSTREAM)

        pushed = [call.args[0] for call in m.push_frame.call_args_list]
        assert start in pushed
        assert stop in pushed


class TestMicMuteTrailingWindow:
    """Audio stays muted for a trailing window after bot stops."""

    @pytest.mark.asyncio
    async def test_audio_dropped_during_trailing_window(self) -> None:
        m = MicMuter(trailing_secs=1.5)
        m.push_frame = AsyncMock()  # type: ignore[method-assign]

        await m.process_frame(BotStartedSpeakingFrame(), FrameDirection.DOWNSTREAM)
        await m.process_frame(BotStoppedSpeakingFrame(), FrameDirection.DOWNSTREAM)

        # Immediately after stop — within trailing window
        audio = _audio_frame()
        await m.process_frame(audio, FrameDirection.DOWNSTREAM)

        pushed = [call.args[0] for call in m.push_frame.call_args_list]
        assert audio not in pushed

    @pytest.mark.asyncio
    async def test_audio_passes_after_trailing_window(self) -> None:
        m = MicMuter(trailing_secs=1.5)
        m.push_frame = AsyncMock()  # type: ignore[method-assign]

        await m.process_frame(BotStartedSpeakingFrame(), FrameDirection.DOWNSTREAM)

        with patch("time.perf_counter") as mock_time:
            mock_time.return_value = 100.0
            await m.process_frame(BotStoppedSpeakingFrame(), FrameDirection.DOWNSTREAM)

            # 2.0 seconds later — past trailing window
            mock_time.return_value = 102.0
            audio = _audio_frame()
            await m.process_frame(audio, FrameDirection.DOWNSTREAM)

        pushed = [call.args[0] for call in m.push_frame.call_args_list]
        assert audio in pushed

    @pytest.mark.asyncio
    async def test_trailing_zero_allows_immediate_audio(self) -> None:
        m = MicMuter(trailing_secs=0.0)
        m.push_frame = AsyncMock()  # type: ignore[method-assign]

        await m.process_frame(BotStartedSpeakingFrame(), FrameDirection.DOWNSTREAM)

        with patch("time.perf_counter") as mock_time:
            mock_time.return_value = 100.0
            await m.process_frame(BotStoppedSpeakingFrame(), FrameDirection.DOWNSTREAM)

            mock_time.return_value = 100.001
            audio = _audio_frame()
            await m.process_frame(audio, FrameDirection.DOWNSTREAM)

        pushed = [call.args[0] for call in m.push_frame.call_args_list]
        assert audio in pushed
