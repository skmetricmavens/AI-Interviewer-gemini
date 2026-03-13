Import a plan from Repoprompt and auto-boot into the project.

## Instructions

The user has pasted a plan output from Repoprompt. Parse it and set up the project.

### 1. Parse Task Graph

Look for a JSON code block containing `"backlog"` array. Extract and validate:

```json
{
  "current_task_id": null,
  "backlog": [
    {
      "id": "task-N",
      "title": "...",
      "description": "...",
      "status": "pending",
      "priority": "high|medium|low",
      "files": ["single-file.py"],
      "dependencies": []
    }
  ]
}
```

**Validation rules:**
- Each task has exactly ONE file in `files` array
- `dependencies` only reference valid task IDs
- `status` is "pending" for all new tasks

### 2. Update tasks_queue.json

Write the parsed task graph to `agent_memory/tasks_queue.json`.

### 3. Extract Scaffolding

Look for a directory structure in the plan (markdown code block with tree structure).
Create the directories using `mkdir -p`.

### 4. Update architecture.md

If the plan contains architecture information or scaffolding spec, append or update
`agent_memory/architecture.md` with the new structure.

### 5. Seed reference_map.json

If the plan contains a reference map seed, merge it into `agent_memory/reference_map.json`.
Otherwise, initialize with empty structure ready for `/sync`.

### 6. Create project_state.yaml

Update `agent_memory/project_state.yaml` with:
- Project name (from plan or directory name)
- Version: 0.1.0
- Current timestamp

### 7. Auto-Boot

After setup, automatically execute the `/boot` command to:
- Read all memory files
- Display project summary
- Show task queue status

## Output Format

After import, display:

```
## Plan Imported Successfully

### Tasks Created: [count]
- task-1: [title]
- task-2: [title]
...

### Scaffolding Created
- [directories created]

### Reference Map
- [N] modules registered (or "Empty - run /sync after first task")

---

[Boot Summary from /boot]

---

Ready to start. Run `/next` to begin [first-task-id].
```

## Error Handling

If no valid JSON found:
```
⚠️ Could not parse task graph.

Please ensure your plan contains a JSON code block with this structure:
{
  "current_task_id": null,
  "backlog": [...]
}

Paste your plan and try again.
```

If validation fails:
```
⚠️ Task validation failed:
- task-3: Multiple files specified (must be ONE file per task)
- task-5: Invalid dependency "task-99" (task does not exist)

Please fix your plan and try again.
```
