"""Tests for TranscriptExporter.save() method in src.storage.exporter."""

import json
import os
from pathlib import Path

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
        "interviewee_name": "Dr. Smith",
    }


class TestSaveMarkdown:
    """Verify save() creates .md files with correct naming convention."""

    def test_save_markdown_creates_md_file(
        self,
        exporter: TranscriptExporter,
        sample_transcript: list[dict[str, str]],
        tmp_path: Path,
    ) -> None:
        exporter.save(
            transcript=sample_transcript,
            output_dir=str(tmp_path),
            session_id="session-001",
            format="markdown",
        )
        expected_file = tmp_path / "session-001_markdown.md"
        assert expected_file.exists()

    def test_saved_markdown_contains_transcript_content(
        self,
        exporter: TranscriptExporter,
        sample_transcript: list[dict[str, str]],
        tmp_path: Path,
    ) -> None:
        exporter.save(
            transcript=sample_transcript,
            output_dir=str(tmp_path),
            session_id="session-001",
            format="markdown",
        )
        expected_file = tmp_path / "session-001_markdown.md"
        content = expected_file.read_text()
        assert "What inspired you to start this project?" in content
        assert "I wanted to solve a real problem." in content

    def test_saved_markdown_with_metadata(
        self,
        exporter: TranscriptExporter,
        sample_transcript: list[dict[str, str]],
        sample_metadata: dict[str, str],
        tmp_path: Path,
    ) -> None:
        exporter.save(
            transcript=sample_transcript,
            output_dir=str(tmp_path),
            session_id="session-001",
            format="markdown",
            session_metadata=sample_metadata,
        )
        expected_file = tmp_path / "session-001_markdown.md"
        content = expected_file.read_text()
        assert "AI in Healthcare" in content
        assert "Dr. Smith" in content


class TestSavePlainText:
    """Verify save() creates .txt files with correct naming convention."""

    def test_save_plain_text_creates_txt_file(
        self,
        exporter: TranscriptExporter,
        sample_transcript: list[dict[str, str]],
        tmp_path: Path,
    ) -> None:
        exporter.save(
            transcript=sample_transcript,
            output_dir=str(tmp_path),
            session_id="session-002",
            format="plain_text",
        )
        expected_file = tmp_path / "session-002_plain_text.txt"
        assert expected_file.exists()

    def test_saved_plain_text_contains_content(
        self,
        exporter: TranscriptExporter,
        sample_transcript: list[dict[str, str]],
        tmp_path: Path,
    ) -> None:
        exporter.save(
            transcript=sample_transcript,
            output_dir=str(tmp_path),
            session_id="session-002",
            format="plain_text",
        )
        expected_file = tmp_path / "session-002_plain_text.txt"
        content = expected_file.read_text()
        for entry in sample_transcript:
            assert entry["content"] in content


class TestSaveJson:
    """Verify save() creates .json files with correct naming convention."""

    def test_save_json_creates_json_file(
        self,
        exporter: TranscriptExporter,
        sample_transcript: list[dict[str, str]],
        tmp_path: Path,
    ) -> None:
        exporter.save(
            transcript=sample_transcript,
            output_dir=str(tmp_path),
            session_id="session-003",
            format="json",
        )
        expected_file = tmp_path / "session-003_json.json"
        assert expected_file.exists()

    def test_saved_json_contains_valid_json(
        self,
        exporter: TranscriptExporter,
        sample_transcript: list[dict[str, str]],
        tmp_path: Path,
    ) -> None:
        exporter.save(
            transcript=sample_transcript,
            output_dir=str(tmp_path),
            session_id="session-003",
            format="json",
        )
        expected_file = tmp_path / "session-003_json.json"
        content = expected_file.read_text()
        parsed = json.loads(content)
        assert isinstance(parsed, dict)
        assert "transcript" in parsed
        assert len(parsed["transcript"]) == len(sample_transcript)

    def test_saved_json_with_metadata(
        self,
        exporter: TranscriptExporter,
        sample_transcript: list[dict[str, str]],
        sample_metadata: dict[str, str],
        tmp_path: Path,
    ) -> None:
        exporter.save(
            transcript=sample_transcript,
            output_dir=str(tmp_path),
            session_id="session-003",
            format="json",
            session_metadata=sample_metadata,
        )
        expected_file = tmp_path / "session-003_json.json"
        parsed = json.loads(expected_file.read_text())
        assert "metadata" in parsed
        assert parsed["metadata"]["topic"] == "AI in Healthcare"


class TestSaveReturnValue:
    """Verify save() returns the full file path."""

    def test_returns_full_file_path_markdown(
        self,
        exporter: TranscriptExporter,
        sample_transcript: list[dict[str, str]],
        tmp_path: Path,
    ) -> None:
        result = exporter.save(
            transcript=sample_transcript,
            output_dir=str(tmp_path),
            session_id="session-001",
            format="markdown",
        )
        expected = str(tmp_path / "session-001_markdown.md")
        assert result == expected

    def test_returns_full_file_path_plain_text(
        self,
        exporter: TranscriptExporter,
        sample_transcript: list[dict[str, str]],
        tmp_path: Path,
    ) -> None:
        result = exporter.save(
            transcript=sample_transcript,
            output_dir=str(tmp_path),
            session_id="session-002",
            format="plain_text",
        )
        expected = str(tmp_path / "session-002_plain_text.txt")
        assert result == expected

    def test_returns_full_file_path_json(
        self,
        exporter: TranscriptExporter,
        sample_transcript: list[dict[str, str]],
        tmp_path: Path,
    ) -> None:
        result = exporter.save(
            transcript=sample_transcript,
            output_dir=str(tmp_path),
            session_id="session-003",
            format="json",
        )
        expected = str(tmp_path / "session-003_json.json")
        assert result == expected

    def test_returned_path_is_string(
        self,
        exporter: TranscriptExporter,
        sample_transcript: list[dict[str, str]],
        tmp_path: Path,
    ) -> None:
        result = exporter.save(
            transcript=sample_transcript,
            output_dir=str(tmp_path),
            session_id="session-001",
            format="markdown",
        )
        assert isinstance(result, str)


class TestSaveDirectoryCreation:
    """Verify save() creates the output directory if it does not exist."""

    def test_creates_output_dir_if_missing(
        self,
        exporter: TranscriptExporter,
        sample_transcript: list[dict[str, str]],
        tmp_path: Path,
    ) -> None:
        nested_dir = tmp_path / "exports" / "transcripts"
        assert not nested_dir.exists()

        exporter.save(
            transcript=sample_transcript,
            output_dir=str(nested_dir),
            session_id="session-001",
            format="markdown",
        )
        assert nested_dir.exists()
        assert (nested_dir / "session-001_markdown.md").exists()

    def test_works_with_existing_dir(
        self,
        exporter: TranscriptExporter,
        sample_transcript: list[dict[str, str]],
        tmp_path: Path,
    ) -> None:
        # tmp_path already exists; should not raise
        exporter.save(
            transcript=sample_transcript,
            output_dir=str(tmp_path),
            session_id="session-001",
            format="markdown",
        )
        assert (tmp_path / "session-001_markdown.md").exists()


class TestSaveErrorCases:
    """Verify save() raises errors for invalid inputs."""

    def test_raises_value_error_for_unknown_format(
        self,
        exporter: TranscriptExporter,
        sample_transcript: list[dict[str, str]],
        tmp_path: Path,
    ) -> None:
        with pytest.raises(ValueError):
            exporter.save(
                transcript=sample_transcript,
                output_dir=str(tmp_path),
                session_id="session-001",
                format="html",
            )

    def test_raises_value_error_for_empty_format(
        self,
        exporter: TranscriptExporter,
        sample_transcript: list[dict[str, str]],
        tmp_path: Path,
    ) -> None:
        with pytest.raises(ValueError):
            exporter.save(
                transcript=sample_transcript,
                output_dir=str(tmp_path),
                session_id="session-001",
                format="",
            )

    def test_unknown_format_does_not_create_file(
        self,
        exporter: TranscriptExporter,
        sample_transcript: list[dict[str, str]],
        tmp_path: Path,
    ) -> None:
        with pytest.raises(ValueError):
            exporter.save(
                transcript=sample_transcript,
                output_dir=str(tmp_path),
                session_id="session-001",
                format="csv",
            )
        # No files should have been created
        assert len(list(tmp_path.iterdir())) == 0


class TestSaveDefaultFormat:
    """Verify save() defaults to markdown format."""

    def test_default_format_is_markdown(
        self,
        exporter: TranscriptExporter,
        sample_transcript: list[dict[str, str]],
        tmp_path: Path,
    ) -> None:
        result = exporter.save(
            transcript=sample_transcript,
            output_dir=str(tmp_path),
            session_id="session-001",
        )
        expected_file = tmp_path / "session-001_markdown.md"
        assert expected_file.exists()
        assert result == str(expected_file)
