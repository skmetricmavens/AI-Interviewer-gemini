# Installation

## Prerequisites

- Python 3.11 or higher
- A working microphone and speakers (for voice interviews)
- API keys for the following services:
    - [Deepgram](https://deepgram.com) — Speech-to-text
    - [Google AI](https://ai.google.dev) — Gemini LLM
    - [ElevenLabs](https://elevenlabs.io) — Text-to-speech
    - [Anthropic](https://anthropic.com) — Claude (content generation + question generation)

## Install

Clone the repository and install dependencies:

```bash
git clone https://github.com/skmetricmavens/AI-Interviewer.git
cd AI-Interviewer
pip install -e .
```

For development (includes testing and linting tools):

```bash
pip install -e ".[dev]"
```

## Verify Installation

```bash
ai-interviewer --help
```

You should see the available commands: `interview`, `prepare`, `write`, `blueprint`, `export`, `topics`, `persona-analyze`, `sessions-list`.

## Serving the Documentation

Install MkDocs Material and serve the docs locally:

```bash
cd /Users/sandykartopawiro/Documents/Personal\ AI\ projects/AI-Interviewer
pip install mkdocs-material
mkdocs serve
```

Then open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser.
