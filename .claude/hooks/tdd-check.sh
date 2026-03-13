#!/bin/bash
# PreToolUse on Write: Enforce TDD - test file should exist or be created first
# Exit code 2 = block, 0 = allow

FILE_PATH="$TOOL_INPUT_file_path"

cd "$CLAUDE_PROJECT_DIR" 2>/dev/null || exit 0

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
    echo '{"continue": true, "systemMessage": "TDD: No tests/ directory. Create tests first!"}'
    exit 0  # Warning only for new projects
fi

# Warn but don't block (some files genuinely don't need tests)
echo "{\"continue\": true, \"systemMessage\": \"TDD Reminder: No test found for ${BASENAME}.py. Write test first! Expected: ${TEST_FILE}\"}"
exit 0
