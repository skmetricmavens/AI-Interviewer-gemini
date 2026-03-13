#!/bin/bash
# Claude Code Starter Kit Setup Script
# Usage: curl -sL <url> | bash -s -- "Your Project Name"

set -e

PROJECT_NAME="${1:-my-project}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🚀 Setting up Claude Code memory structure for: $PROJECT_NAME"
echo ""

# Create directories
mkdir -p agent_memory
mkdir -p agent_memory/handovers
mkdir -p .claude/commands
mkdir -p .claude/hooks
mkdir -p .claude/agents
mkdir -p .claude/rules
mkdir -p .claude/skills/boot
mkdir -p .claude/skills/next
mkdir -p .claude/skills/handover
mkdir -p .claude/skills/review

# Create CLAUDE.md (high-leverage entry point for Claude Code)
cat > CLAUDE.md << 'EOF'
# Project Context

## Quick Start
Run `/boot` to load project context and see current tasks.

## Bash Commands
```bash
pytest tests/ -v              # Run all tests
mypy src/ --ignore-missing-imports  # Type check
ruff check src/               # Lint check
```

## Core Rules

1. **TDD** — Write test FIRST, then implement (RED → GREEN → refactor)
2. **Quality gates** — ruff, mypy, pytest MUST pass before commit
3. **Grounding** — Only import symbols in `reference_map.json`
4. **Atomic tasks** — One focused change per task
5. **Handover** — Run `/handover` after completing each task

Path-specific rules in `.claude/rules/`:
- `workflow.md` — Task execution steps
- `quality-gates.md` — Gate details and retry logic
- `git-workflow.md` — Branch naming, commit format
- `testing.md` — TDD patterns (loads for `tests/**` and `src/**`)
- `poc-workflow.md` — Relaxed rules for POC scripts (loads for `scripts/poc_*`)

## Skills

| Skill | When to Use |
|-------|-------------|
| `/boot` | Start of every session |
| `/next` | Execute next pending task (runs in fork) |
| `/handover` | Generate handover from current work |
| `/review` | Pre-PR review checklist (runs in fork) |
| `/status` | Check progress |
| `/sync` | After adding classes/functions |
| `/import-plan` | When pasting a plan from Repoprompt |

## Subagents

| Subagent | Purpose | Permissions |
|----------|---------|-------------|
| `test-writer` | Generate tests BEFORE code (TDD RED) | READ, WRITE |
| `code-reviewer` | Review code for quality/security | READ only |
| `quality-gate` | Run mypy, pytest, lint checks | READ, EXECUTE |
| `fixer` | Apply minimal fixes for errors | READ, WRITE |

## Memory System

| File | Purpose |
|------|---------|
| `tasks_queue.json` | Current and pending tasks |
| `project_state.yaml` | Classes, functions, codebase state |
| `reference_map.json` | Module exports for import validation |

@agent_memory/architecture.md
@agent_memory/method_of_working.md
EOF

# Create method_of_working.md (copy from starter-kit source)
cat > agent_memory/method_of_working.md << 'MOWEOF'
# Method of Working

## How to Boot Claude Code

When starting a new Claude Code session, use:

```
/boot
```

This reads all memory files and provides a structured summary of your project.

---

## Boot Sequence

On every session start, Claude will:
1. Read this file (`method_of_working.md`)
2. Read `architecture.md` for system design
3. Read `project_state.yaml` for current codebase state
4. Read `tasks_queue.json` for current/next task
5. Read `reference_map.json` for available symbols

## Core Principles

### 1. Grounding
- Only reference symbols that exist in `reference_map.json`
- Validate imports against the symbol table before writing code
- Never hallucinate function names or class methods

### 2. Deterministic Behavior
- Follow tasks in order from `tasks_queue.json`
- Mark tasks as `in_progress` when starting, `completed` when done
- Update memory files after each significant change

### 3. Validation First
- Run tests before committing changes
- Check imports and type hints
- Fix errors before proceeding

### 4. Atomic Changes
- One task = one focused change
- Each task should target specific files
- Don't mix unrelated changes

## Workflow

```
1. Boot (load memory files)
2. Create feature branch
3. Get current task from tasks_queue.json
4. Read relevant files
5. Write failing tests from task description (TDD RED)
6. Implement minimum code to pass tests (TDD GREEN)
7. Run quality gates (mypy, ruff, pytest)
8. If gates fail: fix and retry (max 3 attempts)
9. Update memory files
10. Mark task complete
11. Commit to feature branch
12. Merge when ready
13. Next task
```

### Git Strategy

**One commit per task** for easy rollback:

```bash
# Start work
git checkout -b feature/task-description

# After completing (only when tests pass!)
git add .
git commit -m "task-N: description"

# Merge when ready
git checkout main
git merge feature/task-description
git push
```

**Rollback when needed:**
```bash
git reset --soft HEAD~1  # Undo commit, keep changes
git reset --hard HEAD~1  # Undo commit, discard changes
```

---

## Subagents

Each subagent has ONE responsibility — no overlap:

| Subagent | Main Package Equivalent | Does | Does NOT | Permissions |
|----------|------------------------|------|----------|-------------|
| **test-writer** | TesterAgent | Write tests from task description (TDD RED) | Run tests, write code | READ, WRITE |
| **code-reviewer** | CriticAgent | Review code quality & security | Modify files, run commands | READ only |
| **quality-gate** | Orchestrator (quality gates) | Run mypy, pytest, ruff checks | Modify files | READ, EXECUTE |
| **fixer** | FixerAgent | Apply minimal targeted fixes | Run commands, refactor | READ, WRITE |

> Planner and Coder roles are handled by Claude directly via `/plan` and `/next` commands.

**TDD Workflow:** `PLAN → TEST (RED) → CODE (GREEN) → REVIEW → QUALITY GATES → FIX → COMMIT`

### Extreme Task Decomposition

Break features into granular subtasks:

- ONE function per task
- ONE file per task
- < 100 lines of code per task

❌ Bad: `Implement calculator with basic operations`
✅ Good: `Implement add(a, b) in calculator/ops.py`

---

## TDD Principles

Follow **Test-Driven Development** for every feature:

### The Cycle

```
1. Write test first (RED)
2. Implement feature (GREEN)
3. Refactor if needed
4. Repeat
```

### Key Principles

| Principle | Description |
|-----------|-------------|
| **Test the real code** | Don't test mocks—test actual components |
| **Test with real data** | Use realistic inputs, not simplified data |
| **Test error paths** | Don't just test happy paths |
| **Reproduce bugs in tests** | Every bug gets a regression test |

### Coverage Goals

- **80%+ unit test coverage** (Gold standard)
- **90%+ total coverage** target
- Comprehensive edge cases

---

## Quality Gates

Before marking any task complete, run through these gates:

### Gate 1: Type Checking (Python)

```bash
mypy <file_path> --ignore-missing-imports
```

Fix all type errors before proceeding.

### Gate 2: Tests

```bash
pytest tests/ -v
```

All tests must pass. If tests fail:
1. Read the error message
2. Fix the code
3. Re-run tests
4. Repeat until green

### Gate 3: Import Validation

Verify all imports resolve:
- Check `reference_map.json` for available symbols
- Don't import non-existent modules
- Don't use undefined functions

### Gate 4: Code Quality

Check for common issues:
- No hardcoded secrets or API keys
- Proper error handling
- Consistent naming (snake_case for functions, PascalCase for classes)
- No unused imports or variables

### Quality Retry Loop

If any gate fails:

```
1. Implement feature
2. Run quality gates
3. If FAIL: Fix issues, go to step 2 (max 3 attempts)
4. If PASS: Continue to commit
```

---

## Checkpoints (Human Review)

Pause for human review at these points:

| Checkpoint | When to Pause |
|------------|---------------|
| **Before Task** | Before starting work on a new task |
| **After Planning** | Before starting implementation |
| **Before Commit** | Review changes before committing |
| **After Failure** | When tests/quality gates fail repeatedly |
| **Risky Changes** | Deleting files, changing APIs, security-related |

### How to Checkpoint

Ask the user:
```
🔍 Checkpoint: [type]

Summary: [what was done]
Changes: [files modified]
Risks: [potential issues]

Continue? (y/n)
```

---

## Handover Pattern

When completing a task, create a handover summary with explicit status:

### Handover Status

| Status | When to Use |
|--------|-------------|
| **SUCCESS** | Task completed, all quality gates passed |
| **PARTIAL** | Some work done, needs continuation |
| **FAILED** | Task failed, needs different approach |
| **BLOCKED** | Cannot proceed without external input |

### Handover Template

```markdown
## Task [STATUS]: [title]

### Status: [SUCCESS/PARTIAL/FAILED/BLOCKED]

### What Was Done
- [bullet points of changes]

### Files Modified
- `path/to/file.py` - [what changed]

### Quality Results
- ✅ mypy: passed
- ✅ tests: 5/5 passed
- ✅ imports: valid

### Next Steps
- [what should happen next]

### Blockers (if BLOCKED)
- [what's preventing progress]

### Warnings
- [any issues to be aware of]
```

This helps maintain context between sessions.

---

## Forbidden Actions

- Do NOT create files outside the project structure
- Do NOT modify memory files without validation
- Do NOT skip tests
- Do NOT hallucinate APIs or function signatures
- Do NOT commit broken code

## Invariants

- All imports must resolve to existing modules
- All function calls must match their signatures
- All tests must pass before marking task complete
- Memory files must stay in sync with codebase

## Current Status

- **Phase**: Initial Setup
- **Tests**: Not yet configured
- **In Progress**: None
MOWEOF

# Create architecture.md
cat > agent_memory/architecture.md << EOF
# Architecture - $PROJECT_NAME

## Overview

[Describe your project here]

## Directory Structure

\`\`\`
$PROJECT_NAME/
├── src/                    # Source code
├── tests/                  # Test suite
├── agent_memory/           # Claude Code memory
│   ├── method_of_working.md
│   ├── architecture.md
│   ├── project_state.yaml
│   ├── tasks_queue.json
│   └── reference_map.json
├── .claude/commands/       # Slash commands
├── docs/                   # Documentation
└── README.md
\`\`\`

## Key Components

[Describe your components here]

## Data Flow

[Describe your data flow here]
EOF

# Create project_state.yaml
cat > agent_memory/project_state.yaml << EOF
project_name: $PROJECT_NAME
version: 0.1.0
last_updated: '$(date -u +%Y-%m-%dT%H:%M:%S)'

classes: {}

functions: {}

invariants:
  - "All functions must have type hints"
  - "All public functions must have docstrings"
  - "Tests must pass before merging"

forbidden_actions:
  - "Do not commit without running tests"
  - "Do not skip code review"
EOF

# Create tasks_queue.json
cat > agent_memory/tasks_queue.json << 'EOF'
{
  "current_task_id": null,
  "backlog": [
    {
      "id": "task-1",
      "title": "Initial project setup",
      "description": "Set up the basic project structure and dependencies",
      "status": "pending",
      "priority": "high",
      "files": ["README.md"],
      "dependencies": []
    }
  ]
}
EOF

# Create reference_map.json
cat > agent_memory/reference_map.json << 'EOF'
{
  "modules": {},
  "public_api": {},
  "cross_module_deps": {}
}
EOF

# Create /boot command
cat > .claude/commands/boot.md << 'EOF'
Read the following files to boot into this project:

1. `agent_memory/method_of_working.md` - How to work on this project
2. `agent_memory/architecture.md` - System architecture and structure
3. `agent_memory/project_state.yaml` - Current codebase state
4. `agent_memory/tasks_queue.json` - Current and pending tasks
5. `agent_memory/reference_map.json` - Module exports and dependencies

After reading all files, provide a structured summary:

## Boot Summary

### Project Status
- Project: [name from project_state.yaml]
- Version: [version]
- Last updated: [date]

### Task Queue
- Current task: [from tasks_queue.json or "None"]
- Next pending: [first pending task]
- Total pending: [count]

### Codebase
- Classes: [count]
- Functions: [count]

---

Then ask: "What would you like to work on?"
EOF

# Create /plan command
cat > .claude/commands/plan.md << 'EOF'
You are a project planner. Create a task plan for: "$ARGUMENTS"

First, read:
1. `agent_memory/project_state.yaml`
2. `agent_memory/tasks_queue.json`
3. `agent_memory/architecture.md`

Then create tasks following this format:

```json
{
  "id": "task-N",
  "title": "Brief title",
  "description": "What needs to be done",
  "status": "pending",
  "priority": "high|medium|low",
  "files": ["single-file.py"],
  "dependencies": ["task-ids"]
}
```

**Rules:**
- ONE file per task
- Tasks in dependency order
- Be specific

After planning, offer to update `agent_memory/tasks_queue.json`.
EOF

# Create /next command
cat > .claude/commands/next.md << 'EOF'
Execute the next task in the queue with full quality gates.

First, read:
1. `agent_memory/tasks_queue.json` - Get current/next task
2. `agent_memory/project_state.yaml` - Current state
3. `agent_memory/reference_map.json` - Available symbols
4. `agent_memory/method_of_working.md` - Quality gates and workflow

## Task Execution Flow

### 1. Identify Task
- Find the current task (status: "in_progress") or first pending task
- Display task details
- Mark task as "in_progress" in tasks_queue.json

### 2. Pre-flight Check
- List files that will be modified
- Check dependencies are complete
- Verify symbols exist in reference_map.json

### 3. Execute (with Quality Loop)

```
MAX_RETRIES = 3
for attempt in 1..MAX_RETRIES:
    1. Implement the changes
    2. Run Quality Gates
    3. If all pass: break
    4. If fail: fix issues, continue loop
```

### 4. Quality Gates

Run ALL gates before marking complete:

**Gate 1: Type Check (Python files)**
```bash
mypy <file_path> --ignore-missing-imports
```

**Gate 2: Tests**
```bash
pytest tests/ -v
```

**Gate 3: Import Validation**
- Verify all imports exist in reference_map.json
- No undefined symbols used

**Gate 4: Code Quality**
- No hardcoded secrets
- Proper error handling
- Consistent naming conventions

### 5. Handle Failures

If quality gates fail after 3 attempts:
1. Stop and report the issues
2. Ask user for guidance
3. Create a checkpoint with:
   - What was attempted
   - What failed
   - Suggested fixes

### 6. Update Memory
After ALL quality gates pass:
- Update `project_state.yaml` with new classes/functions
- Update `reference_map.json` with new exports
- Mark task as "completed" in `tasks_queue.json`

### 7. Create Handover

Use explicit status: SUCCESS, PARTIAL, FAILED, or BLOCKED

```markdown
## Task [STATUS]: [title]

### Status: SUCCESS

### What Was Done
- [changes made]

### Quality Results
- ✅ mypy: passed
- ✅ tests: X/Y passed
- ✅ imports: valid

### Files Modified
- `path/to/file.py`

### Next Steps
- [what's next in queue]
```

**Status meanings:**
- **SUCCESS**: All quality gates passed, task complete
- **PARTIAL**: Some work done, needs continuation
- **FAILED**: Task failed, needs different approach
- **BLOCKED**: Cannot proceed without external input

### 8. Commit
```bash
git add .
git commit -m "task-N: [task title]"
```

### 9. Report
Summarize what was done and show next task.
EOF

# Create /status command
cat > .claude/commands/status.md << 'EOF'
Show project status.

Read:
1. `agent_memory/tasks_queue.json`
2. `agent_memory/project_state.yaml`

Display:
- Project name and version
- Task counts (completed/in-progress/pending)
- Current task details
- Next task preview
- Codebase stats (classes/functions)
EOF

# Create /import-plan command
cat > .claude/commands/import-plan.md << 'EOF'
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

### 6. Auto-Boot

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
EOF

# Create /sync command
cat > .claude/commands/sync.md << 'EOF'
Synchronize memory files with the current codebase.

## Instructions

Scan the codebase and update memory files to reflect current state.

### 1. Scan for Classes and Functions

Search Python files for:
- Class definitions: `class ClassName:`
- Function definitions: `def function_name(`
- Method definitions within classes

### 2. Update project_state.yaml

Update `agent_memory/project_state.yaml` with discovered symbols:

```yaml
classes:
  ClassName:
    file_path: path/to/file.py
    methods: [method1, method2]
    docstring: "Class description"

functions:
  function_name:
    file_path: path/to/file.py
    signature: "(arg1: str, arg2: int) -> bool"
```

### 3. Update reference_map.json

Update `agent_memory/reference_map.json` with module exports:

```json
{
  "modules": {
    "module.name": {
      "file_path": "path/to/module.py",
      "classes": ["ClassName"],
      "functions": ["function_name"],
      "exports": ["ClassName", "function_name"]
    }
  }
}
```

### 4. Report Changes

Display what was updated:
- New classes/functions found
- Removed entries (files deleted)
- Modified signatures

## Output

```
## Sync Complete

### project_state.yaml
- Added: ClassName, function_name
- Removed: OldClass
- Updated: existing_function (signature changed)

### reference_map.json
- Modules scanned: 5
- Total exports: 12

Memory files are now in sync with codebase.
```
EOF

# Create hook: session start - load context (progressive disclosure)
cat > .claude/hooks/session-start.sh << 'HOOKEOF'
#!/bin/bash
# SessionStart: Inject key context at session start
# Outputs context that gets added to Claude's initial prompt

cd "$CLAUDE_PROJECT_DIR"

echo "## Project Context (Auto-loaded)"
echo ""

# Load current task
if [ -f "agent_memory/tasks_queue.json" ]; then
    CURRENT_TASK=$(cat agent_memory/tasks_queue.json | grep -A5 '"status": "in_progress"' | head -6)
    if [ -n "$CURRENT_TASK" ]; then
        echo "### Current Task (in_progress)"
        echo "$CURRENT_TASK"
        echo ""
    else
        NEXT_TASK=$(cat agent_memory/tasks_queue.json | grep -A5 '"status": "pending"' | head -6)
        if [ -n "$NEXT_TASK" ]; then
            echo "### Next Task (pending)"
            echo "$NEXT_TASK"
            echo ""
        fi
    fi
fi

# Reminder of key rules
echo "### Reminders"
echo "- TDD: Write test FIRST, then implement"
echo "- Quality gates: ruff, mypy, pytest MUST pass before commit"
echo "- One file per task"
echo "- Create handover after each task"
echo ""
echo "Run /boot for full context, /next to start task"

exit 0
HOOKEOF
chmod +x .claude/hooks/session-start.sh

# Create hook: TDD enforcement - check test exists before implementation
cat > .claude/hooks/tdd-check.sh << 'HOOKEOF'
#!/bin/bash
# PreToolUse on Write: Enforce TDD - test file should exist or be created first
# Exit code 2 = block, 0 = allow

FILE_PATH="$TOOL_INPUT_file_path"

# Skip non-Python files
if [[ ! "$FILE_PATH" =~ \.py$ ]]; then
    exit 0
fi

# Skip if this IS a test file (allow writing tests)
if [[ "$FILE_PATH" =~ ^tests/ ]] || [[ "$FILE_PATH" =~ test_.* ]] || [[ "$FILE_PATH" =~ _test\.py$ ]]; then
    exit 0
fi

# Skip __init__.py and config files
if [[ "$FILE_PATH" =~ __init__\.py$ ]] || [[ "$FILE_PATH" =~ config ]] || [[ "$FILE_PATH" =~ settings ]]; then
    exit 0
fi

# Extract module name to find corresponding test
BASENAME=$(basename "$FILE_PATH" .py)
DIRNAME=$(dirname "$FILE_PATH")

# Look for test file
TEST_FILE="tests/unit/test_${BASENAME}.py"
TEST_FILE_ALT="tests/test_${BASENAME}.py"

if [ -f "$TEST_FILE" ] || [ -f "$TEST_FILE_ALT" ]; then
    exit 0  # Test exists, allow
fi

# Check if tests directory exists at all
if [ ! -d "tests" ]; then
    echo '{"continue": true, "systemMessage": "⚠️ TDD: No tests/ directory. Create tests first!"}'
    exit 0  # Warning only for new projects
fi

# Warn but don't block (some files genuinely don't need tests)
echo "{\"continue\": true, \"systemMessage\": \"⚠️ TDD Reminder: No test found for ${BASENAME}.py. Write test first! Expected: ${TEST_FILE}\"}"
exit 0
HOOKEOF
chmod +x .claude/hooks/tdd-check.sh

# Create hook: lint check after file writes
cat > .claude/hooks/post-edit-lint.sh << 'HOOKEOF'
#!/bin/bash
# PostToolUse on Write|Edit: Run lint/type checks
# Exit code 0 with systemMessage = warning

FILE_PATH="$TOOL_INPUT_file_path"

# Skip non-Python files
if [[ ! "$FILE_PATH" =~ \.py$ ]]; then
    exit 0
fi

cd "$CLAUDE_PROJECT_DIR"
ERRORS=""

# Check ruff
if command -v ruff &> /dev/null; then
    RUFF_OUTPUT=$(ruff check "$FILE_PATH" 2>&1)
    if [ $? -ne 0 ]; then
        ERRORS="$ERRORS\nruff: $RUFF_OUTPUT"
    fi
fi

# Check mypy
if command -v mypy &> /dev/null; then
    MYPY_OUTPUT=$(mypy "$FILE_PATH" --ignore-missing-imports 2>&1 | grep -v "^Success")
    if [ $? -ne 0 ] && [ -n "$MYPY_OUTPUT" ]; then
        ERRORS="$ERRORS\nmypy: $MYPY_OUTPUT"
    fi
fi

if [ -n "$ERRORS" ]; then
    # Escape for JSON
    ERRORS_ESCAPED=$(echo -e "$ERRORS" | head -10 | tr '\n' ' ' | sed 's/"/\\"/g')
    echo "{\"continue\": true, \"systemMessage\": \"❌ Quality issues in $FILE_PATH: $ERRORS_ESCAPED\"}"
fi

exit 0
HOOKEOF
chmod +x .claude/hooks/post-edit-lint.sh

# Create hook: pre-commit quality gate enforcement
cat > .claude/hooks/pre-commit-check.sh << 'HOOKEOF'
#!/bin/bash
# PreToolUse on Bash: Block git commit if quality gates fail
# Exit code 2 = block the commit

COMMAND="$TOOL_INPUT_command"

# Only check git commit commands
if [[ ! "$COMMAND" =~ ^git\ commit ]]; then
    exit 0
fi

cd "$CLAUDE_PROJECT_DIR"
ERRORS=""

# Run ruff
if command -v ruff &> /dev/null; then
    for dir in src/ .; do
        if [ -d "$dir" ]; then
            RUFF_OUTPUT=$(ruff check "$dir" 2>&1)
            if [ $? -ne 0 ]; then
                ERRORS="$ERRORS\n❌ ruff check failed:\n$RUFF_OUTPUT"
            fi
            break
        fi
    done
fi

# Run mypy
if command -v mypy &> /dev/null; then
    for dir in src/ .; do
        if [ -d "$dir" ]; then
            MYPY_OUTPUT=$(mypy "$dir" --ignore-missing-imports 2>&1 | grep -v "^Success")
            if [ $? -ne 0 ] && [ -n "$MYPY_OUTPUT" ]; then
                ERRORS="$ERRORS\n❌ mypy failed:\n$MYPY_OUTPUT"
            fi
            break
        fi
    done
fi

# Run tests
if command -v pytest &> /dev/null && [ -d "tests" ]; then
    PYTEST_OUTPUT=$(pytest tests/ -v --tb=line 2>&1)
    if [ $? -ne 0 ]; then
        ERRORS="$ERRORS\n❌ pytest failed:\n$(echo "$PYTEST_OUTPUT" | tail -20)"
    fi
fi

if [ -n "$ERRORS" ]; then
    echo -e "🚫 COMMIT BLOCKED - Quality gates failed:\n$ERRORS" >&2
    exit 2  # Block the commit
fi

echo "✅ All quality gates passed"
exit 0
HOOKEOF
chmod +x .claude/hooks/pre-commit-check.sh

# Create .claude/settings.json with hooks
cat > .claude/settings.json << 'SETTINGSEOF'
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/session-start.sh",
            "timeout": 10
          }
        ]
      }
    ],
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/inject-context.sh",
            "timeout": 5
          }
        ]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "Write",
        "hooks": [
          {
            "type": "command",
            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/tdd-check.sh",
            "timeout": 5
          }
        ]
      },
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/pre-commit-check.sh",
            "timeout": 120
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/post-edit-lint.sh",
            "timeout": 30
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/stop-check.sh",
            "timeout": 10
          }
        ]
      }
    ],
    "PreCompact": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/pre-compact.sh",
            "timeout": 10
          }
        ]
      }
    ],
    "SessionEnd": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/session-end.sh",
            "timeout": 10
          }
        ]
      }
    ],
    "Setup": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/setup-init.sh",
            "timeout": 30
          }
        ]
      }
    ]
  }
}
SETTINGSEOF

# Create subagent files for specialized tasks
cat > .claude/agents/test-writer.md << 'AGENTEOF'
# Test Writer Subagent

Generate comprehensive pytest tests from a task description using Test-Driven Development (TDD).

## Purpose

This subagent implements the RED phase of TDD - writing tests BEFORE code exists. It generates tests based on the task description and expected behavior, not from existing implementation.

## Input

The subagent receives:
- **Task Description**: What the code should do
- **Task Title**: Name of the feature/function
- **Target File**: The file that will be implemented

## Output

Generate pytest test file with:
- Test file in `tests/` directory
- Test function names that describe expected behavior
- Multiple test cases covering edge cases
- Proper assertions

## Test Generation Guidelines

### 1. Analyze Task Description
Extract:
- Function/class names mentioned
- Input parameters and types
- Expected outputs
- Edge cases (empty input, None, boundaries)

### 2. Write Tests First (TDD RED Phase)
```python
import pytest
# Import will fail until implementation exists - that's expected in TDD

def test_function_normal_case():
    """Test normal operation."""
    result = function_to_implement(valid_input)
    assert result == expected_output

def test_function_edge_case():
    """Test edge case."""
    result = function_to_implement(edge_input)
    assert result == expected_edge_output

def test_function_error_case():
    """Test error handling."""
    with pytest.raises(ValueError):
        function_to_implement(invalid_input)
```

### 3. Coverage Targets
- Happy path (normal inputs)
- Edge cases (empty, None, boundaries)
- Error cases (invalid inputs)
- Type validation (wrong types)

## Tool Restrictions

This subagent can:
- **READ**: Existing files to understand context
- **WRITE**: Test files in tests/ directory

This subagent should NOT:
- **EXECUTE**: Do not run tests (that's quality-gate's job)
- Modify implementation files
AGENTEOF

cat > .claude/agents/code-reviewer.md << 'AGENTEOF'
# Code Reviewer Subagent

Review code for quality, security, and best practices. This is a READ-ONLY agent.

## Purpose

This subagent acts as a code reviewer, identifying issues and providing feedback without modifying any files. It catches problems before code is committed.

## Input

The subagent receives:
- **File Path**: Path to the file to review
- **Task Context**: What the code is supposed to do

## Output

Provide a structured code review with:
- Overall quality assessment
- Security issues (critical)
- Bugs and logic errors
- Code quality concerns
- Recommendations for improvement
- Approval decision (approve/reject)

## Review Checklist

### Security Issues (Critical - Block Commit)
- SQL injection vulnerabilities
- XSS vulnerabilities
- Command injection
- Hardcoded credentials or secrets
- Insecure cryptography
- Unsafe deserialization

### Bugs (High Priority)
- Logic errors
- Off-by-one errors
- Null/None reference errors
- Race conditions
- Resource leaks (files, connections)
- Unhandled exceptions

### Code Quality (Medium Priority)
- Missing type hints
- Poor naming conventions
- Excessive complexity (>10 cyclomatic)
- Missing error handling
- No documentation for public APIs
- Magic numbers/strings

### Performance (Low Priority)
- Inefficient algorithms
- Unnecessary loops
- Memory leaks
- N+1 query patterns

## Tool Restrictions

This subagent is **READ-ONLY**:
- **READ**: Can read any file for review
- **WRITE**: Cannot modify files
- **EXECUTE**: Cannot run commands

The reviewer provides feedback only. Fixes are applied by other agents.
AGENTEOF

cat > .claude/agents/quality-gate.md << 'AGENTEOF'
# Quality Gate Subagent

Run automated quality checks and report pass/fail status.

## Purpose

This subagent runs quality validation checks to ensure code meets quality standards before proceeding. It executes checks and reports results.

## Quality Gates

Run these checks in order:

### Gate 1: Type Check (mypy)
```bash
mypy <file_path> --ignore-missing-imports
```
- PASS: No type errors
- FAIL: Type errors found

### Gate 2: Run Tests (pytest)
```bash
pytest tests/ -v --tb=short
```
- PASS: All tests pass
- FAIL: Test failures

### Gate 3: Import Validation
Check that all imports resolve to existing modules:
- Verify imports exist in codebase
- Check against reference_map.json if available
- PASS: All imports valid
- FAIL: Undefined imports

### Gate 4: Lint Check (optional)
```bash
ruff check <file_path>
```
- PASS: No lint errors
- FAIL: Lint issues found

## Output Format

Report results as structured summary:

```markdown
## Quality Gate Results

### Gate 1: mypy Type Check
Status: PASS / FAIL
Output: [mypy output or "No errors"]

### Gate 2: pytest Tests
Status: PASS / FAIL
Results: X passed, Y failed
Failures: [List failed tests if any]

### Gate 3: Import Validation
Status: PASS / FAIL
Issues: [List invalid imports if any]

### Overall: ALL GATES PASSED / QUALITY FAILED
```

## Tool Restrictions

This subagent can:
- **READ**: Read files to check imports
- **EXECUTE**: Run mypy, pytest, ruff commands

This subagent should NOT:
- **WRITE**: Do not modify any files
- Apply fixes (that's fixer's job)

## Retry Logic

The orchestrating command (/next) handles retries:
1. Run quality-gate
2. If FAIL: spawn fixer subagent
3. Re-run quality-gate
4. Repeat up to MAX_RETRIES (3)
AGENTEOF

cat > .claude/agents/fixer.md << 'AGENTEOF'
# Fixer Subagent

Analyze errors and apply minimal, targeted fixes.

## Purpose

This subagent receives error reports from quality-gate and proposes/applies minimal fixes to resolve them. It makes the smallest changes necessary to pass quality gates.

## Input

The subagent receives:
- **Error Message**: The specific error to fix
- **File Path**: Path to the file with the error
- **Code Context**: Relevant code snippet
- **Stack Trace**: Optional stack trace for runtime errors

## Fix Strategy

### 1. Analyze the Error
- Read the error message carefully
- Identify the root cause
- Understand the context

### 2. Propose Minimal Fix
- Change only what's necessary
- Don't refactor unrelated code
- Preserve existing behavior
- Keep the fix targeted

### 3. Apply the Fix
- Edit the specific lines
- Verify the edit is correct
- Don't introduce new issues

## Common Fix Patterns

### Type Errors (mypy)
| Error | Fix |
|-------|-----|
| Missing type hints | Add type annotations |
| Incompatible types | Fix type mismatch |
| Missing return type | Add return annotation |

### Test Failures
| Error | Fix |
|-------|-----|
| AssertionError | Fix the implementation logic |
| ImportError | Fix import statement |
| AttributeError | Fix attribute access |

### Import Errors
| Error | Fix |
|-------|-----|
| ModuleNotFoundError | Fix module path |
| ImportError | Add missing export |
| Circular import | Restructure imports |

## Tool Restrictions

This subagent can:
- **READ**: Read files to analyze errors
- **WRITE**: Edit files to apply fixes

This subagent should NOT:
- **EXECUTE**: Do not run tests or commands (quality-gate does that)
- Make unnecessary changes
- Refactor working code

## Important Rules

1. **Minimal changes only** - Fix the specific error, nothing else
2. **Targeted edits** - Don't rewrite large sections
3. **One fix at a time** - Address errors incrementally
4. **Preserve behavior** - Don't change what works
5. **Document changes** - Explain what was fixed and why
AGENTEOF

# Create rules (modular, path-specific rule files)
cat > .claude/rules/workflow.md << 'RULEEOF'
# Workflow

## Task Execution (7 Steps)

1. Read previous handover for context
2. Create feature branch (`feature/<task-id>-description`)
3. Implement with TDD (write test first, then code)
4. Run quality gates (mypy, ruff, pytest — ALL must pass)
5. Create handover document
6. Commit, push, create PR
7. Next task

## Atomic Changes

- Each task targets ONE coherent logical change
- Target: source file + its tests (2-5 files typical)
- If >300 lines of new code, evaluate splitting

## Memory System

After significant changes, update memory files via `/sync`:
- `agent_memory/tasks_queue.json` — mark task complete
- `agent_memory/project_state.yaml` — new classes/functions
- `agent_memory/reference_map.json` — new exports
RULEEOF

cat > .claude/rules/quality-gates.md << 'RULEEOF'
# Quality Gates

ALL gates must pass before commit. No exceptions.

```bash
ruff check src/                      # Lint
ruff format src/ --check             # Format
mypy src/ --ignore-missing-imports   # Type check
pytest tests/ -v                     # Tests
```

## Retry Loop

If any gate fails: fix, re-run (max 3 attempts). After 3 failures, STOP and ask the user.

## Import Validation

- Only import symbols that exist in `reference_map.json`
- Never hallucinate APIs or function signatures
- Run `/sync` if reference_map is outdated
RULEEOF

cat > .claude/rules/git-workflow.md << 'RULEEOF'
# Git Workflow

## Branches

- Feature: `feature/<task-id>-description`
- Fix: `fix/<task-id>-description`
- Never commit directly to main

## Commits

- One commit per task, only after quality gates pass
- Format: `task-N: brief description`
- Include `Co-Authored-By: Claude <noreply@anthropic.com>` when AI-assisted

## Pull Requests

- Create PR with summary + test plan
- Wait for review before merging
RULEEOF

cat > .claude/rules/testing.md << 'RULEEOF'
---
paths:
  - "tests/**/*.py"
  - "src/**/*.py"
---

# Testing Rules

## TDD: Write Tests FIRST

1. Write failing test (RED)
2. Implement minimum code to pass (GREEN)
3. Refactor if needed

Every function MUST have a unit test. Every bug fix MUST have a regression test.

## Coverage

- Target: 80%+ unit test coverage
- Test happy path, edge cases, and error paths
- Use realistic inputs, not simplified data

## Test Patterns

```python
import pytest

def test_function_normal_case():
    """Test normal operation."""
    result = function(valid_input)
    assert result == expected

def test_function_edge_case():
    """Test boundary conditions."""
    assert function(None) is None
    assert function([]) == []

def test_function_error():
    """Test error handling."""
    with pytest.raises(ValueError):
        function(invalid_input)
```
RULEEOF

cat > .claude/rules/poc-workflow.md << 'RULEEOF'
---
paths:
  - "scripts/poc_*.py"
  - "scripts/demo_*.py"
  - "notebooks/**"
---

# POC / Prototype Workflow

Scripts in `scripts/` prefixed with `poc_` or `demo_` follow relaxed rules:

## Quality Gates (Reduced)

- mypy + ruff: MUST pass
- pytest: OPTIONAL (throwaway scripts don't need tests)
- TDD: OPTIONAL

## Rules

- Must NOT modify files in `src/` (use imports only)
- Must NOT be in `src/` directory
- Graduating to production requires full TDD reimplementation in `src/`
- Document purpose and usage in script docstring
RULEEOF

# Create skills (SKILL.md format with dynamic context injection)
cat > .claude/skills/boot/SKILL.md << 'SKILLEOF'
---
description: Load project context and show current tasks
---

Read the following files to boot into this project:

1. `agent_memory/method_of_working.md` - How to work on this project
2. `agent_memory/architecture.md` - System architecture and structure
3. `agent_memory/project_state.yaml` - Current codebase state
4. `agent_memory/tasks_queue.json` - Current and pending tasks
5. `agent_memory/reference_map.json` - Module exports and dependencies

## Current Git State

```
!`git branch --show-current && git log --oneline -5`
```

## Pending Handovers

```
!`ls -t agent_memory/handovers/ 2>/dev/null | head -3 || echo "No handovers yet"`
```

After reading all files, provide a structured summary:

## Boot Summary

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

---

Then ask: "What would you like to work on?"
SKILLEOF

cat > .claude/skills/next/SKILL.md << 'SKILLEOF'
---
description: Execute the next task in the queue with full quality gates
context: fork
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
  - Task
  - TodoWrite
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

### 2. Read Previous Handover
- Check `agent_memory/handovers/` for context from previous task

### 3. Execute with TDD
```
1. Write failing test (RED)
2. Implement minimum code to pass (GREEN)
3. Run quality gates
4. If fail: fix and retry (max 3 attempts)
```

### 4. Quality Gates (ALL must pass)
```bash
ruff check src/
mypy <file_path> --ignore-missing-imports
pytest tests/ -v
```

### 5. After Quality Gates Pass
- Update `project_state.yaml` and `reference_map.json`
- Mark task as "completed" in `tasks_queue.json`

### 6. Create Handover
Save to `agent_memory/handovers/handover_<task-id>.md`:
```markdown
## Task [STATUS]: [title]
### Status: SUCCESS | PARTIAL | FAILED | BLOCKED
### What Was Done
### Files Modified
### Quality Results
### Next Steps
```

### 7. Commit
```bash
git add .
git commit -m "task-N: [task title]"
```

### 8. Report
Summarize what was done and show next task.
SKILLEOF

cat > .claude/skills/handover/SKILL.md << 'SKILLEOF'
---
description: Auto-generate handover document from current work
---

Generate a handover document from the current task's work.

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

## Instructions

Using the gathered context above, generate a handover document with this structure:

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

If the task is complete, also mark it as "completed" in `agent_memory/tasks_queue.json`.
SKILLEOF

cat > .claude/skills/review/SKILL.md << 'SKILLEOF'
---
description: Pre-PR review checklist — validates code before creating a pull request
context: fork
allowed-tools:
  - Read
  - Bash
  - Glob
  - Grep
---

Run a pre-PR review checklist on the current branch.

## Branch Info
```
!`echo "Branch: $(git branch --show-current)"; echo "Base: main"; git log --oneline main..HEAD 2>/dev/null || echo "No commits ahead of main"`
```

## Changed Files
```
!`git diff --name-status main...HEAD 2>/dev/null || git diff --name-status HEAD~1 2>/dev/null || echo "No changes found"`
```

## Review Checklist

For each changed file, check:

### 1. Security (CRITICAL)
- [ ] No hardcoded secrets, API keys, or credentials
- [ ] No SQL injection, XSS, or command injection vulnerabilities
- [ ] No unsafe deserialization
- [ ] Proper input validation at boundaries

### 2. Code Quality
- [ ] Type hints on all function signatures
- [ ] No unused imports or variables
- [ ] Functions under 30 lines (recommend)
- [ ] No magic numbers/strings
- [ ] Error handling for external calls

### 3. Testing
- [ ] Every new function has a unit test
- [ ] Edge cases covered (None, empty, boundary)
- [ ] Bug fixes have regression tests
- [ ] Tests are independent (no shared state)

### 4. Quality Gates
Run and report results:
```bash
ruff check src/
mypy src/ --ignore-missing-imports
pytest tests/ -v
```

### 5. Documentation
- [ ] Public functions have docstrings
- [ ] Architecture changes reflected in `agent_memory/architecture.md`
- [ ] Reference map updated (`/sync` run)

## Output

Provide a structured review:
```
## Pre-PR Review: [branch name]

### Commits: [count]
### Files Changed: [count]

### Security: PASS / FAIL
[Issues if any]

### Code Quality: PASS / WARNINGS / FAIL
[Issues if any]

### Testing: PASS / FAIL
[Missing tests if any]

### Quality Gates: PASS / FAIL
- ruff: [result]
- mypy: [result]
- pytest: [X/Y passed]

### Overall: READY / NOT READY
[Summary and recommendations]
```
SKILLEOF

# Create new hooks (Stop, UserPromptSubmit, SessionEnd, PreCompact, Setup)
cat > .claude/hooks/stop-check.sh << 'HOOKEOF'
#!/bin/bash
# Stop hook: Validate work is complete before Claude stops
# Exit 0 = allow stop, Exit 2 = block stop (stderr shown to Claude)

cd "$CLAUDE_PROJECT_DIR" 2>/dev/null || exit 0

WARNINGS=""

# Check if there's an in-progress task that hasn't been completed
if [ -f "agent_memory/tasks_queue.json" ]; then
    IN_PROGRESS=$(python3 -c "
import json
data = json.load(open('agent_memory/tasks_queue.json'))
tasks = [t for t in data.get('backlog', []) if t.get('status') == 'in_progress']
if tasks: print(f\"{tasks[0]['id']}: {tasks[0]['title']}\")
" 2>/dev/null)

    if [ -n "$IN_PROGRESS" ]; then
        WARNINGS="$WARNINGS\n- Task still in_progress: $IN_PROGRESS"
    fi
fi

# Check if there are uncommitted changes
if git diff --quiet 2>/dev/null && git diff --cached --quiet 2>/dev/null; then
    : # Clean working tree
else
    WARNINGS="$WARNINGS\n- Uncommitted changes in working tree"
fi

# Check if handover was created for the current task
if [ -n "$IN_PROGRESS" ]; then
    TASK_ID=$(echo "$IN_PROGRESS" | cut -d: -f1 | xargs)
    HANDOVER="agent_memory/handovers/handover_${TASK_ID}.md"
    if [ ! -f "$HANDOVER" ]; then
        WARNINGS="$WARNINGS\n- No handover document for $TASK_ID"
    fi
fi

if [ -n "$WARNINGS" ]; then
    echo -e "Before stopping, please address:\n$WARNINGS\n\nRun /handover to create a handover document, then mark the task complete." >&2
    exit 2
fi

exit 0
HOOKEOF
chmod +x .claude/hooks/stop-check.sh

cat > .claude/hooks/inject-context.sh << 'HOOKEOF'
#!/bin/bash
# UserPromptSubmit hook: Auto-inject current task context into every prompt
# stdout is added to Claude's context

cd "$CLAUDE_PROJECT_DIR" 2>/dev/null || exit 0

# Show current task context (lightweight — no heavy file reads)
if [ -f "agent_memory/tasks_queue.json" ]; then
    python3 -c "
import json
data = json.load(open('agent_memory/tasks_queue.json'))
current = [t for t in data.get('backlog', []) if t.get('status') == 'in_progress']
pending = [t for t in data.get('backlog', []) if t.get('status') == 'pending']
if current:
    t = current[0]
    print(f\"[Active: {t['id']} — {t['title']}]\")
elif pending:
    t = pending[0]
    print(f\"[Next: {t['id']} — {t['title']}]\")
" 2>/dev/null
fi

exit 0
HOOKEOF
chmod +x .claude/hooks/inject-context.sh

cat > .claude/hooks/session-end.sh << 'HOOKEOF'
#!/bin/bash
# SessionEnd hook: Auto-save session state snapshot
# Runs when Claude session ends

cd "$CLAUDE_PROJECT_DIR" 2>/dev/null || exit 0

# Save a lightweight state snapshot
STATE_DIR="agent_memory/.session_state"
mkdir -p "$STATE_DIR"

# Record session timestamp and branch
{
    echo "session_end: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "branch: $(git branch --show-current 2>/dev/null || echo 'unknown')"
    echo "uncommitted_changes: $(git status --porcelain 2>/dev/null | wc -l | xargs)"
    echo "last_commit: $(git log --oneline -1 2>/dev/null || echo 'none')"
} > "$STATE_DIR/last_session.yaml" 2>/dev/null

# Record task queue status
if [ -f "agent_memory/tasks_queue.json" ]; then
    python3 -c "
import json
data = json.load(open('agent_memory/tasks_queue.json'))
tasks = data.get('backlog', [])
completed = sum(1 for t in tasks if t.get('status') == 'completed')
in_progress = sum(1 for t in tasks if t.get('status') == 'in_progress')
pending = sum(1 for t in tasks if t.get('status') == 'pending')
print(f'tasks_completed: {completed}')
print(f'tasks_in_progress: {in_progress}')
print(f'tasks_pending: {pending}')
in_prog = [t for t in tasks if t.get('status') == 'in_progress']
if in_prog:
    print(f'current_task: {in_prog[0][\"id\"]}: {in_prog[0][\"title\"]}')
" >> "$STATE_DIR/last_session.yaml" 2>/dev/null
fi

exit 0
HOOKEOF
chmod +x .claude/hooks/session-end.sh

cat > .claude/hooks/pre-compact.sh << 'HOOKEOF'
#!/bin/bash
# PreCompact hook: Preserve critical context before conversation compaction
# stdout is included in the compacted summary

cd "$CLAUDE_PROJECT_DIR" 2>/dev/null || exit 0

echo "## Critical Context (Preserved from Pre-Compact)"
echo ""

# Current task
if [ -f "agent_memory/tasks_queue.json" ]; then
    python3 -c "
import json
data = json.load(open('agent_memory/tasks_queue.json'))
current = [t for t in data.get('backlog', []) if t.get('status') == 'in_progress']
pending = [t for t in data.get('backlog', []) if t.get('status') == 'pending']
if current:
    t = current[0]
    print(f'### Current Task: {t[\"id\"]} — {t[\"title\"]}')
    if t.get('description'): print(f'Description: {t[\"description\"]}')
    if t.get('files'): print(f'Files: {\", \".join(t[\"files\"])}')
elif pending:
    t = pending[0]
    print(f'### Next Task: {t[\"id\"]} — {t[\"title\"]}')
print(f'Completed: {sum(1 for t in data.get(\"backlog\",[]) if t.get(\"status\")==\"completed\")} | Pending: {len(pending)}')
" 2>/dev/null
fi

echo ""

# Current branch and recent commits
echo "### Git State"
echo "Branch: $(git branch --show-current 2>/dev/null || echo 'unknown')"
git log --oneline -3 2>/dev/null | while read line; do echo "  $line"; done

echo ""

# Uncommitted changes summary
CHANGES=$(git diff --stat 2>/dev/null)
if [ -n "$CHANGES" ]; then
    echo "### Uncommitted Changes"
    echo "$CHANGES"
fi

# Most recent handover
LATEST_HANDOVER=$(ls -t agent_memory/handovers/*.md 2>/dev/null | head -1)
if [ -n "$LATEST_HANDOVER" ]; then
    echo ""
    echo "### Latest Handover"
    head -20 "$LATEST_HANDOVER"
fi

exit 0
HOOKEOF
chmod +x .claude/hooks/pre-compact.sh

cat > .claude/hooks/setup-init.sh << 'HOOKEOF'
#!/bin/bash
# Setup hook: One-time initialization when Claude Code is first used in this project
# Runs with --init flag, not every session

cd "$CLAUDE_PROJECT_DIR" 2>/dev/null || exit 0

SETUP_LOG=""

# Install pre-commit hooks if config exists
if [ -f ".pre-commit-config.yaml" ] && command -v pre-commit &> /dev/null; then
    if [ ! -f ".git/hooks/pre-commit" ] || ! grep -q "pre-commit" ".git/hooks/pre-commit" 2>/dev/null; then
        pre-commit install 2>/dev/null
        SETUP_LOG="$SETUP_LOG\n- Installed pre-commit hooks"
    fi
fi

# Create agent_memory directories if missing
for dir in agent_memory agent_memory/handovers; do
    if [ ! -d "$dir" ]; then
        mkdir -p "$dir"
        SETUP_LOG="$SETUP_LOG\n- Created $dir/"
    fi
done

# Ensure hook scripts are executable
for hook in .claude/hooks/*.sh; do
    if [ -f "$hook" ] && [ ! -x "$hook" ]; then
        chmod +x "$hook"
        SETUP_LOG="$SETUP_LOG\n- Made $hook executable"
    fi
done

if [ -n "$SETUP_LOG" ]; then
    echo -e "Setup completed:$SETUP_LOG"
else
    echo "Setup: everything already configured"
fi

exit 0
HOOKEOF
chmod +x .claude/hooks/setup-init.sh

echo "✅ Created CLAUDE.md (concise entry point with @imports)"
echo "✅ Created agent_memory/ with memory files:"
echo "   - method_of_working.md, architecture.md, project_state.yaml"
echo "   - tasks_queue.json, reference_map.json"
echo "✅ Created .claude/rules/ (modular, path-specific rules):"
echo "   - workflow.md - 7-step task execution"
echo "   - quality-gates.md - Gate requirements and retry logic"
echo "   - git-workflow.md - Branch naming, commit format"
echo "   - testing.md - TDD rules (loads for tests/** and src/**)"
echo "   - poc-workflow.md - Relaxed POC rules (loads for scripts/poc_*)"
echo "✅ Created .claude/skills/ (SKILL.md with dynamic context):"
echo "   - /boot - Load context with live git state"
echo "   - /next - Execute task in forked context"
echo "   - /handover - Auto-generate handover from git diff"
echo "   - /review - Pre-PR checklist in forked context"
echo "✅ Created .claude/commands/ (legacy slash commands):"
echo "   - /plan, /status, /sync, /import-plan"
echo "✅ Created .claude/agents/ (specialized subagents):"
echo "   - test-writer, code-reviewer, quality-gate, fixer"
echo "✅ Created .claude/hooks/ (9 lifecycle hooks):"
echo "   - SessionStart: load task context"
echo "   - UserPromptSubmit: inject active task"
echo "   - PreToolUse (Write): TDD enforcement"
echo "   - PreToolUse (Bash): commit gate"
echo "   - PostToolUse (Write|Edit): lint check"
echo "   - Stop: require handover before stopping"
echo "   - PreCompact: preserve critical context"
echo "   - SessionEnd: save state snapshot"
echo "   - Setup: one-time init (pre-commit install)"
echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Update agent_memory/architecture.md with your project details"
echo "2. Start Claude Code and run: /boot"
echo "3. Plan your work with: /plan <your goal>"
echo ""
echo "Or use Repoprompt workflow:"
echo "1. Run Discovery prompt in Repoprompt"
echo "2. Run Plan prompt in Repoprompt"
echo "3. Paste plan into Claude Code and run: /import-plan"
echo ""
