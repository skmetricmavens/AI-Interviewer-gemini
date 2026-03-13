"""Tests for InterviewPrep dataclass and markdown parser/writer in src.interview.prep."""

import pytest
from pathlib import Path

from src.interview.prep import InterviewPrep, write_prep_file, parse_prep_file


class TestInterviewPrepDataclass:
    """Verify InterviewPrep dataclass fields and defaults."""

    def test_creation_with_all_fields(self) -> None:
        prep = InterviewPrep(
            topic="CRM data quality",
            pillar="crm_intelligence",
            audience="crm_managers",
            architecture="inverted_pyramid",
            language="nl",
            interviewee="Sandy",
            questions=["What's your approach?", "How do you measure it?"],
            notes="Focus on practical examples.",
        )
        assert prep.topic == "CRM data quality"
        assert prep.pillar == "crm_intelligence"
        assert prep.audience == "crm_managers"
        assert prep.architecture == "inverted_pyramid"
        assert prep.language == "nl"
        assert prep.interviewee == "Sandy"
        assert prep.questions == ["What's your approach?", "How do you measure it?"]
        assert prep.notes == "Focus on practical examples."

    def test_default_values(self) -> None:
        prep = InterviewPrep(topic="AI trends")
        assert prep.pillar == ""
        assert prep.audience == ""
        assert prep.architecture == ""
        assert prep.language == "en"
        assert prep.interviewee == ""
        assert prep.questions == []
        assert prep.notes == ""

    def test_topic_is_required(self) -> None:
        with pytest.raises(TypeError):
            InterviewPrep()  # type: ignore[call-arg]

    def test_questions_default_not_shared(self) -> None:
        """Each instance should get its own list for questions."""
        a = InterviewPrep(topic="A")
        b = InterviewPrep(topic="B")
        a.questions.append("extra")
        assert b.questions == []


class TestWritePrepFile:
    """Verify write_prep_file produces correct markdown output."""

    def test_creates_file(self, tmp_path: Path) -> None:
        prep = InterviewPrep(topic="Test topic")
        out = tmp_path / "prep.md"
        write_prep_file(prep, str(out))
        assert out.exists()

    def test_output_contains_frontmatter_markers(self, tmp_path: Path) -> None:
        prep = InterviewPrep(topic="Test topic")
        out = tmp_path / "prep.md"
        write_prep_file(prep, str(out))
        content = out.read_text()
        assert content.startswith("---\n")
        assert "\n---\n" in content

    def test_output_contains_topic_in_frontmatter(self, tmp_path: Path) -> None:
        prep = InterviewPrep(topic="CRM data quality")
        out = tmp_path / "prep.md"
        write_prep_file(prep, str(out))
        content = out.read_text()
        assert "topic: CRM data quality" in content

    def test_output_contains_all_frontmatter_fields(self, tmp_path: Path) -> None:
        prep = InterviewPrep(
            topic="AI trends",
            pillar="crm_intelligence",
            audience="crm_managers",
            architecture="inverted_pyramid",
            language="nl",
            interviewee="Sandy",
        )
        out = tmp_path / "prep.md"
        write_prep_file(prep, str(out))
        content = out.read_text()
        assert "topic: AI trends" in content
        assert "pillar: crm_intelligence" in content
        assert "audience: crm_managers" in content
        assert "architecture: inverted_pyramid" in content
        assert "language: nl" in content
        assert "interviewee: Sandy" in content

    def test_output_contains_questions_with_dash_prefix(self, tmp_path: Path) -> None:
        prep = InterviewPrep(
            topic="Test",
            questions=["What's your approach?", "How do you measure it?"],
        )
        out = tmp_path / "prep.md"
        write_prep_file(prep, str(out))
        content = out.read_text()
        assert "- What's your approach?" in content
        assert "- How do you measure it?" in content

    def test_output_contains_questions_heading(self, tmp_path: Path) -> None:
        prep = InterviewPrep(topic="Test", questions=["Q1"])
        out = tmp_path / "prep.md"
        write_prep_file(prep, str(out))
        content = out.read_text()
        assert "## Questions" in content

    def test_output_contains_notes_section(self, tmp_path: Path) -> None:
        prep = InterviewPrep(topic="Test", notes="Some important notes.")
        out = tmp_path / "prep.md"
        write_prep_file(prep, str(out))
        content = out.read_text()
        assert "## Notes" in content
        assert "Some important notes." in content

    def test_output_contains_title_heading(self, tmp_path: Path) -> None:
        prep = InterviewPrep(topic="CRM data quality")
        out = tmp_path / "prep.md"
        write_prep_file(prep, str(out))
        content = out.read_text()
        assert "# Interview Prep: CRM data quality" in content

    def test_output_empty_questions(self, tmp_path: Path) -> None:
        prep = InterviewPrep(topic="Test", questions=[])
        out = tmp_path / "prep.md"
        write_prep_file(prep, str(out))
        content = out.read_text()
        assert "## Questions" in content

    def test_output_empty_notes_placeholder(self, tmp_path: Path) -> None:
        prep = InterviewPrep(topic="Test", notes="")
        out = tmp_path / "prep.md"
        write_prep_file(prep, str(out))
        content = out.read_text()
        assert "## Notes" in content
        assert "_Add notes here._" in content


class TestParsePrepFile:
    """Verify parse_prep_file reads markdown back into InterviewPrep."""

    def _write_sample(self, path: Path, content: str) -> str:
        path.write_text(content)
        return str(path)

    def test_extracts_topic_from_frontmatter(self, tmp_path: Path) -> None:
        filepath = self._write_sample(
            tmp_path / "prep.md",
            "---\ntopic: CRM data quality\npillar: \naudience: \n"
            "architecture: \nlanguage: en\ninterviewee: \n---\n\n"
            "# Interview Prep: CRM data quality\n\n## Questions\n\n## Notes\n\n_Add notes here._\n",
        )
        prep = parse_prep_file(filepath)
        assert prep.topic == "CRM data quality"

    def test_extracts_all_frontmatter_fields(self, tmp_path: Path) -> None:
        filepath = self._write_sample(
            tmp_path / "prep.md",
            "---\ntopic: AI trends\npillar: crm_intelligence\naudience: crm_managers\n"
            "architecture: inverted_pyramid\nlanguage: nl\ninterviewee: Sandy\n---\n\n"
            "# Interview Prep: AI trends\n\n## Questions\n\n## Notes\n\n_Add notes here._\n",
        )
        prep = parse_prep_file(filepath)
        assert prep.topic == "AI trends"
        assert prep.pillar == "crm_intelligence"
        assert prep.audience == "crm_managers"
        assert prep.architecture == "inverted_pyramid"
        assert prep.language == "nl"
        assert prep.interviewee == "Sandy"

    def test_extracts_questions_as_list(self, tmp_path: Path) -> None:
        filepath = self._write_sample(
            tmp_path / "prep.md",
            "---\ntopic: Test\npillar: \naudience: \n"
            "architecture: \nlanguage: en\ninterviewee: \n---\n\n"
            "# Interview Prep: Test\n\n## Questions\n\n"
            "- What's your approach?\n- How do you measure it?\n\n"
            "## Notes\n\n_Add notes here._\n",
        )
        prep = parse_prep_file(filepath)
        assert prep.questions == ["What's your approach?", "How do you measure it?"]

    def test_extracts_notes(self, tmp_path: Path) -> None:
        filepath = self._write_sample(
            tmp_path / "prep.md",
            "---\ntopic: Test\npillar: \naudience: \n"
            "architecture: \nlanguage: en\ninterviewee: \n---\n\n"
            "# Interview Prep: Test\n\n## Questions\n\n"
            "- Q1\n\n## Notes\n\nSome important notes.\n",
        )
        prep = parse_prep_file(filepath)
        assert prep.notes == "Some important notes."

    def test_handles_empty_questions_list(self, tmp_path: Path) -> None:
        filepath = self._write_sample(
            tmp_path / "prep.md",
            "---\ntopic: Test\npillar: \naudience: \n"
            "architecture: \nlanguage: en\ninterviewee: \n---\n\n"
            "# Interview Prep: Test\n\n## Questions\n\n## Notes\n\n_Add notes here._\n",
        )
        prep = parse_prep_file(filepath)
        assert prep.questions == []

    def test_handles_missing_notes_section(self, tmp_path: Path) -> None:
        filepath = self._write_sample(
            tmp_path / "prep.md",
            "---\ntopic: Test\npillar: \naudience: \n"
            "architecture: \nlanguage: en\ninterviewee: \n---\n\n"
            "# Interview Prep: Test\n\n## Questions\n\n- Q1\n",
        )
        prep = parse_prep_file(filepath)
        assert prep.notes == ""

    def test_parse_file_not_found_raises(self) -> None:
        with pytest.raises(FileNotFoundError):
            parse_prep_file("/nonexistent/path/prep.md")


class TestRoundtrip:
    """Verify write then parse preserves all fields."""

    def test_roundtrip_all_fields(self, tmp_path: Path) -> None:
        original = InterviewPrep(
            topic="CRM data quality",
            pillar="crm_intelligence",
            audience="crm_managers",
            architecture="inverted_pyramid",
            language="nl",
            interviewee="Sandy",
            questions=["What's your approach?", "How do you measure it?"],
            notes="Focus on practical examples.",
        )
        filepath = str(tmp_path / "prep.md")
        write_prep_file(original, filepath)
        parsed = parse_prep_file(filepath)

        assert parsed.topic == original.topic
        assert parsed.pillar == original.pillar
        assert parsed.audience == original.audience
        assert parsed.architecture == original.architecture
        assert parsed.language == original.language
        assert parsed.interviewee == original.interviewee
        assert parsed.questions == original.questions
        assert parsed.notes == original.notes

    def test_roundtrip_defaults_only(self, tmp_path: Path) -> None:
        original = InterviewPrep(topic="Minimal topic")
        filepath = str(tmp_path / "prep.md")
        write_prep_file(original, filepath)
        parsed = parse_prep_file(filepath)

        assert parsed.topic == "Minimal topic"
        assert parsed.pillar == ""
        assert parsed.audience == ""
        assert parsed.architecture == ""
        assert parsed.language == "en"
        assert parsed.interviewee == ""
        assert parsed.questions == []
        assert parsed.notes == ""

    def test_roundtrip_multiline_notes(self, tmp_path: Path) -> None:
        original = InterviewPrep(
            topic="Test",
            notes="Line one.\nLine two.\nLine three.",
        )
        filepath = str(tmp_path / "prep.md")
        write_prep_file(original, filepath)
        parsed = parse_prep_file(filepath)
        assert parsed.notes == original.notes

    def test_roundtrip_many_questions(self, tmp_path: Path) -> None:
        questions = [f"Question {i}?" for i in range(10)]
        original = InterviewPrep(topic="Big interview", questions=questions)
        filepath = str(tmp_path / "prep.md")
        write_prep_file(original, filepath)
        parsed = parse_prep_file(filepath)
        assert parsed.questions == questions

    def test_roundtrip_special_characters_in_topic(self, tmp_path: Path) -> None:
        original = InterviewPrep(topic="AI & ML: the future?")
        filepath = str(tmp_path / "prep.md")
        write_prep_file(original, filepath)
        parsed = parse_prep_file(filepath)
        assert parsed.topic == original.topic
