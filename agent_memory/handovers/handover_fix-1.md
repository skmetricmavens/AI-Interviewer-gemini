## Task SUCCESS: SSL cert fix for NLTK on macOS

### Status: SUCCESS

### What Was Done
- Added `certifi` dependency to pyproject.toml
- Set `SSL_CERT_FILE` env var from certifi in src/config.py so NLTK downloads work on macOS Python 3.13
- Added pipecat extras `[local,silero]` to pyproject.toml for audio transport + VAD

### Files Modified
- `src/config.py` - Added certifi import and SSL_CERT_FILE env var setup
- `pyproject.toml` - Added certifi dependency and pipecat extras

### Quality Results
- All gates passed (189 tests, mypy clean, ruff clean)
