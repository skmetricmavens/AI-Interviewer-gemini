"""Blueprint data models and generator for article planning."""

from __future__ import annotations

import json
from dataclasses import dataclass, field

import anthropic


@dataclass
class BlueprintSection:
    """A section within an article blueprint."""

    title: str
    key_points: list[str] = field(default_factory=list)
    source_quotes: list[str] = field(default_factory=list)


@dataclass
class ArticleBlueprint:
    """A complete article blueprint with metadata."""

    headline: str
    architecture: str
    sections: list[BlueprintSection]
    target_audience: str = ""
    content_pillar: str = ""
    estimated_word_count: int = 800
    language: str = "en"

    def to_markdown(self) -> str:
        """Render the blueprint as a markdown string."""
        lines: list[str] = []
        lines.append(f"# {self.headline}")
        lines.append("")
        lines.append(f"**Architecture:** {self.architecture}")
        lines.append(f"**Target Audience:** {self.target_audience}")
        lines.append(f"**Content Pillar:** {self.content_pillar}")
        lines.append(f"**Estimated Word Count:** {self.estimated_word_count}")
        lines.append(f"**Language:** {self.language}")
        lines.append("")

        for section in self.sections:
            lines.append(f"## {section.title}")
            lines.append("")
            if section.key_points:
                lines.append("**Key Points:**")
                for point in section.key_points:
                    lines.append(f"- {point}")
                lines.append("")
            if section.source_quotes:
                lines.append("**Source Quotes:**")
                for quote in section.source_quotes:
                    lines.append(f"> {quote}")
                lines.append("")

        return "\n".join(lines)


_LANGUAGE_MAP: dict[str, str] = {
    "en": "English",
    "nl": "Dutch",
}


class BlueprintGenerator:
    """Generates article blueprints from interview transcripts using Claude."""

    def __init__(self, anthropic_api_key: str, model: str = "claude-sonnet-4-20250514") -> None:
        self.api_key = anthropic_api_key
        self.model = model

    def generate(
        self,
        transcript: list[dict[str, str]],
        architecture: str,
        content_pillar: str = "",
        target_audience: str = "",
        language: str = "en",
    ) -> ArticleBlueprint:
        """Generate an article blueprint from a transcript.

        Args:
            transcript: List of {"role": ..., "content": ...} dicts.
            architecture: Article architecture type.
            content_pillar: Optional content pillar.
            target_audience: Optional target audience.
            language: Language code ("en" or "nl").

        Returns:
            An ArticleBlueprint instance.
        """
        prompt = self._build_prompt(
            transcript, architecture, content_pillar, target_audience, language
        )

        client = anthropic.Anthropic(api_key=self.api_key)
        message = client.messages.create(
            model=self.model,
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )

        block = message.content[0]
        raw = block.text  # type: ignore[union-attr]
        data = json.loads(raw)

        sections = [
            BlueprintSection(
                title=s.get("title", ""),
                key_points=s.get("key_points", []),
                source_quotes=s.get("source_quotes", []),
            )
            for s in data.get("sections", [])
        ]

        return ArticleBlueprint(
            headline=data.get("headline", ""),
            architecture=architecture,
            sections=sections,
            target_audience=target_audience,
            content_pillar=content_pillar,
            estimated_word_count=data.get("estimated_word_count", 800),
            language=language,
        )

    def _build_prompt(
        self,
        transcript: list[dict[str, str]],
        architecture: str,
        content_pillar: str = "",
        target_audience: str = "",
        language: str = "en",
    ) -> str:
        """Build the Claude prompt for blueprint generation."""
        lang_name = _LANGUAGE_MAP.get(language, "English")

        transcript_text = "\n".join(
            f"{entry['role'].upper()}: {entry['content']}" for entry in transcript
        )

        context_parts: list[str] = []
        if content_pillar:
            context_parts.append(f"- Content Pillar: {content_pillar}")
        if target_audience:
            context_parts.append(f"- Target Audience: {target_audience}")
        context_block = "\n".join(context_parts)

        return f"""Analyze the interview transcript below and create an article \
blueprint using the "{architecture}" architecture.

## Context

- Architecture: {architecture}
- Language: {lang_name} ({language})
{context_block}

## Interview Transcript

{transcript_text}

## Instructions

Create a structured blueprint with a headline and sections. Each section should \
have a title, key_points (list of strings), and source_quotes (direct quotes from \
the transcript).

Return your response as JSON with this structure:
{{
  "headline": "...",
  "sections": [
    {{
      "title": "...",
      "key_points": ["..."],
      "source_quotes": ["..."]
    }}
  ],
  "estimated_word_count": 800
}}

Return ONLY valid JSON, no other text."""
