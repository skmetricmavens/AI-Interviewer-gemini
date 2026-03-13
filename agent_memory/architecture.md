# Architecture

## Overview

AI Content Interviewer — a voice-first CLI tool that conducts bilingual (Dutch/English) interviews to extract deep insights, then generates human-sounding content (LinkedIn, Blogs) matching the user's writing style.

## Directory Structure

```
ai-interviewer/
├── app.py                  # Typer CLI entrypoint
├── pyproject.toml          # Project config & dependencies
├── .env.example            # API key placeholders
│
├── src/                    # Source code
│   ├── config.py           # Settings & environment management
│   ├── interview/
│   │   ├── pipecat_bot.py  # Pipecat pipeline (Deepgram -> Gemini -> ElevenLabs)
│   │   └── prompts.py      # System instructions for interviewer
│   ├── writing/
│   │   ├── humanizer.py    # Style matching logic (Claude)
│   │   └── templates.py    # LinkedIn/Blog formatting
│   ├── storage/
│   │   └── db.py           # SQLite for transcripts & sessions
│   └── persona/
│       └── analyzer.py     # Writing sample analysis & fingerprinting
│
├── persona/
│   ├── samples/            # User's writing samples (.txt/.md)
│   └── fingerprint.json    # Generated style markers
│
├── tests/                  # Test suite
│   ├── test_*.py
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
- Pipecat pipeline: Deepgram STT -> Gemini 2.0 Flash -> ElevenLabs TTS
- Bilingual prompts with context-aware follow-ups
- VAD for interruption handling

### 2. Persona Engine (src/persona/)
- Analyzes writing samples for linguistic fingerprints
- Anti-AI vocabulary blocklist
- Style markers stored in persona/fingerprint.json

### 3. Content Writer (src/writing/)
- Claude-powered humanizer that matches user's writing style
- Output templates for LinkedIn and Blog formats

### 4. Storage (src/storage/)
- SQLite via aiosqlite
- Sessions and transcript persistence

### 5. CLI (app.py)
- Typer-based CLI with Rich output
- Commands: interview, write, persona analyze, sessions list

## Data Flow

```
[Voice Input] -> Deepgram STT -> Gemini (interview) -> ElevenLabs TTS -> [Voice Output]
                                      |
                                      v
                              [Transcript stored in SQLite]
                                      |
                                      v
                      [Claude + Persona Fingerprint] -> [Humanized Content]
```

## Dependencies

- pipecat-ai: multimodal orchestration
- deepgram-sdk: STT (Nova-3, multilingual)
- google-generativeai: Gemini 2.0 Flash
- elevenlabs: TTS (Turbo v2.5, multilingual)
- anthropic: Claude for content writing
- typer + rich: CLI
- python-dotenv: env management
- aiosqlite: async SQLite

## Configuration

- `.env` — API keys (DEEPGRAM, GOOGLE, ELEVENLABS, ANTHROPIC)
- `persona/samples/` — writing samples for style analysis
- `persona/fingerprint.json` — generated style markers
