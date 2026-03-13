"""Tests for ContentPillar, TargetAudience, and OutputArchitecture enums in src.config."""

import pytest

from src.config import ContentPillar, TargetAudience, OutputArchitecture


class TestContentPillar:
    """Verify ContentPillar StrEnum members and behavior."""

    def test_member_count(self) -> None:
        assert len(ContentPillar) == 5

    def test_all_expected_members_exist(self) -> None:
        expected = {
            "connected_journey",
            "crm_intelligence",
            "building_smart",
            "people_not_prompts",
            "field_notes",
        }
        assert {m.name for m in ContentPillar} == expected

    def test_values_match_names(self) -> None:
        for member in ContentPillar:
            assert member.value == member.name

    def test_is_string_instance(self) -> None:
        for member in ContentPillar:
            assert isinstance(member, str)

    def test_string_comparison(self) -> None:
        assert ContentPillar.field_notes == "field_notes"
        assert ContentPillar.connected_journey == "connected_journey"
        assert ContentPillar.crm_intelligence == "crm_intelligence"
        assert ContentPillar.building_smart == "building_smart"
        assert ContentPillar.people_not_prompts == "people_not_prompts"

    def test_construct_from_string(self) -> None:
        assert ContentPillar("field_notes") is ContentPillar.field_notes

    def test_invalid_value_raises(self) -> None:
        with pytest.raises(ValueError):
            ContentPillar("nonexistent_pillar")


class TestTargetAudience:
    """Verify TargetAudience StrEnum members and behavior."""

    def test_member_count(self) -> None:
        assert len(TargetAudience) == 4

    def test_all_expected_members_exist(self) -> None:
        expected = {
            "crm_managers",
            "performance_marketers",
            "marketing_leaders",
            "c_suite",
        }
        assert {m.name for m in TargetAudience} == expected

    def test_values_match_names(self) -> None:
        for member in TargetAudience:
            assert member.value == member.name

    def test_is_string_instance(self) -> None:
        for member in TargetAudience:
            assert isinstance(member, str)

    def test_string_comparison(self) -> None:
        assert TargetAudience.crm_managers == "crm_managers"
        assert TargetAudience.performance_marketers == "performance_marketers"
        assert TargetAudience.marketing_leaders == "marketing_leaders"
        assert TargetAudience.c_suite == "c_suite"

    def test_construct_from_string(self) -> None:
        assert TargetAudience("c_suite") is TargetAudience.c_suite

    def test_invalid_value_raises(self) -> None:
        with pytest.raises(ValueError):
            TargetAudience("intern")


class TestOutputArchitecture:
    """Verify OutputArchitecture StrEnum members and behavior."""

    def test_member_count(self) -> None:
        assert len(OutputArchitecture) == 3

    def test_all_expected_members_exist(self) -> None:
        expected = {
            "inverted_pyramid",
            "narrative_arc",
            "pillar_cluster",
        }
        assert {m.name for m in OutputArchitecture} == expected

    def test_values_match_names(self) -> None:
        for member in OutputArchitecture:
            assert member.value == member.name

    def test_is_string_instance(self) -> None:
        for member in OutputArchitecture:
            assert isinstance(member, str)

    def test_string_comparison(self) -> None:
        assert OutputArchitecture.inverted_pyramid == "inverted_pyramid"
        assert OutputArchitecture.narrative_arc == "narrative_arc"
        assert OutputArchitecture.pillar_cluster == "pillar_cluster"

    def test_construct_from_string(self) -> None:
        assert OutputArchitecture("narrative_arc") is OutputArchitecture.narrative_arc

    def test_invalid_value_raises(self) -> None:
        with pytest.raises(ValueError):
            OutputArchitecture("free_form")
