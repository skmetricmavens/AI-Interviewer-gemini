# AI Content Interviewer

A voice-first CLI tool that conducts bilingual (Dutch & English) interviews to extract deep insights, then generates human-sounding content (LinkedIn posts, blog articles) that mirrors your specific writing style.

## How It Works

```
Voice Interview (Pipecat)          Content Generation (Claude)
┌─────────────────────────┐        ┌─────────────────────────┐
│ You speak               │        │ Transcript + Fingerprint│
│   ↓                     │        │   ↓                     │
│ Deepgram STT (Nova-3)   │        │ Claude (Humanizer)      │
│   ↓                     │   ──►  │   ↓                     │
│ Gemini 2.0 Flash (Brain)│        │ Anti-AI Filter          │
│   ↓                     │        │   ↓                     │
│ ElevenLabs TTS (Voice)  │        │ LinkedIn / Blog Post    │
└─────────────────────────┘        └─────────────────────────┘
```

## Features

- **Bilingual** — Seamlessly handles Dutch and English
- **Voice-first** — Real-time voice loop via Pipecat with < 600ms latency target
- **Context-aware** — Feed notes or PDFs for intelligent follow-up questions
- **Style cloning** — Persona engine analyzes your writing samples
- **Anti-AI filter** — Strips AI-sounding words (delve, pivotal, tapestry...)
- **Interruption handling** — VAD-based, interrupt the AI mid-sentence

## Setup

### 1. Install dependencies

```bash
pip install -e .
```

Or install from requirements:

```bash
pip install pipecat-ai[deepgram,google,elevenlabs] anthropic typer rich python-dotenv aiosqlite
```

### 2. Configure API keys

Copy `.env.example` to `.env` and fill in your keys:

```bash
cp .env.example .env
```

Required keys:
- `DEEPGRAM_API_KEY` — [deepgram.com](https://deepgram.com)
- `GOOGLE_API_KEY` — [ai.google.dev](https://ai.google.dev)
- `ELEVENLABS_API_KEY` — [elevenlabs.io](https://elevenlabs.io)
- `ANTHROPIC_API_KEY` — [console.anthropic.com](https://console.anthropic.com)
- `ELEVENLABS_VOICE_ID` — Your chosen voice ID from ElevenLabs

### 3. Add writing samples

Place 5+ writing samples (`.txt` or `.md`) in `persona/samples/`:

```
persona/samples/
├── linkedin-post-1.txt
├── linkedin-post-2.txt
├── blog-article-1.md
├── dutch-post-1.txt
└── english-post-1.txt
```

### 4. Generate your style fingerprint

```bash
python app.py persona-analyze
```

This analyzes your samples and saves a linguistic fingerprint to `persona/fingerprint.json`.

## Usage

### Start an interview

```bash
# Basic interview
python app.py interview --topic "My experience building AI tools"

# With context file
python app.py interview --topic "Project retrospective" --context notes.md

# In Dutch
python app.py interview --topic "Mijn ervaring met AI" --language nl
```

### Generate content from a past session

```bash
# LinkedIn post (default)
python app.py write --session-id <id> --format linkedin

# Blog post
python app.py write --session-id <id> --format blog --language nl
```

### List past sessions

```bash
python app.py sessions-list
```

## Architecture

```
ai-interviewer/
├── app.py                  # Typer CLI (4 commands)
├── src/
│   ├── config.py           # Settings from .env
│   ├── interview/
│   │   ├── pipecat_bot.py  # Voice pipeline (Deepgram → Gemini → ElevenLabs)
│   │   └── prompts.py      # Bilingual system prompts
│   ├── writing/
│   │   ├── humanizer.py    # Claude-powered content generation
│   │   └── templates.py    # LinkedIn/Blog format definitions
│   ├── storage/
│   │   └── db.py           # SQLite sessions & transcripts
│   └── persona/
│       └── analyzer.py     # Writing sample analysis & fingerprinting
├── persona/
│   ├── samples/            # Your writing samples
│   └── fingerprint.json    # Generated style markers
└── tests/                  # 195 tests
```

## Cost Estimates

| Service | Cost | Notes |
|---------|------|-------|
| Deepgram STT | $0.0092/min | Nova-3 Multilingual |
| ElevenLabs TTS | $0.30/1k chars | Turbo v2.5 |
| Gemini 2.0 Flash | $0.10/1M tokens | Live interview |
| Claude | ~$0.01/request | Content generation |
| **Total per hour** | **~$1.50 - $2.50** | |

## Development

```bash
# Run tests
pytest tests/ -v

# Type check
mypy src/ --ignore-missing-imports

# Lint
ruff check src/
```

## License

MIT
