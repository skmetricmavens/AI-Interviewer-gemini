"""Tests for src.persona.analyzer — PersonaAnalyzer and AI_VOCABULARY_BLOCKLIST."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.persona.analyzer import AI_VOCABULARY_BLOCKLIST, PersonaAnalyzer


# ---------------------------------------------------------------------------
# AI_VOCABULARY_BLOCKLIST tests
# ---------------------------------------------------------------------------


class TestAIVocabularyBlocklist:
    """Verify the blocklist constant contains expected AI-sounding words."""

    def test_contains_delve(self) -> None:
        assert "delve" in AI_VOCABULARY_BLOCKLIST

    def test_contains_pivotal(self) -> None:
        assert "pivotal" in AI_VOCABULARY_BLOCKLIST

    def test_contains_tapestry(self) -> None:
        assert "tapestry" in AI_VOCABULARY_BLOCKLIST

    def test_contains_leverage(self) -> None:
        assert "leverage" in AI_VOCABULARY_BLOCKLIST

    def test_has_at_least_15_entries(self) -> None:
        assert len(AI_VOCABULARY_BLOCKLIST) >= 15

    def test_is_a_list_of_strings(self) -> None:
        assert isinstance(AI_VOCABULARY_BLOCKLIST, list)
        for word in AI_VOCABULARY_BLOCKLIST:
            assert isinstance(word, str)


# ---------------------------------------------------------------------------
# PersonaAnalyzer constructor tests
# ---------------------------------------------------------------------------


class TestPersonaAnalyzerInit:
    """Verify the constructor stores the API key."""

    def test_stores_api_key(self) -> None:
        analyzer = PersonaAnalyzer(anthropic_api_key="test-key-123")
        assert analyzer.anthropic_api_key == "test-key-123"

    def test_stores_different_api_key(self) -> None:
        analyzer = PersonaAnalyzer(anthropic_api_key="another-key")
        assert analyzer.anthropic_api_key == "another-key"


# ---------------------------------------------------------------------------
# _read_samples tests
# ---------------------------------------------------------------------------


class TestReadSamples:
    """Verify _read_samples reads the correct file types from a directory."""

    def test_reads_txt_files(self, tmp_path: Path) -> None:
        (tmp_path / "sample1.txt").write_text("Hello from sample one.")
        (tmp_path / "sample2.txt").write_text("Hello from sample two.")

        analyzer = PersonaAnalyzer(anthropic_api_key="k")
        results = analyzer._read_samples(str(tmp_path))

        assert len(results) == 2
        assert "Hello from sample one." in results
        assert "Hello from sample two." in results

    def test_reads_md_files(self, tmp_path: Path) -> None:
        (tmp_path / "notes.md").write_text("# Markdown content")

        analyzer = PersonaAnalyzer(anthropic_api_key="k")
        results = analyzer._read_samples(str(tmp_path))

        assert len(results) == 1
        assert "# Markdown content" in results[0]

    def test_reads_both_txt_and_md(self, tmp_path: Path) -> None:
        (tmp_path / "a.txt").write_text("text content")
        (tmp_path / "b.md").write_text("markdown content")

        analyzer = PersonaAnalyzer(anthropic_api_key="k")
        results = analyzer._read_samples(str(tmp_path))

        assert len(results) == 2

    def test_ignores_non_txt_md_files(self, tmp_path: Path) -> None:
        (tmp_path / "a.txt").write_text("keep this")
        (tmp_path / "photo.jpg").write_bytes(b"\x00\x01\x02")
        (tmp_path / "doc.pdf").write_bytes(b"%PDF")
        (tmp_path / "data.csv").write_text("a,b,c")

        analyzer = PersonaAnalyzer(anthropic_api_key="k")
        results = analyzer._read_samples(str(tmp_path))

        assert len(results) == 1
        assert "keep this" in results[0]

    def test_empty_directory_returns_empty_list(self, tmp_path: Path) -> None:
        analyzer = PersonaAnalyzer(anthropic_api_key="k")
        results = analyzer._read_samples(str(tmp_path))

        assert results == []


# ---------------------------------------------------------------------------
# _build_analysis_prompt tests
# ---------------------------------------------------------------------------


class TestBuildAnalysisPrompt:
    """Verify _build_analysis_prompt constructs a proper prompt string."""

    def test_includes_sample_text(self) -> None:
        analyzer = PersonaAnalyzer(anthropic_api_key="k")
        prompt = analyzer._build_analysis_prompt(["This is my writing sample."])

        assert "This is my writing sample." in prompt

    def test_includes_multiple_samples(self) -> None:
        analyzer = PersonaAnalyzer(anthropic_api_key="k")
        samples = ["First sample text.", "Second sample text."]
        prompt = analyzer._build_analysis_prompt(samples)

        assert "First sample text." in prompt
        assert "Second sample text." in prompt

    def test_returns_non_empty_string(self) -> None:
        analyzer = PersonaAnalyzer(anthropic_api_key="k")
        prompt = analyzer._build_analysis_prompt(["Some text."])

        assert isinstance(prompt, str)
        assert len(prompt) > 0


# ---------------------------------------------------------------------------
# save_fingerprint / load_fingerprint tests
# ---------------------------------------------------------------------------


class TestFingerprintPersistence:
    """Verify save and load of fingerprint JSON files."""

    SAMPLE_FINGERPRINT: dict = {
        "sentence_length_avg": 14.5,
        "vocabulary_preferences": ["concise", "technical"],
        "transition_style": "minimal",
        "jargon": ["API", "endpoint"],
        "emoji_usage": "none",
        "tone": "professional",
    }

    def test_save_fingerprint_writes_valid_json(self, tmp_path: Path) -> None:
        filepath = tmp_path / "fingerprint.json"
        analyzer = PersonaAnalyzer(anthropic_api_key="k")
        analyzer.save_fingerprint(self.SAMPLE_FINGERPRINT, str(filepath))

        raw = filepath.read_text()
        parsed = json.loads(raw)
        assert parsed == self.SAMPLE_FINGERPRINT

    def test_load_fingerprint_reads_json(self, tmp_path: Path) -> None:
        filepath = tmp_path / "fingerprint.json"
        filepath.write_text(json.dumps(self.SAMPLE_FINGERPRINT))

        analyzer = PersonaAnalyzer(anthropic_api_key="k")
        result = analyzer.load_fingerprint(str(filepath))

        assert result == self.SAMPLE_FINGERPRINT

    def test_save_load_roundtrip_preserves_data(self, tmp_path: Path) -> None:
        filepath = tmp_path / "roundtrip.json"
        analyzer = PersonaAnalyzer(anthropic_api_key="k")

        analyzer.save_fingerprint(self.SAMPLE_FINGERPRINT, str(filepath))
        loaded = analyzer.load_fingerprint(str(filepath))

        assert loaded == self.SAMPLE_FINGERPRINT

    def test_load_fingerprint_returns_dict(self, tmp_path: Path) -> None:
        filepath = tmp_path / "fp.json"
        filepath.write_text(json.dumps({"tone": "casual"}))

        analyzer = PersonaAnalyzer(anthropic_api_key="k")
        result = analyzer.load_fingerprint(str(filepath))

        assert isinstance(result, dict)


# ---------------------------------------------------------------------------
# analyze_samples tests (mocked Claude API)
# ---------------------------------------------------------------------------


class TestAnalyzeSamples:
    """Verify analyze_samples orchestrates reading, prompting, and API call."""

    def test_returns_dict_with_mocked_api(self, tmp_path: Path) -> None:
        # Create sample files
        (tmp_path / "sample.txt").write_text("I like to write short sentences.")

        fake_fingerprint = {
            "sentence_length_avg": 6.0,
            "vocabulary_preferences": ["short"],
            "transition_style": "direct",
            "jargon": [],
            "emoji_usage": "none",
            "tone": "casual",
        }

        analyzer = PersonaAnalyzer(anthropic_api_key="fake-key")

        # Mock the Anthropic client used inside analyze_samples
        mock_message = MagicMock()
        mock_message.content = [MagicMock(text=json.dumps(fake_fingerprint))]

        with patch("src.persona.analyzer.anthropic.Anthropic") as mock_cls:
            mock_client = MagicMock()
            mock_client.messages.create.return_value = mock_message
            mock_cls.return_value = mock_client

            result = analyzer.analyze_samples(str(tmp_path))

        assert isinstance(result, dict)
        assert result == fake_fingerprint

    def test_analyze_samples_calls_api_with_key(self, tmp_path: Path) -> None:
        (tmp_path / "note.txt").write_text("Some writing.")

        mock_message = MagicMock()
        mock_message.content = [MagicMock(text='{"tone": "neutral"}')]

        analyzer = PersonaAnalyzer(anthropic_api_key="my-secret-key")

        with patch("src.persona.analyzer.anthropic.Anthropic") as mock_cls:
            mock_client = MagicMock()
            mock_client.messages.create.return_value = mock_message
            mock_cls.return_value = mock_client

            analyzer.analyze_samples(str(tmp_path))

            mock_cls.assert_called_once_with(api_key="my-secret-key")
