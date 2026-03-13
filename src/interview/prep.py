"""Interview preparation — dataclass, markdown parser/writer, and question generator."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

import anthropic

from src.interview.prompts import PILLAR_QUESTIONS


@dataclass
class InterviewPrep:
    """Interview preparation data with topic, metadata, questions, and notes."""

    topic: str
    pillar: str = ""
    audience: str = ""
    architecture: str = ""
    language: str = "en"
    interviewee: str = ""
    questions: list[str] = field(default_factory=list)
    notes: str = ""


_FRONTMATTER_FIELDS = [
    "topic",
    "pillar",
    "audience",
    "architecture",
    "language",
    "interviewee",
]


def write_prep_file(prep: InterviewPrep, path: str) -> None:
    """Write an InterviewPrep to a markdown file with YAML-style frontmatter.

    Args:
        prep: The interview preparation data.
        path: File path to write to.
    """
    lines: list[str] = []

    # Frontmatter
    lines.append("---")
    for key in _FRONTMATTER_FIELDS:
        lines.append(f"{key}: {getattr(prep, key)}")
    lines.append("---")
    lines.append("")

    # Title
    lines.append(f"# Interview Prep: {prep.topic}")
    lines.append("")

    # Questions
    lines.append("## Questions")
    lines.append("")
    for q in prep.questions:
        lines.append(f"- {q}")
    if prep.questions:
        lines.append("")

    # Notes
    lines.append("## Notes")
    lines.append("")
    if prep.notes:
        lines.append(prep.notes)
    else:
        lines.append("_Add notes here._")
    lines.append("")

    Path(path).write_text("\n".join(lines), encoding="utf-8")


def parse_prep_file(path: str) -> InterviewPrep:
    """Parse a markdown prep file into an InterviewPrep.

    Args:
        path: Path to the markdown file.

    Returns:
        An InterviewPrep instance.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Prep file not found: {path}")

    content = file_path.read_text(encoding="utf-8")

    # Parse frontmatter
    frontmatter: dict[str, str] = {}
    if content.startswith("---\n"):
        end_idx = content.find("\n---\n", 4)
        if end_idx != -1:
            fm_text = content[4:end_idx]
            for line in fm_text.split("\n"):
                if ": " in line:
                    key, value = line.split(": ", 1)
                    frontmatter[key.strip()] = value.strip()
                elif line.endswith(":"):
                    frontmatter[line[:-1].strip()] = ""
            body = content[end_idx + 5 :]
        else:
            body = content
    else:
        body = content

    # Parse questions from ## Questions section
    questions: list[str] = []
    notes = ""

    questions_start = body.find("## Questions")
    notes_start = body.find("## Notes")

    if questions_start != -1:
        q_end = notes_start if notes_start != -1 else len(body)
        q_section = body[questions_start + len("## Questions") : q_end]
        for line in q_section.strip().split("\n"):
            stripped = line.strip()
            if stripped.startswith("- "):
                questions.append(stripped[2:])

    if notes_start != -1:
        notes_section = body[notes_start + len("## Notes") :].strip()
        if notes_section == "_Add notes here._":
            notes = ""
        else:
            notes = notes_section

    return InterviewPrep(
        topic=frontmatter.get("topic", ""),
        pillar=frontmatter.get("pillar", ""),
        audience=frontmatter.get("audience", ""),
        architecture=frontmatter.get("architecture", ""),
        language=frontmatter.get("language", "en"),
        interviewee=frontmatter.get("interviewee", ""),
        questions=questions,
        notes=notes,
    )


_LANGUAGE_MAP: dict[str, str] = {
    "en": "English",
    "nl": "Dutch",
}


class QuestionGenerator:
    """Generates interview questions for a topic using Claude."""

    def __init__(self, anthropic_api_key: str, model: str = "claude-sonnet-4-20250514") -> None:
        self.api_key = anthropic_api_key
        self.model = model

    def generate(
        self,
        topic: str,
        pillar: str = "",
        audience: str = "",
        language: str = "en",
        count: int = 8,
    ) -> list[str]:
        """Generate interview questions for a topic.

        Args:
            topic: The interview topic.
            pillar: Optional content pillar for context.
            audience: Optional target audience.
            language: Language code ("en" or "nl").
            count: Number of questions to generate.

        Returns:
            List of question strings.
        """
        prompt = self._build_prompt(topic, pillar, audience, language, count)

        client = anthropic.Anthropic(api_key=self.api_key)
        message = client.messages.create(
            model=self.model,
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}],
        )

        block = message.content[0]
        raw = block.text  # type: ignore[union-attr]
        data = json.loads(raw)
        return data.get("questions", [])  # type: ignore[no-any-return]

    def _build_prompt(
        self,
        topic: str,
        pillar: str,
        audience: str,
        language: str,
        count: int,
    ) -> str:
        """Build the Claude prompt for question generation."""
        lang_name = _LANGUAGE_MAP.get(language, "English")

        context_parts: list[str] = []
        if pillar:
            context_parts.append(f"- Content Pillar: {pillar}")
        if audience:
            context_parts.append(f"- Target Audience: {audience}")
        context_block = "\n".join(context_parts)

        # Include pillar-specific example questions if pillar matches
        examples_block = ""
        if pillar and pillar in PILLAR_QUESTIONS:
            example_questions = PILLAR_QUESTIONS[pillar]
            examples_text = "\n".join(f"- {q}" for q in example_questions)
            examples_block = f"\n## Example Questions (for reference)\n\n{examples_text}\n"

        return f"""Generate {count} interview questions for the topic: "{topic}"

## Context

- Language: {lang_name} ({language})
{context_block}
{examples_block}
## Instructions

Create a list of {count} open-ended interview questions that:
1. Extract deep insights and personal experiences
2. Progress from broad to specific
3. Include at least one question that challenges assumptions
4. Are conversational in tone (not formal or academic)
5. Write questions in {lang_name}

Return your response as JSON:
{{"questions": ["question 1", "question 2", ...]}}

Return ONLY valid JSON, no other text."""
