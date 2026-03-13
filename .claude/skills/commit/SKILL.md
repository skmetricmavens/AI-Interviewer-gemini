---
name: commit
description: Run quality gates, verify memory updates, and commit current work
disable-model-invocation: true
---

Run quality gates, verify post-task updates, and commit the current work.

## 1. Pre-flight Check

```
!`echo "Branch: $(git branch --show-current)"; echo "---"; git diff --stat`
```

If on `main` or `master`, STOP: "Create a feature/fix branch first. Never commit directly to main."

## 2. Quality Gates

Run ALL gates — every one must pass before committing:

```bash
ruff check src/
ruff format src/ --check
mypy src/ --ignore-missing-imports
pytest tests/ -v
```

If any gate fails, report the failures and STOP. Do NOT commit with failing gates.
If gates fail, use the `fixer` sub-agent to fix issues (max 3 attempts).

## 3. Post-Task Update Check

Before committing, verify ALL memory files are up to date:

- [ ] `agent_memory/tasks_queue.json` — current task marked `completed`
- [ ] `agent_memory/handovers/handover_<task-id>.md` — handover exists
- [ ] `agent_memory/reference_map.json` — reflects any new/changed symbols
- [ ] `agent_memory/project_state.yaml` — reflects any new/changed classes/functions
- [ ] `agent_memory/architecture.md` — updated if structural changes were made

If any are missing, update them BEFORE committing. Run `/sync` if reference_map or project_state need updating.

## 4. Generate Commit Message

Analyze the staged and unstaged changes and generate a commit message:
- Format: `task-N: brief description` (if a task is active in `tasks_queue.json`)
- Otherwise: `type: brief description` (where type = feat/fix/refactor/test/docs/chore)
- Include `Co-Authored-By: Claude <noreply@anthropic.com>`

## 5. Stage and Commit

```bash
git add <specific-files>
git commit -m "<generated message>"
```

## 6. Confirm

```
## Commit Complete

- Branch: [current branch]
- Commit: [short hash] [message]
- Quality: All gates passed
- Memory: All files updated
- Files: [count] changed
```
