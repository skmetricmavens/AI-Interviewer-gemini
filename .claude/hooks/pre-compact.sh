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
