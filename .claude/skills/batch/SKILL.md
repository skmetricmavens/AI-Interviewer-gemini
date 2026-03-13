---
name: batch
description: Execute multiple independent tasks in parallel using agent teams. Use when there are 4+ independent tasks in the queue that don't depend on each other. Requires CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1 in settings.
disable-model-invocation: true
argument-hint: [optional: number of teammates or task filter]
---

Execute multiple independent tasks in parallel using agent teams.

## Pre-flight Check

```
!`echo "Agent teams enabled: ${CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS:-0}"`
```

If agent teams are not enabled, STOP and tell the user:
```
Agent teams are not enabled. Add this to .claude/settings.json:
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
Then restart Claude Code.
```

## Step 1: Analyze Task Queue

Read `agent_memory/tasks_queue.json` and identify tasks that can run in parallel.

**Parallelizable criteria:**
- Status is `pending`
- No unresolved dependencies (all deps are `completed`)
- Tasks target DIFFERENT files (no file overlap)

**Not parallelizable:**
- Tasks with unresolved dependencies
- Tasks targeting the same files
- Tasks that must run in sequence

Present the analysis:
```
## Batch Execution Plan

### Parallel batch (can run simultaneously)
| # | Task | File | Priority |
|---|------|------|----------|
| task-1 | ... | src/foo.py | high |
| task-2 | ... | src/bar.py | high |
| task-3 | ... | src/baz.py | medium |

### Sequential (must wait)
| # | Task | Depends On | Reason |
|---|------|------------|--------|
| task-4 | ... | task-1 | Depends on task-1 |

### Skipped (not ready)
| # | Task | Reason |
|---|------|--------|
| task-5 | ... | Dependency task-3 not completed |

Teammates needed: [count]
Proceed? (y/n)
```

## Step 2: Confirm with User

Wait for user confirmation before spawning teammates. Show estimated token cost impact (each teammate is a separate Claude session).

## Step 3: Create Agent Team

Spawn one teammate per parallelizable task. Each teammate receives:

1. **The task description** from tasks_queue.json
2. **Instructions to follow the full workflow:**
   - Create a feature branch for their task
   - Write tests first (TDD)
   - Implement the change
   - Run quality gates
   - Create handover and update memory files
   - Commit on their feature branch
3. **File ownership** — each teammate only modifies their assigned files

```
Create an agent team with [N] teammates. Each teammate works on one task:

Teammate 1: "[task-1 title]" — owns [files]. Branch: feature/task-1-description
Teammate 2: "[task-2 title]" — owns [files]. Branch: feature/task-2-description
...

Each teammate must:
1. Create their feature branch
2. Write tests first (TDD)
3. Implement the change
4. Run quality gates (ruff, mypy, pytest)
5. Create handover in agent_memory/handovers/
6. Commit on their branch

Require plan approval before teammates make changes.
Do NOT let teammates edit files outside their ownership.
Wait for all teammates to finish before reporting.
```

## Step 4: Monitor and Synthesize

After all teammates complete:

1. Collect results from each teammate
2. Run `/sync` to update reference_map and project_state from all changes
3. Report summary:

```
## Batch Execution Complete

| Task | Teammate | Status | Branch | Tests |
|------|----------|--------|--------|-------|
| task-1 | #1 | SUCCESS | feature/task-1-... | 5/5 passed |
| task-2 | #2 | SUCCESS | feature/task-2-... | 3/3 passed |
| task-3 | #3 | FAILED | feature/task-3-... | 1/4 failed |

### Completed: [X]/[Y]
### PRs ready for review: [list branches]
### Failed tasks: [list with error summaries]

Next: Review and merge PRs, or use /fix for failed tasks.
```

## Rules

- **Never batch tasks that share files** — file conflicts will cause overwrites
- **Always require plan approval** — teammates must plan before implementing
- **Max 5 teammates** — more than 5 increases coordination overhead without proportional benefit
- **Each teammate follows the full workflow** — no shortcuts for batched tasks
- **Run /sync after batch completes** — consolidate all memory file updates
