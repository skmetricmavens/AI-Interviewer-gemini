"""Tests for src.writing.humanizer — ContentHumanizer class."""

from unittest.mock import MagicMock, patch

import pytest

from src.writing.humanizer import ContentHumanizer


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


# ---------------------------------------------------------------------------
# Constructor tests
# ---------------------------------------------------------------------------


class TestContentHumanizerInit:
    """Verify the constructor stores API key and model."""

    def test_stores_api_key(self) -> None:
        humanizer = ContentHumanizer(anthropic_api_key="test-key-123")
        assert humanizer.anthropic_api_key == "test-key-123"

    def test_default_model(self) -> None:
        humanizer = ContentHumanizer(anthropic_api_key="k")
        assert humanizer.model == "claude-sonnet-4-20250514"

    def test_custom_model(self) -> None:
        humanizer = ContentHumanizer(anthropic_api_key="k", model="claude-haiku-35")
        assert humanizer.model == "claude-haiku-35"

    def test_stores_different_api_key(self) -> None:
        humanizer = ContentHumanizer(anthropic_api_key="another-key")
        assert humanizer.anthropic_api_key == "another-key"


# ---------------------------------------------------------------------------
# _build_prompt tests
# ---------------------------------------------------------------------------


class TestBuildPrompt:
    """Verify _build_prompt constructs a prompt with all required elements."""

    def test_includes_transcript_content(self) -> None:
        humanizer = ContentHumanizer(anthropic_api_key="k")
        prompt = humanizer._build_prompt(
            SAMPLE_TRANSCRIPT, SAMPLE_FINGERPRINT, "linkedin", "en"
        )

        assert "What inspired your project?" in prompt
        assert "I wanted to solve a real problem." in prompt

    def test_includes_fingerprint_tone(self) -> None:
        humanizer = ContentHumanizer(anthropic_api_key="k")
        prompt = humanizer._build_prompt(
            SAMPLE_TRANSCRIPT, SAMPLE_FINGERPRINT, "linkedin", "en"
        )

        assert "casual" in prompt

    def test_includes_fingerprint_data(self) -> None:
        humanizer = ContentHumanizer(anthropic_api_key="k")
        prompt = humanizer._build_prompt(
            SAMPLE_TRANSCRIPT, SAMPLE_FINGERPRINT, "blog", "en"
        )

        # Should reference fingerprint style markers
        assert "direct" in prompt
        assert "minimal" in prompt

    def test_includes_format_type_linkedin(self) -> None:
        humanizer = ContentHumanizer(anthropic_api_key="k")
        prompt = humanizer._build_prompt(
            SAMPLE_TRANSCRIPT, SAMPLE_FINGERPRINT, "linkedin", "en"
        )

        assert "linkedin" in prompt.lower()

    def test_includes_format_type_blog(self) -> None:
        humanizer = ContentHumanizer(anthropic_api_key="k")
        prompt = humanizer._build_prompt(
            SAMPLE_TRANSCRIPT, SAMPLE_FINGERPRINT, "blog", "en"
        )

        assert "blog" in prompt.lower()

    def test_language_english(self) -> None:
        humanizer = ContentHumanizer(anthropic_api_key="k")
        prompt = humanizer._build_prompt(
            SAMPLE_TRANSCRIPT, SAMPLE_FINGERPRINT, "linkedin", "en"
        )

        assert "english" in prompt.lower()

    def test_language_dutch(self) -> None:
        humanizer = ContentHumanizer(anthropic_api_key="k")
        prompt = humanizer._build_prompt(
            SAMPLE_TRANSCRIPT, SAMPLE_FINGERPRINT, "linkedin", "nl"
        )

        assert "dutch" in prompt.lower()

    def test_includes_anti_ai_vocabulary_constraint(self) -> None:
        from src.persona.analyzer import AI_VOCABULARY_BLOCKLIST

        humanizer = ContentHumanizer(anthropic_api_key="k")
        prompt = humanizer._build_prompt(
            SAMPLE_TRANSCRIPT, SAMPLE_FINGERPRINT, "linkedin", "en"
        )

        # The prompt should reference at least some blocked words
        blocklist_words_found = [
            word for word in AI_VOCABULARY_BLOCKLIST if word in prompt.lower()
        ]
        assert len(blocklist_words_found) > 0, (
            "Prompt should include AI vocabulary blocklist words as constraints"
        )

    def test_includes_first_person_instruction(self) -> None:
        humanizer = ContentHumanizer(anthropic_api_key="k")
        prompt = humanizer._build_prompt(
            SAMPLE_TRANSCRIPT, SAMPLE_FINGERPRINT, "linkedin", "en"
        )

        assert "first" in prompt.lower() and "person" in prompt.lower()

    def test_returns_non_empty_string(self) -> None:
        humanizer = ContentHumanizer(anthropic_api_key="k")
        prompt = humanizer._build_prompt(
            SAMPLE_TRANSCRIPT, SAMPLE_FINGERPRINT, "linkedin", "en"
        )

        assert isinstance(prompt, str)
        assert len(prompt) > 0

    def test_no_emoji_constraint_when_emoji_usage_none(self) -> None:
        humanizer = ContentHumanizer(anthropic_api_key="k")
        prompt = humanizer._build_prompt(
            SAMPLE_TRANSCRIPT, SAMPLE_FINGERPRINT, "linkedin", "en"
        )

        # Should mention emoji restriction when fingerprint says no emojis
        assert "emoji" in prompt.lower()


# ---------------------------------------------------------------------------
# generate tests (mocked Claude API)
# ---------------------------------------------------------------------------


class TestGenerate:
    """Verify generate calls the Claude API and returns content."""

    def test_returns_string(self) -> None:
        humanizer = ContentHumanizer(anthropic_api_key="fake-key")

        mock_message = MagicMock()
        mock_message.content = [
            MagicMock(text="Here is a humanized LinkedIn post about my project.")
        ]

        with patch("src.writing.humanizer.anthropic.Anthropic") as mock_cls:
            mock_client = MagicMock()
            mock_client.messages.create.return_value = mock_message
            mock_cls.return_value = mock_client

            result = humanizer.generate(
                SAMPLE_TRANSCRIPT, SAMPLE_FINGERPRINT, "linkedin", "en"
            )

        assert isinstance(result, str)
        assert "humanized LinkedIn post" in result

    def test_calls_api_with_correct_key(self) -> None:
        humanizer = ContentHumanizer(anthropic_api_key="my-secret-key")

        mock_message = MagicMock()
        mock_message.content = [MagicMock(text="Generated content.")]

        with patch("src.writing.humanizer.anthropic.Anthropic") as mock_cls:
            mock_client = MagicMock()
            mock_client.messages.create.return_value = mock_message
            mock_cls.return_value = mock_client

            humanizer.generate(
                SAMPLE_TRANSCRIPT, SAMPLE_FINGERPRINT, "linkedin", "en"
            )

            mock_cls.assert_called_once_with(api_key="my-secret-key")

    def test_passes_correct_model_to_api(self) -> None:
        humanizer = ContentHumanizer(
            anthropic_api_key="k", model="claude-haiku-35"
        )

        mock_message = MagicMock()
        mock_message.content = [MagicMock(text="Output text.")]

        with patch("src.writing.humanizer.anthropic.Anthropic") as mock_cls:
            mock_client = MagicMock()
            mock_client.messages.create.return_value = mock_message
            mock_cls.return_value = mock_client

            humanizer.generate(
                SAMPLE_TRANSCRIPT, SAMPLE_FINGERPRINT, "blog", "en"
            )

            call_kwargs = mock_client.messages.create.call_args
            assert call_kwargs.kwargs.get("model") == "claude-haiku-35" or (
                call_kwargs[1].get("model") == "claude-haiku-35"
                if len(call_kwargs) > 1
                else call_kwargs.kwargs.get("model") == "claude-haiku-35"
            )

    def test_passes_default_model_to_api(self) -> None:
        humanizer = ContentHumanizer(anthropic_api_key="k")

        mock_message = MagicMock()
        mock_message.content = [MagicMock(text="Output text.")]

        with patch("src.writing.humanizer.anthropic.Anthropic") as mock_cls:
            mock_client = MagicMock()
            mock_client.messages.create.return_value = mock_message
            mock_cls.return_value = mock_client

            humanizer.generate(
                SAMPLE_TRANSCRIPT, SAMPLE_FINGERPRINT, "linkedin", "en"
            )

            call_kwargs = mock_client.messages.create.call_args
            # Should use the default model
            assert "claude-sonnet-4-20250514" in str(call_kwargs)

    def test_generate_with_blog_format(self) -> None:
        humanizer = ContentHumanizer(anthropic_api_key="k")

        mock_message = MagicMock()
        mock_message.content = [MagicMock(text="A blog post about my experience.")]

        with patch("src.writing.humanizer.anthropic.Anthropic") as mock_cls:
            mock_client = MagicMock()
            mock_client.messages.create.return_value = mock_message
            mock_cls.return_value = mock_client

            result = humanizer.generate(
                SAMPLE_TRANSCRIPT, SAMPLE_FINGERPRINT, "blog", "nl"
            )

        assert isinstance(result, str)
        assert len(result) > 0
