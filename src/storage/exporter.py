"""Transcript exporter for converting interview transcripts to various formats."""

from __future__ import annotations

import json
from pathlib import Path


class TranscriptExporter:
    """Export interview transcripts to markdown, plain text, or JSON formats.

    Each transcript is a list of dicts with 'role' and 'content' keys.
    Session metadata is an optional dict that may contain: id, topic, language,
    started_at, ended_at, interviewee_name, content_pillar, target_architecture,
    target_audience.
    """

    def to_markdown(
        self,
        transcript: list[dict[str, str]],
        session_metadata: dict[str, str | None] | None = None,
    ) -> str:
        """Convert transcript to markdown format with optional metadata header.

        Args:
            transcript: List of dicts with 'role' and 'content' keys.
            session_metadata: Optional dict with session info for the header.

        Returns:
            Markdown-formatted string.
        """
        parts: list[str] = []

        if session_metadata:
            parts.append("# Interview Transcript")
            parts.append("")
            for key, value in session_metadata.items():
                label = key.replace("_", " ").title()
                parts.append(f"- **{label}**: {value}")
            parts.append("")
            parts.append("---")
            parts.append("")

        for entry in transcript:
            role = entry["role"].title()
            content = entry["content"]
            parts.append(f"**{role}**: {content}")
            parts.append("")

        return "\n".join(parts)

    def to_plain_text(self, transcript: list[dict[str, str]]) -> str:
        """Convert transcript to plain text in ROLE: content format.

        Args:
            transcript: List of dicts with 'role' and 'content' keys.

        Returns:
            Plain text string with one line per entry.
        """
        if not transcript:
            return ""

        lines: list[str] = []
        for entry in transcript:
            role = entry["role"].upper()
            content = entry["content"]
            lines.append(f"{role}: {content}")

        return "\n".join(lines)

    def to_json(
        self,
        transcript: list[dict[str, str]],
        session_metadata: dict[str, str | None] | None = None,
    ) -> str:
        """Convert transcript to a JSON string.

        Args:
            transcript: List of dicts with 'role' and 'content' keys.
            session_metadata: Optional dict with session info.

        Returns:
            JSON-formatted string.
        """
        data: dict[str, object] = {"transcript": transcript}

        if session_metadata is not None:
            data["metadata"] = session_metadata

        return json.dumps(data, indent=2, ensure_ascii=False)

    def save(
        self,
        transcript: list[dict[str, str]],
        output_dir: str,
        session_id: str,
        format: str = "markdown",
        session_metadata: dict[str, str | None] | None = None,
    ) -> str:
        """Save transcript to a file with naming convention.

        Args:
            transcript: List of dicts with 'role' and 'content' keys.
            output_dir: Directory to save the file in.
            session_id: Session identifier for the filename.
            format: Export format ("markdown", "plain_text", or "json").
            session_metadata: Optional dict with session info.

        Returns:
            Full file path of the saved file.

        Raises:
            ValueError: If format is not recognized.
        """
        ext_map = {"markdown": ".md", "plain_text": ".txt", "json": ".json"}
        if format not in ext_map:
            raise ValueError(
                f"Unknown format: {format!r}. Use 'markdown', 'plain_text', or 'json'."
            )

        dir_path = Path(output_dir)
        dir_path.mkdir(parents=True, exist_ok=True)

        ext = ext_map[format]
        file_path = dir_path / f"{session_id}_{format}{ext}"

        if format == "markdown":
            content = self.to_markdown(transcript, session_metadata=session_metadata)
        elif format == "plain_text":
            content = self.to_plain_text(transcript)
        else:
            content = self.to_json(transcript, session_metadata=session_metadata)

        file_path.write_text(content, encoding="utf-8")
        return str(file_path)
