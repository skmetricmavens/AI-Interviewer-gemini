## Task SUCCESS: Define PHASE_DEFINITIONS data structure

### Status: SUCCESS

### What Was Done
- Added `PHASE_DEFINITIONS` constant to `src/interview/prompts.py`
- Tuple of 6 phase dicts, each with: name, title, goal, suggested_turns, techniques
- Phases: warm_up (1), topic_exploration (2), deep_dive (3), challenge (2), personal_connection (2), wrap_up (1) = 11 total turns
- Techniques reference the advanced techniques from INTERVIEW_RULES

### Files Modified
- `src/interview/prompts.py` — Added PHASE_DEFINITIONS constant
- `tests/unit/test_phase_definitions.py` — New test file (17 tests)

### Quality Results
- ruff: passed
- mypy: passed
- pytest: 411 passed

### Next Steps
- Task 34: Inject six-phase structure into system prompt (uses PHASE_DEFINITIONS)
