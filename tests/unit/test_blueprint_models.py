"""Tests for BlueprintSection and ArticleBlueprint data models."""

import pytest

from src.writing.blueprint import ArticleBlueprint, BlueprintSection


class TestBlueprintSection:
    """Verify BlueprintSection dataclass structure."""

    def test_creation_with_all_fields(self) -> None:
        section = BlueprintSection(
            title="Introduction",
            key_points=["point1", "point2"],
            source_quotes=["quote1", "quote2"],
        )
        assert section.title == "Introduction"
        assert section.key_points == ["point1", "point2"]
        assert section.source_quotes == ["quote1", "quote2"]

    def test_default_key_points_is_empty_list(self) -> None:
        section = BlueprintSection(title="Intro")
        assert section.key_points == []

    def test_default_source_quotes_is_empty_list(self) -> None:
        section = BlueprintSection(title="Intro")
        assert section.source_quotes == []

    def test_default_key_points_independent_across_instances(self) -> None:
        a = BlueprintSection(title="A")
        b = BlueprintSection(title="B")
        a.key_points.append("x")
        assert b.key_points == []

    def test_default_source_quotes_independent_across_instances(self) -> None:
        a = BlueprintSection(title="A")
        b = BlueprintSection(title="B")
        a.source_quotes.append("x")
        assert b.source_quotes == []

    def test_title_is_required(self) -> None:
        with pytest.raises(TypeError):
            BlueprintSection()  # type: ignore[call-arg]


class TestArticleBlueprint:
    """Verify ArticleBlueprint dataclass structure."""

    def test_creation_with_all_fields(self) -> None:
        section = BlueprintSection(
            title="Intro", key_points=["kp1"], source_quotes=["sq1"]
        )
        blueprint = ArticleBlueprint(
            headline="My Article",
            architecture="inverted_pyramid",
            sections=[section],
            target_audience="developers",
            content_pillar="engineering",
            estimated_word_count=1200,
            language="nl",
        )
        assert blueprint.headline == "My Article"
        assert blueprint.architecture == "inverted_pyramid"
        assert blueprint.sections == [section]
        assert blueprint.target_audience == "developers"
        assert blueprint.content_pillar == "engineering"
        assert blueprint.estimated_word_count == 1200
        assert blueprint.language == "nl"

    def test_default_target_audience_is_empty_string(self) -> None:
        bp = ArticleBlueprint(
            headline="H", architecture="blog", sections=[]
        )
        assert bp.target_audience == ""

    def test_default_content_pillar_is_empty_string(self) -> None:
        bp = ArticleBlueprint(
            headline="H", architecture="blog", sections=[]
        )
        assert bp.content_pillar == ""

    def test_default_estimated_word_count_is_800(self) -> None:
        bp = ArticleBlueprint(
            headline="H", architecture="blog", sections=[]
        )
        assert bp.estimated_word_count == 800

    def test_default_language_is_en(self) -> None:
        bp = ArticleBlueprint(
            headline="H", architecture="blog", sections=[]
        )
        assert bp.language == "en"

    def test_headline_is_required(self) -> None:
        with pytest.raises(TypeError):
            ArticleBlueprint(architecture="blog", sections=[])  # type: ignore[call-arg]

    def test_architecture_is_required(self) -> None:
        with pytest.raises(TypeError):
            ArticleBlueprint(headline="H", sections=[])  # type: ignore[call-arg]

    def test_sections_is_required(self) -> None:
        with pytest.raises(TypeError):
            ArticleBlueprint(headline="H", architecture="blog")  # type: ignore[call-arg]

    def test_sections_default_not_shared(self) -> None:
        """Sections is required so no mutable default issue, but verify list identity."""
        bp1 = ArticleBlueprint(headline="H", architecture="a", sections=[])
        bp2 = ArticleBlueprint(headline="H", architecture="a", sections=[])
        assert bp1.sections is not bp2.sections


class TestArticleBlueprintToMarkdown:
    """Verify to_markdown() rendering."""

    def _make_blueprint(self) -> ArticleBlueprint:
        sections = [
            BlueprintSection(
                title="Introduction",
                key_points=["AI is evolving", "Impacts are wide"],
                source_quotes=["It changed everything", "We saw 50% growth"],
            ),
            BlueprintSection(
                title="Deep Dive",
                key_points=["Technical details"],
                source_quotes=["The architecture is modular"],
            ),
        ]
        return ArticleBlueprint(
            headline="The Future of AI",
            architecture="narrative_arc",
            sections=sections,
            target_audience="tech leaders",
            content_pillar="innovation",
            estimated_word_count=1500,
            language="en",
        )

    def test_includes_headline(self) -> None:
        md = self._make_blueprint().to_markdown()
        assert "The Future of AI" in md

    def test_includes_architecture(self) -> None:
        md = self._make_blueprint().to_markdown()
        assert "narrative_arc" in md

    def test_includes_section_titles(self) -> None:
        md = self._make_blueprint().to_markdown()
        assert "Introduction" in md
        assert "Deep Dive" in md

    def test_includes_key_points(self) -> None:
        md = self._make_blueprint().to_markdown()
        assert "AI is evolving" in md
        assert "Impacts are wide" in md
        assert "Technical details" in md

    def test_includes_source_quotes(self) -> None:
        md = self._make_blueprint().to_markdown()
        assert "It changed everything" in md
        assert "We saw 50% growth" in md
        assert "The architecture is modular" in md

    def test_includes_target_audience(self) -> None:
        md = self._make_blueprint().to_markdown()
        assert "tech leaders" in md

    def test_includes_content_pillar(self) -> None:
        md = self._make_blueprint().to_markdown()
        assert "innovation" in md

    def test_includes_estimated_word_count(self) -> None:
        md = self._make_blueprint().to_markdown()
        assert "1500" in md

    def test_includes_language(self) -> None:
        md = self._make_blueprint().to_markdown()
        # "en" is short, check it appears in a metadata context
        assert "en" in md

    def test_returns_string(self) -> None:
        md = self._make_blueprint().to_markdown()
        assert isinstance(md, str)

    def test_is_non_empty(self) -> None:
        md = self._make_blueprint().to_markdown()
        assert len(md) > 0

    def test_empty_sections_list(self) -> None:
        bp = ArticleBlueprint(
            headline="Empty Article",
            architecture="blog",
            sections=[],
            target_audience="everyone",
            content_pillar="general",
            estimated_word_count=500,
            language="nl",
        )
        md = bp.to_markdown()
        assert "Empty Article" in md
        assert "blog" in md
        # Should not crash with empty sections
        assert isinstance(md, str)

    def test_section_with_empty_key_points_and_quotes(self) -> None:
        bp = ArticleBlueprint(
            headline="Sparse",
            architecture="linkedin",
            sections=[BlueprintSection(title="Only Title")],
        )
        md = bp.to_markdown()
        assert "Only Title" in md
        assert isinstance(md, str)
