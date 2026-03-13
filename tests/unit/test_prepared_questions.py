"""Tests for prepared_questions parameter in build_system_prompt (task-52).

Verifies that:
1. prepared_questions=None preserves existing behavior.
2. prepared_questions=[] preserves existing behavior.
3. prepared_questions with items adds a '## Prepared Questions' section.
4. Each provided question appears in the prompt.
5. Instructional text about using questions as a guide is present.
6. When prepared_questions is provided, PILLAR_QUESTIONS section is suppressed.
7. When prepared_questions is None and pillar matches, PILLAR_QUESTIONS still works.
8. prepared_questions works alongside all other metadata params.
9. prepared_questions works with both "en" and "nl" language.
"""

from __future__ import annotations

import pytest

from src.interview.prompts import PILLAR_QUESTIONS, build_system_prompt


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _build(**kwargs: object) -> str:
    """Build a system prompt with sensible defaults, overridable by kwargs."""
    defaults: dict[str, object] = {"topic": "AI trends", "context": None, "language": "en"}
    defaults.update(kwargs)
    return build_system_prompt(**defaults)  # type: ignore[arg-type]


_SAMPLE_QUESTIONS = [
    "What is your biggest challenge right now?",
    "How do you measure success in your role?",
    "What trend excites you most for next year?",
]


# ---------------------------------------------------------------------------
# 1. Default behaviour (None / empty list)
# ---------------------------------------------------------------------------


class TestPreparedQuestionsDefault:
    """When prepared_questions is None or empty, prompt behaves as before."""

    def test_none_does_not_add_section(self) -> None:
        result = _build(prepared_questions=None)
        assert "## Prepared Questions" not in result

    def test_omitted_does_not_add_section(self) -> None:
        """Calling without the param at all should not add the section."""
        result = _build()
        assert "## Prepared Questions" not in result

    def test_empty_list_does_not_add_section(self) -> None:
        result = _build(prepared_questions=[])
        assert "## Prepared Questions" not in result

    def test_none_still_returns_valid_prompt(self) -> None:
        result = _build(prepared_questions=None)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_empty_list_still_returns_valid_prompt(self) -> None:
        result = _build(prepared_questions=[])
        assert isinstance(result, str)
        assert len(result) > 0


# ---------------------------------------------------------------------------
# 2. Section presence when questions provided
# ---------------------------------------------------------------------------


class TestPreparedQuestionsSectionPresent:
    """When prepared_questions has items, a Prepared Questions section appears."""

    def test_section_header_present(self) -> None:
        result = _build(prepared_questions=_SAMPLE_QUESTIONS)
        assert "## Prepared Questions" in result

    def test_single_question_adds_section(self) -> None:
        result = _build(prepared_questions=["What is your main goal?"])
        assert "## Prepared Questions" in result

    def test_each_question_appears_in_prompt(self) -> None:
        result = _build(prepared_questions=_SAMPLE_QUESTIONS)
        for q in _SAMPLE_QUESTIONS:
            assert q in result, f"Question not found in prompt: {q!r}"

    def test_questions_prefixed_with_dash(self) -> None:
        result = _build(prepared_questions=_SAMPLE_QUESTIONS)
        for q in _SAMPLE_QUESTIONS:
            assert f"- {q}" in result, f"Question not dash-prefixed: {q!r}"

    def test_instructions_text_present(self) -> None:
        """The section must include guidance about using questions as a guide."""
        result = _build(prepared_questions=_SAMPLE_QUESTIONS)
        lower = result.lower()
        assert "interview guide" in lower or "guide" in lower
        assert "adapt" in lower or "naturally" in lower


# ---------------------------------------------------------------------------
# 3. Prepared questions suppress PILLAR_QUESTIONS
# ---------------------------------------------------------------------------


class TestPreparedQuestionsSuppressesPillar:
    """When prepared_questions is provided, the Pillar Questions section must not appear."""

    @pytest.mark.parametrize("pillar", list(PILLAR_QUESTIONS.keys()))
    def test_pillar_section_absent_with_prepared_questions(self, pillar: str) -> None:
        result = _build(
            content_pillar=pillar,
            prepared_questions=_SAMPLE_QUESTIONS,
        )
        assert "## Pillar Questions" not in result

    @pytest.mark.parametrize("pillar", list(PILLAR_QUESTIONS.keys()))
    def test_prepared_section_present_even_with_pillar(self, pillar: str) -> None:
        result = _build(
            content_pillar=pillar,
            prepared_questions=_SAMPLE_QUESTIONS,
        )
        assert "## Prepared Questions" in result

    def test_pillar_questions_content_absent(self) -> None:
        """Individual pillar questions should not leak into the prompt."""
        pillar = "connected_journey"
        result = _build(
            content_pillar=pillar,
            prepared_questions=_SAMPLE_QUESTIONS,
        )
        for pq in PILLAR_QUESTIONS[pillar]:
            assert pq not in result, f"Pillar question leaked into prompt: {pq!r}"


# ---------------------------------------------------------------------------
# 4. PILLAR_QUESTIONS still works when prepared_questions is absent
# ---------------------------------------------------------------------------


class TestPillarQuestionsStillWork:
    """Backward compatibility: without prepared_questions, pillar questions appear as before."""

    def test_pillar_section_present_when_no_prepared(self) -> None:
        result = _build(content_pillar="connected_journey", prepared_questions=None)
        assert "## Pillar Questions" in result

    def test_pillar_section_present_when_prepared_omitted(self) -> None:
        result = _build(content_pillar="connected_journey")
        assert "## Pillar Questions" in result

    def test_pillar_section_present_when_prepared_empty(self) -> None:
        result = _build(content_pillar="connected_journey", prepared_questions=[])
        assert "## Pillar Questions" in result


# ---------------------------------------------------------------------------
# 5. Combination with other parameters
# ---------------------------------------------------------------------------


class TestPreparedQuestionsWithOtherParams:
    """prepared_questions works alongside all other metadata parameters."""

    def test_with_interviewee_name(self) -> None:
        result = _build(
            interviewee_name="Alice",
            prepared_questions=_SAMPLE_QUESTIONS,
        )
        assert "Alice" in result
        assert "## Prepared Questions" in result

    def test_with_content_pillar_metadata(self) -> None:
        """Content pillar should still appear in metadata, just not as Pillar Questions."""
        result = _build(
            content_pillar="crm_intelligence",
            prepared_questions=_SAMPLE_QUESTIONS,
        )
        assert "crm_intelligence" in result
        assert "## Prepared Questions" in result
        assert "## Pillar Questions" not in result

    def test_with_target_audience(self) -> None:
        result = _build(
            target_audience="CMOs",
            prepared_questions=_SAMPLE_QUESTIONS,
        )
        assert "CMOs" in result
        assert "## Prepared Questions" in result

    def test_with_target_architecture(self) -> None:
        result = _build(
            target_architecture="inverted_pyramid",
            prepared_questions=_SAMPLE_QUESTIONS,
        )
        assert "inverted_pyramid" in result
        assert "## Prepared Questions" in result

    def test_with_context(self) -> None:
        result = _build(
            context="The interviewee is a CRM expert with 10 years experience.",
            prepared_questions=_SAMPLE_QUESTIONS,
        )
        assert "10 years experience" in result
        assert "## Prepared Questions" in result

    def test_with_all_params(self) -> None:
        result = _build(
            topic="MarTech strategy",
            context="Expert panel discussion notes.",
            language="en",
            interviewee_name="Bob",
            content_pillar="building_smart",
            target_architecture="narrative_arc",
            target_audience="Marketing Directors",
            prepared_questions=_SAMPLE_QUESTIONS,
        )
        assert "## Prepared Questions" in result
        assert "## Pillar Questions" not in result
        assert "Bob" in result
        assert "Marketing Directors" in result
        for q in _SAMPLE_QUESTIONS:
            assert q in result


# ---------------------------------------------------------------------------
# 6. Language compatibility
# ---------------------------------------------------------------------------


class TestPreparedQuestionsLanguage:
    """prepared_questions works with both supported languages."""

    def test_english_prompt_includes_prepared(self) -> None:
        result = _build(language="en", prepared_questions=_SAMPLE_QUESTIONS)
        assert "## Prepared Questions" in result
        assert "English" in result

    def test_dutch_prompt_includes_prepared(self) -> None:
        result = _build(language="nl", prepared_questions=_SAMPLE_QUESTIONS)
        assert "## Prepared Questions" in result
        lower = result.lower()
        assert "dutch" in lower or "nederlands" in lower


# ---------------------------------------------------------------------------
# 7. Section ordering
# ---------------------------------------------------------------------------


class TestPreparedQuestionsSectionOrder:
    """The Prepared Questions section should appear after Interview Phases."""

    def test_prepared_questions_after_interview_phases(self) -> None:
        result = _build(prepared_questions=_SAMPLE_QUESTIONS)
        phases_idx = result.find("## Interview Phases")
        prepared_idx = result.find("## Prepared Questions")
        assert phases_idx != -1, "Interview Phases section not found"
        assert prepared_idx != -1, "Prepared Questions section not found"
        assert prepared_idx > phases_idx, (
            "Prepared Questions section should come after Interview Phases"
        )
