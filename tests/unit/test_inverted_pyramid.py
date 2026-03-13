"""Tests for InvertedPyramidArticle dataclass and format_instructions('inverted_pyramid')."""

import pytest

from src.writing.templates import InvertedPyramidArticle, format_instructions


# ---------------------------------------------------------------------------
# InvertedPyramidArticle dataclass tests
# ---------------------------------------------------------------------------


class TestInvertedPyramidArticle:
    """Verify InvertedPyramidArticle dataclass stores fields correctly."""

    def test_instantiate_with_required_fields(self) -> None:
        article = InvertedPyramidArticle(headline="Breaking News", lead="Something happened today.")
        assert article.headline == "Breaking News"
        assert article.lead == "Something happened today."

    def test_default_body_is_empty_list(self) -> None:
        article = InvertedPyramidArticle(headline="H", lead="L")
        assert article.body == []

    def test_default_background_is_empty_string(self) -> None:
        article = InvertedPyramidArticle(headline="H", lead="L")
        assert article.background == ""

    def test_default_cta_is_empty_string(self) -> None:
        article = InvertedPyramidArticle(headline="H", lead="L")
        assert article.cta == ""

    def test_instantiate_with_all_fields(self) -> None:
        article = InvertedPyramidArticle(
            headline="Major Discovery",
            lead="Scientists found a new species in the deep ocean.",
            body=["The species was found at 3000m depth.", "It resembles a jellyfish."],
            background="Deep-sea exploration has accelerated in recent years.",
            cta="Read the full research paper.",
        )
        assert article.headline == "Major Discovery"
        assert article.lead == "Scientists found a new species in the deep ocean."
        assert article.body == [
            "The species was found at 3000m depth.",
            "It resembles a jellyfish.",
        ]
        assert article.background == "Deep-sea exploration has accelerated in recent years."
        assert article.cta == "Read the full research paper."

    def test_headline_is_string(self) -> None:
        article = InvertedPyramidArticle(headline="Test Headline", lead="Test lead")
        assert isinstance(article.headline, str)

    def test_lead_is_string(self) -> None:
        article = InvertedPyramidArticle(headline="Test Headline", lead="Test lead")
        assert isinstance(article.lead, str)

    def test_body_is_list(self) -> None:
        article = InvertedPyramidArticle(
            headline="H", lead="L", body=["para1", "para2"]
        )
        assert isinstance(article.body, list)

    def test_body_default_is_independent_per_instance(self) -> None:
        """Ensure default_factory creates a new list for each instance."""
        a = InvertedPyramidArticle(headline="H1", lead="L1")
        b = InvertedPyramidArticle(headline="H2", lead="L2")
        a.body.append("extra")
        assert b.body == []


# ---------------------------------------------------------------------------
# format_instructions("inverted_pyramid") tests
# ---------------------------------------------------------------------------


class TestFormatInstructionsInvertedPyramid:
    """Verify format_instructions returns correct rules for inverted_pyramid."""

    def test_returns_string(self) -> None:
        result = format_instructions("inverted_pyramid")
        assert isinstance(result, str)

    def test_returns_non_empty_string(self) -> None:
        result = format_instructions("inverted_pyramid")
        assert len(result) > 0

    def test_mentions_headline_or_lead(self) -> None:
        result = format_instructions("inverted_pyramid")
        lower = result.lower()
        assert "headline" in lower or "lead" in lower

    def test_mentions_decreasing_importance(self) -> None:
        result = format_instructions("inverted_pyramid")
        lower = result.lower()
        assert (
            "decreasing" in lower
            or "most important" in lower
            or "importance" in lower
            or "inverted pyramid" in lower
        )

    def test_does_not_raise_value_error(self) -> None:
        # Should not raise — inverted_pyramid is a valid format
        format_instructions("inverted_pyramid")


# ---------------------------------------------------------------------------
# Existing formats still work (regression)
# ---------------------------------------------------------------------------


class TestExistingFormatsRegression:
    """Ensure adding inverted_pyramid did not break existing formats."""

    def test_linkedin_still_works(self) -> None:
        result = format_instructions("linkedin")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_blog_still_works(self) -> None:
        result = format_instructions("blog")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_unknown_format_still_raises_value_error(self) -> None:
        with pytest.raises(ValueError):
            format_instructions("unknown_format")
