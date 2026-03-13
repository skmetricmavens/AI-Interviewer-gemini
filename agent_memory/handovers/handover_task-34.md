## Task SUCCESS: Inject six-phase structure into system prompt

### Status: SUCCESS

### What Was Done
- Replaced hardcoded "## Your Approach" section in `build_system_prompt()` with dynamic "## Interview Phases" section
- Each phase rendered as: `N. **Title** (~X turns): Goal. Techniques: ...`
- All 6 phases from PHASE_DEFINITIONS are injected with their title, goal, suggested turns, and techniques
- Updated existing test that expected "Your Approach" heading

### Files Modified
- `src/interview/prompts.py` — Replaced static approach with dynamic phase injection
- `tests/test_prompts.py` — Updated approach section test
- `tests/unit/test_prompt_phases.py` — New test file (25 tests)

### Quality Results
- ruff: passed
- mypy: passed
- pytest: 436 passed

### Next Steps
- Task 35: Add pillar-specific question banks
