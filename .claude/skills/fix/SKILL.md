---
name: fix
description: Decompose errors and bugs into atomic tasks, then execute fixes through the full workflow. Use when the user reports errors, bugs, failures, or issues to fix.
argument-hint: [error description or paste errors]
---

Decompose the reported errors into atomic fix tasks and execute them through the full development workflow.

## Reported Errors

$ARGUMENTS

## Step 1: Analyze and Decompose

Break the errors into **separate atomic tasks**. Each task must:
- Fix exactly ONE issue
- Target ONE file (plus its test file)
- Be independently testable

Add all fix tasks to `agent_memory/tasks_queue.json` with status `pending` and priority `high`.

Example decomposition:
```json
{
  "id": "fix-1",
  "title": "Fix input validation in process_request()",
  "description": "Add null check for request.body before parsing",
  "status": "pending",
  "priority": "high",
  "files": ["src/api/routes.py"],
  "dependencies": []
}
```

**Rules:**
- ONE fix = ONE task (never combine multiple fixes)
- Include a regression test in the task scope
- Order by dependency (if fix-2 depends on fix-1, list fix-1 first)

## Step 2: Confirm with User

Present the decomposed tasks and ask for confirmation before proceeding:

```
## Fix Plan

| # | Task | File | Description |
|---|------|------|-------------|
| fix-1 | ... | ... | ... |
| fix-2 | ... | ... | ... |

Proceed with these fixes? (y/n)
```

## Step 3: Execute Each Fix

For each fix task, follow the **full workflow**:

1. Mark task as `in_progress` in `tasks_queue.json`
2. Create or stay on fix branch (`fix/<task-id>-description`)
3. Write regression test FIRST (use `test-writer` sub-agent)
4. Apply minimal fix (use `fixer` sub-agent)
5. Run quality gates (use `quality-gate` sub-agent)
6. If gates fail: retry with fixer (max 3 attempts)
7. Run post-task updates (ALL mandatory — see below)
8. Commit on the fix branch

## Step 4: Post-Task Updates (after EACH fix task)

After each fix task passes quality gates, perform ALL updates:

1. **Create handover** — `agent_memory/handovers/handover_<task-id>.md`
2. **Update tasks_queue.json** — mark task `completed`
3. **Update reference_map.json** — if any exports/functions changed
4. **Update project_state.yaml** — if any classes/functions changed, update `last_updated`
5. **Update architecture.md** — if structural changes were made

## Step 5: Report

After all fixes are complete:

```
## Fix Summary

| Task | Status | Test | Quality |
|------|--------|------|---------|
| fix-1 | SUCCESS | test_xxx passed | All gates passed |
| fix-2 | SUCCESS | test_yyy passed | All gates passed |

Branch: fix/<description>
Ready for PR: yes/no
```
