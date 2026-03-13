"""Tests for PHASE_DEFINITIONS data structure in src.interview.prompts."""

import re

import pytest

from src.interview.prompts import PHASE_DEFINITIONS


class TestPhaseDefinitionsStructure:
    """Verify PHASE_DEFINITIONS exists and has the correct top-level structure."""

    def test_exists_and_is_sequence(self) -> None:
        assert isinstance(PHASE_DEFINITIONS, (tuple, list))

    def test_has_exactly_six_phases(self) -> None:
        assert len(PHASE_DEFINITIONS) == 6

    def test_each_phase_is_a_dict(self) -> None:
        for phase in PHASE_DEFINITIONS:
            assert isinstance(phase, dict)


class TestPhaseRequiredKeys:
    """Verify each phase contains all required keys."""

    REQUIRED_KEYS = {"name", "title", "goal", "suggested_turns", "techniques"}

    def test_all_phases_have_required_keys(self) -> None:
        for i, phase in enumerate(PHASE_DEFINITIONS):
            missing = self.REQUIRED_KEYS - set(phase.keys())
            assert not missing, f"Phase {i} is missing keys: {missing}"

    def test_no_extra_keys_beyond_required(self) -> None:
        """Each phase should only have the documented keys (guard against typos)."""
        for i, phase in enumerate(PHASE_DEFINITIONS):
            extra = set(phase.keys()) - self.REQUIRED_KEYS
            assert not extra, f"Phase {i} has unexpected keys: {extra}"


class TestPhaseNames:
    """Verify phase name values are valid and unique."""

    def test_names_are_unique(self) -> None:
        names = [phase["name"] for phase in PHASE_DEFINITIONS]
        assert len(names) == len(set(names)), f"Duplicate phase names found: {names}"

    def test_names_are_snake_case(self) -> None:
        snake_case_pattern = re.compile(r"^[a-z][a-z0-9]*(_[a-z0-9]+)*$")
        for phase in PHASE_DEFINITIONS:
            name = phase["name"]
            assert snake_case_pattern.match(name), (
                f"Phase name '{name}' is not valid snake_case"
            )

    def test_names_are_strings(self) -> None:
        for phase in PHASE_DEFINITIONS:
            assert isinstance(phase["name"], str)


class TestPhaseOrder:
    """Verify phases are in the expected logical interview order."""

    def test_first_phase_is_warm_up(self) -> None:
        assert PHASE_DEFINITIONS[0]["name"] == "warm_up"

    def test_last_phase_is_wrap_up(self) -> None:
        assert PHASE_DEFINITIONS[-1]["name"] == "wrap_up"


class TestPhaseTitles:
    """Verify title field for each phase."""

    def test_titles_are_non_empty_strings(self) -> None:
        for phase in PHASE_DEFINITIONS:
            title = phase["title"]
            assert isinstance(title, str)
            assert len(title) > 0, f"Phase '{phase['name']}' has empty title"


class TestPhaseGoals:
    """Verify goal field for each phase."""

    def test_goals_are_non_empty_strings(self) -> None:
        for phase in PHASE_DEFINITIONS:
            goal = phase["goal"]
            assert isinstance(goal, str)
            assert len(goal) >= 10, (
                f"Phase '{phase['name']}' goal is too short ({len(goal)} chars): '{goal}'"
            )


class TestPhaseSuggestedTurns:
    """Verify suggested_turns field for each phase."""

    def test_suggested_turns_is_positive_integer(self) -> None:
        for phase in PHASE_DEFINITIONS:
            turns = phase["suggested_turns"]
            assert isinstance(turns, int), (
                f"Phase '{phase['name']}' suggested_turns is {type(turns)}, expected int"
            )
            assert turns > 0, (
                f"Phase '{phase['name']}' suggested_turns must be positive, got {turns}"
            )

    def test_total_suggested_turns_in_reasonable_range(self) -> None:
        """Total turns across all phases should be 8-20, matching interview guidance."""
        total = sum(phase["suggested_turns"] for phase in PHASE_DEFINITIONS)
        assert 8 <= total <= 20, (
            f"Total suggested_turns is {total}, expected between 8 and 20"
        )


class TestPhaseTechniques:
    """Verify techniques field for each phase."""

    def test_techniques_is_non_empty_list(self) -> None:
        for phase in PHASE_DEFINITIONS:
            techniques = phase["techniques"]
            assert isinstance(techniques, list), (
                f"Phase '{phase['name']}' techniques is {type(techniques)}, expected list"
            )
            assert len(techniques) > 0, (
                f"Phase '{phase['name']}' has empty techniques list"
            )

    def test_each_technique_is_a_string(self) -> None:
        for phase in PHASE_DEFINITIONS:
            for tech in phase["techniques"]:
                assert isinstance(tech, str), (
                    f"Phase '{phase['name']}' has non-string technique: {tech}"
                )

    def test_each_technique_is_non_empty(self) -> None:
        for phase in PHASE_DEFINITIONS:
            for tech in phase["techniques"]:
                assert len(tech.strip()) > 0, (
                    f"Phase '{phase['name']}' has blank technique string"
                )
