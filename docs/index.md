# AI Content Interviewer

A voice-first CLI tool that conducts bilingual (Dutch/English) deep-dive interviews, then generates human-sounding content matching your writing style.

## What It Does

1. **Interviews** — Conducts natural voice interviews using AI (Gemini 2.0 Flash) with real-time speech-to-text and text-to-speech
2. **Prepares** — Generates tailored interview questions based on your topic and content pillar
3. **Writes** — Transforms interview transcripts into LinkedIn posts, blog articles, and structured content using your personal writing style

## Key Features

- **Voice-first**: Real-time voice pipeline (Deepgram STT + Gemini LLM + ElevenLabs TTS)
- **Bilingual**: Full Dutch and English support across all components
- **Style matching**: Analyzes your writing samples to generate content that sounds like you
- **Interview preparation**: Generate, edit, and load custom question sets
- **Multiple output formats**: LinkedIn, blog, inverted pyramid, narrative arc, pillar-cluster
- **Content pillars**: Built-in topic banks and AI-powered topic suggestions

## Quick Example

```bash
# Prepare interview questions
ai-interviewer prepare --topic "AI in CRM" --pillar crm_intelligence --suggest

# Edit questions in the generated markdown file
# Then start the interview with your prepared questions
ai-interviewer interview --topic "AI in CRM" --prep interviews/prep_ai_in_crm.md

# Generate content from the interview
ai-interviewer write --session-id <id> --format linkedin
```
