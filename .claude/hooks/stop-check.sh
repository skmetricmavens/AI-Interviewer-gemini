#!/bin/bash
# Stop hook: Validate work is complete before Claude stops
# Exit 0 = allow stop, Exit 2 = block stop (stderr shown to Claude)

cd "$CLAUDE_PROJECT_DIR" 2>/dev/null || exit 0

BLOCKERS=""
WARNINGS=""

# Check if there's an in-progress task
if [ -f "agent_memory/tasks_queue.json" ]; then
    IN_PROGRESS=$(python3 -c "
import json
data = json.load(open('agent_memory/tasks_queue.json'))
tasks = [t for t in data.get('backlog', []) if t.get('status') == 'in_progress']
if tasks: print(f\"{tasks[0]['id']}: {tasks[0]['title']}\")
" 2>/dev/null)
fi

# Check if there are uncommitted changes (BLOCKER)
if git diff --quiet 2>/dev/null && git diff --cached --quiet 2>/dev/null; then
    : # Clean working tree
else
    BLOCKERS="$BLOCKERS\n- Uncommitted changes in working tree"
fi

# Check handover for in-progress task
if [ -n "$IN_PROGRESS" ]; then
    TASK_ID=$(echo "$IN_PROGRESS" | cut -d: -f1 | xargs)
    HANDOVER="agent_memory/handovers/handover_${TASK_ID}.md"
    if [ ! -f "$HANDOVER" ]; then
        BLOCKERS="$BLOCKERS\n- No handover document for $TASK_ID"
    else
        WARNINGS="$WARNINGS\n- Task still in_progress: $IN_PROGRESS (handover exists, safe to resume)"
    fi
fi

# Check if memory files have uncommitted changes or if source files changed
# without a corresponding memory update. Uses git diff (content-based) instead
# of filesystem timestamps to avoid false positives after merges/checkouts.
if [ -f "agent_memory/project_state.yaml" ] && [ -f "agent_memory/reference_map.json" ]; then
    # Only flag if source files have uncommitted changes but memory files don't
    SRC_CHANGED=$(git diff --name-only -- 'src/*.py' 'src/**/*.py' 2>/dev/null | head -1)
    MEM_CHANGED=$(git diff --name-only -- 'agent_memory/reference_map.json' 'agent_memory/project_state.yaml' 2>/dev/null | head -1)
    if [ -n "$SRC_CHANGED" ] && [ -z "$MEM_CHANGED" ]; then
        WARNINGS="$WARNINGS\n- Source files modified but memory files unchanged. Consider running /sync."
    fi
fi

# Blockers prevent stop (exit 2), warnings just inform (exit 0)
if [ -n "$BLOCKERS" ]; then
    echo -e "Before stopping, please address:\n$BLOCKERS\n\nRun /handover to create a handover document, then commit changes." >&2
    exit 2
fi

if [ -n "$WARNINGS" ]; then
    echo -e "Note:\n$WARNINGS" >&2
fi

exit 0
