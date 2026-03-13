# Configuration

## Environment Variables

Create a `.env` file in the project root with your API keys:

```bash
# Required — core services
DEEPGRAM_API_KEY=your_deepgram_key
GOOGLE_API_KEY=your_google_key
ELEVENLABS_API_KEY=your_elevenlabs_key
ANTHROPIC_API_KEY=your_anthropic_key
ELEVENLABS_VOICE_ID=your_voice_id

# Optional — model overrides
GEMINI_MODEL=gemini-2.0-flash           # Default LLM for interviews
CLAUDE_MODEL=claude-sonnet-4-20250514    # Default model for content generation
DEEPGRAM_LANGUAGE=multi                  # STT language (multi = auto-detect)
DEEPGRAM_MODEL=nova-3                    # STT model

# Optional — voice tuning
ELEVENLABS_TTS_MODEL=eleven_turbo_v2_5
ELEVENLABS_STABILITY=0.5
ELEVENLABS_SIMILARITY_BOOST=0.75
ELEVENLABS_STYLE=0.3

# Dutch-specific voice params (higher stability for guttural sounds)
ELEVENLABS_STABILITY_NL=0.65
ELEVENLABS_SIMILARITY_BOOST_NL=0.7
ELEVENLABS_STYLE_NL=0.2

# Optional — VAD tuning
VAD_STOP_SECS=0.5          # Silence before end-of-turn
VAD_CONFIDENCE=0.7          # VAD activation threshold

# Optional — echo suppression
ECHO_SIMILARITY_THRESHOLD=0.6
ECHO_SUPPRESS_WINDOW_SECS=8.0
ECHO_MIN_LENGTH=1
ECHO_TRAILING_WINDOW_SECS=1.5

# Optional — storage
DB_PATH=interviews.db       # SQLite database path
```

## Getting API Keys

### Deepgram (Speech-to-Text)

1. Sign up at [console.deepgram.com](https://console.deepgram.com)
2. Create an API key with "Member" permissions
3. Nova-3 model is recommended for best multilingual support

### Google AI (Gemini)

1. Go to [ai.google.dev](https://ai.google.dev)
2. Get an API key from Google AI Studio
3. Gemini 2.0 Flash is used for real-time interview responses

### ElevenLabs (Text-to-Speech)

1. Sign up at [elevenlabs.io](https://elevenlabs.io)
2. Create an API key in your profile settings
3. Choose a voice and copy its Voice ID
4. Turbo v2.5 model is recommended for low latency

### Anthropic (Claude)

1. Sign up at [console.anthropic.com](https://console.anthropic.com)
2. Create an API key
3. Used for content generation, question generation, and persona analysis

## ElevenLabs Voice Selection

The `ELEVENLABS_VOICE_ID` determines the interviewer's speaking voice. To find voices:

1. Browse the [ElevenLabs Voice Library](https://elevenlabs.io/voice-library)
2. Pick a voice that supports your target languages
3. Copy the Voice ID from the voice settings

!!! tip "Multilingual voices"
    For Dutch/English interviews, choose a voice from the "Multilingual v2" category. These handle language switching naturally.
