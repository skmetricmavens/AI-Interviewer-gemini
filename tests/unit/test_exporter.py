"""Tests for TranscriptExporter in src.storage.exporter."""

import json

import pytest

from src.storage.exporter import TranscriptExporter


@pytest.fixture
def exporter() -> TranscriptExporter:
    return TranscriptExporter()


@pytest.fixture
def sample_transcript() -> list[dict[str, str]]:
    return [
        {"role": "interviewer", "content": "What inspired you to start this project?"},
        {"role": "interviewee", "content": "I wanted to solve a real problem."},
        {"role": "interviewer", "content": "Can you tell me more about that?"},
        {"role": "interviewee", "content": "Sure. It started with a personal frustration."},
    ]


@pytest.fixture
def sample_metadata() -> dict[str, str]:
    return {
        "id": "session-001",
        "topic": "AI in Healthcare",
        "language": "en",
        "started_at": "2026-03-08T10:00:00",
        "ended_at": "2026-03-08T10:30:00",
        "interviewee_name": "Dr. Smith",
        "content_pillar": "connected_journey",
        "target_architecture": "linkedin_post",
        "target_audience": "tech_leaders",
    }


class TestTranscriptExporterInit:
    """Verify TranscriptExporter instantiation."""

    def test_can_instantiate(self) -> None:
        exporter = TranscriptExporter()
        assert exporter is not None

    def test_no_required_params(self) -> None:
        # Should not raise
        TranscriptExporter()


class TestToMarkdown:
    """Verify markdown export."""

    def test_basic_transcript(
        self, exporter: TranscriptExporter, sample_transcript: list[dict[str, str]]
    ) -> None:
        result = exporter.to_markdown(sample_transcript)
        assert "**interviewer**" in result.lower() or "**Interviewer**" in result
        assert "What inspired you to start this project?" in result
        assert "I wanted to solve a real problem." in result

    def test_returns_string(
        self, exporter: TranscriptExporter, sample_transcript: list[dict[str, str]]
    ) -> None:
        result = exporter.to_markdown(sample_transcript)
        assert isinstance(result, str)

    def test_with_metadata_header(
        self,
        exporter: TranscriptExporter,
        sample_transcript: list[dict[str, str]],
        sample_metadata: dict[str, str],
    ) -> None:
        result = exporter.to_markdown(sample_transcript, session_metadata=sample_metadata)
        assert "AI in Healthcare" in result
        assert "Dr. Smith" in result
        assert "session-001" in result

    def test_without_metadata(
        self, exporter: TranscriptExporter, sample_transcript: list[dict[str, str]]
    ) -> None:
        result = exporter.to_markdown(sample_transcript)
        # Should still work, just no metadata header
        assert "What inspired you to start this project?" in result

    def test_empty_transcript(self, exporter: TranscriptExporter) -> None:
        result = exporter.to_markdown([])
        assert isinstance(result, str)

    def test_all_entries_present(
        self, exporter: TranscriptExporter, sample_transcript: list[dict[str, str]]
    ) -> None:
        result = exporter.to_markdown(sample_transcript)
        for entry in sample_transcript:
            assert entry["content"] in result

    def test_metadata_none_default(
        self, exporter: TranscriptExporter, sample_transcript: list[dict[str, str]]
    ) -> None:
        # Calling without metadata keyword should work
        result_no_meta = exporter.to_markdown(sample_transcript)
        result_none = exporter.to_markdown(sample_transcript, session_metadata=None)
        assert result_no_meta == result_none


class TestToPlainText:
    """Verify plain text export."""

    def test_basic_format(
        self, exporter: TranscriptExporter, sample_transcript: list[dict[str, str]]
    ) -> None:
        result = exporter.to_plain_text(sample_transcript)
        # Should use ROLE: content format
        assert "interviewer: What inspired you to start this project?" in result.lower() or \
            "INTERVIEWER: What inspired you to start this project?" in result

    def test_returns_string(
        self, exporter: TranscriptExporter, sample_transcript: list[dict[str, str]]
    ) -> None:
        result = exporter.to_plain_text(sample_transcript)
        assert isinstance(result, str)

    def test_all_entries_present(
        self, exporter: TranscriptExporter, sample_transcript: list[dict[str, str]]
    ) -> None:
        result = exporter.to_plain_text(sample_transcript)
        for entry in sample_transcript:
            assert entry["content"] in result

    def test_empty_transcript(self, exporter: TranscriptExporter) -> None:
        result = exporter.to_plain_text([])
        assert isinstance(result, str)
        assert result == ""

    def test_role_content_colon_format(
        self, exporter: TranscriptExporter, sample_transcript: list[dict[str, str]]
    ) -> None:
        result = exporter.to_plain_text(sample_transcript)
        lines = [line for line in result.strip().split("\n") if line.strip()]
        for line in lines:
            # Each line should have ROLE: content format
            assert ": " in line


class TestToJson:
    """Verify JSON export."""

    def test_returns_valid_json(
        self, exporter: TranscriptExporter, sample_transcript: list[dict[str, str]]
    ) -> None:
        result = exporter.to_json(sample_transcript)
        parsed = json.loads(result)
        assert isinstance(parsed, dict)

    def test_transcript_in_output(
        self, exporter: TranscriptExporter, sample_transcript: list[dict[str, str]]
    ) -> None:
        result = exporter.to_json(sample_transcript)
        parsed = json.loads(result)
        assert "transcript" in parsed
        assert len(parsed["transcript"]) == 4

    def test_with_metadata(
        self,
        exporter: TranscriptExporter,
        sample_transcript: list[dict[str, str]],
        sample_metadata: dict[str, str],
    ) -> None:
        result = exporter.to_json(sample_transcript, session_metadata=sample_metadata)
        parsed = json.loads(result)
        assert "metadata" in parsed
        assert parsed["metadata"]["topic"] == "AI in Healthcare"

    def test_without_metadata(
        self, exporter: TranscriptExporter, sample_transcript: list[dict[str, str]]
    ) -> None:
        result = exporter.to_json(sample_transcript)
        parsed = json.loads(result)
        assert "metadata" not in parsed

    def test_empty_transcript(self, exporter: TranscriptExporter) -> None:
        result = exporter.to_json([])
        parsed = json.loads(result)
        assert parsed["transcript"] == []

    def test_roundtrip_entries(
        self, exporter: TranscriptExporter, sample_transcript: list[dict[str, str]]
    ) -> None:
        result = exporter.to_json(sample_transcript)
        parsed = json.loads(result)
        for i, entry in enumerate(sample_transcript):
            assert parsed["transcript"][i]["role"] == entry["role"]
            assert parsed["transcript"][i]["content"] == entry["content"]

    def test_metadata_none_default(
        self, exporter: TranscriptExporter, sample_transcript: list[dict[str, str]]
    ) -> None:
        result_no_meta = exporter.to_json(sample_transcript)
        result_none = exporter.to_json(sample_transcript, session_metadata=None)
        assert result_no_meta == result_none
