---
name: plan
description: Create a comprehensive task plan for a project goal, breaking it into atomic tasks
argument-hint: [goal description]
---

You are a project planner. Create a comprehensive task plan for the project goal provided.

First, read the current project state:
1. `agent_memory/project_state.yaml` - Current state
2. `agent_memory/tasks_queue.json` - Existing tasks
3. `agent_memory/architecture.md` - Project structure

Then, for the goal "$ARGUMENTS", create a detailed plan:

## Planning Output

### 1. Goal Analysis
- Break down the goal into specific deliverables
- Identify dependencies and prerequisites
- Note any constraints or considerations

### 2. Task List
Create tasks following this format for each task:

```json
{
  "id": "task-N",
  "title": "Brief title (5-10 words)",
  "description": "Detailed description of what needs to be done",
  "status": "pending",
  "priority": "high|medium|low",
  "files": ["single-file.py"],
  "dependencies": ["task-ids-that-must-complete-first"]
}
```

**CRITICAL RULES:**
- ONE file per task (this is essential for quality)
- Tasks must be in dependency order
- Each task should be completable in one session
- Be specific about what each task produces

### 3. Update Tasks Queue
After planning, ask if you should update `agent_memory/tasks_queue.json` with the new tasks.

### 4. Suggested First Steps
Recommend which task to start with and why.

---

**Example usage:**
```
/plan Build a REST API for user management with authentication
```
