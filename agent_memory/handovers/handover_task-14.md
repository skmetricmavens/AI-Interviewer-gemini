## Task SUCCESS: Tune VAD silence threshold for faster turn-taking

### Status: SUCCESS

### What Was Done
- Added `vad_stop_secs` (default 0.3) and `vad_confidence` (default 0.7) to Settings
- Wired VADParams into SileroVADAnalyzer in pipeline for configurable turn-taking
- 4 new config tests for VAD settings

### Files Modified
- `src/config.py` — Added vad_stop_secs and vad_confidence settings
- `src/interview/pipecat_bot.py` — Pass VADParams to SileroVADAnalyzer
- `tests/test_config.py` — Added TestVADSettings (4 tests)

### Quality Results
- ruff: passed
- mypy: passed
- tests: 234/234 passed

### Next Steps
- task-15: Build interstitial filler system
