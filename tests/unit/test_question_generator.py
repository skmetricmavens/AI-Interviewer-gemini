"""Tests for QuestionGenerator class in src.interview.prep.

Tests focus on _build_prompt() behavior and constructor initialization.
The generate() method calls the Claude API and is not tested here.
"""

from __future__ import annotations

import inspect

import pytest

from src.interview.prep import QuestionGenerator
from src.interview.prompts import PILLAR_QUESTIONS


# ---------------------------------------------------------------------------
# Constructor tests
# ---------------------------------------------------------------------------


class TestQuestionGeneratorInit:
    """Verify QuestionGenerator stores configuration on init."""

    def test_stores_api_key(self) -> None:
        gen = QuestionGenerator(anthropic_api_key="sk-test-key-123")
        assert gen.api_key == "sk-test-key-123"

    def test_stores_custom_model(self) -> None:
        gen = QuestionGenerator(
            anthropic_api_key="sk-test", model="claude-opus-4-20250514"
        )
        assert gen.model == "claude-opus-4-20250514"

    def test_default_model_is_sonnet(self) -> None:
        gen = QuestionGenerator(anthropic_api_key="sk-test")
        assert gen.model == "claude-sonnet-4-20250514"


# ---------------------------------------------------------------------------
# _build_prompt tests — topic
# ---------------------------------------------------------------------------


class TestBuildPromptTopic:
    """Verify _build_prompt includes the topic."""

    @pytest.fixture()
    def generator(self) -> QuestionGenerator:
        return QuestionGenerator(anthropic_api_key="sk-test")

    def test_includes_topic(self, generator: QuestionGenerator) -> None:
        prompt = generator._build_prompt(
            topic="Customer journey optimization",
            pillar="",
            audience="",
            language="en",
            count=5,
        )
        assert "Customer journey optimization" in prompt

    def test_includes_specific_topic(self, generator: QuestionGenerator) -> None:
        prompt = generator._build_prompt(
            topic="AI in healthcare diagnostics",
            pillar="",
            audience="",
            language="en",
            count=5,
        )
        assert "AI in healthcare diagnostics" in prompt


# ---------------------------------------------------------------------------
# _build_prompt tests — count
# ---------------------------------------------------------------------------


class TestBuildPromptCount:
    """Verify _build_prompt includes the requested count."""

    @pytest.fixture()
    def generator(self) -> QuestionGenerator:
        return QuestionGenerator(anthropic_api_key="sk-test")

    def test_includes_count_as_number(self, generator: QuestionGenerator) -> None:
        prompt = generator._build_prompt(
            topic="Marketing automation",
            pillar="",
            audience="",
            language="en",
            count=8,
        )
        assert "8" in prompt

    def test_includes_different_count(self, generator: QuestionGenerator) -> None:
        prompt = generator._build_prompt(
            topic="Marketing automation",
            pillar="",
            audience="",
            language="en",
            count=12,
        )
        assert "12" in prompt


# ---------------------------------------------------------------------------
# _build_prompt tests — language
# ---------------------------------------------------------------------------


class TestBuildPromptLanguage:
    """Verify _build_prompt includes language information."""

    @pytest.fixture()
    def generator(self) -> QuestionGenerator:
        return QuestionGenerator(anthropic_api_key="sk-test")

    def test_includes_english(self, generator: QuestionGenerator) -> None:
        prompt = generator._build_prompt(
            topic="CRM strategy",
            pillar="",
            audience="",
            language="en",
            count=5,
        )
        assert "en" in prompt.lower() or "english" in prompt.lower()

    def test_includes_dutch(self, generator: QuestionGenerator) -> None:
        prompt = generator._build_prompt(
            topic="CRM strategy",
            pillar="",
            audience="",
            language="nl",
            count=5,
        )
        assert "nl" in prompt.lower() or "dutch" in prompt.lower()


# ---------------------------------------------------------------------------
# _build_prompt tests — pillar
# ---------------------------------------------------------------------------


class TestBuildPromptPillar:
    """Verify _build_prompt includes pillar when provided."""

    @pytest.fixture()
    def generator(self) -> QuestionGenerator:
        return QuestionGenerator(anthropic_api_key="sk-test")

    def test_includes_pillar_when_provided(
        self, generator: QuestionGenerator
    ) -> None:
        prompt = generator._build_prompt(
            topic="Data-driven marketing",
            pillar="connected_journey",
            audience="",
            language="en",
            count=5,
        )
        assert "connected_journey" in prompt

    def test_includes_different_pillar(
        self, generator: QuestionGenerator
    ) -> None:
        prompt = generator._build_prompt(
            topic="Data-driven marketing",
            pillar="crm_intelligence",
            audience="",
            language="en",
            count=5,
        )
        assert "crm_intelligence" in prompt


# ---------------------------------------------------------------------------
# _build_prompt tests — audience
# ---------------------------------------------------------------------------


class TestBuildPromptAudience:
    """Verify _build_prompt includes audience when provided."""

    @pytest.fixture()
    def generator(self) -> QuestionGenerator:
        return QuestionGenerator(anthropic_api_key="sk-test")

    def test_includes_audience_when_provided(
        self, generator: QuestionGenerator
    ) -> None:
        prompt = generator._build_prompt(
            topic="Marketing tech stack",
            pillar="",
            audience="senior marketers",
            language="en",
            count=5,
        )
        assert "senior marketers" in prompt.lower()

    def test_includes_different_audience(
        self, generator: QuestionGenerator
    ) -> None:
        prompt = generator._build_prompt(
            topic="Marketing tech stack",
            pillar="",
            audience="CTOs and VPs",
            language="en",
            count=5,
        )
        prompt_lower = prompt.lower()
        assert "ctos" in prompt_lower or "vps" in prompt_lower


# ---------------------------------------------------------------------------
# _build_prompt tests — pillar questions as examples
# ---------------------------------------------------------------------------


class TestBuildPromptPillarQuestions:
    """Verify _build_prompt includes PILLAR_QUESTIONS as examples when pillar matches."""

    @pytest.fixture()
    def generator(self) -> QuestionGenerator:
        return QuestionGenerator(anthropic_api_key="sk-test")

    def test_includes_pillar_questions_for_connected_journey(
        self, generator: QuestionGenerator
    ) -> None:
        prompt = generator._build_prompt(
            topic="Journey mapping",
            pillar="connected_journey",
            audience="",
            language="en",
            count=5,
        )
        for q in PILLAR_QUESTIONS["connected_journey"]:
            assert q in prompt

    def test_includes_pillar_questions_for_crm_intelligence(
        self, generator: QuestionGenerator
    ) -> None:
        prompt = generator._build_prompt(
            topic="CRM data",
            pillar="crm_intelligence",
            audience="",
            language="en",
            count=5,
        )
        for q in PILLAR_QUESTIONS["crm_intelligence"]:
            assert q in prompt

    def test_includes_pillar_questions_for_field_notes(
        self, generator: QuestionGenerator
    ) -> None:
        prompt = generator._build_prompt(
            topic="Field experiments",
            pillar="field_notes",
            audience="",
            language="en",
            count=5,
        )
        for q in PILLAR_QUESTIONS["field_notes"]:
            assert q in prompt

    def test_no_pillar_questions_without_pillar(
        self, generator: QuestionGenerator
    ) -> None:
        prompt = generator._build_prompt(
            topic="General marketing",
            pillar="",
            audience="",
            language="en",
            count=5,
        )
        # Should not contain any pillar-specific questions
        for pillar_key, questions in PILLAR_QUESTIONS.items():
            for q in questions:
                assert q not in prompt, (
                    f"Unexpected pillar question found: {q}"
                )

    def test_no_pillar_questions_for_unknown_pillar(
        self, generator: QuestionGenerator
    ) -> None:
        prompt = generator._build_prompt(
            topic="General marketing",
            pillar="nonexistent_pillar",
            audience="",
            language="en",
            count=5,
        )
        for pillar_key, questions in PILLAR_QUESTIONS.items():
            for q in questions:
                assert q not in prompt


# ---------------------------------------------------------------------------
# _build_prompt tests — asks for list of questions
# ---------------------------------------------------------------------------


class TestBuildPromptFormat:
    """Verify _build_prompt asks for a list of questions in the response."""

    @pytest.fixture()
    def generator(self) -> QuestionGenerator:
        return QuestionGenerator(anthropic_api_key="sk-test")

    def test_asks_for_list_of_questions(
        self, generator: QuestionGenerator
    ) -> None:
        prompt = generator._build_prompt(
            topic="Marketing automation",
            pillar="",
            audience="",
            language="en",
            count=5,
        )
        prompt_lower = prompt.lower()
        assert "list" in prompt_lower or "questions" in prompt_lower

    def test_returns_string(self, generator: QuestionGenerator) -> None:
        prompt = generator._build_prompt(
            topic="Test topic",
            pillar="",
            audience="",
            language="en",
            count=5,
        )
        assert isinstance(prompt, str)
        assert len(prompt.strip()) > 0


# ---------------------------------------------------------------------------
# generate() method signature
# ---------------------------------------------------------------------------


class TestGenerateSignature:
    """Verify generate() method exists with correct signature and defaults."""

    def test_generate_method_exists(self) -> None:
        gen = QuestionGenerator(anthropic_api_key="sk-test")
        assert hasattr(gen, "generate")
        assert callable(gen.generate)

    def test_generate_default_count_is_eight(self) -> None:
        sig = inspect.signature(QuestionGenerator.generate)
        assert sig.parameters["count"].default == 8

    def test_generate_default_language_is_en(self) -> None:
        sig = inspect.signature(QuestionGenerator.generate)
        assert sig.parameters["language"].default == "en"

    def test_generate_default_pillar_is_empty(self) -> None:
        sig = inspect.signature(QuestionGenerator.generate)
        assert sig.parameters["pillar"].default == ""

    def test_generate_default_audience_is_empty(self) -> None:
        sig = inspect.signature(QuestionGenerator.generate)
        assert sig.parameters["audience"].default == ""
