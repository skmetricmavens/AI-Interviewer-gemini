---
paths:
  - "scripts/poc_*.py"
  - "scripts/demo_*.py"
  - "notebooks/**"
---

# POC / Prototype Workflow

Scripts in `scripts/` prefixed with `poc_` or `demo_` follow relaxed rules:

## Quality Gates (Reduced)

- mypy + ruff: MUST pass
- pytest: OPTIONAL (throwaway scripts don't need tests)
- TDD: OPTIONAL

## Rules

- Must NOT modify files in `src/` (use imports only)
- Must NOT be in `src/` directory
- Graduating to production requires full TDD reimplementation in `src/`
- Document purpose and usage in script docstring
