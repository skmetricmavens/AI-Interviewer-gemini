## Task SUCCESS: Wire EchoSuppressor into pipeline

### Status: SUCCESS

### What Was Done
- Imported EchoSuppressor in pipecat_bot.py
- Instantiated EchoSuppressor with settings values (threshold, window_secs, min_length)
- Inserted between STT and user context aggregator in pipeline
- Registered bot utterance capture via assistant turn event handler
- Registered greeting as bot utterance on pipeline start
- Added wiring test in test_pipecat_bot.py
- Pipeline order: input → vad → stt → echo_suppressor → user_agg → latency → llm → tts → output → assistant_agg

### Files Modified
- `src/interview/pipecat_bot.py` — import, instantiation, pipeline wiring, event registration
- `tests/test_pipecat_bot.py` — added TestEchoSuppressorWiring class

### Quality Results
- ✅ ruff: passed
- ✅ mypy: passed
- ✅ pytest: 295/295 passed
- ✅ imports: valid

### Echo Suppression Complete
All 4 echo suppression tasks (19-22) are now complete:
- task-19: Removed forced reaction starters from prompts
- task-20: Added echo suppression settings to config
- task-21: Built EchoSuppressor FrameProcessor
- task-22: Wired EchoSuppressor into pipeline

### Next Steps
- Merge all 4 PRs (#26-28 + this one)
- Test without headphones to verify echo suppression works
- task-18 (deferred): Investigate local AEC for additional echo cancellation
