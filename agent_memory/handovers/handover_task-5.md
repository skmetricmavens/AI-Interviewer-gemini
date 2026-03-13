## Task SUCCESS: Pipecat voice pipeline (STT->LLM->TTS)

### Status: SUCCESS

### What Was Done
- Created src/interview/pipecat_bot.py with InterviewBot class
- Pipeline: Deepgram STT -> Google Gemini LLM -> ElevenLabs TTS via Pipecat
- Session management: start_session creates DB session + builds pipeline, stop_session cleans up
- Transcript callbacks: _on_user_transcript and _on_assistant_transcript save to SessionStore
- Installed pipecat-ai with deepgram, google, elevenlabs extras
- 15 new tests (111 total) all passing

### Files Created
- `src/interview/pipecat_bot.py` - InterviewBot class
- `tests/test_pipecat_bot.py` - 15 tests (mocked _build_pipeline, real SessionStore)

### Quality Results
- ruff check: passed
- ruff format: passed
- mypy: passed
- pytest: 111/111 passed

### Notes
- _build_pipeline is mocked in tests since it instantiates external service clients
- run() is a placeholder — needs real audio transport to function
- VAD/interruption handling configured via Pipecat's built-in processors

### Next Steps
- task-6: Persona analyzer & fingerprinting (src/persona/analyzer.py)
