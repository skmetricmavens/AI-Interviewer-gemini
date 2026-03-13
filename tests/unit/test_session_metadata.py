"""Tests for session metadata columns and get_session_metadata()."""

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


class TestCreateSessionMetadata:
    """Verify create_session() accepts and stores new metadata columns."""

    @pytest.mark.asyncio
    async def test_create_with_all_metadata(self, store: SessionStore) -> None:
        sid = await store.create_session(
            topic="CRM Strategy",
            context_file=None,
            language="en",
            interviewee_name="Sandy",
            content_pillar="crm_intelligence",
            target_architecture="narrative_arc",
            target_audience="marketing_leaders",
        )
        meta = await store.get_session_metadata(sid)
        assert meta["interviewee_name"] == "Sandy"
        assert meta["content_pillar"] == "crm_intelligence"
        assert meta["target_architecture"] == "narrative_arc"
        assert meta["target_audience"] == "marketing_leaders"

    @pytest.mark.asyncio
    async def test_create_without_metadata_defaults_none(
        self, store: SessionStore
    ) -> None:
        sid = await store.create_session(
            topic="Generic", context_file=None, language="en"
        )
        meta = await store.get_session_metadata(sid)
        assert meta["interviewee_name"] is None
        assert meta["content_pillar"] is None
        assert meta["target_architecture"] is None
        assert meta["target_audience"] is None

    @pytest.mark.asyncio
    async def test_create_with_partial_metadata(self, store: SessionStore) -> None:
        sid = await store.create_session(
            topic="Data Strategy",
            context_file=None,
            language="nl",
            interviewee_name="Julian",
            content_pillar="connected_journey",
        )
        meta = await store.get_session_metadata(sid)
        assert meta["interviewee_name"] == "Julian"
        assert meta["content_pillar"] == "connected_journey"
        assert meta["target_architecture"] is None
        assert meta["target_audience"] is None

    @pytest.mark.asyncio
    async def test_backward_compat_existing_fields(
        self, store: SessionStore
    ) -> None:
        """Existing fields still work when new metadata is provided."""
        sid = await store.create_session(
            topic="Test Topic",
            context_file="notes.pdf",
            language="en",
            interviewee_name="Sandy",
        )
        meta = await store.get_session_metadata(sid)
        assert meta["topic"] == "Test Topic"
        assert meta["context_file"] == "notes.pdf"
        assert meta["language"] == "en"
        assert meta["id"] == sid


class TestGetSessionMetadata:
    """Verify get_session_metadata() returns full session info."""

    @pytest.mark.asyncio
    async def test_returns_all_expected_keys(self, store: SessionStore) -> None:
        sid = await store.create_session(
            topic="Keys Test", context_file=None, language="en"
        )
        meta = await store.get_session_metadata(sid)
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
        assert set(meta.keys()) == expected_keys

    @pytest.mark.asyncio
    async def test_nonexistent_session_returns_none(
        self, store: SessionStore
    ) -> None:
        result = await store.get_session_metadata("nonexistent-id")
        assert result is None

    @pytest.mark.asyncio
    async def test_includes_timestamps(self, store: SessionStore) -> None:
        sid = await store.create_session(
            topic="Timestamps", context_file=None, language="en"
        )
        meta = await store.get_session_metadata(sid)
        assert meta["started_at"] is not None
        assert meta["ended_at"] is None


class TestListSessionsWithMetadata:
    """Verify list_sessions() returns new metadata columns."""

    @pytest.mark.asyncio
    async def test_list_includes_metadata_keys(self, store: SessionStore) -> None:
        await store.create_session(
            topic="List Test",
            context_file=None,
            language="en",
            interviewee_name="Sandy",
            content_pillar="field_notes",
        )
        sessions = await store.list_sessions()
        session = sessions[0]
        assert "interviewee_name" in session
        assert "content_pillar" in session
        assert session["interviewee_name"] == "Sandy"
        assert session["content_pillar"] == "field_notes"


class TestSchemaMigration:
    """Verify schema migration adds columns to existing databases."""

    @pytest.mark.asyncio
    async def test_migrate_existing_db(self, db_path: str) -> None:
        """A db created without metadata columns should gain them on reconnect."""
        # Create old-style db
        s1 = SessionStore(db_path)
        await s1.connect()
        sid = await s1.create_session(
            topic="Old Session", context_file=None, language="en"
        )
        await s1.close()

        # Reconnect — migration should add new columns
        s2 = SessionStore(db_path)
        await s2.connect()
        meta = await s2.get_session_metadata(sid)
        assert meta is not None
        assert meta["interviewee_name"] is None
        assert meta["content_pillar"] is None
        await s2.close()
