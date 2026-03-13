## Task SUCCESS: Add pillar-specific question banks

### Status: SUCCESS

### What Was Done
- Added `PILLAR_QUESTIONS` constant to `src/interview/prompts.py` — dict mapping 5 ContentPillar values to lists of 5 suggested questions each
- Pillars: connected_journey, crm_intelligence, building_smart, people_not_prompts, field_notes
- When `content_pillar` is provided to `build_system_prompt()`, a "## Pillar Questions" section is injected after Interview Phases
- Questions are presented as inspiration ("adapt, don't read verbatim")
- No section added when pillar is None, empty, or unrecognized

### Files Modified
- `src/interview/prompts.py` — Added PILLAR_QUESTIONS + injection logic
- `tests/unit/test_pillar_questions.py` — New test file (26 tests)

### Quality Results
- ruff: passed
- mypy: passed
- pytest: 462 passed

### Next Steps
- Task 36: Add Inverted Pyramid article template
