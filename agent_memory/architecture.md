# Architecture

## Overview

AI Content Interviewer — a voice-first CLI tool that conducts bilingual (Dutch/English) interviews to extract deep insights, then generates human-sounding content (LinkedIn, Blogs) matching the user's writing style.

## Directory Structure

```
ai-interviewer/
├── app.py                  # Typer CLI entrypoint
├── pyproject.toml          # Project config & dependencies
├── .env                    # API keys (GOOGLE, ELEVENLABS, ANTHROPIC)
│
├── src/                    # Source code
│   ├── config.py           # Settings & environment management
│   ├── interview/
│   │   ├── pipecat_bot.py  # Pipecat pipeline (GeminiLive -> ElevenLabs)
│   │   ├── echo_suppressor.py  # Echo cancellation processor
│   │   ├── latency_logger.py   # Pipeline latency tracking
│   │   ├── mic_muter.py        # Mic mute during bot speech
│   │   ├── fillers.py          # Filler phrases for slow LLM
│   │   ├── prompts.py          # System instructions for interviewer
│   │   └── prep.py             # Interview prep file generation
│   ├── writing/
│   │   ├── humanizer.py    # Style matching logic (Claude)
│   │   ├── templates.py    # LinkedIn/Blog formatting
│   │   └── blueprint.py    # Article structure blueprints
│   ├── storage/
│   │   ├── db.py           # SQLite for transcripts & sessions
│   │   └── exporter.py     # Export transcripts to markdown/JSON
│   ├── persona/
│   │   └── analyzer.py     # Writing sample analysis & fingerprinting
│   └── topics/
│       ├── evergreen.py    # Topic bank by content pillar
│       └── generator.py    # AI-powered topic suggestions
│
├── scripts/                # POC & demo scripts
│   ├── poc_gemini_live_text_elevenlabs.py   # POC: TEXT mode + ElevenLabs
│   ├── poc_gemini_live_audio_native.py      # POC: AUDIO mode baseline
│   └── poc_gemini_live_transcription.py     # POC: Transcription + echo
│
├── persona/
│   ├── samples/            # User's writing samples (.txt/.md)
│   └── fingerprint.json    # Generated style markers
│
├── tests/                  # Test suite (799 tests)
│   ├── test_*.py
│   ├── unit/
│   └── conftest.py
│
└── agent_memory/           # Claude Code memory
    ├── method_of_working.md
    ├── architecture.md
    ├── project_state.yaml
    ├── tasks_queue.json
    └── reference_map.json
```

## Key Components

### 1. Interview Engine (src/interview/)
- **GeminiLive pipeline**: Audio input → GeminiLiveLLMService (native STT + LLM via WebSocket) → ElevenLabs TTS
- Uses TEXT modality: Gemini handles STT internally, outputs LLMTextFrame for ElevenLabs
- Built-in VAD (replaces Silero)
- Bilingual prompts with context-aware follow-ups
- Session timer with graceful wrap-up (14min warn → 14:30 wrap → 14:55 disconnect)

### 2. Persona Engine (src/persona/)
- Analyzes writing samples for linguistic fingerprints
- Anti-AI vocabulary blocklist
- Style markers stored in persona/fingerprint.json

### 3. Content Writer (src/writing/)
- Claude-powered humanizer that matches user's writing style
- Output templates for LinkedIn and Blog formats
- Article blueprint generation

### 4. Storage (src/storage/)
- SQLite via aiosqlite
- Sessions and transcript persistence
- Transcript export (markdown, plain text, JSON)

### 5. CLI (app.py)
- Typer-based CLI with Rich output
- Commands: interview, write, persona analyze, sessions list, blueprint, export, topics, prepare

## Data Flow

```
[Voice Input] → GeminiLive WebSocket (native STT + LLM) → [Text response]
                        |                                        |
                        v                                        v
              [TranscriptionFrame → SQLite]              [ElevenLabs TTS → Speaker]
                        |
                        v
        [Claude + Persona Fingerprint] → [Humanized Content]
```

### Pipeline Architecture

```
Mic → LocalAudioTransport
  → MicMuter (drops audio during bot speech)
  → GeminiLiveLLMService (TEXT mode, WebSocket)
    - Audio in: native STT (no Deepgram)
    - Built-in VAD (no Silero)
    - LLM response as text stream
  → EchoSuppressor (filters bot speech echoes)
  → TranscriptCollector (captures user + assistant text for DB)
  → LatencyLogger (measures pipeline timing)
  → ElevenLabsTTSService (custom voice)
  → LocalAudioTransport → Speaker
```

## Dependencies

- pipecat-ai[google,elevenlabs,local]: multimodal orchestration + Gemini Live
- google-genai: Gemini Live API client
- elevenlabs: TTS (Turbo v2.5, multilingual)
- anthropic: Claude for content writing
- typer + rich: CLI
- python-dotenv: env management
- aiosqlite: async SQLite
- certifi: SSL certificate management

## Configuration

- `.env` — API keys (GOOGLE, ELEVENLABS, ANTHROPIC)
- `persona/samples/` — writing samples for style analysis
- `persona/fingerprint.json` — generated style markers
