"""Tests for BlueprintGenerator class in src/writing/blueprint.py.

Tests focus on _build_prompt() behavior and constructor initialization.
The generate() method calls the Claude API and is not tested here.
"""

from __future__ import annotations

import pytest

from src.writing.blueprint import BlueprintGenerator


# ---------------------------------------------------------------------------
# Shared test data
# ---------------------------------------------------------------------------

SAMPLE_TRANSCRIPT: list[dict[str, str]] = [
    {"role": "assistant", "content": "What challenges did you face?"},
    {"role": "user", "content": "Scaling was the hardest part."},
    {"role": "assistant", "content": "How did you overcome that?"},
    {"role": "user", "content": "We redesigned the data pipeline."},
]

MINIMAL_TRANSCRIPT: list[dict[str, str]] = [
    {"role": "user", "content": "Just one message here."},
]


# ---------------------------------------------------------------------------
# Constructor tests
# ---------------------------------------------------------------------------


class TestBlueprintGeneratorInit:
    """Verify BlueprintGenerator stores api_key and model."""

    def test_stores_api_key(self) -> None:
        gen = BlueprintGenerator(anthropic_api_key="test-key-123")
        assert gen.api_key == "test-key-123"

    def test_stores_custom_model(self) -> None:
        gen = BlueprintGenerator(
            anthropic_api_key="k", model="claude-opus-4-20250514"
        )
        assert gen.model == "claude-opus-4-20250514"

    def test_default_model_is_sonnet(self) -> None:
        gen = BlueprintGenerator(anthropic_api_key="k")
        assert gen.model == "claude-sonnet-4-20250514"


# ---------------------------------------------------------------------------
# _build_prompt tests
# ---------------------------------------------------------------------------


class TestBuildPromptTranscript:
    """Verify _build_prompt includes transcript content."""

    def test_includes_transcript_user_content(self) -> None:
        gen = BlueprintGenerator(anthropic_api_key="k")
        prompt = gen._build_prompt(
            SAMPLE_TRANSCRIPT, "inverted_pyramid"
        )
        assert "Scaling was the hardest part." in prompt
        assert "We redesigned the data pipeline." in prompt

    def test_includes_transcript_assistant_content(self) -> None:
        gen = BlueprintGenerator(anthropic_api_key="k")
        prompt = gen._build_prompt(
            SAMPLE_TRANSCRIPT, "inverted_pyramid"
        )
        assert "What challenges did you face?" in prompt
        assert "How did you overcome that?" in prompt

    def test_includes_single_message_transcript(self) -> None:
        gen = BlueprintGenerator(anthropic_api_key="k")
        prompt = gen._build_prompt(
            MINIMAL_TRANSCRIPT, "blog"
        )
        assert "Just one message here." in prompt


class TestBuildPromptArchitecture:
    """Verify _build_prompt includes architecture type."""

    def test_includes_inverted_pyramid(self) -> None:
        gen = BlueprintGenerator(anthropic_api_key="k")
        prompt = gen._build_prompt(
            SAMPLE_TRANSCRIPT, "inverted_pyramid"
        )
        assert "inverted_pyramid" in prompt.lower() or "inverted pyramid" in prompt.lower()

    def test_includes_narrative_arc(self) -> None:
        gen = BlueprintGenerator(anthropic_api_key="k")
        prompt = gen._build_prompt(
            SAMPLE_TRANSCRIPT, "narrative_arc"
        )
        assert "narrative_arc" in prompt.lower() or "narrative arc" in prompt.lower()

    def test_includes_pillar_cluster(self) -> None:
        gen = BlueprintGenerator(anthropic_api_key="k")
        prompt = gen._build_prompt(
            SAMPLE_TRANSCRIPT, "pillar_cluster"
        )
        assert "pillar_cluster" in prompt.lower() or "pillar cluster" in prompt.lower()

    def test_includes_linkedin(self) -> None:
        gen = BlueprintGenerator(anthropic_api_key="k")
        prompt = gen._build_prompt(
            SAMPLE_TRANSCRIPT, "linkedin"
        )
        assert "linkedin" in prompt.lower()

    def test_includes_blog(self) -> None:
        gen = BlueprintGenerator(anthropic_api_key="k")
        prompt = gen._build_prompt(
            SAMPLE_TRANSCRIPT, "blog"
        )
        assert "blog" in prompt.lower()


class TestBuildPromptContentPillar:
    """Verify _build_prompt includes content_pillar when provided."""

    def test_includes_content_pillar_when_provided(self) -> None:
        gen = BlueprintGenerator(anthropic_api_key="k")
        prompt = gen._build_prompt(
            SAMPLE_TRANSCRIPT,
            "blog",
            content_pillar="engineering leadership",
        )
        assert "engineering leadership" in prompt.lower()

    def test_omits_content_pillar_when_empty(self) -> None:
        gen = BlueprintGenerator(anthropic_api_key="k")
        prompt = gen._build_prompt(
            SAMPLE_TRANSCRIPT, "blog", content_pillar=""
        )
        # Should not crash, prompt is still valid
        assert isinstance(prompt, str)
        assert len(prompt) > 0

    def test_default_content_pillar_is_empty(self) -> None:
        gen = BlueprintGenerator(anthropic_api_key="k")
        # Call without content_pillar argument
        prompt = gen._build_prompt(SAMPLE_TRANSCRIPT, "blog")
        assert isinstance(prompt, str)


class TestBuildPromptTargetAudience:
    """Verify _build_prompt includes target_audience when provided."""

    def test_includes_target_audience_when_provided(self) -> None:
        gen = BlueprintGenerator(anthropic_api_key="k")
        prompt = gen._build_prompt(
            SAMPLE_TRANSCRIPT,
            "blog",
            target_audience="senior developers",
        )
        assert "senior developers" in prompt.lower()

    def test_omits_target_audience_when_empty(self) -> None:
        gen = BlueprintGenerator(anthropic_api_key="k")
        prompt = gen._build_prompt(
            SAMPLE_TRANSCRIPT, "blog", target_audience=""
        )
        assert isinstance(prompt, str)
        assert len(prompt) > 0

    def test_default_target_audience_is_empty(self) -> None:
        gen = BlueprintGenerator(anthropic_api_key="k")
        prompt = gen._build_prompt(SAMPLE_TRANSCRIPT, "blog")
        assert isinstance(prompt, str)


class TestBuildPromptLanguage:
    """Verify _build_prompt includes language."""

    def test_includes_english_language(self) -> None:
        gen = BlueprintGenerator(anthropic_api_key="k")
        prompt = gen._build_prompt(
            SAMPLE_TRANSCRIPT, "blog", language="en"
        )
        # Should mention English or "en"
        assert "en" in prompt.lower() or "english" in prompt.lower()

    def test_includes_dutch_language(self) -> None:
        gen = BlueprintGenerator(anthropic_api_key="k")
        prompt = gen._build_prompt(
            SAMPLE_TRANSCRIPT, "blog", language="nl"
        )
        assert "nl" in prompt.lower() or "dutch" in prompt.lower()

    def test_default_language_is_en(self) -> None:
        gen = BlueprintGenerator(anthropic_api_key="k")
        prompt = gen._build_prompt(SAMPLE_TRANSCRIPT, "blog")
        # Default is "en", should appear in prompt
        assert "en" in prompt.lower() or "english" in prompt.lower()


class TestBuildPromptJsonFormat:
    """Verify _build_prompt asks for JSON response format."""

    def test_prompt_requests_json_response(self) -> None:
        gen = BlueprintGenerator(anthropic_api_key="k")
        prompt = gen._build_prompt(SAMPLE_TRANSCRIPT, "blog")
        assert "json" in prompt.lower()

    def test_prompt_mentions_expected_json_fields(self) -> None:
        """The prompt should describe the expected JSON structure."""
        gen = BlueprintGenerator(anthropic_api_key="k")
        prompt = gen._build_prompt(SAMPLE_TRANSCRIPT, "blog")
        prompt_lower = prompt.lower()
        assert "headline" in prompt_lower
        assert "sections" in prompt_lower

    def test_prompt_mentions_key_points_field(self) -> None:
        gen = BlueprintGenerator(anthropic_api_key="k")
        prompt = gen._build_prompt(SAMPLE_TRANSCRIPT, "blog")
        assert "key_points" in prompt.lower() or "key points" in prompt.lower()

    def test_prompt_mentions_source_quotes_field(self) -> None:
        gen = BlueprintGenerator(anthropic_api_key="k")
        prompt = gen._build_prompt(SAMPLE_TRANSCRIPT, "blog")
        assert "source_quotes" in prompt.lower() or "source quotes" in prompt.lower()


# ---------------------------------------------------------------------------
# _build_prompt with all parameters combined
# ---------------------------------------------------------------------------


class TestBuildPromptCombined:
    """Verify _build_prompt works with all parameters specified."""

    def test_all_parameters_present_in_prompt(self) -> None:
        gen = BlueprintGenerator(anthropic_api_key="k")
        prompt = gen._build_prompt(
            transcript=SAMPLE_TRANSCRIPT,
            architecture="narrative_arc",
            content_pillar="thought leadership",
            target_audience="CTOs and VPs of Engineering",
            language="nl",
        )
        prompt_lower = prompt.lower()
        assert "scaling was the hardest part" in prompt_lower
        assert "narrative" in prompt_lower
        assert "thought leadership" in prompt_lower
        assert "ctos" in prompt_lower or "vps" in prompt_lower
        assert "nl" in prompt_lower or "dutch" in prompt_lower
        assert "json" in prompt_lower
