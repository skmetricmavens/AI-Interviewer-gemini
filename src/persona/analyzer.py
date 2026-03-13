"""Persona analyzer — extracts linguistic fingerprints from writing samples."""

from __future__ import annotations

import json
from pathlib import Path

import anthropic

AI_VOCABULARY_BLOCKLIST: list[str] = [
    "delve",
    "pivotal",
    "tapestry",
    "leverage",
    "transformative",
    "groundbreaking",
    "cutting-edge",
    "paradigm",
    "synergy",
    "holistic",
    "robust",
    "seamless",
    "elevate",
    "foster",
    "harness",
    "navigate",
    "nuanced",
    "resonate",
    "spearhead",
    "streamline",
    "underscore",
    "unlock",
    "empower",
    "landscape",
    "ecosystem",
]


class PersonaAnalyzer:
    """Analyzes writing samples to extract a linguistic fingerprint."""

    def __init__(self, anthropic_api_key: str) -> None:
        self.anthropic_api_key = anthropic_api_key

    def analyze_samples(self, sample_dir: str) -> dict:
        """Read writing samples and extract a linguistic fingerprint via Claude.

        Args:
            sample_dir: Path to directory containing .txt/.md writing samples.

        Returns:
            A fingerprint dict with style markers.
        """
        samples = self._read_samples(sample_dir)
        prompt = self._build_analysis_prompt(samples)

        client = anthropic.Anthropic(api_key=self.anthropic_api_key)
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}],
        )

        block = message.content[0]
        text = block.text  # type: ignore[union-attr]
        result: dict = json.loads(text)
        return result

    def save_fingerprint(self, fingerprint: dict, path: str) -> None:
        """Save a fingerprint dict as JSON."""
        Path(path).write_text(json.dumps(fingerprint, indent=2, ensure_ascii=False))

    def load_fingerprint(self, path: str) -> dict:
        """Load a fingerprint dict from a JSON file."""
        result: dict = json.loads(Path(path).read_text())
        return result

    def _read_samples(self, sample_dir: str) -> list[str]:
        """Read all .txt and .md files from a directory."""
        sample_path = Path(sample_dir)
        contents: list[str] = []
        for ext in ("*.txt", "*.md"):
            for file in sorted(sample_path.glob(ext)):
                contents.append(file.read_text())
        return contents

    def _build_analysis_prompt(self, samples: list[str]) -> str:
        """Build the Claude prompt for linguistic fingerprint extraction."""
        combined = "\n\n---\n\n".join(samples)
        return f"""Analyze the following writing samples and extract a linguistic fingerprint.

Return a JSON object with these exact keys:
- "sentence_length_avg": average number of words per sentence (float)
- "vocabulary_preferences": list of characteristic words/phrases the author uses
- "transition_style": how the author transitions between ideas (e.g., "direct", "flowing")
- "jargon": list of domain-specific terms the author uses
- "emoji_usage": how the author uses emojis ("none", "minimal", "frequent")
- "tone": overall writing tone (e.g., "professional", "casual", "conversational")

Return ONLY the JSON object, no additional text.

## Writing Samples

{combined}"""
