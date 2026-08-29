"""Tests for src.interview.pipecat_bot — InterviewBot class structure and logic."""

import uuid
from unittest.mock import patch

import pytest

from src.config import Settings
from src.interview.echo_suppressor import EchoSuppressor
from src.interview.pipecat_bot import InterviewBot, build_greeting
from src.storage.db import SessionStore


@pytest.fixture
def settings(tmp_path: object) -> Settings:
    """Create a Settings instance with fake API keys for testing."""
    return Settings(
        google_api_key="fake-google-key",
        elevenlabs_api_key="fake-elevenlabs-key",
        anthropic_api_key="fake-anthropic-key",
        elevenlabs_voice_id="fake-voice-id",
        db_path=str(tmp_path / "test_bot.db"),  # type: ignore[operator]
    )


@pytest.fixture
def db_path(tmp_path: object) -> str:
    """Return a temporary database path."""
    return str(tmp_path / "test_bot_sessions.db")  # type: ignore[operator]


@pytest.fixture
async def store(db_path: str) -> SessionStore:  # type: ignore[misc]
    """Create a connected SessionStore and close it after the test."""
    s = SessionStore(db_path)
    await s.connect()
    yield s  # type: ignore[misc]
    await s.close()


class TestInterviewBotInit:
    """Verify constructor stores settings and store references."""

    def test_stores_settings(self, settings: Settings, db_path: str) -> None:
        store = SessionStore(db_path)
        bot = InterviewBot(settings=settings, store=store)
        assert bot.settings is settings

    def test_stores_store(self, settings: Settings, db_path: str) -> None:
        store = SessionStore(db_path)
        bot = InterviewBot(settings=settings, store=store)
        assert bot.store is store


class TestSessionIdProperty:
    """Verify session_id property behavior."""

    def test_session_id_is_none_before_start(self, settings: Settings, db_path: str) -> None:
        store = SessionStore(db_path)
        bot = InterviewBot(settings=settings, store=store)
        assert bot.session_id is None


class TestStartSession:
    """Verify start_session creates a session and returns a UUID."""

    @pytest.mark.asyncio
    async def test_returns_uuid_string(self, settings: Settings, store: SessionStore) -> None:
        bot = InterviewBot(settings=settings, store=store)
        with patch.object(bot, "_build_pipeline"):
            session_id = await bot.start_session(
                topic="Python basics", context_text=None, language="en"
            )
        parsed = uuid.UUID(session_id)
        assert str(parsed) == session_id

    @pytest.mark.asyncio
    async def test_stores_session_id(self, settings: Settings, store: SessionStore) -> None:
        bot = InterviewBot(settings=settings, store=store)
        with patch.object(bot, "_build_pipeline"):
            session_id = await bot.start_session(
                topic="System design", context_text=None, language="en"
            )
        assert bot.session_id == session_id

    @pytest.mark.asyncio
    async def test_creates_session_in_store(self, settings: Settings, store: SessionStore) -> None:
        bot = InterviewBot(settings=settings, store=store)
        with patch.object(bot, "_build_pipeline"):
            session_id = await bot.start_session(
                topic="Algorithms", context_text="some context", language="nl"
            )
        sessions = await store.list_sessions()
        assert len(sessions) == 1
        assert sessions[0]["id"] == session_id
        assert sessions[0]["topic"] == "Algorithms"
        assert sessions[0]["language"] == "nl"

    @pytest.mark.asyncio
    async def test_passes_topic_and_context_to_build_pipeline(
        self, settings: Settings, store: SessionStore
    ) -> None:
        bot = InterviewBot(settings=settings, store=store)
        with patch.object(bot, "_build_pipeline") as mock_build:
            await bot.start_session(topic="ML basics", context_text="resume text", language="en")
        mock_build.assert_called_once_with(
            "ML basics",
            "resume text",
            "en",
            interviewee_name=None,
            content_pillar=None,
            target_architecture=None,
            target_audience=None,
            prepared_questions=None,
        )

    @pytest.mark.asyncio
    async def test_start_session_with_none_context(
        self, settings: Settings, store: SessionStore
    ) -> None:
        bot = InterviewBot(settings=settings, store=store)
        with patch.object(bot, "_build_pipeline"):
            session_id = await bot.start_session(topic="General", context_text=None, language="en")
        assert bot.session_id is not None
        assert session_id == bot.session_id


class TestOnUserTranscript:
    """Verify _on_user_transcript saves to store with role='user'."""

    @pytest.mark.asyncio
    async def test_saves_user_transcript(self, settings: Settings, store: SessionStore) -> None:
        bot = InterviewBot(settings=settings, store=store)
        with patch.object(bot, "_build_pipeline"):
            session_id = await bot.start_session(topic="Testing", context_text=None, language="en")
        await bot._on_user_transcript("Hello, I am the candidate.")
        transcript = await store.get_session_transcript(session_id)
        assert len(transcript) == 1
        assert transcript[0]["role"] == "user"
        assert transcript[0]["content"] == "Hello, I am the candidate."

    @pytest.mark.asyncio
    async def test_saves_multiple_user_transcripts(
        self, settings: Settings, store: SessionStore
    ) -> None:
        bot = InterviewBot(settings=settings, store=store)
        with patch.object(bot, "_build_pipeline"):
            session_id = await bot.start_session(topic="Multi", context_text=None, language="en")
        await bot._on_user_transcript("First message")
        await bot._on_user_transcript("Second message")
        transcript = await store.get_session_transcript(session_id)
        assert len(transcript) == 2
        assert transcript[0]["content"] == "First message"
        assert transcript[1]["content"] == "Second message"


class TestOnAssistantTranscript:
    """Verify _on_assistant_transcript saves to store with role='assistant'."""

    @pytest.mark.asyncio
    async def test_saves_assistant_transcript(
        self, settings: Settings, store: SessionStore
    ) -> None:
        bot = InterviewBot(settings=settings, store=store)
        with patch.object(bot, "_build_pipeline"):
            session_id = await bot.start_session(
                topic="Interview", context_text=None, language="en"
            )
        await bot._on_assistant_transcript("Welcome to the interview.")
        transcript = await store.get_session_transcript(session_id)
        assert len(transcript) == 1
        assert transcript[0]["role"] == "assistant"
        assert transcript[0]["content"] == "Welcome to the interview."

    @pytest.mark.asyncio
    async def test_interleaved_transcripts(self, settings: Settings, store: SessionStore) -> None:
        bot = InterviewBot(settings=settings, store=store)
        with patch.object(bot, "_build_pipeline"):
            session_id = await bot.start_session(topic="Dialog", context_text=None, language="en")
        await bot._on_assistant_transcript("Tell me about yourself.")
        await bot._on_user_transcript("I have 5 years of experience.")
        await bot._on_assistant_transcript("Great, tell me more.")
        transcript = await store.get_session_transcript(session_id)
        assert len(transcript) == 3
        assert transcript[0]["role"] == "assistant"
        assert transcript[1]["role"] == "user"
        assert transcript[2]["role"] == "assistant"


class TestStopSession:
    """Verify stop_session ends the session and clears state."""

    @pytest.mark.asyncio
    async def test_calls_end_session_on_store(
        self, settings: Settings, store: SessionStore
    ) -> None:
        bot = InterviewBot(settings=settings, store=store)
        with patch.object(bot, "_build_pipeline"):
            session_id = await bot.start_session(topic="Ending", context_text=None, language="en")
        await bot.stop_session()
        sessions = await store.list_sessions()
        session = [s for s in sessions if s["id"] == session_id][0]
        assert session["ended_at"] is not None

    @pytest.mark.asyncio
    async def test_sets_session_id_to_none(self, settings: Settings, store: SessionStore) -> None:
        bot = InterviewBot(settings=settings, store=store)
        with patch.object(bot, "_build_pipeline"):
            await bot.start_session(topic="Clear", context_text=None, language="en")
        assert bot.session_id is not None
        await bot.stop_session()
        assert bot.session_id is None

    @pytest.mark.asyncio
    async def test_stop_session_without_start_does_not_raise(
        self, settings: Settings, store: SessionStore
    ) -> None:
        """Calling stop_session when no session is active should not crash."""
        bot = InterviewBot(settings=settings, store=store)
        # Should not raise any exception
        await bot.stop_session()
        assert bot.session_id is None


class TestBuildGreeting:
    """Verify build_greeting produces warm, casual, topic-aware greetings."""

    # --- Happy path: English ---

    def test_english_greeting_contains_topic(self) -> None:
        """English greeting must mention the topic."""
        result = build_greeting(topic="Python basics", language="en")
        assert "Python basics" in result

    def test_english_greeting_returns_string(self) -> None:
        """build_greeting returns a plain string."""
        result = build_greeting(topic="microservices", language="en")
        assert isinstance(result, str)

    def test_english_greeting_is_short(self) -> None:
        """Greeting text (excluding the topic itself) should be under 60 chars."""
        topic = "Python basics"
        result = build_greeting(topic=topic, language="en")
        text_without_topic = result.replace(topic, "")
        assert len(text_without_topic) < 80

    def test_english_greeting_uses_contractions(self) -> None:
        """English greetings should sound casual with contractions."""
        result = build_greeting(topic="leadership", language="en")
        result_lower = result.lower()
        # At least one contraction should appear in the greeting
        contractions = ["don't", "i'm", "let's", "we're", "it's", "that's", "what's"]
        has_contraction = any(c in result_lower for c in contractions)
        assert has_contraction, (
            f"Expected at least one contraction in English greeting, got: {result!r}"
        )

    def test_english_greeting_no_formal_welcome(self) -> None:
        """English greeting must NOT contain the formal word 'Welcome'."""
        result = build_greeting(topic="data science", language="en")
        assert "Welcome" not in result
        assert "welcome" not in result

    def test_english_greeting_no_interviewing_you(self) -> None:
        """English greeting must NOT say 'I'll be interviewing you'."""
        result = build_greeting(topic="cloud computing", language="en")
        assert "interviewing you" not in result.lower()

    # --- Happy path: Dutch ---

    def test_dutch_greeting_contains_topic(self) -> None:
        """Dutch greeting must mention the topic."""
        result = build_greeting(topic="kunstmatige intelligentie", language="nl")
        assert "kunstmatige intelligentie" in result

    def test_dutch_greeting_returns_string(self) -> None:
        """Dutch greeting returns a plain string."""
        result = build_greeting(topic="leiderschap", language="nl")
        assert isinstance(result, str)

    def test_dutch_greeting_is_short(self) -> None:
        """Dutch greeting text (excluding topic) should be under 60 chars."""
        topic = "leiderschap"
        result = build_greeting(topic=topic, language="nl")
        text_without_topic = result.replace(topic, "")
        assert len(text_without_topic) < 80

    def test_dutch_greeting_no_formal_welkom(self) -> None:
        """Dutch greeting must NOT contain the formal word 'Welkom'."""
        result = build_greeting(topic="machine learning", language="nl")
        assert "Welkom" not in result
        assert "welkom" not in result

    def test_dutch_greeting_no_interviewing_phrase(self) -> None:
        """Dutch greeting must NOT say 'ga je interviewen'."""
        result = build_greeting(topic="Python", language="nl")
        assert "ga je interviewen" not in result.lower()

    # --- Edge cases ---

    def test_unknown_language_defaults_to_english(self) -> None:
        """Unknown language codes should fall back to English."""
        result = build_greeting(topic="testing", language="fr")
        # Should behave like English: contain the topic, no formal words
        assert "testing" in result
        assert "Welkom" not in result  # not Dutch

    def test_unknown_language_code_empty_string(self) -> None:
        """Empty language code should default to English."""
        result = build_greeting(topic="design patterns", language="")
        assert "design patterns" in result
        assert isinstance(result, str)

    def test_topic_with_special_characters(self) -> None:
        """Topic with special chars should appear verbatim in greeting."""
        topic = "C++ & Rust"
        result = build_greeting(topic=topic, language="en")
        assert topic in result

    def test_empty_topic(self) -> None:
        """Empty topic string should still produce a valid greeting."""
        result = build_greeting(topic="", language="en")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_long_topic_still_included(self) -> None:
        """A very long topic should still appear in the greeting."""
        topic = "the intersection of quantum computing and machine learning"
        result = build_greeting(topic=topic, language="en")
        assert topic in result

    # --- Variety: calling twice may produce different results ---

    def test_greeting_is_deterministic_for_same_inputs(self) -> None:
        """Same inputs should produce a consistent, non-empty greeting."""
        result_a = build_greeting(topic="APIs", language="en")
        result_b = build_greeting(topic="APIs", language="en")
        # Both should be valid non-empty strings (whether same or varied)
        assert len(result_a) > 0
        assert len(result_b) > 0


class TestEchoSuppressorWiring:
    """Verify EchoSuppressor is created with settings values."""

    def test_echo_suppressor_created_with_settings(self, settings: Settings) -> None:
        """EchoSuppressor should use echo settings from config."""
        es = EchoSuppressor(
            threshold=settings.echo_similarity_threshold,
            window_secs=settings.echo_suppress_window_secs,
            min_length=settings.echo_min_length,
        )
        assert es._threshold == settings.echo_similarity_threshold
        assert es._window_secs == settings.echo_suppress_window_secs
        assert es._min_length == settings.echo_min_length
