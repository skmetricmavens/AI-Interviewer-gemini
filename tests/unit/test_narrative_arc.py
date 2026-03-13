"""Tests for NarrativeArcArticle dataclass and format_instructions support."""

from src.writing.templates import NarrativeArcArticle, format_instructions


class TestNarrativeArcArticle:
    """Verify NarrativeArcArticle dataclass structure."""

    def test_instantiate_with_required_fields(self) -> None:
        article = NarrativeArcArticle(
            headline="Test", setup="Once upon a time"
        )
        assert article.headline == "Test"
        assert article.setup == "Once upon a time"

    def test_default_rising_action_is_empty_list(self) -> None:
        article = NarrativeArcArticle(headline="H", setup="S")
        assert article.rising_action == []

    def test_default_climax_is_empty_string(self) -> None:
        article = NarrativeArcArticle(headline="H", setup="S")
        assert article.climax == ""

    def test_default_resolution_is_empty_string(self) -> None:
        article = NarrativeArcArticle(headline="H", setup="S")
        assert article.resolution == ""

    def test_default_cta_is_empty_string(self) -> None:
        article = NarrativeArcArticle(headline="H", setup="S")
        assert article.cta == ""

    def test_instantiate_with_all_fields(self) -> None:
        article = NarrativeArcArticle(
            headline="H",
            setup="S",
            rising_action=["tension builds"],
            climax="the turning point",
            resolution="lessons learned",
            cta="share your story",
        )
        assert article.headline == "H"
        assert article.rising_action == ["tension builds"]
        assert article.climax == "the turning point"
        assert article.resolution == "lessons learned"
        assert article.cta == "share your story"

    def test_headline_is_string(self) -> None:
        article = NarrativeArcArticle(headline="H", setup="S")
        assert isinstance(article.headline, str)

    def test_rising_action_is_list(self) -> None:
        article = NarrativeArcArticle(headline="H", setup="S")
        assert isinstance(article.rising_action, list)

    def test_rising_action_default_is_independent(self) -> None:
        a = NarrativeArcArticle(headline="H", setup="S")
        b = NarrativeArcArticle(headline="H", setup="S")
        a.rising_action.append("x")
        assert b.rising_action == []


class TestFormatInstructionsNarrativeArc:
    """Verify format_instructions supports 'narrative_arc'."""

    def test_returns_string(self) -> None:
        result = format_instructions("narrative_arc")
        assert isinstance(result, str)

    def test_returns_non_empty(self) -> None:
        result = format_instructions("narrative_arc")
        assert len(result) > 0

    def test_mentions_narrative_or_story(self) -> None:
        result = format_instructions("narrative_arc").lower()
        assert "narrative" in result or "story" in result

    def test_mentions_climax_or_turning_point(self) -> None:
        result = format_instructions("narrative_arc").lower()
        assert "climax" in result or "turning point" in result

    def test_does_not_raise(self) -> None:
        format_instructions("narrative_arc")


class TestExistingFormatsRegression:
    """Verify existing formats still work."""

    def test_linkedin_still_works(self) -> None:
        assert isinstance(format_instructions("linkedin"), str)

    def test_blog_still_works(self) -> None:
        assert isinstance(format_instructions("blog"), str)

    def test_inverted_pyramid_still_works(self) -> None:
        assert isinstance(format_instructions("inverted_pyramid"), str)

    def test_unknown_still_raises(self) -> None:
        import pytest

        with pytest.raises(ValueError):
            format_instructions("unknown_format")
