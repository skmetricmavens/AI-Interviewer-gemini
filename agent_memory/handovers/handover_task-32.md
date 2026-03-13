## Task SUCCESS: Update build_system_prompt for metadata

### Status: SUCCESS

### What Was Done
- Extended `build_system_prompt()` with 4 keyword-only params: `interviewee_name`, `content_pillar`, `target_architecture`, `target_audience`
- When provided, metadata is injected as a "## Session Metadata" section in the system prompt
- Empty/whitespace-only values are treated as absent (no "None" literals)
- Updated `_build_pipeline()` in pipecat_bot.py to forward metadata from `start_session()` to `build_system_prompt()`
- Updated existing test that expected old `_build_pipeline` call signature

### Files Modified
- `src/interview/prompts.py` — Extended `build_system_prompt()` signature + metadata section injection
- `src/interview/pipecat_bot.py` — Extended `_build_pipeline()` to forward metadata params
- `tests/unit/test_prompt_metadata.py` — New test file (26 tests)
- `tests/test_pipecat_bot.py` — Updated mock assertion for new `_build_pipeline` signature

### Quality Results
- ruff: passed
- mypy: passed
- pytest: 394 passed

### Next Steps
- Task 33: Define PHASE_DEFINITIONS data structure
- Task 34: Inject six-phase structure into system prompt
