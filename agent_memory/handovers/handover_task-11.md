## Task SUCCESS: Conversational tone + response length control in prompts

### Status: SUCCESS

### What Was Done
- Added response length control: under 30 words for reactions, under 50 for questions
- Added mandatory contractions rule (don't, isn't, you're — never formal forms)
- Changed acknowledgment rule to "briefly" — a few words, not a paragraph
- Changed active listening to pick up on ONE thing, not summarize everything
- Fixed 2 existing tests that referenced old "2 questions" rule
- Added 9 new tests: response length rules, conversational tone, approach section

### Files Modified
- `src/interview/prompts.py` — Added 4 new core rules for tone and brevity
- `tests/test_prompts.py` — Fixed 2 tests, added 9 new tests (25 total)

### Quality Results
- ruff: passed
- mypy: passed
- tests: 198/198 passed

### Next Steps
- task-12: Warm up greetings and vary by language
