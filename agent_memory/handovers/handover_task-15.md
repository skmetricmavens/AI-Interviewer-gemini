## Task SUCCESS: Build interstitial filler system

### Status: SUCCESS

### What Was Done
- Created FillerProcessor (Pipecat FrameProcessor) that injects filler phrases on slow LLM responses
- Bilingual filler library: 5 EN phrases, 5 NL phrases
- Timer-based: starts on UserStoppedSpeakingFrame, cancels on LLMFullResponseStartFrame
- If LLM takes >400ms (configurable), plays random filler via TTSTextFrame
- 17 new tests covering phrases, randomization, and processor init

### Files Created
- `src/interview/fillers.py` — FillerProcessor, FILLER_PHRASES, get_random_filler
- `tests/test_fillers.py` — 17 tests

### Quality Results
- ruff: passed
- mypy: passed
- tests: 251/251 passed

### Next Steps
- task-16: Verify streaming behavior and optimize if needed
- task-17: Wire FillerProcessor into the pipeline in pipecat_bot.py
