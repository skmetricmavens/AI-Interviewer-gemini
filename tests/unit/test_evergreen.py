"""Tests for evergreen topic bank in src.topics.evergreen."""

import pytest

from src.config import ContentPillar
from src.topics.evergreen import EVERGREEN_TOPICS, get_all_topics, get_topics

ALL_PILLARS = {
    "connected_journey",
    "crm_intelligence",
    "building_smart",
    "people_not_prompts",
    "field_notes",
}


class TestEvergreenTopicsConstant:
    """Verify EVERGREEN_TOPICS dict structure and content."""

    def test_has_all_five_pillars(self) -> None:
        assert set(EVERGREEN_TOPICS.keys()) == ALL_PILLARS

    def test_keys_match_content_pillar_values(self) -> None:
        expected = {member.value for member in ContentPillar}
        assert set(EVERGREEN_TOPICS.keys()) == expected

    def test_each_pillar_has_at_least_five_topics(self) -> None:
        for pillar, topics in EVERGREEN_TOPICS.items():
            assert len(topics) >= 5, f"Pillar '{pillar}' has only {len(topics)} topics"

    def test_all_topics_are_non_empty_strings(self) -> None:
        for pillar, topics in EVERGREEN_TOPICS.items():
            for topic in topics:
                assert isinstance(topic, str), (
                    f"Topic in '{pillar}' is not a string: {topic!r}"
                )
                assert len(topic.strip()) > 0, (
                    f"Topic in '{pillar}' is empty or whitespace"
                )

    def test_values_are_lists(self) -> None:
        for pillar, topics in EVERGREEN_TOPICS.items():
            assert isinstance(topics, list), (
                f"Value for '{pillar}' is not a list: {type(topics)}"
            )

    def test_no_duplicate_topics_within_pillar(self) -> None:
        for pillar, topics in EVERGREEN_TOPICS.items():
            assert len(topics) == len(set(topics)), (
                f"Pillar '{pillar}' contains duplicate topics"
            )


class TestGetTopics:
    """Verify get_topics() returns correct topics for a pillar."""

    @pytest.mark.parametrize("pillar", list(ALL_PILLARS))
    def test_returns_list_for_valid_pillar(self, pillar: str) -> None:
        result = get_topics(pillar)
        assert isinstance(result, list)
        assert len(result) >= 5

    def test_returns_same_data_as_constant(self) -> None:
        for pillar in ALL_PILLARS:
            assert get_topics(pillar) == EVERGREEN_TOPICS[pillar]

    def test_raises_value_error_for_unknown_pillar(self) -> None:
        with pytest.raises(ValueError):
            get_topics("nonexistent_pillar")

    def test_raises_value_error_for_empty_string(self) -> None:
        with pytest.raises(ValueError):
            get_topics("")

    def test_accepts_content_pillar_enum_value(self) -> None:
        result = get_topics(ContentPillar.field_notes)
        assert isinstance(result, list)
        assert len(result) >= 5


class TestGetAllTopics:
    """Verify get_all_topics() returns full topic bank."""

    def test_returns_dict(self) -> None:
        result = get_all_topics()
        assert isinstance(result, dict)

    def test_contains_all_five_pillars(self) -> None:
        result = get_all_topics()
        assert set(result.keys()) == ALL_PILLARS

    def test_returns_same_data_as_constant(self) -> None:
        assert get_all_topics() == EVERGREEN_TOPICS

    def test_returns_copy_not_reference(self) -> None:
        result = get_all_topics()
        assert result is not EVERGREEN_TOPICS
