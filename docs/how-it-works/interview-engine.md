# Interview Engine

The interview engine conducts real-time voice conversations using a multi-service pipeline. It handles speech recognition, AI responses, voice synthesis, echo suppression, and transcript persistence.

## Voice Pipeline

The core of the interview engine is a [Pipecat](https://github.com/pipecat-ai/pipecat) pipeline that chains audio processors together:

```
Mic → MicMuter → VAD → STT → EchoSuppressor → UserAgg → LLM → TTS → Speaker → AssistantAgg
```

Each processor handles one responsibility:

| Processor | What It Does |
|-----------|-------------|
| **LocalAudioTransport** | Reads from microphone, writes to speakers |
| **MicMuter** | Drops audio frames while the bot is speaking (prevents VAD echo) |
| **VADProcessor** | Detects speech start/end using Silero VAD |
| **DeepgramSTT** | Converts speech to text (Nova-3, multilingual) |
| **EchoSuppressor** | Filters transcriptions that match recent bot speech |
| **LLMContextAggregator** | Maintains conversation history for the LLM |
| **GoogleLLMService** | Generates interview responses (Gemini 2.0 Flash) |
| **ElevenLabsTTS** | Converts text responses to speech |

### Echo Suppression

Without echo suppression, the bot's own speech gets picked up by the microphone and transcribed as user input. Two layers prevent this:

1. **MicMuter** — Drops raw audio frames while the bot is speaking (+ a trailing window after it stops). This prevents the VAD from triggering on bot audio.

2. **EchoSuppressor** — Compares incoming transcriptions against recent bot utterances using text similarity (difflib). Drops anything above the similarity threshold. Catches edge cases the MicMuter misses.

## Interview Prompts

The system prompt is built dynamically by `build_system_prompt()` in `src/interview/prompts.py`. It includes:

### Interview Rules

Core behavioral rules that shape the interviewer's style:

- Ask only ONE question per turn
- Keep responses short (under 30 words for reactions, under 50 for questions)
- Use contractions, casual tone
- Pick up on one specific thing, don't summarize everything
- Never give opinions or advice

### Advanced Techniques

The interviewer naturally applies these when appropriate:

- **Steel-man challenges** — Ask the interviewee to argue against their own position
- **Devil's advocate** — Present counterarguments to draw out stronger reasoning
- **Time anchors** — Use specific dates/timeframes to make topics concrete
- **Build on analogies** — Reuse the interviewee's metaphors in follow-ups
- **Summarize-then-challenge** — Reflect a point back, then probe a weakness

### Interview Phases

Each interview progresses through six phases:

| Phase | Turns | Goal |
|-------|-------|------|
| **Warm-up** | ~1 | Build rapport with a broad question |
| **Topic Exploration** | ~2 | Map knowledge and key themes |
| **Deep Dive** | ~3 | Extract examples, stories, data |
| **Challenge** | ~2 | Stress-test positions with counterarguments |
| **Personal Connection** | ~2 | Explore emotional and personal dimensions |
| **Wrap-up** | ~1 | Summarize, check for missed topics |

### Pillar Questions

When a content pillar is specified, the system prompt includes pillar-specific questions as inspiration. Five pillars are supported:

- `connected_journey` — Customer journey mapping and orchestration
- `crm_intelligence` — CRM data, segmentation, and ROI
- `building_smart` — Martech stack decisions and integration
- `people_not_prompts` — Human element in AI-driven marketing
- `field_notes` — Practical experiments and lessons learned

### Session Metadata

The prompt adapts based on optional metadata:

- **Interviewee name** — Personalizes the conversation
- **Content pillar** — Focuses questions on the pillar's domain
- **Target architecture** — Hints at the desired output structure
- **Target audience** — Adjusts depth and terminology

## Bilingual Support

The interviewer operates in English or Dutch, controlled by the `--language` flag:

- **Prompt language** — System prompt instructs the LLM to respond in the target language
- **STT** — Deepgram Nova-3 with `multi` language mode auto-detects
- **TTS** — ElevenLabs voice parameters are tuned per language (Dutch uses higher stability for guttural sounds)
- **Greeting** — Opening line is language-appropriate

## Transcript Persistence

Every turn is saved to SQLite in real-time:

```python
# User speech → stored via context aggregator event
await store.add_transcript_entry(session_id, "user", text)

# Assistant speech → stored via context aggregator event
await store.add_transcript_entry(session_id, "assistant", text)
```

Sessions include metadata (topic, pillar, audience, etc.) and can be listed, exported, or used for content generation.
