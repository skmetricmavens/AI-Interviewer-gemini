#!/bin/bash
# SessionStart: Inject key context at session start
# Outputs context that gets added to Claude's initial prompt

cd "$CLAUDE_PROJECT_DIR" 2>/dev/null || exit 0

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

# Reminder of key workflow rules
echo "### Workflow Rules"
echo "- ALL changes require: feature branch + task in tasks_queue.json"
echo "- TDD: write test FIRST, then implement"
echo "- Use sub-agents: test-writer, fixer, quality-gate, code-reviewer"
echo "- Errors: decompose into atomic tasks with /fix before coding"
echo "- After each task: run /handover (updates ALL memory files)"
echo "- Quality gates: ruff, mypy, pytest MUST pass before /commit"
echo "- Never commit to main — always branch, PR, merge"
echo ""
echo "### Progressive Disclosure"
echo "- reference_map.json: defer until writing code"
echo "- architecture.md: defer until structural changes"
echo "- Delegate heavy work to sub-agents to preserve main context"
echo ""
echo "Run /boot for full context, /next to start task, /fix to decompose errors"

exit 0
