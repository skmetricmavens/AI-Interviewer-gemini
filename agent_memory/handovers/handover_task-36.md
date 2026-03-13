## Task SUCCESS: Add Inverted Pyramid article template

### Status: SUCCESS

### What Was Done
- Added `InvertedPyramidArticle` dataclass with fields: headline, lead, body, background, cta
- Extended `format_instructions()` to support "inverted_pyramid" format type
- Updated ValueError message to list all supported formats

### Files Modified
- `src/writing/templates.py` — Added dataclass + format instructions
- `tests/unit/test_inverted_pyramid.py` — New test file (17 tests)

### Quality Results
- ruff: passed
- mypy: passed
- pytest: 479 passed

### Next Steps
- Task 37: Add Narrative Arc article template
