"""Configuration and environment management for AI Content Interviewer."""

from __future__ import annotations

import os
from dataclasses import dataclass, fields
from enum import StrEnum

import certifi
from dotenv import load_dotenv

# Fix SSL certificates for macOS Python — needed for NLTK downloads
os.environ.setdefault("SSL_CERT_FILE", certifi.where())


class ContentPillar(StrEnum):
    """MetricMavens content pillar categories."""

    connected_journey = "connected_journey"
    crm_intelligence = "crm_intelligence"
    building_smart = "building_smart"
    people_not_prompts = "people_not_prompts"
    field_notes = "field_notes"


class TargetAudience(StrEnum):
    """Target audience segments for content."""

    crm_managers = "crm_managers"
    performance_marketers = "performance_marketers"
    marketing_leaders = "marketing_leaders"
    c_suite = "c_suite"


class OutputArchitecture(StrEnum):
    """Article architecture types for content output."""

    inverted_pyramid = "inverted_pyramid"
    narrative_arc = "narrative_arc"
    pillar_cluster = "pillar_cluster"


_REQUIRED_ENV_KEYS = [
    "DEEPGRAM_API_KEY",
    "GOOGLE_API_KEY",
    "ELEVENLABS_API_KEY",
    "ANTHROPIC_API_KEY",
    "ELEVENLABS_VOICE_ID",
]


@dataclass
class Settings:
    """Application settings loaded from environment variables."""

    deepgram_api_key: str
    google_api_key: str
    elevenlabs_api_key: str
    anthropic_api_key: str
    elevenlabs_voice_id: str

    gemini_model: str = "gemini-2.0-flash"
    claude_model: str = "claude-sonnet-4-20250514"
    deepgram_language: str = "multi"
    deepgram_model: str = "nova-3"
    elevenlabs_tts_model: str = "eleven_turbo_v2_5"
    max_latency_ms: int = 600
    db_path: str = "sessions.db"

    # VAD tuning — lower = faster turn-taking, higher = more patience for pauses
    vad_stop_secs: float = 0.3
    vad_confidence: float = 0.7

    # ElevenLabs voice tuning — English defaults
    elevenlabs_stability: float = 0.5
    elevenlabs_similarity_boost: float = 0.75
    elevenlabs_style: float = 0.4

    # ElevenLabs voice tuning — Dutch overrides (higher stability for guttural sounds)
    elevenlabs_stability_nl: float = 0.7
    elevenlabs_similarity_boost_nl: float = 0.8
    elevenlabs_style_nl: float = 0.2

    # Echo suppression — prevents bot speech from being transcribed as user input
    echo_similarity_threshold: float = 0.6
    echo_suppress_window_secs: float = 8.0
    echo_min_length: int = 1
    echo_trailing_window_secs: float = 1.5

    def get_tts_params(self, language: str) -> dict[str, float]:
        """Return ElevenLabs voice params for the given language."""
        if language == "nl":
            return {
                "stability": self.elevenlabs_stability_nl,
                "similarity_boost": self.elevenlabs_similarity_boost_nl,
                "style": self.elevenlabs_style_nl,
            }
        return {
            "stability": self.elevenlabs_stability,
            "similarity_boost": self.elevenlabs_similarity_boost,
            "style": self.elevenlabs_style,
        }

    def validate(self) -> None:
        """Raise ValueError if any API key is empty or a placeholder."""
        api_fields = [f for f in fields(self) if f.name.endswith(("_key", "_id"))]
        for f in api_fields:
            value = getattr(self, f.name)
            if not value:
                raise ValueError(f"{f.name} must not be empty")
            if value.startswith("your-"):
                raise ValueError(f"{f.name} still contains a placeholder value: {value}")


def load_settings() -> Settings:
    """Load settings from environment variables (.env file)."""
    load_dotenv()

    env_values: dict[str, str] = {}
    for key in _REQUIRED_ENV_KEYS:
        value = os.environ.get(key)
        if value is None:
            raise ValueError(f"Missing required environment variable: {key}")
        env_values[key] = value

    return Settings(
        deepgram_api_key=env_values["DEEPGRAM_API_KEY"],
        google_api_key=env_values["GOOGLE_API_KEY"],
        elevenlabs_api_key=env_values["ELEVENLABS_API_KEY"],
        anthropic_api_key=env_values["ANTHROPIC_API_KEY"],
        elevenlabs_voice_id=env_values["ELEVENLABS_VOICE_ID"],
    )
