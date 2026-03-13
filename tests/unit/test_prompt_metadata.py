"""Tests for build_system_prompt metadata parameters (task-32).

Verifies that the new keyword-only metadata params (interviewee_name,
content_pillar, target_architecture, target_audience) are correctly
injected into the system prompt when provided and omitted when None.
"""

from __future__ import annotations

import pytest

from src.interview.prompts import build_system_prompt


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_BASE_KWARGS: dict[str, object] = {
    "topic": "artificial intelligence",
    "context": None,
    "language": "en",
}


def _build(**overrides: object) -> str:
    """Shortcut: build a prompt with base kwargs + any overrides."""
    kwargs = {**_BASE_KWARGS, **overrides}
    return build_system_prompt(**kwargs)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# 1. Each metadata field appears when provided
# ---------------------------------------------------------------------------


class TestIndividualMetadataFields:
    """Each metadata field must appear in the prompt when a value is given."""

    def test_interviewee_name_appears(self) -> None:
        result = _build(interviewee_name="Alice van der Berg")
        assert "Alice van der Berg" in result

    def test_content_pillar_appears(self) -> None:
        result = _build(content_pillar="Thought Leadership")
        assert "Thought Leadership" in result

    def test_target_architecture_appears(self) -> None:
        result = _build(target_architecture="LinkedIn Post")
        assert "LinkedIn Post" in result

    def test_target_audience_appears(self) -> None:
        result = _build(target_audience="Senior engineering managers")
        assert "Senior engineering managers" in result


# ---------------------------------------------------------------------------
# 2. No "None" literal when metadata is omitted
# ---------------------------------------------------------------------------


class TestNoNoneLiteral:
    """When metadata params are None (default), the string 'None' must not leak."""

    def test_no_none_with_all_defaults(self) -> None:
        result = _build()
        assert "None" not in result

    def test_no_none_with_name_only(self) -> None:
        result = _build(interviewee_name="Bob")
        assert "None" not in result

    def test_no_none_with_pillar_only(self) -> None:
        result = _build(content_pillar="Innovation")
        assert "None" not in result

    def test_no_none_with_architecture_only(self) -> None:
        result = _build(target_architecture="Blog")
        assert "None" not in result

    def test_no_none_with_audience_only(self) -> None:
        result = _build(target_audience="Developers")
        assert "None" not in result

    def test_no_none_with_some_fields_set(self) -> None:
        """Mix of set and unset metadata fields should not produce 'None'."""
        result = _build(
            interviewee_name="Eve",
            target_audience="CTOs",
        )
        assert "None" not in result


# ---------------------------------------------------------------------------
# 3. All metadata combined
# ---------------------------------------------------------------------------


class TestAllMetadataCombined:
    """When all four metadata fields are provided, each must appear."""

    def test_all_fields_present(self) -> None:
        result = _build(
            interviewee_name="Charlie",
            content_pillar="Data Engineering",
            target_architecture="Newsletter",
            target_audience="Junior developers",
        )
        assert "Charlie" in result
        assert "Data Engineering" in result
        assert "Newsletter" in result
        assert "Junior developers" in result

    def test_all_fields_no_none_literal(self) -> None:
        result = _build(
            interviewee_name="Charlie",
            content_pillar="Data Engineering",
            target_architecture="Newsletter",
            target_audience="Junior developers",
        )
        assert "None" not in result


# ---------------------------------------------------------------------------
# 4. Backward compatibility
# ---------------------------------------------------------------------------


class TestBackwardCompatibility:
    """Existing calls without metadata kwargs must continue to work."""

    def test_positional_args_still_work(self) -> None:
        """Calling with only the three original positional args must not raise."""
        result = build_system_prompt("Python", None, "en")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_keyword_args_still_work(self) -> None:
        result = build_system_prompt(topic="Python", context=None, language="en")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_topic_still_in_prompt(self) -> None:
        result = build_system_prompt("machine learning", None, "en")
        assert "machine learning" in result

    def test_context_still_in_prompt(self) -> None:
        result = build_system_prompt("ML", "expert with 10 years", "en")
        assert "10 years" in result

    def test_language_still_respected(self) -> None:
        result = build_system_prompt("ML", None, "nl")
        lower = result.lower()
        assert "dutch" in lower or "nederlands" in lower

    def test_no_metadata_section_when_all_none(self) -> None:
        """When no metadata is supplied, there should be no metadata header."""
        result = build_system_prompt("Python", None, "en")
        lower = result.lower()
        assert "metadata" not in lower


# ---------------------------------------------------------------------------
# 5. Metadata section has a clear header
# ---------------------------------------------------------------------------


class TestMetadataSectionHeader:
    """When at least one metadata field is provided, a dedicated section header
    must appear so the LLM can parse it."""

    def test_header_present_with_name(self) -> None:
        result = _build(interviewee_name="Dana")
        lower = result.lower()
        assert "metadata" in lower or "session" in lower

    def test_header_present_with_all_fields(self) -> None:
        result = _build(
            interviewee_name="Dana",
            content_pillar="AI Ethics",
            target_architecture="LinkedIn Post",
            target_audience="Tech leads",
        )
        lower = result.lower()
        assert "metadata" in lower or "session" in lower

    def test_header_uses_markdown_heading(self) -> None:
        """The metadata section should use a markdown heading (## or similar)."""
        result = _build(interviewee_name="Dana")
        # Look for a line starting with ## that contains metadata/session
        lines = result.lower().split("\n")
        has_heading = any(
            line.strip().startswith("##") and ("metadata" in line or "session" in line)
            for line in lines
        )
        assert has_heading, "Expected a markdown ## heading for the metadata section"

    def test_header_absent_when_no_metadata(self) -> None:
        """No metadata section should exist when all metadata fields are None."""
        result = _build()
        lower = result.lower()
        # The word 'metadata' should not appear in the prompt
        assert "session metadata" not in lower


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


class TestMetadataEdgeCases:
    """Edge cases for metadata fields."""

    def test_empty_string_name_treated_as_absent(self) -> None:
        """An empty string should behave like None — no 'None' literal, no header."""
        result = _build(interviewee_name="")
        assert "None" not in result

    def test_whitespace_only_name_treated_as_absent(self) -> None:
        result = _build(interviewee_name="   ")
        assert "None" not in result

    def test_special_characters_in_metadata(self) -> None:
        """Metadata with special chars should appear verbatim."""
        result = _build(interviewee_name="O'Brien-Smith")
        assert "O'Brien-Smith" in result

    def test_metadata_params_are_keyword_only(self) -> None:
        """The four metadata params must be keyword-only (cannot be passed positionally)."""
        with pytest.raises(TypeError):
            # Attempt to pass a 4th positional arg — should fail because
            # metadata params are keyword-only.
            build_system_prompt("topic", None, "en", "should_fail")  # type: ignore[misc]
