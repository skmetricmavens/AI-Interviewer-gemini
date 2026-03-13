"""Content humanizer — generates human-sounding content from interview transcripts."""

from __future__ import annotations

import json

import anthropic

from src.persona.analyzer import AI_VOCABULARY_BLOCKLIST
from src.writing.templates import format_instructions

_LANGUAGE_MAP: dict[str, str] = {
    "en": "English",
    "nl": "Dutch",
}


class ContentHumanizer:
    """Generates humanized content from interview transcripts using Claude."""

    def __init__(self, anthropic_api_key: str, model: str = "claude-sonnet-4-20250514") -> None:
        self.anthropic_api_key = anthropic_api_key
        self.model = model

    def generate(
        self,
        transcript: list[dict[str, str]],
        fingerprint: dict,
        format_type: str,
        language: str,
    ) -> str:
        """Generate humanized content from a transcript.

        Args:
            transcript: List of {"role": ..., "content": ...} dicts.
            fingerprint: Linguistic fingerprint from PersonaAnalyzer.
            format_type: Output format ("linkedin" or "blog").
            language: Language code ("en" or "nl").

        Returns:
            Generated content string.
        """
        prompt = self._build_prompt(transcript, fingerprint, format_type, language)

        client = anthropic.Anthropic(api_key=self.anthropic_api_key)
        message = client.messages.create(
            model=self.model,
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )

        block = message.content[0]
        return block.text  # type: ignore[union-attr]

    def _build_prompt(
        self,
        transcript: list[dict[str, str]],
        fingerprint: dict,
        format_type: str,
        language: str,
    ) -> str:
        """Build the Claude prompt for content generation."""
        lang_name = _LANGUAGE_MAP.get(language, "English")

        transcript_text = "\n".join(
            f"{entry['role'].upper()}: {entry['content']}" for entry in transcript
        )

        fingerprint_text = json.dumps(fingerprint, indent=2, ensure_ascii=False)

        blocklist_text = ", ".join(AI_VOCABULARY_BLOCKLIST)

        fmt_instructions = format_instructions(format_type)

        return f"""You are a ghostwriter. Your task is to write a {format_type} post \
based on the interview transcript below.

## Output Requirements

- Write in {lang_name}.
- Write in first person ("I" / "Ik") — as if the interviewee is the author.
- Match the writing style described in the fingerprint below.
- Do NOT use emoji unless the fingerprint indicates emoji usage.
- Do NOT use any of these AI-sounding words: {blocklist_text}
- If writing in Dutch, use idiomatic Dutch — not a literal translation from English.

## Format Instructions

{fmt_instructions}

## Linguistic Fingerprint (match this style)

{fingerprint_text}

## Interview Transcript

{transcript_text}

## Instructions

Write the {format_type} post now. Return ONLY the content, no meta-commentary."""
