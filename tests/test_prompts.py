"""Tests for src.interview.prompts — system prompt builder and interview rules."""

import pytest

from src.interview.prompts import INTERVIEW_RULES, build_system_prompt


class TestBuildSystemPromptTopic:
    """Verify the topic is always included in the output."""

    def test_topic_appears_in_prompt(self) -> None:
        result = build_system_prompt(topic="machine learning", context=None, language="en")
        assert "machine learning" in result

    def test_different_topic_appears(self) -> None:
        result = build_system_prompt(topic="distributed systems", context=None, language="en")
        assert "distributed systems" in result


class TestBuildSystemPromptContext:
    """Verify context handling — present, None, and empty string."""

    def test_context_included_when_provided(self) -> None:
        result = build_system_prompt(
            topic="Python", context="The candidate has 5 years experience", language="en"
        )
        assert "5 years experience" in result

    def test_works_when_context_is_none(self) -> None:
        result = build_system_prompt(topic="Python", context=None, language="en")
        # Should return a valid non-empty prompt without raising
        assert isinstance(result, str)
        assert len(result) > 0

    def test_works_when_context_is_empty_string(self) -> None:
        result = build_system_prompt(topic="Python", context="", language="en")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_context_not_mentioned_when_none(self) -> None:
        """When context is None, the prompt should not contain a stray 'None' literal."""
        result = build_system_prompt(topic="Python", context=None, language="en")
        assert "None" not in result


class TestBuildSystemPromptLanguage:
    """Verify the language parameter controls the response language instruction."""

    def test_english_language_mentioned(self) -> None:
        result = build_system_prompt(topic="Python", context=None, language="en")
        assert "english" in result.lower() or "English" in result

    def test_dutch_language_mentioned(self) -> None:
        result = build_system_prompt(topic="Python", context=None, language="nl")
        lower = result.lower()
        assert "dutch" in lower or "nederlands" in lower


class TestBuildSystemPromptRules:
    """Verify interview rules are embedded in the system prompt."""

    def test_one_question_per_turn_rule(self) -> None:
        result = build_system_prompt(topic="Python", context=None, language="en")
        lower = result.lower()
        assert "one" in lower or "1" in result

    def test_natural_reaction_before_question(self) -> None:
        result = build_system_prompt(topic="Python", context=None, language="en")
        assert "reaction" in result.lower() or "react" in result.lower()

    def test_prompt_instructs_interviewer_role(self) -> None:
        result = build_system_prompt(topic="Python", context=None, language="en")
        assert "interview" in result.lower()


class TestBuildSystemPromptReturnType:
    """Verify the function returns a string."""

    def test_returns_string(self) -> None:
        result = build_system_prompt(topic="Python", context=None, language="en")
        assert isinstance(result, str)


class TestInterviewRulesConstant:
    """Verify INTERVIEW_RULES is a non-empty string with expected content."""

    def test_is_string(self) -> None:
        assert isinstance(INTERVIEW_RULES, str)

    def test_is_non_empty(self) -> None:
        assert len(INTERVIEW_RULES) > 0

    def test_mentions_question_limit(self) -> None:
        lower = INTERVIEW_RULES.lower()
        assert "one" in lower or "1" in INTERVIEW_RULES

    def test_mentions_natural_reaction(self) -> None:
        assert "reaction" in INTERVIEW_RULES.lower() or "react" in INTERVIEW_RULES.lower()


class TestResponseLengthRules:
    """Verify INTERVIEW_RULES includes word-limit guidance for responses."""

    def test_mentions_reaction_word_limit(self) -> None:
        """Reactions/acknowledgements should be capped at ~30 words."""
        assert "30" in INTERVIEW_RULES

    def test_mentions_question_word_limit(self) -> None:
        """Questions should be capped at ~50 words."""
        assert "50" in INTERVIEW_RULES

    def test_mentions_brevity_keyword(self) -> None:
        """Rules should explicitly encourage short/brief/concise responses."""
        lower = INTERVIEW_RULES.lower()
        assert "short" in lower or "brief" in lower or "concise" in lower

    def test_word_limit_appears_before_advanced_techniques(self) -> None:
        """Length rules belong in the Core Rules section, before Advanced Techniques."""
        lower = INTERVIEW_RULES.lower()
        brevity_pos = -1
        for keyword in ("30", "50"):
            pos = INTERVIEW_RULES.find(keyword)
            if pos != -1:
                brevity_pos = pos
                break
        advanced_pos = lower.find("advanced techniques")
        assert brevity_pos != -1, "No word-limit number found in INTERVIEW_RULES"
        assert advanced_pos != -1, "Advanced Techniques section not found"
        assert brevity_pos < advanced_pos, "Word-limit rules should appear before Advanced Techniques"


class TestConversationalTone:
    """Verify INTERVIEW_RULES encourages a conversational, informal tone."""

    def test_mentions_contractions(self) -> None:
        """Rules should instruct the interviewer to use contractions."""
        lower = INTERVIEW_RULES.lower()
        assert "contraction" in lower

    def test_mentions_casual_or_natural_tone(self) -> None:
        """Rules should reference a casual, relaxed, or natural speaking style."""
        lower = INTERVIEW_RULES.lower()
        assert (
            "casual" in lower
            or "relaxed" in lower
            or "natural" in lower
            or "conversational" in lower
        )

    def test_tone_guidance_in_core_rules(self) -> None:
        """Tone instructions belong in the Core Rules section."""
        lower = INTERVIEW_RULES.lower()
        contraction_pos = lower.find("contraction")
        advanced_pos = lower.find("advanced techniques")
        assert contraction_pos != -1, "Contraction guidance not found in INTERVIEW_RULES"
        assert contraction_pos < advanced_pos, (
            "Contraction guidance should appear in Core Rules, before Advanced Techniques"
        )


class TestBuildSystemPromptApproach:
    """Verify the built prompt contains interview structure guidance."""

    def test_approach_mentions_keeping_responses_short(self) -> None:
        """The prompt should remind the model to keep responses short."""
        result = build_system_prompt(topic="Python", context=None, language="en")
        lower = result.lower()
        assert (
            "short" in lower or "brief" in lower or "concise" in lower
        ), "Built prompt should mention keeping responses short/brief/concise"

    def test_interview_phases_section_exists(self) -> None:
        """The built prompt must contain an 'Interview Phases' section."""
        result = build_system_prompt(topic="Python", context=None, language="en")
        assert "Interview Phases" in result
