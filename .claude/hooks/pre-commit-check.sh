#!/bin/bash
# PreToolUse on Bash: Block git commit if quality gates fail
# Exit code 2 = block the commit

COMMAND="$TOOL_INPUT_command"

# Only check git commit commands
if [[ ! "$COMMAND" =~ ^git\ commit ]]; then
    exit 0
fi

cd "$CLAUDE_PROJECT_DIR" 2>/dev/null || exit 0
ERRORS=""

# Run ruff
if command -v ruff &> /dev/null; then
    for dir in src/ .; do
        if [ -d "$dir" ]; then
            RUFF_OUTPUT=$(ruff check "$dir" 2>&1)
            if [ $? -ne 0 ]; then
                ERRORS="$ERRORS\nruff check failed:\n$RUFF_OUTPUT"
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
                ERRORS="$ERRORS\nmypy failed:\n$MYPY_OUTPUT"
            fi
            break
        fi
    done
fi

# Run tests
if command -v pytest &> /dev/null && [ -d "tests" ]; then
    PYTEST_OUTPUT=$(pytest tests/ -v --tb=line 2>&1)
    if [ $? -ne 0 ]; then
        ERRORS="$ERRORS\npytest failed:\n$(echo "$PYTEST_OUTPUT" | tail -20)"
    fi
fi

# Block commits on main — must use feature/fix branch
BRANCH=$(git branch --show-current 2>/dev/null)
if [ "$BRANCH" = "main" ] || [ "$BRANCH" = "master" ]; then
    echo "COMMIT BLOCKED: Cannot commit directly to $BRANCH. Create a feature or fix branch first." >&2
    exit 2
fi

if [ -n "$ERRORS" ]; then
    echo -e "COMMIT BLOCKED - Quality gates failed:\n$ERRORS\n\nUse the fixer sub-agent for targeted fixes, then quality-gate sub-agent to verify." >&2
    exit 2  # Block the commit
fi

echo "All quality gates passed"
exit 0
