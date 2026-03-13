"""Pipecat voice pipeline for conducting AI interviews.

Uses GeminiLiveLLMService for native STT + LLM in a single WebSocket,
with ElevenLabs TTS for high-quality custom voice output.
"""

from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING

from pipecat.frames.frames import (
    EndFrame,
    LLMTextFrame,
    TranscriptionFrame,
    TTSTextFrame,
)
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.frame_processor import FrameDirection, FrameProcessor
from pipecat.services.elevenlabs.tts import ElevenLabsTTSService
from pipecat.services.google.gemini_live.llm import (
    GeminiLiveLLMService,
    GeminiModalities,
    InputParams,
)
from pipecat.transports.local.audio import LocalAudioTransport, LocalAudioTransportParams

from src.interview.echo_suppressor import EchoSuppressor
from src.interview.latency_logger import LatencyLogger
from src.interview.mic_muter import MicMuter
from src.interview.prompts import build_system_prompt

if TYPE_CHECKING:
    from pipecat.frames.frames import Frame

    from src.config import Settings
    from src.storage.db import SessionStore

logger = logging.getLogger("ai_interviewer.bot")

# GeminiLive uses 24kHz for audio I/O
AUDIO_SAMPLE_RATE = 24000

# Session timer thresholds (seconds)
SESSION_WARN_SECS = 14 * 60  # 14 min — warn interviewer
SESSION_WRAPUP_SECS = 14.5 * 60  # 14:30 — start wrap-up
SESSION_DISCONNECT_SECS = 14 * 60 + 55  # 14:55 — disconnect


def build_greeting(topic: str, language: str) -> str:
    """Build a casual, warm greeting for the interview opener.

    Args:
        topic: The interview topic.
        language: Language code ("en" or "nl").

    Returns:
        A short, conversational greeting string.
    """
    if language == "nl":
        return f"Hey, leuk dat je er bent! We duiken in {topic}. Wat houdt je bezig?"
    return f"Hey, great to have you! Let's talk about {topic}. What's on your mind?"


class TranscriptCollector(FrameProcessor):
    """Captures TranscriptionFrame (user) and LLMTextFrame (assistant) for persistence.

    GeminiLive emits TranscriptionFrame for user speech transcription and
    LLMTextFrame for assistant text output (in TEXT mode). This processor
    captures both and forwards them to the session store.
    """

    def __init__(
        self,
        *,
        on_user_transcript: object,
        on_assistant_transcript: object,
        echo_suppressor: EchoSuppressor,
    ) -> None:
        super().__init__()
        self._on_user_transcript = on_user_transcript
        self._on_assistant_transcript = on_assistant_transcript
        self._echo_suppressor = echo_suppressor
        self._current_assistant_text: list[str] = []
        self._collecting_assistant: bool = False

    async def process_frame(self, frame: Frame, direction: FrameDirection) -> None:
        await super().process_frame(frame, direction)

        if isinstance(frame, TranscriptionFrame):
            # User speech transcription from GeminiLive
            if self._on_user_transcript and frame.text.strip():
                await self._on_user_transcript(frame.text)  # type: ignore[operator]

        elif isinstance(frame, LLMTextFrame):
            # Collect assistant text chunks
            self._collecting_assistant = True
            self._current_assistant_text.append(frame.text)

        elif isinstance(frame, TTSTextFrame):
            # TTSTextFrame signals a complete sentence going to TTS
            # Record it for echo suppression
            self._echo_suppressor.record_bot_utterance(frame.text)

        # Flush assistant text on non-text frames if we were collecting
        if self._collecting_assistant and not isinstance(frame, LLMTextFrame):
            full_text = "".join(self._current_assistant_text).strip()
            if full_text and self._on_assistant_transcript:
                await self._on_assistant_transcript(full_text)  # type: ignore[operator]
            self._current_assistant_text = []
            self._collecting_assistant = False

        await self.push_frame(frame, direction)


class InterviewBot:
    """Orchestrates a Pipecat voice pipeline for conducting interviews."""

    def __init__(self, settings: Settings, store: SessionStore) -> None:
        self.settings = settings
        self.store = store
        self._session_id: str | None = None
        self._pipeline: Pipeline | None = None
        self._task: PipelineTask | None = None
        self._transport: LocalAudioTransport | None = None

    @property
    def session_id(self) -> str | None:
        """Current session ID, or None if no session is active."""
        return self._session_id

    async def start_session(
        self,
        topic: str,
        context_text: str | None,
        language: str,
        *,
        interviewee_name: str | None = None,
        content_pillar: str | None = None,
        target_architecture: str | None = None,
        target_audience: str | None = None,
        prepared_questions: list[str] | None = None,
    ) -> str:
        """Create a new interview session and build the pipeline.

        Args:
            topic: The interview topic.
            context_text: Optional context from a file.
            language: Language code ("en" or "nl").
            interviewee_name: Name of the interviewee.
            content_pillar: MetricMavens content pillar.
            target_architecture: Article architecture type.
            target_audience: Target audience segment.
            prepared_questions: Pre-written questions from a prep file.

        Returns:
            The session ID.
        """
        self._session_id = await self.store.create_session(
            topic=topic,
            context_file=None,
            language=language,
            interviewee_name=interviewee_name,
            content_pillar=content_pillar,
            target_architecture=target_architecture,
            target_audience=target_audience,
        )
        self._build_pipeline(
            topic,
            context_text,
            language,
            interviewee_name=interviewee_name,
            content_pillar=content_pillar,
            target_architecture=target_architecture,
            target_audience=target_audience,
            prepared_questions=prepared_questions,
        )
        return self._session_id

    async def run(self) -> None:
        """Run the voice pipeline. Blocks until the session ends."""
        if self._task is None:
            return
        runner = PipelineRunner(handle_sigint=True)
        await runner.run(self._task)

    async def stop_session(self) -> None:
        """End the current session and clean up."""
        if self._session_id is not None:
            await self.store.end_session(self._session_id)
        self._session_id = None
        self._pipeline = None
        self._task = None
        self._transport = None

    def _build_pipeline(
        self,
        topic: str,
        context_text: str | None,
        language: str,
        *,
        interviewee_name: str | None = None,
        content_pillar: str | None = None,
        target_architecture: str | None = None,
        target_audience: str | None = None,
        prepared_questions: list[str] | None = None,
    ) -> None:
        """Construct the Pipecat pipeline with Gemini Live + ElevenLabs."""
        system_prompt = build_system_prompt(
            topic,
            context_text,
            language,
            interviewee_name=interviewee_name,
            content_pillar=content_pillar,
            target_architecture=target_architecture,
            target_audience=target_audience,
            prepared_questions=prepared_questions,
        )

        # Local audio transport (mic input + speaker output)
        self._transport = LocalAudioTransport(
            LocalAudioTransportParams(
                audio_in_enabled=True,
                audio_in_sample_rate=AUDIO_SAMPLE_RATE,
                audio_out_enabled=True,
                audio_out_sample_rate=AUDIO_SAMPLE_RATE,
            )
        )

        # GeminiLive — native STT + LLM in a single WebSocket
        # TEXT mode: emits LLMTextFrame for downstream TTS
        gemini = GeminiLiveLLMService(
            api_key=self.settings.google_api_key,
            model=self.settings.gemini_live_model,
            system_instruction=system_prompt,
            params=InputParams(
                modalities=GeminiModalities.TEXT,
                temperature=0.7,
            ),
        )

        # ElevenLabs TTS — custom voice output
        tts_voice_params = self.settings.get_tts_params(language)
        tts = ElevenLabsTTSService(
            api_key=self.settings.elevenlabs_api_key,
            voice_id=self.settings.elevenlabs_voice_id,
            model=self.settings.elevenlabs_tts_model,
            params=ElevenLabsTTSService.InputParams(
                stability=tts_voice_params["stability"],
                similarity_boost=tts_voice_params["similarity_boost"],
                style=tts_voice_params["style"],
            ),
        )

        greeting = build_greeting(topic, language)

        # Echo suppression — prevents bot speech from being transcribed as user input
        echo_suppressor = EchoSuppressor(
            threshold=self.settings.echo_similarity_threshold,
            window_secs=self.settings.echo_suppress_window_secs,
            min_length=self.settings.echo_min_length,
            trailing_secs=self.settings.echo_trailing_window_secs,
        )

        # Mic muter — drops audio input while bot is speaking to prevent VAD echo
        mic_muter = MicMuter(
            trailing_secs=self.settings.echo_trailing_window_secs,
        )

        # Transcript collector — captures user and assistant speech for DB persistence
        transcript_collector = TranscriptCollector(
            on_user_transcript=self._on_user_transcript,
            on_assistant_transcript=self._on_assistant_transcript,
            echo_suppressor=echo_suppressor,
        )

        # Latency logger — measures pipeline timing
        latency = LatencyLogger()

        # Pipeline: mic → mic_muter → GeminiLive(TEXT) → echo_sup → transcript → latency → TTS → out
        self._pipeline = Pipeline(
            processors=[
                self._transport.input(),
                mic_muter,
                gemini,
                echo_suppressor,
                transcript_collector,
                latency,
                tts,
                self._transport.output(),
            ]
        )

        self._task = PipelineTask(
            pipeline=self._pipeline,
            params=PipelineParams(
                audio_in_sample_rate=AUDIO_SAMPLE_RATE,
                audio_out_sample_rate=AUDIO_SAMPLE_RATE,
            ),
        )

        # Speak greeting directly via TTS (bypasses LLM for a clean start)
        @self._task.event_handler("on_pipeline_started")
        async def on_started(task: PipelineTask, frame: object) -> None:
            echo_suppressor.record_bot_utterance(greeting)
            await task.queue_frame(TTSTextFrame(text=greeting, aggregated_by="SENTENCE"))

        # Session timer — graceful wrap-up before 15-min limit
        max_secs = self.settings.session_max_minutes * 60

        @self._task.event_handler("on_pipeline_started")
        async def on_session_timer(task: PipelineTask, frame: object) -> None:
            await self._session_timer(task, language, max_secs)

    async def _session_timer(self, task: PipelineTask, language: str, max_secs: float) -> None:
        """Manage session time limits with warnings and graceful shutdown."""
        warn_secs = min(SESSION_WARN_SECS, max_secs * 0.93)
        wrapup_secs = min(SESSION_WRAPUP_SECS, max_secs * 0.97)
        disconnect_secs = min(SESSION_DISCONNECT_SECS, max_secs * 0.99)

        await asyncio.sleep(warn_secs)
        logger.info("Session approaching time limit — warning issued")

        warn_msg = (
            "We hebben nog ongeveer een minuut. Laten we afronden."
            if language == "nl"
            else "We have about a minute left. Let's wrap up."
        )
        await task.queue_frame(TTSTextFrame(text=warn_msg, aggregated_by="SENTENCE"))

        await asyncio.sleep(wrapup_secs - warn_secs)
        logger.info("Session wrapping up")

        wrapup_msg = (
            "Bedankt voor het gesprek! Tot de volgende keer."
            if language == "nl"
            else "Thanks for the conversation! Until next time."
        )
        await task.queue_frame(TTSTextFrame(text=wrapup_msg, aggregated_by="SENTENCE"))

        await asyncio.sleep(disconnect_secs - wrapup_secs)
        logger.info("Session time limit reached — disconnecting")
        await task.queue_frame(EndFrame())

    async def _on_user_transcript(self, text: str) -> None:
        """Callback for user speech transcription."""
        if self._session_id is not None:
            await self.store.add_transcript_entry(self._session_id, "user", text)

    async def _on_assistant_transcript(self, text: str) -> None:
        """Callback for assistant speech transcription."""
        if self._session_id is not None:
            await self.store.add_transcript_entry(self._session_id, "assistant", text)
