"""Tests for task-34: Inject six-phase structure into system prompt.

Verifies that build_system_prompt() renders PHASE_DEFINITIONS as a dynamic
"## Interview Phases" section, replacing the old hardcoded "## Your Approach".
"""

from __future__ import annotations

import re

from src.interview.prompts import PHASE_DEFINITIONS, build_system_prompt


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_BASE_KWARGS: dict[str, object] = {
    "topic": "AI trends",
    "context": None,
    "language": "en",
}


def _build(**overrides: object) -> str:
    """Build a prompt with sensible defaults, overridable per-test."""
    kwargs = {**_BASE_KWARGS, **overrides}
    return build_system_prompt(**kwargs)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# 1. Section heading
# ---------------------------------------------------------------------------


class TestInterviewPhasesHeading:
    """The prompt must contain an '## Interview Phases' heading."""

    def test_interview_phases_heading_present(self) -> None:
        result = _build()
        assert "## Interview Phases" in result

    def test_your_approach_heading_absent(self) -> None:
        """The old hardcoded '## Your Approach' section must be removed."""
        result = _build()
        assert "## Your Approach" not in result


# ---------------------------------------------------------------------------
# 2. All six phase titles appear
# ---------------------------------------------------------------------------


class TestPhaseTitlesInPrompt:
    """Every phase title from PHASE_DEFINITIONS must appear in the output."""

    def test_all_phase_titles_present(self) -> None:
        result = _build()
        for phase in PHASE_DEFINITIONS:
            title = phase["title"]
            assert str(title) in result, (
                f"Phase title '{title}' not found in the built prompt"
            )

    def test_each_phase_title_individually(self) -> None:
        """Parametric-style check for each of the six phases."""
        result = _build()
        expected_titles = [str(p["title"]) for p in PHASE_DEFINITIONS]
        assert len(expected_titles) == 6, "Expected exactly 6 phase definitions"
        for title in expected_titles:
            assert title in result


# ---------------------------------------------------------------------------
# 3. All six phase goals appear
# ---------------------------------------------------------------------------


class TestPhaseGoalsInPrompt:
    """Every phase goal from PHASE_DEFINITIONS must appear in the output."""

    def test_all_phase_goals_present(self) -> None:
        result = _build()
        for phase in PHASE_DEFINITIONS:
            goal = str(phase["goal"])
            assert goal in result, (
                f"Phase goal for '{phase['name']}' not found in the built prompt"
            )


# ---------------------------------------------------------------------------
# 4. Phases are numbered 1-6
# ---------------------------------------------------------------------------


class TestPhaseNumbering:
    """Phases should be numbered 1 through 6 in the output."""

    def test_numbers_1_through_6_present(self) -> None:
        result = _build()
        for i in range(1, 7):
            assert f"{i}." in result, (
                f"Numbered item '{i}.' not found in the prompt"
            )

    def test_phases_appear_in_numbered_order(self) -> None:
        """Phase titles should appear in order 1-6 matching PHASE_DEFINITIONS."""
        result = _build()
        positions = []
        for i, phase in enumerate(PHASE_DEFINITIONS, start=1):
            pattern = rf"{i}\.\s*.*{re.escape(str(phase['title']))}"
            match = re.search(pattern, result)
            assert match is not None, (
                f"Phase {i} with title '{phase['title']}' not found as numbered item"
            )
            positions.append(match.start())
        # Verify monotonically increasing positions
        assert positions == sorted(positions), (
            "Phases are not in the expected 1-6 order"
        )


# ---------------------------------------------------------------------------
# 5. Turn guidance is included
# ---------------------------------------------------------------------------


class TestTurnGuidance:
    """The prompt should include turn count guidance for phases."""

    def test_turn_related_keyword_present(self) -> None:
        result = _build().lower()
        assert "turn" in result or "suggested" in result, (
            "Expected 'turn' or 'suggested' keyword in the prompt for turn guidance"
        )

    def test_suggested_turns_values_appear(self) -> None:
        """At least one concrete suggested_turns number should appear near a phase."""
        result = _build()
        found_any = False
        for phase in PHASE_DEFINITIONS:
            turns = str(phase["suggested_turns"])
            if turns in result:
                found_any = True
                break
        assert found_any, "No suggested_turns value found in the prompt"


# ---------------------------------------------------------------------------
# 6. At least one technique name appears
# ---------------------------------------------------------------------------


class TestTechniquesInPrompt:
    """At least one technique name from PHASE_DEFINITIONS should be in the output."""

    def test_at_least_one_technique_present(self) -> None:
        result = _build().lower()
        all_techniques = [
            str(tech).lower()
            for phase in PHASE_DEFINITIONS
            for tech in phase["techniques"]  # type: ignore[union-attr]
        ]
        found = any(tech in result for tech in all_techniques)
        assert found, (
            "No technique name from PHASE_DEFINITIONS found in the prompt"
        )


# ---------------------------------------------------------------------------
# 7. Phases section comes after interview rules
# ---------------------------------------------------------------------------


class TestSectionOrdering:
    """The '## Interview Phases' section must come after '## Interview Rules'."""

    def test_phases_after_rules(self) -> None:
        result = _build()
        rules_pos = result.find("## Interview Rules")
        phases_pos = result.find("## Interview Phases")
        assert rules_pos != -1, "'## Interview Rules' not found in prompt"
        assert phases_pos != -1, "'## Interview Phases' not found in prompt"
        assert phases_pos > rules_pos, (
            "Expected '## Interview Phases' to appear after '## Interview Rules'"
        )


# ---------------------------------------------------------------------------
# 8. Old hardcoded approach steps are removed
# ---------------------------------------------------------------------------


class TestOldApproachRemoved:
    """The old hardcoded 'Your Approach' step text must be gone."""

    def test_old_step_warm_broad_question_absent(self) -> None:
        result = _build()
        assert "Start with a warm, broad question" not in result

    def test_old_step_follow_logic_chain_absent(self) -> None:
        result = _build()
        assert "Follow the interviewee's logic chain" not in result

    def test_old_step_narrow_from_broad_absent(self) -> None:
        result = _build()
        assert "Gradually narrow from broad themes" not in result

    def test_old_step_explore_framework_absent(self) -> None:
        result = _build()
        assert "explore each one before moving on" not in result

    def test_old_step_mix_heavy_intellectual_absent(self) -> None:
        result = _build()
        assert "Mix heavy/intellectual questions" not in result

    def test_old_step_8_12_exchanges_absent(self) -> None:
        result = _build()
        assert "8-12 exchanges" not in result


# ---------------------------------------------------------------------------
# 9. Backward compatibility: existing params still work
# ---------------------------------------------------------------------------


class TestBackwardCompatibility:
    """topic, context, language, and metadata params still function."""

    def test_topic_still_present(self) -> None:
        result = _build(topic="quantum computing")
        assert "quantum computing" in result

    def test_context_still_present(self) -> None:
        result = _build(context="Expert with 15 years experience")
        assert "15 years experience" in result

    def test_language_dutch_still_works(self) -> None:
        result = _build(language="nl")
        lower = result.lower()
        assert "dutch" in lower or "nederlands" in lower

    def test_metadata_interviewee_name_still_works(self) -> None:
        result = _build(interviewee_name="Jan de Vries")
        assert "Jan de Vries" in result

    def test_metadata_content_pillar_still_works(self) -> None:
        result = _build(content_pillar="Innovation")
        assert "Innovation" in result

    def test_metadata_target_architecture_still_works(self) -> None:
        result = _build(target_architecture="Blog Post")
        assert "Blog Post" in result

    def test_metadata_target_audience_still_works(self) -> None:
        result = _build(target_audience="Product managers")
        assert "Product managers" in result

    def test_interview_rules_still_present(self) -> None:
        """Core interview rules section must remain intact."""
        result = _build()
        assert "## Interview Rules" in result
        assert "Core Rules" in result
