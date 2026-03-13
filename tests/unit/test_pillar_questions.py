"""Tests for PILLAR_QUESTIONS constant and its integration with build_system_prompt (task-35).

Verifies that:
1. PILLAR_QUESTIONS is a well-structured dict mapping pillar string values to question lists.
2. build_system_prompt injects a '## Pillar Questions' section when content_pillar matches.
3. No pillar questions section appears when content_pillar is None or unknown.
"""

from __future__ import annotations

import pytest

from src.config import ContentPillar
from src.interview.prompts import PILLAR_QUESTIONS, build_system_prompt

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_EXPECTED_PILLARS = {
    "connected_journey",
    "crm_intelligence",
    "building_smart",
    "people_not_prompts",
    "field_notes",
}


def _build(**kwargs: object) -> str:
    """Build a system prompt with sensible defaults, overridable by kwargs."""
    defaults: dict[str, object] = {"topic": "AI trends", "context": None, "language": "en"}
    defaults.update(kwargs)
    return build_system_prompt(**defaults)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# 1. PILLAR_QUESTIONS structure
# ---------------------------------------------------------------------------


class TestPillarQuestionsStructure:
    """PILLAR_QUESTIONS must be a dict with correct shape."""

    def test_is_dict(self) -> None:
        assert isinstance(PILLAR_QUESTIONS, dict)

    def test_has_exactly_five_keys(self) -> None:
        assert len(PILLAR_QUESTIONS) == 5

    def test_keys_match_content_pillar_values(self) -> None:
        assert set(PILLAR_QUESTIONS.keys()) == _EXPECTED_PILLARS

    def test_keys_match_enum_members(self) -> None:
        """Each key must correspond to an actual ContentPillar enum value."""
        for key in PILLAR_QUESTIONS:
            assert key in [m.value for m in ContentPillar]

    def test_each_value_is_nonempty_list(self) -> None:
        for pillar, questions in PILLAR_QUESTIONS.items():
            assert isinstance(questions, list), f"{pillar}: value is not a list"
            assert len(questions) > 0, f"{pillar}: question list is empty"

    def test_each_value_contains_strings(self) -> None:
        for pillar, questions in PILLAR_QUESTIONS.items():
            for q in questions:
                assert isinstance(q, str), f"{pillar}: question is not a string: {q!r}"

    def test_each_question_is_at_least_10_chars(self) -> None:
        for pillar, questions in PILLAR_QUESTIONS.items():
            for q in questions:
                assert len(q) >= 10, f"{pillar}: question too short: {q!r}"

    def test_each_question_contains_question_mark(self) -> None:
        for pillar, questions in PILLAR_QUESTIONS.items():
            for q in questions:
                assert "?" in q, f"{pillar}: question missing '?': {q!r}"

    def test_at_least_three_questions_per_pillar(self) -> None:
        for pillar, questions in PILLAR_QUESTIONS.items():
            assert len(questions) >= 3, (
                f"{pillar}: expected >= 3 questions, got {len(questions)}"
            )


# ---------------------------------------------------------------------------
# 2. Integration with build_system_prompt
# ---------------------------------------------------------------------------


class TestPillarQuestionsInPrompt:
    """When content_pillar is a known pillar, the prompt includes pillar questions."""

    def test_pillar_questions_section_present(self) -> None:
        result = _build(content_pillar="connected_journey")
        assert "## Pillar Questions" in result

    def test_at_least_one_question_injected(self) -> None:
        result = _build(content_pillar="connected_journey")
        expected_questions = PILLAR_QUESTIONS["connected_journey"]
        found = any(q in result for q in expected_questions)
        assert found, "None of the connected_journey questions found in prompt"

    @pytest.mark.parametrize("pillar", list(_EXPECTED_PILLARS))
    def test_each_pillar_injects_section(self, pillar: str) -> None:
        result = _build(content_pillar=pillar)
        assert "## Pillar Questions" in result

    @pytest.mark.parametrize("pillar", list(_EXPECTED_PILLARS))
    def test_each_pillar_injects_at_least_one_question(self, pillar: str) -> None:
        result = _build(content_pillar=pillar)
        expected_questions = PILLAR_QUESTIONS[pillar]
        found = any(q in result for q in expected_questions)
        assert found, f"No questions from {pillar} found in prompt"


class TestPillarQuestionsAbsent:
    """When content_pillar is None or unknown, no pillar questions section appears."""

    def test_no_section_when_pillar_is_none(self) -> None:
        result = _build(content_pillar=None)
        assert "## Pillar Questions" not in result

    def test_no_section_when_pillar_not_provided(self) -> None:
        result = _build()
        assert "## Pillar Questions" not in result

    def test_no_section_when_pillar_is_unknown(self) -> None:
        result = _build(content_pillar="nonexistent_pillar")
        assert "## Pillar Questions" not in result

    def test_no_section_when_pillar_is_empty_string(self) -> None:
        result = _build(content_pillar="")
        assert "## Pillar Questions" not in result


class TestPillarQuestionsSectionOrder:
    """The pillar questions section should come after the interview phases section."""

    def test_pillar_questions_after_interview_phases(self) -> None:
        result = _build(content_pillar="field_notes")
        phases_idx = result.find("## Interview Phases")
        pillar_idx = result.find("## Pillar Questions")
        assert phases_idx != -1, "Interview Phases section not found"
        assert pillar_idx != -1, "Pillar Questions section not found"
        assert pillar_idx > phases_idx, (
            "Pillar Questions section should come after Interview Phases"
        )
