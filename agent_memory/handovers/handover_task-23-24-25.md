## Tasks 23-25 SUCCESS: Bot-speaking-state echo suppression

### Status: SUCCESS

### What Was Done
- Enhanced EchoSuppressor with bot-speaking-state tracking via BotStartedSpeakingFrame/BotStoppedSpeakingFrame
- All TranscriptionFrames are now suppressed while bot is speaking (no text matching needed)
- Added configurable trailing window (default 1.5s) after bot stops speaking to catch trailing echoes
- Lowered echo_min_length default from 3 to 1 to catch short echo fragments
- Added echo_trailing_window_secs setting to config
- Wired trailing_secs into pipeline constructor
- Three-layer echo suppression: (1) bot speaking state, (2) trailing window, (3) text similarity fallback

### Files Modified
- `src/interview/echo_suppressor.py` — Added _bot_speaking, _bot_stopped_at, _trailing_secs, _in_trailing_window(); updated process_frame to check speaking state before text similarity
- `src/config.py` — Added echo_trailing_window_secs (default 1.5), changed echo_min_length default from 3 to 1
- `src/interview/pipecat_bot.py` — Pass trailing_secs to EchoSuppressor constructor
- `tests/unit/test_echo_suppressor_bot_speaking.py` — 22 new tests for bot-speaking-state suppression
- `tests/test_echo_suppressor.py` — Updated min_length default assertion
- `tests/test_config.py` — Added tests for new config defaults

### Quality Results
- ruff: passed
- mypy: passed
- tests: 319/319 passed

### Root Cause of Original Issue
The bot's TTS output was being picked up by the mic and transcribed as short fragments (1-2 words like "What", "So", "hey there."). The old echo suppressor only did text-similarity matching with min_length=3, so these short fragments slipped through and triggered constant interruptions.

### Next Steps
- Test with headphones to verify the echo loop is resolved
- If echo still occurs, tune echo_trailing_window_secs (increase from 1.5 to 2-3s)
- task-18 (local AEC without external service) is deferred for speaker-only usage
