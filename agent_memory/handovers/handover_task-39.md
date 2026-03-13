## Task SUCCESS: Update humanizer for new architectures

### Status: SUCCESS

### What Was Done
- Updated `ContentHumanizer._build_prompt()` to use `format_instructions()` from templates.py instead of hardcoded `- Format: {format_type}` line
- Imported `format_instructions` in humanizer.py
- Added `## Format Instructions` section to the generated prompt with detailed formatting rules
- Updated CLI `write` command format option help text to list all 5 formats (linkedin, blog, inverted_pyramid, narrative_arc, pillar_cluster)

### Files Modified
- `src/writing/humanizer.py` — import format_instructions, replace bare format line with full instructions
- `app.py` — update format option help text
- `tests/unit/test_humanizer_architectures.py` — 27 new tests (all passing)

### Quality Results
- ruff check: passed
- ruff format: passed
- mypy: passed (no issues in 16 files)
- pytest: 546 tests passed

### Next Steps
- task-40: Create blueprint data models
