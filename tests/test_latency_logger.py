"""Tests for src.interview.latency_logger — LatencyLogger pure logic."""

import time
from unittest.mock import patch

from src.interview.latency_logger import LatencyLogger


class TestLatencyLoggerInit:
    """Verify LatencyLogger initialisation creates expected attributes."""

    def test_has_timestamps_dict(self) -> None:
        logger = LatencyLogger()
        assert hasattr(logger, "_timestamps")
        assert isinstance(logger._timestamps, dict)

    def test_timestamps_starts_empty(self) -> None:
        logger = LatencyLogger()
        assert logger._timestamps == {}

    def test_has_logger(self) -> None:
        logger = LatencyLogger()
        assert hasattr(logger, "_logger")


class TestLatencyLoggerRecord:
    """Verify _record and _elapsed pure-logic methods."""

    def test_record_stores_timestamp(self) -> None:
        logger = LatencyLogger()
        logger._record("user_stopped")
        assert "user_stopped" in logger._timestamps
        assert isinstance(logger._timestamps["user_stopped"], float)

    def test_record_overwrites_previous(self) -> None:
        logger = LatencyLogger()
        logger._record("user_stopped")
        first = logger._timestamps["user_stopped"]
        # Small sleep to guarantee a different perf_counter value
        time.sleep(0.001)
        logger._record("user_stopped")
        second = logger._timestamps["user_stopped"]
        assert second > first

    def test_elapsed_returns_none_when_no_start(self) -> None:
        logger = LatencyLogger()
        # Only end event recorded, start missing
        logger._record("llm_start")
        result = logger._elapsed("user_stopped", "llm_start")
        assert result is None

    def test_elapsed_returns_none_when_no_end(self) -> None:
        logger = LatencyLogger()
        # Only start event recorded, end missing
        logger._record("user_stopped")
        result = logger._elapsed("user_stopped", "llm_start")
        assert result is None

    def test_elapsed_returns_none_when_neither_exist(self) -> None:
        logger = LatencyLogger()
        result = logger._elapsed("user_stopped", "llm_start")
        assert result is None

    def test_elapsed_returns_float_when_both_exist(self) -> None:
        logger = LatencyLogger()
        logger._record("user_stopped")
        time.sleep(0.001)
        logger._record("llm_start")
        result = logger._elapsed("user_stopped", "llm_start")
        assert isinstance(result, float)

    def test_elapsed_returns_positive_value(self) -> None:
        logger = LatencyLogger()
        logger._record("user_stopped")
        time.sleep(0.001)
        logger._record("llm_start")
        result = logger._elapsed("user_stopped", "llm_start")
        assert result is not None
        assert result > 0.0
