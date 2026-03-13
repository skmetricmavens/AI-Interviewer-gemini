## Task SUCCESS: Add Narrative Arc article template

### Status: SUCCESS

### What Was Done
- Added `NarrativeArcArticle` dataclass with fields: headline, setup, rising_action, climax, resolution, cta
- Extended `format_instructions()` to support "narrative_arc" format type
- Storytelling structure: setup -> rising action -> climax -> resolution

### Files Modified
- `src/writing/templates.py` — Added dataclass + format instructions
- `tests/unit/test_narrative_arc.py` — New test file (18 tests)

### Quality Results
- ruff: passed
- mypy: passed
- pytest: 497 passed

### Next Steps
- Task 38: Add Pillar-Cluster template + CTA patterns
