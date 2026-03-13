---
name: verify
description: Run all quality gates and report results without committing or modifying files
context: fork
allowed-tools:
  - Bash
  - Read
---

Run all quality gates and report results. Does NOT commit or modify any files.

## Quality Gates

Run each gate and collect results:

### Gate 1: Lint
```bash
ruff check src/
```

### Gate 2: Format
```bash
ruff format src/ --check
```

### Gate 3: Type Check
```bash
mypy src/ --ignore-missing-imports
```

### Gate 4: Tests
```bash
pytest tests/ -v
```

## Report

Provide a structured summary:

```
## Quality Gate Report

| Gate | Status |
|------|--------|
| Lint (ruff) | PASS / FAIL |
| Format (ruff) | PASS / FAIL |
| Types (mypy) | PASS / FAIL |
| Tests (pytest) | PASS / FAIL (X/Y passed) |

### Overall: PASS / FAIL

[If any failures: list specific errors and suggested fixes]
```
