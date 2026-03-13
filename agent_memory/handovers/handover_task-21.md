## Task SUCCESS: Build EchoSuppressor FrameProcessor

### Status: SUCCESS

### What Was Done
- Created `EchoSuppressor(FrameProcessor)` in `src/interview/echo_suppressor.py`
- Tracks bot utterances via TTSTextFrame with timestamps in a bounded deque (max 10)
- On TranscriptionFrame, compares text against recent bot utterances using difflib.SequenceMatcher
- Drops frames above similarity threshold within time window
- Handles partial matches (STT fragments compared against start of bot utterance)
- Short transcripts (below min_length words) pass through unchecked
- Logs suppressed frames for debugging
- Pure logic methods (`record_bot_utterance`, `is_echo`) are testable without async pipeline

### Files Created
- `src/interview/echo_suppressor.py` — EchoSuppressor class
- `tests/test_echo_suppressor.py` — 21 tests covering init, recording, and echo detection

### Quality Results
- ✅ ruff: passed
- ✅ mypy: passed
- ✅ pytest: 288/288 passed
- ✅ imports: valid

### Next Steps
- task-22: Wire EchoSuppressor into pipeline in pipecat_bot.py
