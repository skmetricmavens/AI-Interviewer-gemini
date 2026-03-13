## Task SUCCESS: Pass metadata through InterviewBot.start_session

### Status: SUCCESS

### What Was Done
- Extended `InterviewBot.start_session()` with 4 keyword-only params: `interviewee_name`, `content_pillar`, `target_architecture`, `target_audience`
- Forwards all metadata to `store.create_session()`
- Updated `app.py` interview command to pass CLI metadata options through to `bot.start_session()`

### Files Modified
- `src/interview/pipecat_bot.py` — Extended `start_session()` signature and forwarding
- `app.py` — Wired CLI options to `bot.start_session()` call
- `tests/unit/test_bot_metadata.py` — New test file (4 tests)

### Quality Results
- ruff: passed
- mypy: passed
- pytest: 368 passed

### Next Steps
- Task 32: Update build_system_prompt to accept and inject metadata into the system prompt
