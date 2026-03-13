"""Async SQLite storage for interview sessions and transcripts."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import aiosqlite


class SessionStore:
    """Async SQLite storage for sessions and transcripts."""

    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        self._conn: aiosqlite.Connection | None = None

    async def connect(self) -> None:
        """Open database connection and create tables if needed."""
        self._conn = await aiosqlite.connect(self.db_path)
        self._conn.row_factory = aiosqlite.Row
        await self._conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                topic TEXT NOT NULL,
                context_file TEXT,
                language TEXT NOT NULL,
                started_at TEXT NOT NULL,
                ended_at TEXT
            );
            CREATE TABLE IF NOT EXISTS transcripts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (session_id) REFERENCES sessions(id)
            );
            """
        )
        await self._conn.commit()
        # Migrate: add metadata columns if they don't exist yet
        for col in (
            "interviewee_name",
            "content_pillar",
            "target_architecture",
            "target_audience",
        ):
            try:
                await self._conn.execute(f"ALTER TABLE sessions ADD COLUMN {col} TEXT")
            except Exception:  # noqa: BLE001
                pass  # Column already exists
        await self._conn.commit()

    async def close(self) -> None:
        """Close the database connection."""
        if self._conn:
            await self._conn.close()
            self._conn = None

    async def create_session(
        self,
        topic: str,
        context_file: str | None,
        language: str,
        *,
        interviewee_name: str | None = None,
        content_pillar: str | None = None,
        target_architecture: str | None = None,
        target_audience: str | None = None,
    ) -> str:
        """Create a new interview session. Returns the session ID."""
        session_id = str(uuid.uuid4())
        started_at = datetime.now(timezone.utc).isoformat()
        assert self._conn is not None
        await self._conn.execute(
            "INSERT INTO sessions "
            "(id, topic, context_file, language, started_at, "
            "interviewee_name, content_pillar, target_architecture, target_audience) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                session_id,
                topic,
                context_file,
                language,
                started_at,
                interviewee_name,
                content_pillar,
                target_architecture,
                target_audience,
            ),
        )
        await self._conn.commit()
        return session_id

    async def end_session(self, session_id: str) -> None:
        """Mark a session as ended."""
        ended_at = datetime.now(timezone.utc).isoformat()
        assert self._conn is not None
        await self._conn.execute(
            "UPDATE sessions SET ended_at = ? WHERE id = ?",
            (ended_at, session_id),
        )
        await self._conn.commit()

    async def add_transcript_entry(self, session_id: str, role: str, content: str) -> None:
        """Add a transcript entry to a session."""
        timestamp = datetime.now(timezone.utc).isoformat()
        assert self._conn is not None
        await self._conn.execute(
            "INSERT INTO transcripts (session_id, role, content, timestamp) VALUES (?, ?, ?, ?)",
            (session_id, role, content, timestamp),
        )
        await self._conn.commit()

    async def get_session_transcript(self, session_id: str) -> list[dict[str, str]]:
        """Get all transcript entries for a session, ordered by timestamp."""
        assert self._conn is not None
        async with self._conn.execute(
            "SELECT role, content, timestamp FROM transcripts WHERE session_id = ? ORDER BY id",
            (session_id,),
        ) as cursor:
            rows = await cursor.fetchall()
        return [
            {"role": row["role"], "content": row["content"], "timestamp": row["timestamp"]}
            for row in rows
        ]

    async def get_session_metadata(self, session_id: str) -> dict[str, str | None] | None:
        """Get full metadata for a session, or None if not found."""
        assert self._conn is not None
        async with self._conn.execute(
            "SELECT id, topic, context_file, language, started_at, ended_at, "
            "interviewee_name, content_pillar, target_architecture, target_audience "
            "FROM sessions WHERE id = ?",
            (session_id,),
        ) as cursor:
            row = await cursor.fetchone()
        if row is None:
            return None
        return {
            "id": row["id"],
            "topic": row["topic"],
            "context_file": row["context_file"],
            "language": row["language"],
            "started_at": row["started_at"],
            "ended_at": row["ended_at"],
            "interviewee_name": row["interviewee_name"],
            "content_pillar": row["content_pillar"],
            "target_architecture": row["target_architecture"],
            "target_audience": row["target_audience"],
        }

    async def list_sessions(self) -> list[dict[str, str | None]]:
        """List all sessions."""
        assert self._conn is not None
        async with self._conn.execute(
            "SELECT id, topic, context_file, language, started_at, ended_at, "
            "interviewee_name, content_pillar, target_architecture, target_audience "
            "FROM sessions"
        ) as cursor:
            rows = await cursor.fetchall()
        return [
            {
                "id": row["id"],
                "topic": row["topic"],
                "context_file": row["context_file"],
                "language": row["language"],
                "started_at": row["started_at"],
                "ended_at": row["ended_at"],
                "interviewee_name": row["interviewee_name"],
                "content_pillar": row["content_pillar"],
                "target_architecture": row["target_architecture"],
                "target_audience": row["target_audience"],
            }
            for row in rows
        ]
