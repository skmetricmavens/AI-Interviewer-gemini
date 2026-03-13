---
name: next
description: Execute the next task in the queue with full quality gates. Use when ready to start working on the next planned task.
disable-model-invocation: true
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
  - Agent
  - AskUserQuestion
---

Execute the next task in the queue with full quality gates.

## Current State

```
!`cat agent_memory/tasks_queue.json 2>/dev/null | python3 -c "
import json,sys
data=json.load(sys.stdin)
current=[t for t in data.get('backlog',[]) if t.get('status')=='in_progress']
pending=[t for t in data.get('backlog',[]) if t.get('status')=='pending']
if current: print(f'IN PROGRESS: {current[0][\"id\"]}: {current[0][\"title\"]}')
elif pending: print(f'NEXT: {pending[0][\"id\"]}: {pending[0][\"title\"]}')
else: print('No tasks in queue')
" 2>/dev/null || echo "No tasks_queue.json found"`
```

## Task Execution Flow

### 1. Identify Task
- Find current (in_progress) or first pending task
- Mark as "in_progress" in tasks_queue.json
- Read `agent_memory/reference_map.json` NOW (needed for import validation during coding)

### 2. Create Feature Branch
```bash
git checkout main
git pull origin main
git checkout -b feature/<task-id>-<short-description>
```

### 3. Read Previous Handover
- Check `agent_memory/handovers/` for context from the previous task

### 4. Execute with TDD (delegate to sub-agents)
1. **test-writer sub-agent** — write failing test (RED)
2. **Implement** minimum code to pass (GREEN)
3. **quality-gate sub-agent** — run all quality gates
4. If fail: **fixer sub-agent** → **quality-gate sub-agent** (max 3 retries)

Delegating quality checks and fixes to sub-agents keeps their verbose output out of this context.

### 5. Post-Task Updates (ALL mandatory)

After quality gates pass, perform ALL updates before committing:

1. **Create handover** — `agent_memory/handovers/handover_<task-id>.md`
2. **Update tasks_queue.json** — mark task `completed`, update `current_task_id`
3. **Update reference_map.json** — new/changed exports, classes, functions
4. **Update project_state.yaml** — new/changed classes/functions, set `last_updated`
5. **Update architecture.md** — if new components, data flows, or dependencies

Or run `/handover` which performs all 5 updates.

### 6. Commit, Push, and Create PR
```bash
git add <specific-files>
git commit -m "task-N: [task title]"
git push -u origin feature/<task-id>-<short-description>
gh pr create --base main --title "task-N: [task title]" --body "## Summary\n- ...\n\n## Test plan\n- ..."
```

### 7. Report
Summarize what was done, include PR URL, and show next task.
