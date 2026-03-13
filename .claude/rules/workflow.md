# Workflow

**ALL code changes follow this workflow — planned tasks, bug fixes, and iterative fixes alike.**

## Task Execution (7 Steps)

1. Read previous handover for context
2. Create feature branch (`feature/<task-id>-description` or `fix/<description>`)
3. Implement with TDD (write test first, then code)
4. Run quality gates (mypy, ruff, pytest — ALL must pass)
5. Create handover document
6. Commit, push, create PR
7. Next task

## Fix Iterations

When errors occur during development (quality gate failures, runtime errors, user-reported bugs):

### Step 1: Decompose into Atomic Tasks

**Always break errors into atomic tasks first**, even for "simple" fixes. Add them to `tasks_queue.json` before starting any fix work.

Example — user reports "the API returns 500 on empty input and the date parser crashes":
```json
{
  "id": "fix-1",
  "title": "Add input validation to /api/process endpoint",
  "status": "pending",
  "priority": "high",
  "files": ["src/api/routes.py", "tests/test_routes.py"]
},
{
  "id": "fix-2",
  "title": "Fix date parser crash on malformed input",
  "status": "pending",
  "priority": "high",
  "files": ["src/utils/date_parser.py", "tests/test_date_parser.py"]
}
```

**One fix = one task.** Do NOT combine multiple fixes into a single task.

### Step 2: Execute Each Fix as a Full Task

For each fix task, follow the standard workflow:
1. **Mark as in_progress** in `tasks_queue.json`
2. **Stay on the feature branch** — do NOT fix directly on main
3. **Write a regression test** — use `test-writer` to cover the error before fixing
4. **Delegate to sub-agents** — use `fixer` for targeted fixes, `quality-gate` to verify
5. **Run post-task updates** (see below)
6. **Commit the fix** — on the same feature branch, then PR and merge

**Never skip steps because "it's just a small fix."** Small fixes accumulate into untracked, untested changes on main.

### Fix Workflow Summary

```
ERROR → decompose into atomic tasks in tasks_queue.json → for each task: branch → test → fix → quality-gate → post-task updates → commit → PR
```

## Post-Task Updates (Mandatory)

After EVERY completed task (planned or fix), perform ALL of these updates before committing:

1. **Create handover** — `agent_memory/handovers/handover_<task-id>.md`
2. **Update tasks_queue.json** — mark task as `completed`, set `current_task_id` to next task or null
3. **Update reference_map.json** — add/remove/modify any changed exports, classes, functions
4. **Update project_state.yaml** — add/remove/modify classes, functions, update `last_updated`
5. **Update architecture.md** — if new components, data flows, or dependencies were added

**These updates are not optional.** Skipping them causes context drift that compounds across tasks.

### Post-Task Checklist

```
[ ] handover created
[ ] tasks_queue.json updated (task marked completed)
[ ] reference_map.json updated (new/changed symbols)
[ ] project_state.yaml updated (new/changed classes/functions)
[ ] architecture.md updated (if structural changes)
```

## Atomic Changes

- Each task targets ONE coherent logical change
- Target: source file + its tests (2-5 files typical)
- If >300 lines of new code, evaluate splitting

## Memory System

After significant changes, update memory files via `/sync`:
- `agent_memory/tasks_queue.json` — mark task complete
- `agent_memory/project_state.yaml` — new classes/functions
- `agent_memory/reference_map.json` — new exports
