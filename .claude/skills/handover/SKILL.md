---
name: handover
description: Complete a task by generating handover, updating all memory files, and marking task done. Use after finishing any task or fix.
---

Complete the current task by generating a handover document AND performing all post-task updates.

## Gather Context

### Recent Changes
```
!`git diff --stat HEAD 2>/dev/null || echo "No git changes"`
```

### Recent Commits (this branch)
```
!`git log --oneline -5 2>/dev/null || echo "No commits"`
```

### Current Task
```
!`cat agent_memory/tasks_queue.json 2>/dev/null | python3 -c "
import json,sys
data=json.load(sys.stdin)
current=[t for t in data.get('backlog',[]) if t.get('status')=='in_progress']
if current: print(json.dumps(current[0], indent=2))
else: print('No in-progress task')
" 2>/dev/null || echo "No task queue found"`
```

### Test Results
```
!`pytest tests/ -v --tb=line 2>&1 | tail -20 || echo "No tests found"`
```

### Quality Gate Status
```
!`(ruff check src/ 2>&1 | tail -5; echo "---"; mypy src/ --ignore-missing-imports 2>&1 | tail -5) || echo "Quality tools not available"`
```

## Step 1: Create Handover Document

Using the gathered context above, generate a handover document:

```markdown
## Task [STATUS]: [title from task queue]

### Status: SUCCESS | PARTIAL | FAILED | BLOCKED

### What Was Done
- [bullet points from git diff and commits]

### Files Modified
- `path/to/file.py` - [what changed, from git diff]

### Quality Results
- mypy: [pass/fail from output above]
- ruff: [pass/fail from output above]
- pytest: [X/Y passed from output above]

### Context for Next Task
- [Dependencies created]
- [Decisions made and why]

### Warnings
- [Any issues found]
```

Save the handover to `agent_memory/handovers/handover_<task-id>.md`.

## Step 2: Update tasks_queue.json

- Mark the current task as `completed`
- Update `current_task_id` to the next pending task or `null`

## Step 3: Update reference_map.json

Scan the modified files and update `agent_memory/reference_map.json`:
- Add any new classes, functions, or exports
- Remove any deleted symbols
- Update changed signatures

If no symbols changed, skip this step but confirm it was checked.

## Step 4: Update project_state.yaml

Update `agent_memory/project_state.yaml`:
- Add/update classes and functions from modified files
- Set `last_updated` to the current timestamp

If no classes/functions changed, update only `last_updated`.

## Step 5: Update architecture.md (if needed)

If the changes introduced new components, data flows, API boundaries, or dependencies, update `agent_memory/architecture.md`.

If no structural changes, skip but confirm it was checked.

## Step 6: Report

```
## Handover Complete

- Task: [id] — [title]
- Status: [SUCCESS/PARTIAL/FAILED/BLOCKED]
- Handover: agent_memory/handovers/handover_<task-id>.md

### Memory Updates
- [x] tasks_queue.json — task marked completed
- [x] reference_map.json — [updated / no changes needed]
- [x] project_state.yaml — [updated / timestamp only]
- [x] architecture.md — [updated / no changes needed]

### Next Task
- [next pending task or "No pending tasks"]
```
