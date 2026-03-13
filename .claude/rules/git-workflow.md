# Git Workflow

## Branches

- Feature: `feature/<task-id>-description`
- Fix: `fix/<task-id>-description`
- Never commit directly to main

## Commits

- One commit per task, only after quality gates pass
- Format: `task-N: brief description`
- Include `Co-Authored-By: Claude <noreply@anthropic.com>` when AI-assisted

## Pull Requests

- Create PR with summary + test plan
- Wait for review before merging
