"""Topic generator — suggests interview topics using Claude."""

from __future__ import annotations

import json

import anthropic

from src.topics.evergreen import get_topics

_LANGUAGE_MAP: dict[str, str] = {
    "en": "English",
    "nl": "Dutch",
}


class TopicGenerator:
    """Suggests interview topics based on content pillars using Claude."""

    def __init__(self, anthropic_api_key: str, model: str = "claude-sonnet-4-20250514") -> None:
        self.api_key = anthropic_api_key
        self.model = model

    def suggest(self, pillar: str, count: int = 3, language: str = "en") -> list[str]:
        """Suggest interview topics for a content pillar.

        Args:
            pillar: Content pillar key (e.g. "connected_journey").
            count: Number of topics to suggest.
            language: Language code ("en" or "nl").

        Returns:
            List of topic strings.
        """
        evergreen_topics = get_topics(pillar)
        prompt = self._build_prompt(pillar, count, language, evergreen_topics)

        client = anthropic.Anthropic(api_key=self.api_key)
        message = client.messages.create(
            model=self.model,
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}],
        )

        block = message.content[0]
        raw = block.text  # type: ignore[union-attr]
        data = json.loads(raw)
        return data.get("topics", [])  # type: ignore[no-any-return]

    def _build_prompt(
        self,
        pillar: str,
        count: int,
        language: str,
        evergreen_topics: list[str],
    ) -> str:
        """Build the Claude prompt for topic suggestion."""
        lang_name = _LANGUAGE_MAP.get(language, "English")

        topics_text = ""
        if evergreen_topics:
            topics_text = "\n".join(f"- {t}" for t in evergreen_topics)

        return f"""Suggest {count} fresh interview topics for the content pillar \
"{pillar}".

## Context

- Content Pillar: {pillar}
- Language: {lang_name} ({language})
- Requested: {count} topics

## Existing Evergreen Topics (for reference, suggest NEW ones)

{topics_text}

## Instructions

Generate a list of {count} new interview topics that:
1. Fit the "{pillar}" content pillar
2. Are different from the existing evergreen topics above
3. Are timely and relevant
4. Would make for an engaging interview

Return your response as JSON:
{{"topics": ["topic 1", "topic 2", ...]}}

Return ONLY valid JSON, no other text."""
