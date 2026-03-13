## Task SUCCESS: Interview system prompts (bilingual)

### Status: SUCCESS

### What Was Done
- Created src/interview/prompts.py with build_system_prompt() and INTERVIEW_RULES constant
- Bilingual support: "en" (English) and "nl" (Dutch/Nederlands)
- Context-aware: injects optional context into the prompt for intelligent follow-ups
- Interview rules: max 2 questions per turn, acknowledge before probing, signal wrap-up
- 16 new tests (96 total) all passing

### Files Created
- `src/interview/prompts.py` - build_system_prompt() + INTERVIEW_RULES
- `tests/test_prompts.py` - 16 tests

### Quality Results
- ruff check: passed
- ruff format: passed
- mypy: passed
- pytest: 96/96 passed

### Next Steps
- task-5: Pipecat voice pipeline (src/interview/pipecat_bot.py) — depends on task-3 + task-4
