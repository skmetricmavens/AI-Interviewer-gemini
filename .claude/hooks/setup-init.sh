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
