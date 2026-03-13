#!/bin/bash
# UserPromptSubmit hook: Inject workflow state into every prompt
# stdout is added to Claude's context

cd "$CLAUDE_PROJECT_DIR" 2>/dev/null || exit 0

# Show current task context
if [ -f "agent_memory/tasks_queue.json" ]; then
    python3 -c "
import json
data = json.load(open('agent_memory/tasks_queue.json'))
current = [t for t in data.get('backlog', []) if t.get('status') == 'in_progress']
pending = [t for t in data.get('backlog', []) if t.get('status') == 'pending']
if current:
    t = current[0]
    print(f'[Active: {t[\"id\"]} — {t[\"title\"]}]')
elif pending:
    t = pending[0]
    print(f'[Next: {t[\"id\"]} — {t[\"title\"]} | Run /next to start]')
else:
    print('[No tasks queued | Use /plan or /fix to create tasks before coding]')
" 2>/dev/null
fi

# Show branch state
BRANCH=$(git branch --show-current 2>/dev/null)
if [ -n "$BRANCH" ]; then
    echo "[Branch: $BRANCH]"
fi

# WARN: on main with changes
if [ "$BRANCH" = "main" ] || [ "$BRANCH" = "master" ]; then
    CHANGES=$(git status --porcelain 2>/dev/null | head -1)
    if [ -n "$CHANGES" ]; then
        echo "[WORKFLOW VIOLATION: On $BRANCH with uncommitted changes. Create a feature/fix branch immediately.]"
    fi
fi

# WARN: no active task but on a feature branch (forgot to mark in_progress)
if [ -f "agent_memory/tasks_queue.json" ]; then
    HAS_ACTIVE=$(python3 -c "
import json
data = json.load(open('agent_memory/tasks_queue.json'))
tasks = [t for t in data.get('backlog', []) if t.get('status') == 'in_progress']
print('yes' if tasks else 'no')
" 2>/dev/null)

    if [ "$HAS_ACTIVE" = "no" ] && [[ "$BRANCH" == feature/* || "$BRANCH" == fix/* ]]; then
        echo "[REMINDER: On branch $BRANCH but no task is in_progress. Mark a task as in_progress in tasks_queue.json.]"
    fi
fi

exit 0
