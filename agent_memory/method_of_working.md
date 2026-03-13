# Method of Working

## How to Boot Claude Code

When starting a new Claude Code session, use:

```
/boot
```

This reads all memory files and provides a structured summary of your project.

---

## Boot Sequence (Progressive Disclosure)

On every session start, Claude loads context progressively — not all at once:

**Always load (core context):**
1. Read this file (`method_of_working.md`)
2. Read `tasks_queue.json` for current/next task
3. Read `project_state.yaml` for current codebase state

**Defer until needed:**
4. `architecture.md` — load before structural changes or new features
5. `reference_map.json` — load before writing code (import validation)
6. Handovers — load only the most recent, only if a task is in_progress

This prevents context rot from loading large files that aren't needed yet.

## Core Principles

### 1. Grounding
- Only reference symbols that exist in `reference_map.json`
- Validate imports against the symbol table before writing code
- Never hallucinate function names or class methods

### 2. Deterministic Behavior
- Follow tasks in order from `tasks_queue.json`
- Mark tasks as `in_progress` when starting, `completed` when done
- Update memory files after each significant change

### 3. Validation First
- Run tests before committing changes
- Check imports and type hints
- Fix errors before proceeding

### 4. Atomic Changes
- One task = one focused change
- Each task should target specific files
- Don't mix unrelated changes

### 5. Progressive Disclosure (Context Management)
- Load only what's needed for the current step
- Defer `reference_map.json` until writing code
- Defer `architecture.md` until structural changes
- Delegate verbose operations (quality gates, fixes, reviews) to **sub-agents** — their output stays in their context, not the main conversation
- After compaction, the `pre-compact.sh` hook preserves critical state (current task, branch, handover)
- Keep the main conversation focused on orchestration, not execution details

## Workflow

```
1. Boot (load memory files)
2. Create feature branch
3. Get current task from tasks_queue.json
4. Read relevant files
5. Write failing tests from task description (TDD RED)
6. Implement minimum code to pass tests (TDD GREEN)
7. Run quality gates (mypy, ruff, pytest)
8. If gates fail: fix and retry (max 3 attempts)
9. Post-task updates (ALL mandatory):
   a. Create handover document
   b. Update tasks_queue.json (mark completed)
   c. Update reference_map.json (new/changed symbols)
   d. Update project_state.yaml (new/changed classes/functions)
   e. Update architecture.md (if structural changes)
10. Commit to feature branch
11. Push and create PR
12. Next task
```

### Error Handling

When the user reports errors or bugs, **always decompose into atomic tasks first**:
1. Break each distinct error into a separate task in `tasks_queue.json`
2. One fix = one task (never combine multiple fixes)
3. Execute each fix task through the full workflow above
4. Each fix gets its own regression test, handover, and memory updates

### Git Strategy

**One commit per task** for easy rollback:

```bash
# Start work
git checkout -b feature/task-description

# After completing (only when tests pass!)
git add .
git commit -m "task-N: description"

# Merge when ready
git checkout main
git merge feature/task-description
git push
```

**Rollback when needed:**
```bash
git reset --soft HEAD~1  # Undo commit, keep changes
git reset --hard HEAD~1  # Undo commit, discard changes
```

---

## Subagents

Each subagent has ONE responsibility — no overlap. Delegate to sub-agents to keep verbose output out of the main context.

| Subagent | Does | Does NOT | Tools | Preloaded Skills |
|----------|------|----------|-------|------------------|
| **test-writer** | Write tests (TDD RED) | Run tests, write code | Read, Write, Glob, Grep | — |
| **code-reviewer** | Review quality & security | Modify files, run commands | Read, Glob, Grep | — |
| **quality-gate** | Run mypy, pytest, ruff | Modify files | Read, Bash, Glob, Grep | verify |
| **fixer** | Apply minimal fixes | Run commands, refactor | Read, Edit, Glob, Grep | sync |

> Planner and Coder roles are handled by Claude directly via `/plan` and `/next` skills.

**TDD Workflow:** `PLAN → TEST (RED) → CODE (GREEN) → REVIEW → QUALITY GATES → FIX → COMMIT`

### Why Delegate

Sub-agents run in their own context window. Their verbose output (test results, lint errors, diffs) stays isolated and only a summary returns to the main conversation. This prevents context rot during fix loops.

## Agent Teams (Optional — Experimental)

For large tasks with 5+ independent fix tasks or parallel feature work, you can use agent teams. Each teammate is an independent Claude Code session that works on its own task.

**Enable in settings.json:**
```json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

**When to use agent teams:**
- 5+ independent tasks that don't depend on each other
- Cross-layer work (frontend + backend + tests, each owned by a teammate)
- Research and review where multiple perspectives add value

**When NOT to use:**
- Sequential tasks with dependencies
- Same-file edits
- Tasks under 3 (sub-agents are cheaper and simpler)

**Limitations:** experimental feature, no session resumption, higher token cost, one team per session.

### Extreme Task Decomposition

Break features into granular subtasks:

- ONE function per task
- ONE file per task
- < 100 lines of code per task

❌ Bad: `Implement calculator with basic operations`
✅ Good: `Implement add(a, b) in calculator/ops.py`

---

## TDD Principles

Follow **Test-Driven Development** for every feature:

### The Cycle

```
1. Write test first (RED)
2. Implement feature (GREEN)
3. Refactor if needed
4. Repeat
```

### Key Principles

| Principle | Description |
|-----------|-------------|
| **Test the real code** | Don't test mocks—test actual components |
| **Test with real data** | Use realistic inputs, not simplified data |
| **Test error paths** | Don't just test happy paths |
| **Reproduce bugs in tests** | Every bug gets a regression test |

### Coverage Goals

- **80%+ unit test coverage** (Gold standard)
- **90%+ total coverage** target
- Comprehensive edge cases

---

## Quality Gates

Before marking any task complete, run through these gates:

### Gate 1: Type Checking (Python)

```bash
mypy <file_path> --ignore-missing-imports
```

Fix all type errors before proceeding.

### Gate 2: Tests

```bash
pytest tests/ -v
```

All tests must pass. If tests fail:
1. Read the error message
2. Fix the code
3. Re-run tests
4. Repeat until green

### Gate 3: Import Validation

Verify all imports resolve:
- Check `reference_map.json` for available symbols
- Don't import non-existent modules
- Don't use undefined functions

### Gate 4: Code Quality

Check for common issues:
- No hardcoded secrets or API keys
- Proper error handling
- Consistent naming (snake_case for functions, PascalCase for classes)
- No unused imports or variables

### Quality Retry Loop

If any gate fails:

```
1. Implement feature
2. Run quality gates
3. If FAIL: Fix issues, go to step 2 (max 3 attempts)
4. If PASS: Continue to commit
```

---

## Checkpoints (Human Review)

Pause for human review at these points:

| Checkpoint | When to Pause |
|------------|---------------|
| **Before Task** | Before starting work on a new task |
| **After Planning** | Before starting implementation |
| **Before Commit** | Review changes before committing |
| **After Failure** | When tests/quality gates fail repeatedly |
| **Risky Changes** | Deleting files, changing APIs, security-related |

### How to Checkpoint

Ask the user:
```
🔍 Checkpoint: [type]

Summary: [what was done]
Changes: [files modified]
Risks: [potential issues]

Continue? (y/n)
```

---

## Handover Pattern

When completing a task, create a handover summary with explicit status:

### Handover Status

| Status | When to Use |
|--------|-------------|
| **SUCCESS** | Task completed, all quality gates passed |
| **PARTIAL** | Some work done, needs continuation |
| **FAILED** | Task failed, needs different approach |
| **BLOCKED** | Cannot proceed without external input |

### Handover Template

```markdown
## Task [STATUS]: [title]

### Status: [SUCCESS/PARTIAL/FAILED/BLOCKED]

### What Was Done
- [bullet points of changes]

### Files Modified
- `path/to/file.py` - [what changed]

### Quality Results
- ✅ mypy: passed
- ✅ tests: 5/5 passed
- ✅ imports: valid

### Next Steps
- [what should happen next]

### Blockers (if BLOCKED)
- [what's preventing progress]

### Warnings
- [any issues to be aware of]
```

This helps maintain context between sessions.

---

## Forbidden Actions

- Do NOT create files outside the project structure
- Do NOT modify memory files without validation
- Do NOT skip tests
- Do NOT hallucinate APIs or function signatures
- Do NOT commit broken code

## Invariants

- All imports must resolve to existing modules
- All function calls must match their signatures
- All tests must pass before marking task complete
- Memory files must stay in sync with codebase

## Current Status

- **Phase**: [Update this as you progress]
- **Tests**: [Update after running tests]
- **In Progress**: [Current task]

## Key Documentation

Update these paths based on your project:
- `README.md` - Project overview
- `docs/` - Documentation
- `tests/` - Test suite
