#!/bin/bash
# SessionEnd hook: Assemble build log JSON from session data
# Reads start time, task queue, quality gate results, and git state

cd "$CLAUDE_PROJECT_DIR" 2>/dev/null || exit 0

BUILD_LOG_DIR="agent_memory/.build_logs"

# Check if session was tracked
if [ ! -f "$BUILD_LOG_DIR/.session_start_time" ]; then
    exit 0
fi

START_TIME=$(cat "$BUILD_LOG_DIR/.session_start_time" 2>/dev/null || echo "")
START_COMMIT=$(cat "$BUILD_LOG_DIR/.session_start_commit" 2>/dev/null || echo "none")
BRANCH=$(cat "$BUILD_LOG_DIR/.session_branch" 2>/dev/null || echo "unknown")
END_TIME=$(date -u +%Y-%m-%dT%H:%M:%SZ)
FINAL_COMMIT=$(git rev-parse --short HEAD 2>/dev/null || echo "none")

# Generate build ID
BUILD_ID="build_$(date -u +%Y%m%d_%H%M%S)_${BRANCH}"

# Assemble build log using Python for JSON handling
python3 -c "
import json, os
from datetime import datetime
from pathlib import Path

build_dir = Path('$BUILD_LOG_DIR')
build_id = '${BUILD_ID}'

# Parse task queue for task stats
tasks_completed = 0
tasks_failed = 0
tasks_attempted = 0
task_executions = []

tasks_file = Path('agent_memory/tasks_queue.json')
if tasks_file.exists():
    try:
        data = json.load(open(tasks_file))
        for task in data.get('backlog', []):
            status = task.get('status', 'pending')
            if status == 'completed':
                tasks_completed += 1
                tasks_attempted += 1
                task_executions.append({
                    'task_id': task.get('id', ''),
                    'task_title': task.get('title', ''),
                    'status': 'completed',
                })
            elif status == 'failed':
                tasks_failed += 1
                tasks_attempted += 1
                task_executions.append({
                    'task_id': task.get('id', ''),
                    'task_title': task.get('title', ''),
                    'status': 'failed',
                })
    except Exception:
        pass

# Parse quality gate JSONL if it exists
quality_checks = 0
quality_passes = 0
quality_gates_file = build_dir / '.session_quality_gates.jsonl'
if quality_gates_file.exists():
    try:
        for line in open(quality_gates_file):
            line = line.strip()
            if not line:
                continue
            entry = json.loads(line)
            quality_checks += 1
            if entry.get('passed', False):
                quality_passes += 1
    except Exception:
        pass

quality_pass_rate = quality_passes / quality_checks if quality_checks > 0 else 0.0

# Build the log entry
build_log = {
    'build_id': build_id,
    'started_at': '${START_TIME}',
    'ended_at': '${END_TIME}',
    'branch': '${BRANCH}',
    'initial_commit': '${START_COMMIT}',
    'final_commit': '${FINAL_COMMIT}',
    'tasks_attempted': tasks_attempted,
    'tasks_completed': tasks_completed,
    'tasks_failed': tasks_failed,
    'total_quality_checks': quality_checks,
    'total_quality_passes': quality_passes,
    'quality_pass_rate': quality_pass_rate,
    'task_executions': task_executions,
}

# Write build log
log_file = build_dir / f'{build_id}.json'
with open(log_file, 'w') as f:
    json.dump(build_log, f, indent=2)

# Update index
index_file = build_dir / 'index.json'
index = []
if index_file.exists():
    try:
        index = json.load(open(index_file))
    except Exception:
        index = []

index.append({
    'build_id': build_id,
    'started_at': '${START_TIME}',
    'branch': '${BRANCH}',
    'tasks_completed': tasks_completed,
    'tasks_failed': tasks_failed,
    'quality_pass_rate': quality_pass_rate,
})

with open(index_file, 'w') as f:
    json.dump(index, f, indent=2)
" 2>/dev/null

# Cleanup session temp files
rm -f "$BUILD_LOG_DIR/.session_start_time"
rm -f "$BUILD_LOG_DIR/.session_start_commit"
rm -f "$BUILD_LOG_DIR/.session_branch"
rm -f "$BUILD_LOG_DIR/.session_quality_gates.jsonl"

exit 0
