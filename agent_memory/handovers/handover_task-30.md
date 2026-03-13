## Task SUCCESS: Add CLI interview options for metadata

### Status: SUCCESS

### What Was Done
- Added 4 optional CLI options to the `interview` command: `--interviewee`, `--pillar`, `--architecture`, `--audience`
- Updated Panel display to show metadata when provided
- Options are all optional — backward compatible

### Files Modified
- `app.py` — Added 4 typer.Option params to interview()
- `tests/unit/test_cli_metadata.py` — New test file (5 tests)

### Quality Results
- ruff: passed
- mypy: passed
- pytest: 364 passed

### Note
- Options are accepted but not yet passed to `bot.start_session()` — that's task-31

### Next Steps
- Task 31: Pass metadata through InterviewBot.start_session
