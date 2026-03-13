---
name: boot
description: Load project context and show current tasks. Use at the start of every session.
---

Boot into this project using progressive disclosure — load only what's needed now, defer the rest.

## Step 1: Read Core Context (always)

Read these files:
1. `agent_memory/method_of_working.md` - Workflow and rules
2. `agent_memory/tasks_queue.json` - Current and pending tasks
3. `agent_memory/project_state.yaml` - Current codebase state (classes, functions)

## Step 2: Read If Relevant (defer if not needed yet)

- `agent_memory/architecture.md` - Read only if starting a NEW feature or the user asks about system design
- `agent_memory/reference_map.json` - Read only when about to write code (import validation). Do NOT read at boot.
- `agent_memory/handovers/` - Read the most recent handover ONLY if a task is in_progress or was recently completed

## Current Git State

```
!`git branch --show-current && git log --oneline -5`
```

## Pending Handovers

```
!`ls -t agent_memory/handovers/ 2>/dev/null | head -3 || echo "No handovers yet"`
```

## Boot Summary

After reading core files, provide a structured summary:

### Project Status
- Project: [name from project_state.yaml]
- Branch: [current git branch]
- Last updated: [date]

### Task Queue
- Current task: [from tasks_queue.json or "None"]
- Next pending: [first pending task]
- Total pending: [count]

### Recent Context
- Last handover: [most recent handover file, if any]

### Deferred (will load when needed)
- reference_map.json — loaded before writing code
- architecture.md — loaded before structural changes

---

Then ask: "What would you like to work on?"
