## Task SUCCESS: Improve interview prompts with advanced techniques

### Status: SUCCESS

### What Was Done
- Analyzed two reference interview transcripts (podcast-style deep interviews)
- Extracted 10 advanced interview techniques and saved to persistent memory
- Updated `src/interview/prompts.py` with advanced techniques: steel-man challenges, devil's advocate, time anchors, building on analogies, summarize-then-challenge, categorize-and-explore, personal questions, referencing guest's own words
- Improved approach flow: follow logic chain, explore frameworks systematically, mix depth with personal moments
- Changed to 1 question per turn (from 2) per user feedback
- Added relaxed conversational tone instruction per user feedback

### Files Modified
- `src/interview/prompts.py` — Enhanced INTERVIEW_RULES and approach section
- `memory/MEMORY.md` — Created with interview style references
- `memory/interview_techniques.md` — Detailed technique catalog

### Quality Results
- ruff: passed
- mypy: passed
- tests: 189/189 passed (including 16 prompt tests)

### Next Steps
- Test the updated prompts in a live interview session
- Fine-tune technique usage based on real conversation quality
