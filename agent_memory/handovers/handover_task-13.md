## Task SUCCESS: ElevenLabs voice tuning + bilingual prosody switching

### Status: SUCCESS

### What Was Done
- Added 6 ElevenLabs voice tuning settings to Settings (EN + NL-specific)
- EN defaults: stability=0.5, similarity_boost=0.75, style=0.4
- NL defaults: stability=0.7, similarity_boost=0.8, style=0.2 (higher stability for guttural sounds)
- Added `get_tts_params(language)` method to Settings
- Wired params into ElevenLabsTTSService via InputParams in pipeline
- 15 new config tests

### Files Modified
- `src/config.py` — Added 6 voice settings + `get_tts_params()` method
- `src/interview/pipecat_bot.py` — Pass voice params to ElevenLabsTTSService
- `tests/test_config.py` — Added TestTTSSettings (15 tests)

### Quality Results
- ruff: passed
- mypy: passed
- tests: 230/230 passed

### Next Steps
- task-14: Tune VAD silence threshold for faster turn-taking
