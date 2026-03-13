#!/bin/bash
# PreToolUse on Write|Edit: Enforce workflow before any source code changes
# Exit code 2 = BLOCK, 0 = allow
#
# Blocks:
# 1. Writing/editing source files on main/master branch
# 2. Writing/editing source files with no task in_progress

FILE_PATH="$TOOL_INPUT_file_path"

cd "$CLAUDE_PROJECT_DIR" 2>/dev/null || exit 0

# Skip non-source files (allow editing configs, tests, memory, docs freely)
if [[ ! "$FILE_PATH" =~ ^src/ ]] && [[ ! "$FILE_PATH" =~ ^app/ ]] && [[ ! "$FILE_PATH" =~ ^lib/ ]]; then
    exit 0
fi

# Skip if file path is empty
if [ -z "$FILE_PATH" ]; then
    exit 0
fi

# --- Check 1: Block source edits on main/master ---
BRANCH=$(git branch --show-current 2>/dev/null)
if [ "$BRANCH" = "main" ] || [ "$BRANCH" = "master" ]; then
    echo "BLOCKED: Cannot edit source files on $BRANCH. Create a feature/fix branch first:" >&2
    echo "  git checkout -b fix/<description>" >&2
    echo "  git checkout -b feature/<task-id>-<description>" >&2
    exit 2
fi

# --- Check 2: Block source edits with no task in_progress ---
if [ -f "agent_memory/tasks_queue.json" ]; then
    HAS_ACTIVE_TASK=$(python3 -c "
import json
data = json.load(open('agent_memory/tasks_queue.json'))
tasks = [t for t in data.get('backlog', []) if t.get('status') == 'in_progress']
print('yes' if tasks else 'no')
" 2>/dev/null)

    if [ "$HAS_ACTIVE_TASK" = "no" ]; then
        echo "BLOCKED: No task is in_progress. Before editing source files:" >&2
        echo "  1. Use /fix to decompose errors into atomic tasks, or" >&2
        echo "  2. Use /plan to create tasks, or" >&2
        echo "  3. Use /next to start the next pending task" >&2
        echo "  Each task must be tracked in tasks_queue.json before coding begins." >&2
        exit 2
    fi
fi

exit 0
