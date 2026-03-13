"""Tests for src.config — Settings dataclass and load_settings function."""

import pytest

from src.config import Settings, load_settings

# --- Required environment variable names ---
REQUIRED_ENV_KEYS = [
    "GOOGLE_API_KEY",
    "ELEVENLABS_API_KEY",
    "ANTHROPIC_API_KEY",
    "ELEVENLABS_VOICE_ID",
]


def _valid_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Set all required env vars to realistic fake values."""
    monkeypatch.setenv("GOOGLE_API_KEY", "goog-key-abc123")
    monkeypatch.setenv("ELEVENLABS_API_KEY", "el-key-abc123")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "ant-key-abc123")
    monkeypatch.setenv("ELEVENLABS_VOICE_ID", "voice-id-abc123")


def _make_settings(**overrides: object) -> Settings:
    """Create a Settings instance with minimal required args and optional overrides."""
    defaults = {
        "google_api_key": "k",
        "elevenlabs_api_key": "k",
        "anthropic_api_key": "k",
        "elevenlabs_voice_id": "v",
    }
    defaults.update(overrides)
    return Settings(**defaults)  # type: ignore[arg-type]


class TestSettingsDefaults:
    """Verify default field values on the Settings dataclass."""

    def test_gemini_live_model_default(self) -> None:
        s = _make_settings()
        assert s.gemini_live_model == "gemini-2.0-flash"

    def test_claude_model_default(self) -> None:
        s = _make_settings()
        assert s.claude_model == "claude-sonnet-4-20250514"

    def test_elevenlabs_tts_model_default(self) -> None:
        s = _make_settings()
        assert s.elevenlabs_tts_model == "eleven_turbo_v2_5"

    def test_max_latency_ms_default(self) -> None:
        s = _make_settings()
        assert s.max_latency_ms == 600

    def test_db_path_default(self) -> None:
        s = _make_settings()
        assert s.db_path == "sessions.db"

    def test_session_max_minutes_default(self) -> None:
        s = _make_settings()
        assert s.session_max_minutes == 15.0


class TestSettingsValidate:
    """Verify the validate() method catches empty and placeholder API keys."""

    def test_valid_settings_passes(self) -> None:
        s = Settings(
            google_api_key="real-key-2",
            elevenlabs_api_key="real-key-3",
            anthropic_api_key="real-key-4",
            elevenlabs_voice_id="real-voice-id",
        )
        # Should not raise
        s.validate()

    @pytest.mark.parametrize(
        "field",
        [
            "google_api_key",
            "elevenlabs_api_key",
            "anthropic_api_key",
            "elevenlabs_voice_id",
        ],
    )
    def test_empty_api_key_raises(self, field: str) -> None:
        kwargs = {
            "google_api_key": "real-key",
            "elevenlabs_api_key": "real-key",
            "anthropic_api_key": "real-key",
            "elevenlabs_voice_id": "real-voice",
        }
        kwargs[field] = ""
        s = Settings(**kwargs)
        with pytest.raises(ValueError):
            s.validate()

    @pytest.mark.parametrize(
        "field,placeholder",
        [
            ("google_api_key", "your-google-api-key"),
            ("elevenlabs_api_key", "your-elevenlabs-api-key"),
            ("anthropic_api_key", "your-anthropic-api-key"),
            ("elevenlabs_voice_id", "your-elevenlabs-voice-id"),
        ],
    )
    def test_placeholder_value_raises(self, field: str, placeholder: str) -> None:
        kwargs = {
            "google_api_key": "real-key",
            "elevenlabs_api_key": "real-key",
            "anthropic_api_key": "real-key",
            "elevenlabs_voice_id": "real-voice",
        }
        kwargs[field] = placeholder
        s = Settings(**kwargs)
        with pytest.raises(ValueError):
            s.validate()

    def test_placeholder_prefix_your_dash_raises(self) -> None:
        """Any value starting with 'your-' should be rejected."""
        s = Settings(
            google_api_key="your-something-else",
            elevenlabs_api_key="real-key",
            anthropic_api_key="real-key",
            elevenlabs_voice_id="real-voice",
        )
        with pytest.raises(ValueError):
            s.validate()


class TestSettingsCustomValues:
    """Verify that non-default values are stored correctly."""

    def test_custom_model_values(self) -> None:
        s = _make_settings(
            gemini_live_model="gemini-pro",
            claude_model="claude-opus-4-20250514",
            max_latency_ms=1000,
            db_path="custom.db",
        )
        assert s.gemini_live_model == "gemini-pro"
        assert s.claude_model == "claude-opus-4-20250514"
        assert s.max_latency_ms == 1000
        assert s.db_path == "custom.db"


class TestLoadSettings:
    """Verify load_settings() reads environment and returns Settings."""

    def test_load_settings_from_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        _valid_env(monkeypatch)
        settings = load_settings()
        assert settings.google_api_key == "goog-key-abc123"
        assert settings.elevenlabs_api_key == "el-key-abc123"
        assert settings.anthropic_api_key == "ant-key-abc123"
        assert settings.elevenlabs_voice_id == "voice-id-abc123"

    def test_load_settings_returns_settings_instance(self, monkeypatch: pytest.MonkeyPatch) -> None:
        _valid_env(monkeypatch)
        settings = load_settings()
        assert isinstance(settings, Settings)

    @pytest.mark.parametrize("missing_key", REQUIRED_ENV_KEYS)
    def test_load_settings_missing_key_raises(
        self, monkeypatch: pytest.MonkeyPatch, missing_key: str
    ) -> None:
        _valid_env(monkeypatch)
        monkeypatch.delenv(missing_key, raising=False)
        # Prevent load_dotenv() from re-loading the real .env file
        monkeypatch.setattr("src.config.load_dotenv", lambda: None)
        with pytest.raises(ValueError):
            load_settings()

    def test_load_settings_uses_defaults_for_optional_fields(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _valid_env(monkeypatch)
        settings = load_settings()
        # Optional fields should get their defaults
        assert settings.gemini_live_model == "gemini-2.0-flash"
        assert settings.claude_model == "claude-sonnet-4-20250514"
        assert settings.elevenlabs_tts_model == "eleven_turbo_v2_5"
        assert settings.max_latency_ms == 600
        assert settings.db_path == "sessions.db"


class TestTTSSettings:
    """Verify ElevenLabs voice tuning defaults and bilingual prosody switching."""

    # --- EN (default) TTS parameter defaults ---

    def test_elevenlabs_stability_default(self) -> None:
        s = _make_settings()
        assert s.elevenlabs_stability == 0.5

    def test_elevenlabs_similarity_boost_default(self) -> None:
        s = _make_settings()
        assert s.elevenlabs_similarity_boost == 0.75

    def test_elevenlabs_style_default(self) -> None:
        s = _make_settings()
        assert s.elevenlabs_style == 0.4

    # --- NL-specific TTS parameter defaults ---

    def test_elevenlabs_stability_nl_default(self) -> None:
        s = _make_settings()
        assert s.elevenlabs_stability_nl == 0.7

    def test_elevenlabs_similarity_boost_nl_default(self) -> None:
        s = _make_settings()
        assert s.elevenlabs_similarity_boost_nl == 0.8

    def test_elevenlabs_style_nl_default(self) -> None:
        s = _make_settings()
        assert s.elevenlabs_style_nl == 0.2

    # --- Custom TTS values are stored correctly ---

    def test_custom_en_tts_values(self) -> None:
        s = _make_settings(
            elevenlabs_stability=0.3,
            elevenlabs_similarity_boost=0.9,
            elevenlabs_style=0.6,
        )
        assert s.elevenlabs_stability == 0.3
        assert s.elevenlabs_similarity_boost == 0.9
        assert s.elevenlabs_style == 0.6

    def test_custom_nl_tts_values(self) -> None:
        s = _make_settings(
            elevenlabs_stability_nl=0.9,
            elevenlabs_similarity_boost_nl=0.5,
            elevenlabs_style_nl=0.1,
        )
        assert s.elevenlabs_stability_nl == 0.9
        assert s.elevenlabs_similarity_boost_nl == 0.5
        assert s.elevenlabs_style_nl == 0.1

    # --- get_tts_params() bilingual switching ---

    def test_get_tts_params_en_returns_en_values(self) -> None:
        """English language should return EN default parameters."""
        s = _make_settings()
        params = s.get_tts_params("en")
        assert params == {
            "stability": 0.5,
            "similarity_boost": 0.75,
            "style": 0.4,
        }

    def test_get_tts_params_nl_returns_nl_values(self) -> None:
        """Dutch language should return NL-specific parameters."""
        s = _make_settings()
        params = s.get_tts_params("nl")
        assert params == {
            "stability": 0.7,
            "similarity_boost": 0.8,
            "style": 0.2,
        }

    def test_get_tts_params_unknown_language_defaults_to_en(self) -> None:
        """Unknown language codes should fall back to EN parameters."""
        s = _make_settings()
        params = s.get_tts_params("fr")
        assert params == {
            "stability": 0.5,
            "similarity_boost": 0.75,
            "style": 0.4,
        }

    def test_get_tts_params_with_custom_values(self) -> None:
        """get_tts_params should reflect custom (non-default) values."""
        s = _make_settings(
            elevenlabs_stability=0.1,
            elevenlabs_similarity_boost=0.2,
            elevenlabs_style=0.3,
            elevenlabs_stability_nl=0.4,
            elevenlabs_similarity_boost_nl=0.5,
            elevenlabs_style_nl=0.6,
        )
        en_params = s.get_tts_params("en")
        assert en_params == {
            "stability": 0.1,
            "similarity_boost": 0.2,
            "style": 0.3,
        }
        nl_params = s.get_tts_params("nl")
        assert nl_params == {
            "stability": 0.4,
            "similarity_boost": 0.5,
            "style": 0.6,
        }

    def test_get_tts_params_returns_dict_of_floats(self) -> None:
        """Return type should be dict[str, float]."""
        s = _make_settings()
        params = s.get_tts_params("en")
        assert isinstance(params, dict)
        for key, value in params.items():
            assert isinstance(key, str), f"Key {key!r} is not a string"
            assert isinstance(value, float), f"Value {value!r} for {key!r} is not a float"

    def test_get_tts_params_has_exactly_three_keys(self) -> None:
        """Params dict should contain exactly stability, similarity_boost, style."""
        s = _make_settings()
        expected_keys = {"stability", "similarity_boost", "style"}
        assert set(s.get_tts_params("en").keys()) == expected_keys
        assert set(s.get_tts_params("nl").keys()) == expected_keys

    def test_get_tts_params_empty_string_defaults_to_en(self) -> None:
        """Empty string language should fall back to EN parameters."""
        s = _make_settings()
        params = s.get_tts_params("")
        assert params == {
            "stability": 0.5,
            "similarity_boost": 0.75,
            "style": 0.4,
        }


class TestEchoSuppressionSettings:
    """Verify echo suppression settings on Settings dataclass."""

    def test_echo_similarity_threshold_default(self) -> None:
        s = _make_settings()
        assert s.echo_similarity_threshold == 0.6

    def test_echo_suppress_window_secs_default(self) -> None:
        s = _make_settings()
        assert s.echo_suppress_window_secs == 8.0

    def test_echo_min_length_default(self) -> None:
        """Default echo_min_length should be 1 (lowered from 3)."""
        s = _make_settings()
        assert s.echo_min_length == 1

    def test_echo_trailing_window_secs_default(self) -> None:
        """Default echo_trailing_window_secs should be 1.5."""
        s = _make_settings()
        assert s.echo_trailing_window_secs == 1.5

    def test_echo_similarity_threshold_custom(self) -> None:
        s = _make_settings(echo_similarity_threshold=0.8)
        assert s.echo_similarity_threshold == 0.8

    def test_echo_suppress_window_secs_custom(self) -> None:
        s = _make_settings(echo_suppress_window_secs=5.0)
        assert s.echo_suppress_window_secs == 5.0

    def test_echo_min_length_custom(self) -> None:
        s = _make_settings(echo_min_length=5)
        assert s.echo_min_length == 5

    def test_echo_trailing_window_secs_custom(self) -> None:
        """echo_trailing_window_secs can be set to a custom value."""
        s = _make_settings(echo_trailing_window_secs=3.0)
        assert s.echo_trailing_window_secs == 3.0
