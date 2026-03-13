"""Tests for task-39: humanizer integration with new article architectures.

Verifies that _build_prompt() uses format_instructions() from templates.py
for all 5 format types, replacing the hardcoded '- Format: {format_type}' line.
"""

from __future__ import annotations

import pytest

from src.writing.humanizer import ContentHumanizer
from src.writing.templates import format_instructions


# ---------------------------------------------------------------------------
# Shared test data
# ---------------------------------------------------------------------------

SAMPLE_TRANSCRIPT: list[dict[str, str]] = [
    {"role": "assistant", "content": "What inspired your project?"},
    {"role": "user", "content": "I wanted to solve a real problem."},
]

SAMPLE_FINGERPRINT: dict = {
    "tone": "casual",
    "sentence_length_avg": 12.0,
    "vocabulary_preferences": ["direct"],
    "transition_style": "minimal",
    "jargon": [],
    "emoji_usage": "none",
}

ALL_FORMAT_TYPES = ["linkedin", "blog", "inverted_pyramid", "narrative_arc", "pillar_cluster"]


# ---------------------------------------------------------------------------
# _build_prompt includes format_instructions for all 5 types
# ---------------------------------------------------------------------------


class TestBuildPromptUsesFormatInstructions:
    """Verify _build_prompt embeds format_instructions() output for each format type."""

    @pytest.mark.parametrize("format_type", ALL_FORMAT_TYPES)
    def test_prompt_contains_format_instructions(self, format_type: str) -> None:
        """The built prompt must include the full format_instructions text."""
        humanizer = ContentHumanizer(anthropic_api_key="k")
        prompt = humanizer._build_prompt(
            SAMPLE_TRANSCRIPT, SAMPLE_FINGERPRINT, format_type, "en"
        )
        expected_instructions = format_instructions(format_type)
        assert expected_instructions in prompt, (
            f"Prompt for '{format_type}' must contain the output of "
            f"format_instructions('{format_type}')"
        )

    @pytest.mark.parametrize("format_type", ALL_FORMAT_TYPES)
    def test_prompt_no_longer_uses_bare_format_line(self, format_type: str) -> None:
        """The old hardcoded '- Format: {format_type}' line should be replaced."""
        humanizer = ContentHumanizer(anthropic_api_key="k")
        prompt = humanizer._build_prompt(
            SAMPLE_TRANSCRIPT, SAMPLE_FINGERPRINT, format_type, "en"
        )
        # The bare format line should no longer appear as a standalone instruction
        assert f"- Format: {format_type}" not in prompt, (
            f"Prompt should no longer contain the hardcoded '- Format: {format_type}' line; "
            "it should use format_instructions() instead"
        )


# ---------------------------------------------------------------------------
# New architecture types work in _build_prompt
# ---------------------------------------------------------------------------


class TestBuildPromptNewArchitectures:
    """Verify _build_prompt works correctly with the 3 new architecture types."""

    def test_inverted_pyramid_includes_key_elements(self) -> None:
        humanizer = ContentHumanizer(anthropic_api_key="k")
        prompt = humanizer._build_prompt(
            SAMPLE_TRANSCRIPT, SAMPLE_FINGERPRINT, "inverted_pyramid", "en"
        )
        assert "Inverted Pyramid" in prompt
        assert "Lead" in prompt
        assert "decreasing order of importance" in prompt

    def test_narrative_arc_includes_key_elements(self) -> None:
        humanizer = ContentHumanizer(anthropic_api_key="k")
        prompt = humanizer._build_prompt(
            SAMPLE_TRANSCRIPT, SAMPLE_FINGERPRINT, "narrative_arc", "en"
        )
        assert "Narrative Arc" in prompt
        assert "Rising Action" in prompt
        assert "Climax" in prompt
        assert "Resolution" in prompt

    def test_pillar_cluster_includes_key_elements(self) -> None:
        humanizer = ContentHumanizer(anthropic_api_key="k")
        prompt = humanizer._build_prompt(
            SAMPLE_TRANSCRIPT, SAMPLE_FINGERPRINT, "pillar_cluster", "en"
        )
        assert "Pillar-Cluster" in prompt
        assert "Clusters" in prompt
        assert "SEO" in prompt

    @pytest.mark.parametrize(
        "format_type",
        ["inverted_pyramid", "narrative_arc", "pillar_cluster"],
    )
    def test_new_formats_include_transcript(self, format_type: str) -> None:
        """New format types must still include the transcript content."""
        humanizer = ContentHumanizer(anthropic_api_key="k")
        prompt = humanizer._build_prompt(
            SAMPLE_TRANSCRIPT, SAMPLE_FINGERPRINT, format_type, "en"
        )
        assert "What inspired your project?" in prompt
        assert "I wanted to solve a real problem." in prompt

    @pytest.mark.parametrize(
        "format_type",
        ["inverted_pyramid", "narrative_arc", "pillar_cluster"],
    )
    def test_new_formats_include_fingerprint(self, format_type: str) -> None:
        """New format types must still include the fingerprint data."""
        humanizer = ContentHumanizer(anthropic_api_key="k")
        prompt = humanizer._build_prompt(
            SAMPLE_TRANSCRIPT, SAMPLE_FINGERPRINT, format_type, "en"
        )
        assert "casual" in prompt
        assert "direct" in prompt

    @pytest.mark.parametrize(
        "format_type",
        ["inverted_pyramid", "narrative_arc", "pillar_cluster"],
    )
    def test_new_formats_include_language(self, format_type: str) -> None:
        """New format types must still specify the language."""
        humanizer = ContentHumanizer(anthropic_api_key="k")
        prompt = humanizer._build_prompt(
            SAMPLE_TRANSCRIPT, SAMPLE_FINGERPRINT, format_type, "nl"
        )
        assert "dutch" in prompt.lower()

    @pytest.mark.parametrize(
        "format_type",
        ["inverted_pyramid", "narrative_arc", "pillar_cluster"],
    )
    def test_new_formats_include_blocklist(self, format_type: str) -> None:
        """New format types must still reference the AI vocabulary blocklist."""
        from src.persona.analyzer import AI_VOCABULARY_BLOCKLIST

        humanizer = ContentHumanizer(anthropic_api_key="k")
        prompt = humanizer._build_prompt(
            SAMPLE_TRANSCRIPT, SAMPLE_FINGERPRINT, format_type, "en"
        )
        blocklist_words_found = [
            word for word in AI_VOCABULARY_BLOCKLIST if word in prompt.lower()
        ]
        assert len(blocklist_words_found) > 0


# ---------------------------------------------------------------------------
# Existing formats still work with format_instructions
# ---------------------------------------------------------------------------


class TestBuildPromptExistingFormatsStillWork:
    """Ensure linkedin and blog formats still produce valid prompts after refactor."""

    def test_linkedin_includes_hook_body_cta(self) -> None:
        humanizer = ContentHumanizer(anthropic_api_key="k")
        prompt = humanizer._build_prompt(
            SAMPLE_TRANSCRIPT, SAMPLE_FINGERPRINT, "linkedin", "en"
        )
        assert "Hook" in prompt
        assert "Body" in prompt
        assert "CTA" in prompt

    def test_blog_includes_title_intro_sections(self) -> None:
        humanizer = ContentHumanizer(anthropic_api_key="k")
        prompt = humanizer._build_prompt(
            SAMPLE_TRANSCRIPT, SAMPLE_FINGERPRINT, "blog", "en"
        )
        assert "Title" in prompt
        assert "Intro" in prompt
        assert "Sections" in prompt
        assert "Conclusion" in prompt
