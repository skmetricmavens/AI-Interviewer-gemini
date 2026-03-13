# Plan Prompt Template

Use this prompt in Repoprompt after Discovery to create an executable task plan.

---

## Prompt

```
You are a technical project planner. Convert the discovery document into an
executable task plan compatible with Claude Code's starter kit.

## Discovery Document

[PASTE YOUR DISCOVERY OUTPUT HERE]

## Plan Output Requirements

Create a detailed implementation plan with the following sections:

### 1. Task Graph

Create 8-14 atomic tasks. Output the COMPLETE JSON that can be saved to `tasks_queue.json`:

```json
{
  "current_task_id": null,
  "backlog": [
    {
      "id": "task-1",
      "title": "Brief title (5-10 words)",
      "description": "Detailed description of what this task produces",
      "status": "pending",
      "priority": "high",
      "files": ["path/to/single-file.py"],
      "dependencies": []
    },
    {
      "id": "task-2",
      "title": "Second task title",
      "description": "What this task accomplishes",
      "status": "pending",
      "priority": "high",
      "files": ["path/to/another-file.py"],
      "dependencies": ["task-1"]
    }
  ]
}
```

**CRITICAL RULES:**
- ONE file per task (non-negotiable for quality)
- Tasks MUST be in strict dependency order
- First task(s) have empty dependencies array
- Each task produces testable, reviewable output
- Include test tasks after implementation tasks
- Use priority: high for foundation, medium for features, low for polish

### 2. Build Order

List tasks in execution order with rationale:

| Order | Task ID | Title | Why This Order |
|-------|---------|-------|----------------|
| 1 | task-1 | ... | Foundation, no deps |
| 2 | task-2 | ... | Depends on task-1 |
| ... | ... | ... | ... |

### 3. File → Task Mapping

Complete mapping of every file to its task:

| File Path | Task | Purpose |
|-----------|------|---------|
| src/models/base.py | task-1 | Database foundation |
| src/models/user.py | task-2 | User data model |
| tests/test_models.py | task-7 | Model unit tests |
| ... | ... | ... |

### 4. Scaffolding Specification

Directory structure to create:

```
project/
├── src/
│   ├── __init__.py
│   ├── models/
│   │   └── __init__.py
│   └── services/
│       └── __init__.py
├── tests/
│   └── __init__.py
└── ...
```

### 5. Reference Map Seed

Initial exports for grounding (update this as tasks complete):

```json
{
  "modules": {
    "models.base": {
      "file_path": "src/models/base.py",
      "classes": ["Base"],
      "functions": [],
      "exports": ["Base"]
    }
  },
  "public_api": {},
  "cross_module_deps": {}
}
```

### 6. MVP Completion Checklist

When these tasks are done, MVP is complete:

- [ ] task-1 through task-N completed
- [ ] All tests passing
- [ ] [specific acceptance criteria from discovery]

---

## Claude Code Instructions

When you paste this plan into Claude Code, run:

```
/import-plan
```

This will:
1. Parse the task graph into tasks_queue.json
2. Create directory scaffolding
3. Update architecture.md
4. Seed reference_map.json
5. Auto-run /boot to start your session

Then run `/next` to begin the first task.
```

---

## Example Output

See `examples/plan-output.md` for a complete example.

## Tips

1. **Task Granularity**: Each task should be completable in one focused session
2. **Test Tasks**: Always include separate tasks for tests
3. **Dependencies**: Be explicit - don't assume implicit ordering
4. **One File Rule**: Breaking this rule leads to messy commits and harder reviews
