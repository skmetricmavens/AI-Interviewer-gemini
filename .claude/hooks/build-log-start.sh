#!/bin/bash
# SessionStart hook: Record build session start time and commit
# Used by build-log-end.sh to compute build duration and diff

cd "$CLAUDE_PROJECT_DIR" 2>/dev/null || exit 0

BUILD_LOG_DIR="agent_memory/.build_logs"
mkdir -p "$BUILD_LOG_DIR"

# Record session start time
date -u +%Y-%m-%dT%H:%M:%SZ > "$BUILD_LOG_DIR/.session_start_time"

# Record starting commit
git rev-parse --short HEAD > "$BUILD_LOG_DIR/.session_start_commit" 2>/dev/null || echo "none" > "$BUILD_LOG_DIR/.session_start_commit"

# Record branch
git branch --show-current > "$BUILD_LOG_DIR/.session_branch" 2>/dev/null || echo "unknown" > "$BUILD_LOG_DIR/.session_branch"

exit 0
