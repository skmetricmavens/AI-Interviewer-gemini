---
paths:
  - "tests/**/*.py"
  - "src/**/*.py"
---

# Testing Rules

## TDD: Write Tests FIRST

1. Write failing test (RED)
2. Implement minimum code to pass (GREEN)
3. Refactor if needed

Every function MUST have a unit test. Every bug fix MUST have a regression test.

## Coverage

- Target: 80%+ unit test coverage
- Test happy path, edge cases, and error paths
- Use realistic inputs, not simplified data

## Test Patterns

```python
import pytest

def test_function_normal_case():
    """Test normal operation."""
    result = function(valid_input)
    assert result == expected

def test_function_edge_case():
    """Test boundary conditions."""
    assert function(None) is None
    assert function([]) == []

def test_function_error():
    """Test error handling."""
    with pytest.raises(ValueError):
        function(invalid_input)
```
