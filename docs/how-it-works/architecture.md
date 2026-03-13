# Architecture

## System Overview

The AI Content Interviewer is built from four main subsystems that work together in a pipeline:

```
┌──────────────────────────────────────────────────────────────┐
│                        CLI (app.py)                          │
│  prepare │ interview │ write │ blueprint │ export │ topics   │
└────┬─────────┬───────────┬───────────┬───────────┬───────────┘
     │         │           │           │           │
     v         v           │           │           │
┌─────────┐ ┌──────────┐  │           │           │
│  Prep   │ │Interview │  │           │           │
│ Engine  │ │ Engine   │  │           │           │
│         │ │(Pipecat) │  │           │           │
└─────────┘ └────┬─────┘  │           │           │
                 │         v           v           │
                 │   ┌──────────┐ ┌─────────┐     │
                 │   │ Content  │ │Blueprint│     │
                 │   │ Writer   │ │Generator│     │
                 │   │(Claude)  │ │(Claude) │     │
                 │   └──────────┘ └─────────┘     │
                 │         │           │           │
                 v         v           v           v
              ┌────────────────────────────────────────┐
              │        Storage (SQLite + Files)        │
              │   sessions │ transcripts │ exports     │
              └────────────────────────────────────────┘
```

## Directory Structure

```
ai-interviewer/
├── app.py                      # Typer CLI entrypoint
├── pyproject.toml               # Project config
├── .env                         # API keys (not committed)
│
├── src/
│   ├── config.py                # Settings, enums, env loading
│   │
│   ├── interview/
│   │   ├── pipecat_bot.py       # Voice pipeline orchestration
│   │   ├── prompts.py           # System prompts, phases, pillar questions
│   │   ├── prep.py              # Interview preparation (dataclass, parser, generator)
│   │   ├── echo_suppressor.py   # Prevents bot echo in transcription
│   │   ├── mic_muter.py         # Mutes mic during bot speech
│   │   ├── fillers.py           # "Hmm", "Right..." while LLM thinks
│   │   └── latency_logger.py    # STT→LLM→TTS timing metrics
│   │
│   ├── writing/
│   │   ├── humanizer.py         # Claude-powered style-matched writing
│   │   ├── templates.py         # Format templates (LinkedIn, blog, etc.)
│   │   └── blueprint.py         # Article blueprint generator
│   │
│   ├── storage/
│   │   ├── db.py                # SQLite session/transcript store
│   │   └── exporter.py          # Transcript export (markdown, JSON, text)
│   │
│   ├── persona/
│   │   └── analyzer.py          # Writing sample analysis
│   │
│   └── topics/
│       ├── evergreen.py         # Built-in topic bank per pillar
│       └── generator.py         # AI topic suggestions
│
├── persona/
│   ├── samples/                 # User's writing samples
│   └── fingerprint.json         # Generated style markers
│
├── interviews/                  # Generated prep files
│   └── prep_*.md
│
└── tests/                       # Test suite (800+ tests)
```

## Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Voice pipeline | [Pipecat](https://github.com/pipecat-ai/pipecat) | Orchestrates real-time audio processing |
| Speech-to-text | Deepgram Nova-3 | Multilingual transcription |
| Interview LLM | Gemini 2.0 Flash | Low-latency conversational responses |
| Text-to-speech | ElevenLabs Turbo v2.5 | Natural-sounding voice output |
| Content generation | Claude (Anthropic) | Writing, blueprints, questions, personas |
| CLI framework | Typer + Rich | Command-line interface |
| Database | SQLite (aiosqlite) | Session and transcript storage |
| Audio | Local microphone/speakers | Direct audio I/O |

## Data Flow

### Interview Session

```
Microphone
  → MicMuter (drops audio while bot speaks)
  → VAD (detects speech/silence boundaries)
  → Deepgram STT (speech → text)
  → EchoSuppressor (filters out bot echo)
  → Context Aggregator (builds conversation history)
  → Gemini LLM (generates response)
  → ElevenLabs TTS (text → speech)
  → Speaker output
  → Context Aggregator (records assistant turn)
  → SQLite (persists transcript)
```

### Content Generation

```
SQLite transcript
  → Persona fingerprint (style markers)
  → Format template (LinkedIn/blog/article rules)
  → Claude (generates style-matched content)
  → CLI output
```
