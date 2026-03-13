# Quality Gates

ALL gates must pass before commit. No exceptions.

```bash
ruff check src/                      # Lint
ruff format src/ --check             # Format
mypy src/ --ignore-missing-imports   # Type check
pytest tests/ -v                     # Tests
```

## Retry Loop

If any gate fails:
1. Use **quality-gate** sub-agent to run checks (not manual commands)
2. Use **fixer** sub-agent to apply minimal fixes
3. Re-run quality-gate (max 3 attempts)
4. After 3 failures, STOP and ask the user

**Use sub-agents for the fix loop — do not bypass them by editing and running commands directly.**

## Import Validation

- Only import symbols that exist in `reference_map.json`
- Never hallucinate APIs or function signatures
- Run `/sync` if reference_map is outdated
