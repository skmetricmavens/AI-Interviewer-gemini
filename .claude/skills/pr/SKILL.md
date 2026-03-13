---
name: pr
description: Create a pull request for the current branch with generated summary
disable-model-invocation: true
allowed-tools:
  - Bash
  - Read
---

Create a pull request for the current branch with a generated summary.

## 1. Pre-flight Checks

```
!`echo "Branch: $(git branch --show-current)"; echo "Base: main"; echo "---"; git log --oneline main..HEAD 2>/dev/null || echo "No commits ahead of main"`
```

If on `main`, STOP and say "Create a feature branch first."
If no commits ahead of main, STOP and say "No commits to create a PR for."

## 2. Run Quality Gates

Run all gates — a PR must not be created with failing gates:

```bash
ruff check src/
mypy src/ --ignore-missing-imports
pytest tests/ -v
```

If any gate fails, STOP and report failures. Suggest running `/commit` first.

## 3. Push Branch

```bash
git push -u origin $(git branch --show-current)
```

## 4. Generate PR Content

Analyze the full diff against main:

```
!`git diff main...HEAD --stat`
```

```
!`git log --oneline main..HEAD`
```

Generate:
- **Title**: Short (<70 chars), describes the change
- **Summary**: 1-3 bullet points of what changed and why
- **Test plan**: What was tested and how

## 5. Create PR

```bash
gh pr create --title "<title>" --body "$(cat <<'EOF'
## Summary
<bullet points>

## Test plan
<test details>

---
Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

## 6. Confirm

```
## PR Created

- Title: [title]
- URL: [pr url]
- Branch: [branch] -> main
- Commits: [count]
- Files changed: [count]
```
