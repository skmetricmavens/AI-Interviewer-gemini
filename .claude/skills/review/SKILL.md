---
name: review
description: Pre-PR review checklist — validates code quality, security, testing, and documentation before creating a pull request
context: fork
allowed-tools:
  - Read
  - Bash
  - Glob
  - Grep
---

Run a pre-PR review checklist on the current branch.

## Branch Info
```
!`echo "Branch: $(git branch --show-current)"; echo "Base: main"; git log --oneline main..HEAD 2>/dev/null || echo "No commits ahead of main"`
```

## Changed Files
```
!`git diff --name-status main...HEAD 2>/dev/null || git diff --name-status HEAD~1 2>/dev/null || echo "No changes found"`
```

## Review Checklist

For each changed file, check:

### 1. Security (CRITICAL)
- [ ] No hardcoded secrets, API keys, or credentials
- [ ] No SQL injection, XSS, or command injection vulnerabilities
- [ ] No unsafe deserialization
- [ ] Proper input validation at boundaries

### 2. Code Quality
- [ ] Type hints on all function signatures
- [ ] No unused imports or variables
- [ ] Functions under 30 lines (recommend)
- [ ] No magic numbers/strings
- [ ] Error handling for external calls

### 3. Testing
- [ ] Every new function has a unit test
- [ ] Edge cases covered (None, empty, boundary)
- [ ] Bug fixes have regression tests
- [ ] Tests are independent (no shared state)

### 4. Quality Gates
Run and report results:
```bash
ruff check src/
mypy src/ --ignore-missing-imports
pytest tests/ -v
```

### 5. Documentation
- [ ] Public functions have docstrings
- [ ] Architecture changes reflected in `agent_memory/architecture.md`
- [ ] Reference map updated (`/sync` run)

## Output

Provide a structured review:
```
## Pre-PR Review: [branch name]

### Commits: [count]
### Files Changed: [count]

### Security: PASS / FAIL
[Issues if any]

### Code Quality: PASS / WARNINGS / FAIL
[Issues if any]

### Testing: PASS / FAIL
[Missing tests if any]

### Quality Gates: PASS / FAIL
- ruff: [result]
- mypy: [result]
- pytest: [X/Y passed]

### Overall: READY / NOT READY
[Summary and recommendations]
```
