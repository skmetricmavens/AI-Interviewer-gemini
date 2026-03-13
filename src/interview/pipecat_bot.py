"""Pipecat voice pipeline for conducting AI interviews."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.audio.vad.vad_analyzer import VADParams
from pipecat.frames.frames import TTSTextFrame
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.aggregators.llm_context import LLMContext
from pipecat.processors.aggregators.llm_response_universal import LLMContextAggregatorPair
from pipecat.processors.audio.vad_processor import VADProcessor
from pipecat.services.deepgram.stt import DeepgramSTTService
from pipecat.services.elevenlabs.tts import ElevenLabsTTSService
from pipecat.services.google.llm import GoogleLLMService
from pipecat.transports.local.audio import LocalAudioTransport, LocalAudioTransportParams

from src.interview.echo_suppressor import EchoSuppressor
from src.interview.latency_logger import LatencyLogger
from src.interview.mic_muter import MicMuter
from src.interview.prompts import build_system_prompt

if TYPE_CHECKING:
    from src.config import Settings
    from src.storage.db import SessionStore

AUDIO_IN_SAMPLE_RATE = 16000
AUDIO_OUT_SAMPLE_RATE = 24000


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
        """Construct the Pipecat pipeline with local audio transport."""
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
                audio_in_sample_rate=AUDIO_IN_SAMPLE_RATE,
                audio_out_enabled=True,
                audio_out_sample_rate=AUDIO_OUT_SAMPLE_RATE,
            )
        )

        # VAD for interruption handling — tuned for conversational turn-taking
        vad_params = VADParams(
            stop_secs=self.settings.vad_stop_secs,
            confidence=self.settings.vad_confidence,
        )
        vad = VADProcessor(
            vad_analyzer=SileroVADAnalyzer(
                sample_rate=AUDIO_IN_SAMPLE_RATE,
                params=vad_params,
            )
        )

        # STT, LLM, TTS services
        stt = DeepgramSTTService(
            api_key=self.settings.deepgram_api_key,
        )

        llm = GoogleLLMService(
            api_key=self.settings.google_api_key,
            model=self.settings.gemini_model,
            system_instruction=system_prompt,
        )

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

        # Context aggregators convert STT transcriptions <-> LLM messages
        # Seed with system prompt + pre-filled greeting so LLM has context
        context = LLMContext(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "assistant", "content": greeting},
            ]
        )
        context_aggregator = LLMContextAggregatorPair(context)

        # Wire transcript persistence via aggregator events
        # User event passes (aggregator, strategy, UserTurnStoppedMessage)
        # Assistant event passes (aggregator, AssistantTurnStoppedMessage)
        @context_aggregator.user().event_handler("on_user_turn_stopped")
        async def on_user_turn(aggregator: object, strategy: object, message: object) -> None:
            text = getattr(message, "content", None)
            if text:
                await self._on_user_transcript(str(text))

        @context_aggregator.assistant().event_handler("on_assistant_turn_stopped")
        async def on_assistant_turn(aggregator: object, message: object) -> None:
            text = getattr(message, "content", None)
            if text:
                echo_suppressor.record_bot_utterance(str(text))
                await self._on_assistant_transcript(str(text))

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

        # Latency logger — measures STT→LLM→TTS timing
        latency = LatencyLogger()

        # Pipeline: mic -> mic_muter -> VAD -> STT -> echo_sup -> user_agg -> LLM -> TTS -> out
        self._pipeline = Pipeline(
            processors=[
                self._transport.input(),
                mic_muter,
                vad,
                stt,
                echo_suppressor,
                context_aggregator.user(),
                latency,
                llm,
                tts,
                self._transport.output(),
                context_aggregator.assistant(),
            ]
        )

        self._task = PipelineTask(
            pipeline=self._pipeline,
            params=PipelineParams(
                audio_in_sample_rate=AUDIO_IN_SAMPLE_RATE,
                audio_out_sample_rate=AUDIO_OUT_SAMPLE_RATE,
            ),
        )

        # Speak greeting directly via TTS (bypasses LLM for a clean start)
        @self._task.event_handler("on_pipeline_started")
        async def on_started(task: PipelineTask, frame: object) -> None:
            echo_suppressor.record_bot_utterance(greeting)
            await task.queue_frame(TTSTextFrame(text=greeting, aggregated_by="SENTENCE"))

    async def _on_user_transcript(self, text: str) -> None:
        """Callback for user speech transcription."""
        if self._session_id is not None:
            await self.store.add_transcript_entry(self._session_id, "user", text)

    async def _on_assistant_transcript(self, text: str) -> None:
        """Callback for assistant speech transcription."""
        if self._session_id is not None:
            await self.store.add_transcript_entry(self._session_id, "assistant", text)
