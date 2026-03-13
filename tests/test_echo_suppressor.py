"""Tests for src.interview.echo_suppressor — EchoSuppressor pure logic."""

import time

from src.interview.echo_suppressor import EchoSuppressor


class TestEchoSuppressorInit:
    """Verify EchoSuppressor initialises with expected attributes."""

    def test_has_bot_utterances_deque(self) -> None:
        es = EchoSuppressor()
        assert hasattr(es, "_bot_utterances")
        assert len(es._bot_utterances) == 0

    def test_default_threshold(self) -> None:
        es = EchoSuppressor()
        assert es._threshold == 0.6

    def test_default_window_secs(self) -> None:
        es = EchoSuppressor()
        assert es._window_secs == 8.0

    def test_default_min_length(self) -> None:
        es = EchoSuppressor()
        assert es._min_length == 1

    def test_custom_threshold(self) -> None:
        es = EchoSuppressor(threshold=0.8)
        assert es._threshold == 0.8

    def test_custom_window_secs(self) -> None:
        es = EchoSuppressor(window_secs=5.0)
        assert es._window_secs == 5.0

    def test_custom_min_length(self) -> None:
        es = EchoSuppressor(min_length=5)
        assert es._min_length == 5

    def test_deque_has_max_size(self) -> None:
        es = EchoSuppressor()
        assert es._bot_utterances.maxlen == 10


class TestRecordBotUtterance:
    """Verify record_bot_utterance stores text with timestamp."""

    def test_records_utterance(self) -> None:
        es = EchoSuppressor()
        es.record_bot_utterance("Hello, great to have you!")
        assert len(es._bot_utterances) == 1

    def test_records_text_and_timestamp(self) -> None:
        es = EchoSuppressor()
        es.record_bot_utterance("Hello!")
        text, ts = es._bot_utterances[0]
        assert text == "hello!"
        assert isinstance(ts, float)

    def test_normalizes_to_lowercase(self) -> None:
        es = EchoSuppressor()
        es.record_bot_utterance("Oh Wow, Interesting!")
        text, _ = es._bot_utterances[0]
        assert text == "oh wow, interesting!"

    def test_multiple_utterances_stored(self) -> None:
        es = EchoSuppressor()
        es.record_bot_utterance("First")
        es.record_bot_utterance("Second")
        assert len(es._bot_utterances) == 2

    def test_deque_evicts_oldest_when_full(self) -> None:
        es = EchoSuppressor()
        for i in range(12):
            es.record_bot_utterance(f"Utterance number {i}")
        assert len(es._bot_utterances) == 10
        # Oldest (0, 1) should be evicted
        texts = [t for t, _ in es._bot_utterances]
        assert "utterance number 0" not in texts
        assert "utterance number 1" not in texts
        assert "utterance number 11" in texts


class TestIsEcho:
    """Verify is_echo correctly identifies echoed bot speech."""

    def test_exact_match_is_echo(self) -> None:
        es = EchoSuppressor()
        es.record_bot_utterance("That's really interesting, tell me more")
        assert es.is_echo("That's really interesting, tell me more") is True

    def test_case_insensitive_match(self) -> None:
        es = EchoSuppressor()
        es.record_bot_utterance("That's really interesting")
        assert es.is_echo("THAT'S REALLY INTERESTING") is True

    def test_partial_match_is_echo(self) -> None:
        """STT often captures fragments of bot speech."""
        es = EchoSuppressor()
        es.record_bot_utterance("That's really interesting, tell me more about it")
        assert es.is_echo("really interesting tell me more") is True

    def test_different_text_not_echo(self) -> None:
        es = EchoSuppressor()
        es.record_bot_utterance("What do you think about machine learning?")
        assert es.is_echo("I think it's fascinating") is False

    def test_short_text_below_min_length_not_suppressed(self) -> None:
        """Very short transcripts like 'yeah' or 'ok' should not be suppressed."""
        es = EchoSuppressor(min_length=3)
        es.record_bot_utterance("Yeah, that makes sense")
        assert es.is_echo("Yeah") is False

    def test_text_at_min_length_is_checked(self) -> None:
        es = EchoSuppressor(min_length=3)
        es.record_bot_utterance("Right right right makes sense")
        assert es.is_echo("right right right") is True

    def test_no_bot_utterances_not_echo(self) -> None:
        es = EchoSuppressor()
        assert es.is_echo("Hello there") is False

    def test_expired_utterance_not_echo(self) -> None:
        """Utterances outside the time window should not cause suppression."""
        es = EchoSuppressor(window_secs=0.01)
        es.record_bot_utterance("That's interesting")
        time.sleep(0.02)
        assert es.is_echo("That's interesting") is False

    def test_within_window_is_echo(self) -> None:
        es = EchoSuppressor(window_secs=10.0)
        es.record_bot_utterance("That's really quite interesting")
        assert es.is_echo("That's really quite interesting") is True

    def test_high_threshold_requires_closer_match(self) -> None:
        es = EchoSuppressor(threshold=0.95)
        es.record_bot_utterance("What do you think about this topic?")
        # A loose match should fail with high threshold
        assert es.is_echo("What do you think") is False

    def test_low_threshold_accepts_loose_match(self) -> None:
        es = EchoSuppressor(threshold=0.3)
        es.record_bot_utterance("What do you think about this particular topic?")
        assert es.is_echo("What do you think") is True

    def test_fuzzy_match_with_stt_artifacts(self) -> None:
        """STT may add/remove punctuation or slightly alter words."""
        es = EchoSuppressor(threshold=0.6)
        es.record_bot_utterance("Hmm, that's a really good point.")
        assert es.is_echo("Hmm that's a really good point") is True

    def test_empty_text_not_echo(self) -> None:
        es = EchoSuppressor()
        es.record_bot_utterance("Something")
        assert es.is_echo("") is False

    def test_whitespace_only_not_echo(self) -> None:
        es = EchoSuppressor()
        es.record_bot_utterance("Something")
        assert es.is_echo("   ") is False
