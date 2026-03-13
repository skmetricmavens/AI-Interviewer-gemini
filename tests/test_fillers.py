"""Tests for src.interview.fillers — filler phrases and random filler selection."""

import pytest

from src.interview.fillers import FILLER_PHRASES, FillerProcessor, get_random_filler


class TestFillerPhrases:
    """Verify FILLER_PHRASES contains correct entries for supported languages."""

    def test_en_fillers_exist(self) -> None:
        assert "en" in FILLER_PHRASES
        assert len(FILLER_PHRASES["en"]) > 0

    def test_nl_fillers_exist(self) -> None:
        assert "nl" in FILLER_PHRASES
        assert len(FILLER_PHRASES["nl"]) > 0

    def test_en_fillers_are_strings(self) -> None:
        for phrase in FILLER_PHRASES["en"]:
            assert isinstance(phrase, str)

    def test_nl_fillers_are_strings(self) -> None:
        for phrase in FILLER_PHRASES["nl"]:
            assert isinstance(phrase, str)

    def test_en_fillers_are_short(self) -> None:
        for phrase in FILLER_PHRASES["en"]:
            assert len(phrase) < 30, f"English filler too long: {phrase!r}"

    def test_nl_fillers_are_short(self) -> None:
        for phrase in FILLER_PHRASES["nl"]:
            assert len(phrase) < 30, f"Dutch filler too long: {phrase!r}"

    def test_no_duplicate_fillers_en(self) -> None:
        en = FILLER_PHRASES["en"]
        assert len(en) == len(set(en)), "English fillers contain duplicates"

    def test_no_duplicate_fillers_nl(self) -> None:
        nl = FILLER_PHRASES["nl"]
        assert len(nl) == len(set(nl)), "Dutch fillers contain duplicates"


class TestGetRandomFiller:
    """Verify get_random_filler returns appropriate filler phrases."""

    def test_returns_string(self) -> None:
        result = get_random_filler("en")
        assert isinstance(result, str)

    def test_returns_en_filler_from_list(self) -> None:
        result = get_random_filler("en")
        assert result in FILLER_PHRASES["en"]

    def test_returns_nl_filler_from_list(self) -> None:
        result = get_random_filler("nl")
        assert result in FILLER_PHRASES["nl"]

    def test_unknown_language_defaults_to_en(self) -> None:
        result = get_random_filler("xx")
        assert result in FILLER_PHRASES["en"]

    def test_empty_language_defaults_to_en(self) -> None:
        result = get_random_filler("")
        assert result in FILLER_PHRASES["en"]

    def test_randomness(self) -> None:
        """Calling 20 times should produce at least 2 different results."""
        results = {get_random_filler("en") for _ in range(20)}
        assert len(results) >= 2, "Expected at least 2 distinct fillers in 20 calls"


class TestFillerProcessorInit:
    """Verify FillerProcessor stores constructor arguments correctly."""

    def test_stores_language(self) -> None:
        processor = FillerProcessor(language="nl")
        assert processor.language == "nl"

    def test_stores_timeout(self) -> None:
        processor = FillerProcessor(language="en", timeout_secs=1.0)
        assert processor.timeout_secs == 1.0

    def test_default_timeout_is_0_4(self) -> None:
        processor = FillerProcessor(language="en")
        assert processor.timeout_secs == pytest.approx(0.4)
