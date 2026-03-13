"""Tests for passing metadata through InterviewBot.start_session."""

import uuid
from unittest.mock import patch

import pytest

from src.config import Settings
from src.interview.pipecat_bot import InterviewBot
from src.storage.db import SessionStore


@pytest.fixture
def settings() -> Settings:
    """Create test settings with dummy API keys."""
    return Settings(
        deepgram_api_key="test-dg-key",
        google_api_key="test-google-key",
        elevenlabs_api_key="test-el-key",
        anthropic_api_key="test-anthropic-key",
        elevenlabs_voice_id="test-voice-id",
    )


@pytest.fixture
async def store(tmp_path: object) -> SessionStore:  # type: ignore[misc]
    """Create a connected SessionStore."""
    s = SessionStore(str(tmp_path / "test.db"))  # type: ignore[operator]
    await s.connect()
    yield s  # type: ignore[misc]
    await s.close()


class TestStartSessionMetadata:
    """Verify start_session forwards metadata to store."""

    @pytest.mark.asyncio
    async def test_passes_metadata_to_store(
        self, settings: Settings, store: SessionStore
    ) -> None:
        bot = InterviewBot(settings=settings, store=store)
        with patch.object(bot, "_build_pipeline"):
            session_id = await bot.start_session(
                topic="CRM Strategy",
                context_text=None,
                language="en",
                interviewee_name="Sandy",
                content_pillar="crm_intelligence",
                target_architecture="narrative_arc",
                target_audience="marketing_leaders",
            )
        meta = await store.get_session_metadata(session_id)
        assert meta is not None
        assert meta["interviewee_name"] == "Sandy"
        assert meta["content_pillar"] == "crm_intelligence"
        assert meta["target_architecture"] == "narrative_arc"
        assert meta["target_audience"] == "marketing_leaders"

    @pytest.mark.asyncio
    async def test_metadata_defaults_none(
        self, settings: Settings, store: SessionStore
    ) -> None:
        bot = InterviewBot(settings=settings, store=store)
        with patch.object(bot, "_build_pipeline"):
            session_id = await bot.start_session(
                topic="Generic", context_text=None, language="en"
            )
        meta = await store.get_session_metadata(session_id)
        assert meta is not None
        assert meta["interviewee_name"] is None
        assert meta["content_pillar"] is None

    @pytest.mark.asyncio
    async def test_partial_metadata(
        self, settings: Settings, store: SessionStore
    ) -> None:
        bot = InterviewBot(settings=settings, store=store)
        with patch.object(bot, "_build_pipeline"):
            session_id = await bot.start_session(
                topic="Data Strategy",
                context_text=None,
                language="nl",
                interviewee_name="Julian",
            )
        meta = await store.get_session_metadata(session_id)
        assert meta is not None
        assert meta["interviewee_name"] == "Julian"
        assert meta["target_audience"] is None

    @pytest.mark.asyncio
    async def test_returns_valid_uuid(
        self, settings: Settings, store: SessionStore
    ) -> None:
        bot = InterviewBot(settings=settings, store=store)
        with patch.object(bot, "_build_pipeline"):
            session_id = await bot.start_session(
                topic="Test",
                context_text=None,
                language="en",
                interviewee_name="Sandy",
            )
        parsed = uuid.UUID(session_id)
        assert str(parsed) == session_id
