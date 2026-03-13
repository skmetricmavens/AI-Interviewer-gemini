## Task SUCCESS: SQLite storage for sessions & transcripts

### Status: SUCCESS

### What Was Done
- Created src/storage/db.py with SessionStore class using aiosqlite
- Tables: sessions (id, topic, context_file, language, started_at, ended_at) and transcripts (id, session_id, role, content, timestamp)
- Methods: connect(), close(), create_session(), end_session(), add_transcript_entry(), get_session_transcript(), list_sessions()
- Auto-migration on connect (CREATE TABLE IF NOT EXISTS)
- 23 new tests (80 total) all passing

### Files Created
- `src/storage/db.py` - SessionStore class with async SQLite storage
- `tests/test_storage.py` - 23 tests covering CRUD, isolation, idempotent connect

### Quality Results
- ruff check: passed
- ruff format: passed
- mypy: passed
- pytest: 80/80 passed

### Next Steps
- task-4: Interview system prompts (src/interview/prompts.py)
