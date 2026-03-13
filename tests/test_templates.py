"""Tests for src.writing.templates — LinkedInPost, BlogPost, format_instructions."""

import pytest

from src.writing.templates import BlogPost, LinkedInPost, format_instructions


# ---------------------------------------------------------------------------
# LinkedInPost dataclass tests
# ---------------------------------------------------------------------------


class TestLinkedInPost:
    """Verify LinkedInPost dataclass stores fields correctly."""

    def test_default_max_chars_is_3000(self) -> None:
        post = LinkedInPost(hook="Hook", body="Body", cta="CTA")
        assert post.max_chars == 3000

    def test_stores_hook(self) -> None:
        post = LinkedInPost(hook="Did you know?", body="Body text", cta="Follow me")
        assert post.hook == "Did you know?"

    def test_stores_body(self) -> None:
        post = LinkedInPost(hook="Hook", body="Main content here", cta="CTA")
        assert post.body == "Main content here"

    def test_stores_cta(self) -> None:
        post = LinkedInPost(hook="Hook", body="Body", cta="Share this post!")
        assert post.cta == "Share this post!"

    def test_custom_max_chars(self) -> None:
        post = LinkedInPost(hook="H", body="B", cta="C", max_chars=1500)
        assert post.max_chars == 1500

    def test_all_fields_together(self) -> None:
        post = LinkedInPost(
            hook="Big news!", body="Details here.", cta="Comment below", max_chars=2000
        )
        assert post.hook == "Big news!"
        assert post.body == "Details here."
        assert post.cta == "Comment below"
        assert post.max_chars == 2000


# ---------------------------------------------------------------------------
# BlogPost dataclass tests
# ---------------------------------------------------------------------------


class TestBlogPost:
    """Verify BlogPost dataclass stores fields correctly."""

    def test_stores_title(self) -> None:
        post = BlogPost(
            title="My Title", intro="Intro", sections=["S1"], conclusion="End"
        )
        assert post.title == "My Title"

    def test_stores_intro(self) -> None:
        post = BlogPost(
            title="T", intro="Introduction paragraph", sections=[], conclusion="C"
        )
        assert post.intro == "Introduction paragraph"

    def test_stores_sections_as_list(self) -> None:
        sections = ["Section one", "Section two", "Section three"]
        post = BlogPost(title="T", intro="I", sections=sections, conclusion="C")
        assert isinstance(post.sections, list)
        assert post.sections == sections

    def test_stores_conclusion(self) -> None:
        post = BlogPost(
            title="T", intro="I", sections=[], conclusion="Final thoughts"
        )
        assert post.conclusion == "Final thoughts"

    def test_empty_sections_list(self) -> None:
        post = BlogPost(title="T", intro="I", sections=[], conclusion="C")
        assert post.sections == []

    def test_single_section(self) -> None:
        post = BlogPost(title="T", intro="I", sections=["Only one"], conclusion="C")
        assert len(post.sections) == 1
        assert post.sections[0] == "Only one"


# ---------------------------------------------------------------------------
# format_instructions tests
# ---------------------------------------------------------------------------


class TestFormatInstructions:
    """Verify format_instructions returns correct formatting rules."""

    # --- LinkedIn ---

    def test_linkedin_returns_non_empty_string(self) -> None:
        result = format_instructions("linkedin")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_linkedin_mentions_hook(self) -> None:
        result = format_instructions("linkedin")
        assert "hook" in result.lower()

    def test_linkedin_mentions_cta(self) -> None:
        result = format_instructions("linkedin")
        lower = result.lower()
        assert "cta" in lower or "call to action" in lower

    def test_linkedin_mentions_character_limit(self) -> None:
        result = format_instructions("linkedin")
        lower = result.lower()
        assert "3000" in result or "character" in lower or "limit" in lower

    # --- Blog ---

    def test_blog_returns_non_empty_string(self) -> None:
        result = format_instructions("blog")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_blog_mentions_title(self) -> None:
        result = format_instructions("blog")
        assert "title" in result.lower()

    def test_blog_mentions_sections(self) -> None:
        result = format_instructions("blog")
        assert "section" in result.lower()

    def test_blog_mentions_conclusion(self) -> None:
        result = format_instructions("blog")
        assert "conclusion" in result.lower()

    # --- Error handling ---

    def test_unknown_format_raises_value_error(self) -> None:
        with pytest.raises(ValueError):
            format_instructions("newsletter")

    def test_empty_string_raises_value_error(self) -> None:
        with pytest.raises(ValueError):
            format_instructions("")

    def test_arbitrary_string_raises_value_error(self) -> None:
        with pytest.raises(ValueError):
            format_instructions("podcast")
