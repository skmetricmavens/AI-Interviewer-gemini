"""Tests for src.storage.db — SessionStore with async SQLite storage."""

import uuid

import pytest

from src.storage.db import SessionStore


@pytest.fixture
def db_path(tmp_path: object) -> str:
    """Return a temporary database path."""
    return str(tmp_path / "test_sessions.db")  # type: ignore[operator]


@pytest.fixture
async def store(db_path: str) -> SessionStore:  # type: ignore[misc]
    """Create a connected SessionStore and close it after the test."""
    s = SessionStore(db_path)
    await s.connect()
    yield s  # type: ignore[misc]
    await s.close()


class TestSessionStoreInit:
    """Verify constructor stores db_path."""

    def test_stores_db_path(self, db_path: str) -> None:
        store = SessionStore(db_path)
        assert store.db_path == db_path


class TestConnect:
    """Verify connect() creates required tables."""

    @pytest.mark.asyncio
    async def test_creates_sessions_table(self, store: SessionStore) -> None:
        """After connect(), the sessions table should exist."""
        async with store._conn.execute(  # type: ignore[union-attr]
            "SELECT name FROM sqlite_master WHERE type='table' AND name='sessions'"
        ) as cursor:
            row = await cursor.fetchone()
        assert row is not None
        assert row[0] == "sessions"

    @pytest.mark.asyncio
    async def test_creates_transcripts_table(self, store: SessionStore) -> None:
        """After connect(), the transcripts table should exist."""
        async with store._conn.execute(  # type: ignore[union-attr]
            "SELECT name FROM sqlite_master WHERE type='table' AND name='transcripts'"
        ) as cursor:
            row = await cursor.fetchone()
        assert row is not None
        assert row[0] == "transcripts"

    @pytest.mark.asyncio
    async def test_connect_is_idempotent(self, db_path: str) -> None:
        """Calling connect() twice should not raise or corrupt data."""
        s = SessionStore(db_path)
        await s.connect()
        await s.connect()
        await s.close()


class TestCreateSession:
    """Verify create_session() stores a session and returns a UUID."""

    @pytest.mark.asyncio
    async def test_returns_uuid_string(self, store: SessionStore) -> None:
        session_id = await store.create_session(
            topic="Python basics", context_file=None, language="en"
        )
        # Should be a valid UUID
        parsed = uuid.UUID(session_id)
        assert str(parsed) == session_id

    @pytest.mark.asyncio
    async def test_session_is_persisted(self, store: SessionStore) -> None:
        session_id = await store.create_session(
            topic="System design", context_file="resume.pdf", language="en"
        )
        sessions = await store.list_sessions()
        assert len(sessions) == 1
        assert sessions[0]["id"] == session_id
        assert sessions[0]["topic"] == "System design"
        assert sessions[0]["context_file"] == "resume.pdf"
        assert sessions[0]["language"] == "en"

    @pytest.mark.asyncio
    async def test_session_has_started_at(self, store: SessionStore) -> None:
        session_id = await store.create_session(
            topic="Algorithms", context_file=None, language="en"
        )
        sessions = await store.list_sessions()
        assert sessions[0]["started_at"] is not None
        assert sessions[0]["started_at"] != ""

    @pytest.mark.asyncio
    async def test_session_ended_at_is_null(self, store: SessionStore) -> None:
        await store.create_session(
            topic="Algorithms", context_file=None, language="en"
        )
        sessions = await store.list_sessions()
        assert sessions[0]["ended_at"] is None

    @pytest.mark.asyncio
    async def test_context_file_none(self, store: SessionStore) -> None:
        await store.create_session(
            topic="Databases", context_file=None, language="nl"
        )
        sessions = await store.list_sessions()
        assert sessions[0]["context_file"] is None

    @pytest.mark.asyncio
    async def test_unique_ids_for_multiple_sessions(
        self, store: SessionStore
    ) -> None:
        id1 = await store.create_session(
            topic="Topic A", context_file=None, language="en"
        )
        id2 = await store.create_session(
            topic="Topic B", context_file=None, language="en"
        )
        assert id1 != id2


class TestEndSession:
    """Verify end_session() sets the ended_at timestamp."""

    @pytest.mark.asyncio
    async def test_sets_ended_at(self, store: SessionStore) -> None:
        session_id = await store.create_session(
            topic="Testing", context_file=None, language="en"
        )
        await store.end_session(session_id)
        sessions = await store.list_sessions()
        session = [s for s in sessions if s["id"] == session_id][0]
        assert session["ended_at"] is not None
        assert session["ended_at"] != ""

    @pytest.mark.asyncio
    async def test_end_session_does_not_affect_other_sessions(
        self, store: SessionStore
    ) -> None:
        id1 = await store.create_session(
            topic="Session 1", context_file=None, language="en"
        )
        id2 = await store.create_session(
            topic="Session 2", context_file=None, language="en"
        )
        await store.end_session(id1)
        sessions = await store.list_sessions()
        s1 = [s for s in sessions if s["id"] == id1][0]
        s2 = [s for s in sessions if s["id"] == id2][0]
        assert s1["ended_at"] is not None
        assert s2["ended_at"] is None


class TestAddTranscriptEntry:
    """Verify add_transcript_entry() stores role and content."""

    @pytest.mark.asyncio
    async def test_adds_user_entry(self, store: SessionStore) -> None:
        session_id = await store.create_session(
            topic="Chat", context_file=None, language="en"
        )
        await store.add_transcript_entry(session_id, "user", "Hello")
        transcript = await store.get_session_transcript(session_id)
        assert len(transcript) == 1
        assert transcript[0]["role"] == "user"
        assert transcript[0]["content"] == "Hello"

    @pytest.mark.asyncio
    async def test_adds_assistant_entry(self, store: SessionStore) -> None:
        session_id = await store.create_session(
            topic="Chat", context_file=None, language="en"
        )
        await store.add_transcript_entry(session_id, "assistant", "Hi there")
        transcript = await store.get_session_transcript(session_id)
        assert len(transcript) == 1
        assert transcript[0]["role"] == "assistant"
        assert transcript[0]["content"] == "Hi there"

    @pytest.mark.asyncio
    async def test_entry_has_timestamp(self, store: SessionStore) -> None:
        session_id = await store.create_session(
            topic="Chat", context_file=None, language="en"
        )
        await store.add_transcript_entry(session_id, "user", "Test")
        transcript = await store.get_session_transcript(session_id)
        assert "timestamp" in transcript[0]
        assert transcript[0]["timestamp"] is not None
        assert transcript[0]["timestamp"] != ""


class TestGetSessionTranscript:
    """Verify get_session_transcript() returns entries in order."""

    @pytest.mark.asyncio
    async def test_returns_entries_in_order(self, store: SessionStore) -> None:
        session_id = await store.create_session(
            topic="Interview", context_file=None, language="en"
        )
        await store.add_transcript_entry(session_id, "assistant", "First question")
        await store.add_transcript_entry(session_id, "user", "My answer")
        await store.add_transcript_entry(session_id, "assistant", "Follow up")

        transcript = await store.get_session_transcript(session_id)
        assert len(transcript) == 3
        assert transcript[0]["content"] == "First question"
        assert transcript[1]["content"] == "My answer"
        assert transcript[2]["content"] == "Follow up"

    @pytest.mark.asyncio
    async def test_empty_transcript(self, store: SessionStore) -> None:
        session_id = await store.create_session(
            topic="Empty", context_file=None, language="en"
        )
        transcript = await store.get_session_transcript(session_id)
        assert transcript == []

    @pytest.mark.asyncio
    async def test_returns_dict_with_expected_keys(
        self, store: SessionStore
    ) -> None:
        session_id = await store.create_session(
            topic="Keys", context_file=None, language="en"
        )
        await store.add_transcript_entry(session_id, "user", "Check keys")
        transcript = await store.get_session_transcript(session_id)
        entry = transcript[0]
        assert set(entry.keys()) == {"role", "content", "timestamp"}


class TestListSessions:
    """Verify list_sessions() returns all sessions."""

    @pytest.mark.asyncio
    async def test_empty_list_initially(self, store: SessionStore) -> None:
        sessions = await store.list_sessions()
        assert sessions == []

    @pytest.mark.asyncio
    async def test_returns_all_sessions(self, store: SessionStore) -> None:
        await store.create_session(topic="A", context_file=None, language="en")
        await store.create_session(topic="B", context_file="file.pdf", language="nl")
        await store.create_session(topic="C", context_file=None, language="de")

        sessions = await store.list_sessions()
        assert len(sessions) == 3
        topics = {s["topic"] for s in sessions}
        assert topics == {"A", "B", "C"}

    @pytest.mark.asyncio
    async def test_sessions_contain_expected_keys(
        self, store: SessionStore
    ) -> None:
        await store.create_session(topic="Keys", context_file=None, language="en")
        sessions = await store.list_sessions()
        session = sessions[0]
        expected_keys = {
            "id",
            "topic",
            "context_file",
            "language",
            "started_at",
            "ended_at",
            "interviewee_name",
            "content_pillar",
            "target_architecture",
            "target_audience",
        }
        assert set(session.keys()) == expected_keys


class TestSessionIsolation:
    """Verify multiple sessions don't interfere with each other."""

    @pytest.mark.asyncio
    async def test_transcripts_are_isolated(self, store: SessionStore) -> None:
        id1 = await store.create_session(
            topic="Session 1", context_file=None, language="en"
        )
        id2 = await store.create_session(
            topic="Session 2", context_file=None, language="en"
        )

        await store.add_transcript_entry(id1, "user", "Message for session 1")
        await store.add_transcript_entry(id2, "user", "Message for session 2")
        await store.add_transcript_entry(id1, "assistant", "Reply in session 1")

        t1 = await store.get_session_transcript(id1)
        t2 = await store.get_session_transcript(id2)

        assert len(t1) == 2
        assert len(t2) == 1
        assert t1[0]["content"] == "Message for session 1"
        assert t1[1]["content"] == "Reply in session 1"
        assert t2[0]["content"] == "Message for session 2"


class TestClose:
    """Verify close() can be called without error."""

    @pytest.mark.asyncio
    async def test_close_after_connect(self, db_path: str) -> None:
        s = SessionStore(db_path)
        await s.connect()
        await s.close()
        # Should not raise
