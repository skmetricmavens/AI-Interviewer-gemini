#!/bin/bash
# PostToolUse on Write|Edit: BLOCK if ruff or mypy fails on the edited file
# Exit code 2 = BLOCK (forces immediate fix), 0 = allow
#
# This ensures lint/type issues are fixed per-file, not accumulated.

FILE_PATH="$TOOL_INPUT_file_path"

# Skip non-Python files
if [[ ! "$FILE_PATH" =~ \.py$ ]]; then
    exit 0
fi

# Skip test files for mypy (test fixtures can be loosely typed)
IS_TEST=false
if [[ "$FILE_PATH" =~ ^tests/ ]] || [[ "$FILE_PATH" =~ test_.* ]]; then
    IS_TEST=true
fi

cd "$CLAUDE_PROJECT_DIR" 2>/dev/null || exit 0
ERRORS=""

# Check ruff (always, including tests)
if command -v ruff &> /dev/null; then
    RUFF_OUTPUT=$(ruff check "$FILE_PATH" 2>&1)
    if [ $? -ne 0 ]; then
        ERRORS="$ERRORS\nruff lint failed:\n$RUFF_OUTPUT"
    fi

    # Also check formatting
    RUFF_FMT=$(ruff format "$FILE_PATH" --check 2>&1)
    if [ $? -ne 0 ]; then
        ERRORS="$ERRORS\nruff format failed: $FILE_PATH needs formatting"
    fi
fi

# Check mypy (skip for test files)
if [ "$IS_TEST" = false ] && command -v mypy &> /dev/null; then
    MYPY_OUTPUT=$(mypy "$FILE_PATH" --ignore-missing-imports 2>&1)
    if [ $? -ne 0 ]; then
        MYPY_ERRORS=$(echo "$MYPY_OUTPUT" | grep -v "^Success" | head -10)
        if [ -n "$MYPY_ERRORS" ]; then
            ERRORS="$ERRORS\nmypy failed:\n$MYPY_ERRORS"
        fi
    fi
fi

if [ -n "$ERRORS" ]; then
    echo -e "BLOCKED: Fix quality issues in $FILE_PATH before continuing:\n$ERRORS\n\nUse the fixer sub-agent for targeted fixes, then quality-gate sub-agent to verify. Do not bypass sub-agents." >&2
    exit 2
fi

exit 0
