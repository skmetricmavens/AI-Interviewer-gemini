---
name: status
description: Show current project status including task progress, codebase stats, and recent activity
context: fork
allowed-tools:
  - Read
---

Show the current project status.

Read:
1. `agent_memory/tasks_queue.json`
2. `agent_memory/project_state.yaml`

## Project Status Report

### Overview
- **Project**: [name]
- **Version**: [version]
- **Last Updated**: [date]

### Task Progress
| Status | Count |
|--------|-------|
| Completed | X |
| In Progress | X |
| Pending | X |
| **Total** | X |

### Current Task
```
ID: [id]
Title: [title]
Status: [status]
Files: [files]
```

### Next Up
```
ID: [id]
Title: [title]
Priority: [priority]
Dependencies: [deps]
```

### Codebase Stats
- Classes: X
- Functions: X
- Modules: X

### Recent Activity
[List recently completed tasks]

---

**Quick Actions:**
- `/next` - Execute next task
- `/plan <goal>` - Plan new work
- `/fix <errors>` - Decompose and fix errors
- `/boot` - Full boot with context
