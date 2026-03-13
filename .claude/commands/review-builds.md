Analyze recent build logs and identify patterns.

Read:
1. `agent_memory/.build_logs/index.json` — list of all build logs
2. The 5 most recent build log JSON files from `agent_memory/.build_logs/`

## Build Analysis Report

For each recent build, extract:
- **Build ID**, **Branch**, **Date**
- **Tasks**: attempted / completed / failed
- **Quality Pass Rate**: percentage of quality gates that passed
- **Duration**: if available

### Trend Analysis

Compare across builds:

1. **Success Rate Trend** — Is the success rate improving, stable, or declining?
2. **Quality Gate Bottlenecks** — Which gates fail most often? (pytest, mypy, ruff)
3. **Context Deterioration** — Do tasks later in a build fail more than early ones? (look at per-task quality rates)
4. **Retry Effectiveness** — When tasks are retried, do they succeed? Or are retries wasting effort?
5. **Common Failure Modes** — What error types keep recurring?

### Recommendations

Based on the patterns found, provide actionable recommendations:
- If quality is declining: suggest what to fix
- If a specific gate always fails: suggest focusing on that area
- If context deterioration is detected: suggest more frequent context resets or smaller task batches
- If retries are ineffective: suggest different fix strategies

### Output Format

```
## Build History (Last 5)

| Build | Date | Branch | Tasks | Pass Rate | Duration |
|-------|------|--------|-------|-----------|----------|
| ... | ... | ... | X/Y | Z% | Nm |

## Trends
- Success rate: [improving/stable/declining]
- Quality bottleneck: [gate name]
- Context deterioration: [none/mild/significant]

## Top Recommendations
1. [Most impactful recommendation]
2. [Second recommendation]
3. [Third recommendation]
```

If no build logs exist yet, inform the user that build logs will be generated after completing tasks. Suggest running `/next` to execute a task.
