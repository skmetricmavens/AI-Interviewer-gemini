"""Tests for TopicGenerator class in src.topics.generator."""

from __future__ import annotations

import pytest

from src.topics.generator import TopicGenerator


class TestTopicGeneratorInit:
    """Verify TopicGenerator stores configuration on init."""

    def test_stores_api_key(self) -> None:
        gen = TopicGenerator(anthropic_api_key="sk-test-key-123")
        assert gen.api_key == "sk-test-key-123"

    def test_stores_custom_model(self) -> None:
        gen = TopicGenerator(
            anthropic_api_key="sk-test", model="claude-opus-4-20250514"
        )
        assert gen.model == "claude-opus-4-20250514"

    def test_default_model_is_sonnet(self) -> None:
        gen = TopicGenerator(anthropic_api_key="sk-test")
        assert gen.model == "claude-sonnet-4-20250514"


class TestBuildPrompt:
    """Verify _build_prompt produces correct prompt text."""

    @pytest.fixture()
    def generator(self) -> TopicGenerator:
        return TopicGenerator(anthropic_api_key="sk-test")

    def test_includes_pillar_name(self, generator: TopicGenerator) -> None:
        prompt = generator._build_prompt(
            pillar="connected_journey",
            count=3,
            language="en",
            evergreen_topics=["topic A"],
        )
        assert "connected_journey" in prompt

    def test_includes_requested_count(self, generator: TopicGenerator) -> None:
        prompt = generator._build_prompt(
            pillar="crm_intelligence",
            count=7,
            language="en",
            evergreen_topics=["topic A"],
        )
        assert "7" in prompt

    def test_includes_language_english(self, generator: TopicGenerator) -> None:
        prompt = generator._build_prompt(
            pillar="building_smart",
            count=3,
            language="en",
            evergreen_topics=["topic A"],
        )
        assert "en" in prompt.lower() or "english" in prompt.lower()

    def test_includes_language_dutch(self, generator: TopicGenerator) -> None:
        prompt = generator._build_prompt(
            pillar="building_smart",
            count=3,
            language="nl",
            evergreen_topics=["topic A"],
        )
        assert "nl" in prompt.lower() or "dutch" in prompt.lower()

    def test_includes_evergreen_topics_as_context(
        self, generator: TopicGenerator
    ) -> None:
        evergreen = [
            "How to map the full customer journey across channels",
            "Breaking down data silos between marketing and sales",
        ]
        prompt = generator._build_prompt(
            pillar="connected_journey",
            count=3,
            language="en",
            evergreen_topics=evergreen,
        )
        for topic in evergreen:
            assert topic in prompt

    def test_asks_for_list_of_topics(self, generator: TopicGenerator) -> None:
        prompt = generator._build_prompt(
            pillar="field_notes",
            count=5,
            language="en",
            evergreen_topics=["topic A"],
        )
        # The prompt should instruct the model to return a list
        prompt_lower = prompt.lower()
        assert "list" in prompt_lower or "topics" in prompt_lower

    def test_returns_string(self, generator: TopicGenerator) -> None:
        prompt = generator._build_prompt(
            pillar="connected_journey",
            count=3,
            language="en",
            evergreen_topics=["topic A"],
        )
        assert isinstance(prompt, str)
        assert len(prompt.strip()) > 0

    def test_handles_empty_evergreen_topics(
        self, generator: TopicGenerator
    ) -> None:
        prompt = generator._build_prompt(
            pillar="connected_journey",
            count=3,
            language="en",
            evergreen_topics=[],
        )
        assert isinstance(prompt, str)
        assert "connected_journey" in prompt


class TestSuggestSignature:
    """Verify suggest() method exists with correct signature."""

    def test_suggest_method_exists(self) -> None:
        gen = TopicGenerator(anthropic_api_key="sk-test")
        assert hasattr(gen, "suggest")
        assert callable(gen.suggest)

    def test_suggest_default_count_is_three(self) -> None:
        import inspect

        sig = inspect.signature(TopicGenerator.suggest)
        assert sig.parameters["count"].default == 3

    def test_suggest_default_language_is_en(self) -> None:
        import inspect

        sig = inspect.signature(TopicGenerator.suggest)
        assert sig.parameters["language"].default == "en"
