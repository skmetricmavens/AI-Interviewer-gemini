# Project Context

## Quick Start
Run `/boot` to load project context and see current tasks.

## Bash Commands
```bash
pytest tests/ -v              # Run all tests
mypy src/ --ignore-missing-imports  # Type check
ruff check src/               # Lint check
```

## Definition of Done

A task is complete when ALL of the following are true:

1. **Tests pass** — `pytest tests/ -v` exits clean (80%+ unit coverage)
2. **Types pass** — `mypy src/ --ignore-missing-imports` reports no errors
3. **Lint passes** — `ruff check src/` and `ruff format src/ --check` report no issues
4. **Imports valid** — All imports resolve to symbols in `reference_map.json`
5. **Handover created** — `agent_memory/handovers/handover_<task-id>.md`
6. **tasks_queue.json updated** — task marked `completed`, `current_task_id` updated
7. **reference_map.json updated** — new/changed exports, classes, functions reflected
8. **project_state.yaml updated** — new/changed classes, functions, `last_updated` set
9. **architecture.md updated** — if structural changes were made
10. **Changes committed** — One commit per task, only after all gates pass

## Core Rules

1. **Plan before code** — Non-trivial changes (new features, multi-file edits) require `/plan` before implementation. Trivial fixes (typos, single-line bugs, config) can skip planning.
2. **TDD** — Write test FIRST, then implement (RED → GREEN → refactor)
3. **Quality gates** — ruff, mypy, pytest MUST pass before commit
4. **Grounding** — Only import symbols in `reference_map.json`
5. **Atomic tasks** — One focused change per task
6. **Handover** — Run `/handover` after completing each task
7. **Always use the workflow** — ALL code changes (including small fixes and error iterations) must follow the full workflow: feature branch → tests → quality gates → commit → PR. Use sub-agents (fixer, quality-gate, test-writer) instead of editing and running commands directly.
8. **Never commit directly to main** — Always work on a feature or fix branch, then merge via PR.
9. **Decompose errors into atomic tasks** — When the user reports errors or bugs, break them into separate atomic tasks in `tasks_queue.json` BEFORE starting any fix work. One fix = one task. Never do one big fix.
10. **Always run post-task updates** — After every completed task, update ALL memory files: handover, tasks_queue.json, reference_map.json, project_state.yaml, and architecture.md (if structural changes). These updates are mandatory, not optional.

Path-specific rules in `.claude/rules/`:
- `workflow.md` — Task execution steps
- `quality-gates.md` — Gate details and retry logic
- `git-workflow.md` — Branch naming, commit format
- `testing.md` — TDD patterns (loads for `tests/**` and `src/**`)
- `poc-workflow.md` — Relaxed rules for POC scripts (loads for `scripts/poc_*`)

## Skills & Commands

### Auto-triggered by Claude (when relevant)
| Skill | When Claude Uses It |
|-------|---------------------|
| `/boot` | Start of every session |
| `/fix <errors>` | When user reports errors or bugs — decomposes into atomic tasks |
| `/handover` | After completing a task — creates handover + updates all memory files |
| `/sync` | After code changes — updates reference_map.json and project_state.yaml |
| `/plan <goal>` | When user describes a new feature or goal |
| `/status` | When user asks about progress (runs in fork) |
| `/review` | Pre-PR code review checklist (runs in fork) |
| `/verify` | Quality gate check without committing (runs in fork) |

### User-only (disable-model-invocation)
| Skill | When to Use |
|-------|-------------|
| `/next` | Execute next pending task |
| `/commit` | Run quality gates + verify memory updates + commit |
| `/pr` | Push branch and create pull request |
| `/batch` | Execute 4+ independent tasks in parallel using agent teams (experimental) |

### Commands (not migrated to skills)
| Command | When to Use |
|---------|-------------|
| `/import-plan` | When pasting a plan from Repoprompt |
| `/review-builds` | Analyze build logs for patterns and trends |

## Subagents

| Subagent | Purpose | Permissions |
|----------|---------|-------------|
| `test-writer` | Generate tests BEFORE code (TDD RED) | READ, WRITE |
| `code-reviewer` | Review code for quality/security | READ only |
| `quality-gate` | Run mypy, pytest, lint checks | READ, EXECUTE |
| `fixer` | Apply minimal fixes for errors | READ, WRITE |

## Memory System

| File | Purpose |
|------|---------|
| `tasks_queue.json` | Current and pending tasks |
| `project_state.yaml` | Classes, functions, codebase state |
| `reference_map.json` | Module exports for import validation |

@agent_memory/architecture.md
@agent_memory/method_of_working.md
