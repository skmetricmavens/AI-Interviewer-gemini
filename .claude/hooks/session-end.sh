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
