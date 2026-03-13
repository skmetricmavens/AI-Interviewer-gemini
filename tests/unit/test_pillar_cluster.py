"""Tests for PillarClusterArticle, CTA_PATTERNS, and format_instructions."""

import pytest

from src.writing.templates import (
    CTA_PATTERNS,
    PillarClusterArticle,
    format_instructions,
)


class TestPillarClusterArticle:
    """Verify PillarClusterArticle dataclass structure."""

    def test_instantiate_with_required_fields(self) -> None:
        article = PillarClusterArticle(
            headline="Pillar", pillar_summary="Overview"
        )
        assert article.headline == "Pillar"
        assert article.pillar_summary == "Overview"

    def test_default_clusters_is_empty_list(self) -> None:
        article = PillarClusterArticle(headline="H", pillar_summary="S")
        assert article.clusters == []

    def test_default_internal_links_is_empty_list(self) -> None:
        article = PillarClusterArticle(headline="H", pillar_summary="S")
        assert article.internal_links == []

    def test_default_cta_is_empty_string(self) -> None:
        article = PillarClusterArticle(headline="H", pillar_summary="S")
        assert article.cta == ""

    def test_instantiate_with_all_fields(self) -> None:
        article = PillarClusterArticle(
            headline="H",
            pillar_summary="S",
            clusters=["cluster1"],
            internal_links=["link1"],
            cta="subscribe",
        )
        assert article.clusters == ["cluster1"]
        assert article.internal_links == ["link1"]
        assert article.cta == "subscribe"

    def test_clusters_default_is_independent(self) -> None:
        a = PillarClusterArticle(headline="H", pillar_summary="S")
        b = PillarClusterArticle(headline="H", pillar_summary="S")
        a.clusters.append("x")
        assert b.clusters == []

    def test_internal_links_default_is_independent(self) -> None:
        a = PillarClusterArticle(headline="H", pillar_summary="S")
        b = PillarClusterArticle(headline="H", pillar_summary="S")
        a.internal_links.append("x")
        assert b.internal_links == []


class TestFormatInstructionsPillarCluster:
    """Verify format_instructions supports 'pillar_cluster'."""

    def test_returns_string(self) -> None:
        assert isinstance(format_instructions("pillar_cluster"), str)

    def test_returns_non_empty(self) -> None:
        assert len(format_instructions("pillar_cluster")) > 0

    def test_mentions_pillar_or_cluster(self) -> None:
        result = format_instructions("pillar_cluster").lower()
        assert "pillar" in result or "cluster" in result

    def test_mentions_links_or_seo(self) -> None:
        result = format_instructions("pillar_cluster").lower()
        assert "link" in result or "seo" in result

    def test_does_not_raise(self) -> None:
        format_instructions("pillar_cluster")


class TestCtaPatterns:
    """Verify CTA_PATTERNS constant."""

    def test_is_dict(self) -> None:
        assert isinstance(CTA_PATTERNS, dict)

    def test_has_at_least_three_keys(self) -> None:
        assert len(CTA_PATTERNS) >= 3

    def test_each_value_is_nonempty_list(self) -> None:
        for key, patterns in CTA_PATTERNS.items():
            assert isinstance(patterns, list), f"{key} is not a list"
            assert len(patterns) > 0, f"{key} has empty list"

    def test_each_pattern_is_nonempty_string(self) -> None:
        for key, patterns in CTA_PATTERNS.items():
            for p in patterns:
                assert isinstance(p, str), f"{key} has non-string: {p}"
                assert len(p.strip()) > 0, f"{key} has blank pattern"

    def test_keys_are_strings(self) -> None:
        for key in CTA_PATTERNS:
            assert isinstance(key, str)


class TestExistingFormatsRegression:
    """Existing formats still work."""

    def test_linkedin(self) -> None:
        assert isinstance(format_instructions("linkedin"), str)

    def test_blog(self) -> None:
        assert isinstance(format_instructions("blog"), str)

    def test_inverted_pyramid(self) -> None:
        assert isinstance(format_instructions("inverted_pyramid"), str)

    def test_narrative_arc(self) -> None:
        assert isinstance(format_instructions("narrative_arc"), str)

    def test_unknown_raises(self) -> None:
        with pytest.raises(ValueError):
            format_instructions("nope")
