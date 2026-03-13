#!/bin/bash
# PostToolUse hook (Bash): Log quality gate results as JSONL
# Detects pytest, mypy, ruff commands and records pass/fail

cd "$CLAUDE_PROJECT_DIR" 2>/dev/null || exit 0

# Read tool input from stdin
INPUT=$(cat)

# Extract the command that was run
COMMAND=$(echo "$INPUT" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(data.get('tool_input', {}).get('command', ''))
except Exception:
    print('')
" 2>/dev/null)

# Extract exit code
EXIT_CODE=$(echo "$INPUT" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(data.get('tool_result', {}).get('exitCode', -1))
except Exception:
    print('-1')
" 2>/dev/null)

# Only log quality-related commands
case "$COMMAND" in
    *pytest*|*mypy*|*ruff\ check*|*ruff\ format*)
        ;;
    *)
        exit 0
        ;;
esac

# Determine gate name
GATE_NAME="unknown"
case "$COMMAND" in
    *pytest*)  GATE_NAME="pytest" ;;
    *mypy*)    GATE_NAME="mypy" ;;
    *ruff\ format*) GATE_NAME="ruff_format" ;;
    *ruff\ check*)  GATE_NAME="ruff_check" ;;
esac

# Determine pass/fail
PASSED="false"
if [ "$EXIT_CODE" = "0" ]; then
    PASSED="true"
fi

# Append to JSONL file
BUILD_LOG_DIR="agent_memory/.build_logs"
mkdir -p "$BUILD_LOG_DIR"

TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)
echo "{\"gate_name\":\"${GATE_NAME}\",\"passed\":${PASSED},\"timestamp\":\"${TIMESTAMP}\",\"command\":\"${COMMAND}\"}" >> "$BUILD_LOG_DIR/.session_quality_gates.jsonl"

exit 0
