## Task SUCCESS: Warm up greetings and vary by language

### Status: SUCCESS

### What Was Done
- Extracted greeting logic into testable `build_greeting(topic, language)` function
- Replaced formal "Welcome! I'll be interviewing you about..." with casual "Hey, great to have you! Let's talk about..."
- Replaced formal Dutch "Welkom! Ik ga je interviewen over..." with casual "Hey, leuk dat je er bent! We duiken in..."
- Unknown language codes default to English
- Added 17 new tests for greeting behavior

### Files Modified
- `src/interview/pipecat_bot.py` — Extracted `build_greeting()`, simplified `_build_pipeline`
- `tests/test_pipecat_bot.py` — Added `TestBuildGreeting` class (17 tests, 32 total)

### Quality Results
- ruff: passed
- mypy: passed
- tests: 215/215 passed

### Next Steps
- task-13: ElevenLabs voice tuning + bilingual prosody switching
