## Task SUCCESS: Add echo suppression settings to config

### Status: SUCCESS

### What Was Done
- Added 3 new settings to `Settings` dataclass for echo suppression control:
  - `echo_similarity_threshold: float = 0.6` — fuzzy match ratio above which transcript is considered echo
  - `echo_suppress_window_secs: float = 8.0` — only suppress within this window after bot speaks
  - `echo_min_length: int = 3` — ignore very short transcripts (single words like "yeah")
- Added 6 tests covering defaults and custom values

### Files Modified
- `src/config.py` — added 3 echo suppression fields to Settings
- `tests/test_config.py` — added TestEchoSuppressionSettings class with 6 tests

### Quality Results
- ✅ ruff: passed
- ✅ mypy: passed
- ✅ pytest: 267/267 passed
- ✅ imports: valid

### Next Steps
- task-21: Build EchoSuppressor FrameProcessor (uses these settings)
- task-22: Wire EchoSuppressor into pipeline
