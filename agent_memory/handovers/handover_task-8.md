## Task SUCCESS: Output format templates (LinkedIn, Blog)

### Status: SUCCESS

### What Was Done
- Created src/writing/templates.py with LinkedInPost and BlogPost dataclasses
- format_instructions() returns Claude-ready formatting rules per type
- LinkedInPost: hook, body, cta, max_chars=3000
- BlogPost: title, intro, sections list, conclusion
- ValueError for unknown format types
- 23 new tests (176 total) all passing

### Files Created
- `src/writing/templates.py` - LinkedInPost, BlogPost, format_instructions()
- `tests/test_templates.py` - 23 tests

### Quality Results
- ruff check: passed
- ruff format: passed
- mypy: passed
- pytest: 176/176 passed

### Next Steps
- task-9: Typer CLI entrypoint (app.py)
