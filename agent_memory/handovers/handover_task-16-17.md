## Task SUCCESS: Verify streaming + wire fillers into pipeline

### Status: SUCCESS

### What Was Done (task-16 + task-17 combined)
- task-16: Verified Pipecat streams LLM->TTS at sentence level by default. No custom chunker needed — sub-sentence chunking would hurt ElevenLabs prosody quality.
- task-17: Wired FillerProcessor into pipeline between user context aggregator and LLM
- Pipeline order: mic -> VAD -> STT -> user_agg -> filler -> LLM -> TTS -> speaker -> assistant_agg
- Added FillerProcessor import to pipecat_bot.py

### Files Modified
- `src/interview/pipecat_bot.py` — Import FillerProcessor, insert into pipeline

### Quality Results
- ruff: passed
- mypy: passed
- tests: 251/251 passed

### Next Steps
- task-18: Switch to Daily.co transport for echo cancellation
