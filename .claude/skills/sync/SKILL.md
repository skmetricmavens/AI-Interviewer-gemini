---
name: sync
description: Synchronize memory files (reference_map.json, project_state.yaml) with the actual codebase
---

Synchronize memory files with the actual codebase.

This skill scans the codebase and updates:
- `agent_memory/project_state.yaml` - Classes, functions, attributes
- `agent_memory/reference_map.json` - Module exports, dependencies

## Sync Process

### 1. Scan Codebase
Look for:
- Python files (*.py)
- Class definitions
- Function definitions
- Module exports (__all__)
- Import statements

### 2. Update project_state.yaml
For each class found:
```yaml
ClassName:
  name: ClassName
  file_path: relative/path.py
  methods: [method1, method2]
  attributes: [attr1, attr2]
  bases: [BaseClass]
  docstring: "First line of docstring"
```

For each function found:
```yaml
function_name:
  name: function_name
  file_path: relative/path.py
  signature: "(arg1: type, arg2: type) -> return_type"
  is_async: true/false
  docstring: "First line of docstring"
```

Set `last_updated` to the current timestamp.

### 3. Update reference_map.json
```json
{
  "modules": {
    "module_name": {
      "file_path": "path/to/module.py",
      "classes": ["Class1", "Class2"],
      "functions": ["func1", "func2"],
      "exports": ["Class1", "func1"],
      "imports": ["os", "typing"]
    }
  },
  "public_api": {
    "module_name": ["exported_symbol1", "exported_symbol2"]
  },
  "cross_module_deps": {
    "module_a": ["module_b", "module_c"]
  }
}
```

### 4. Report Changes
Show what was added, removed, or modified.

---

**Run this after:**
- Adding new files
- Refactoring code
- Completing a task (part of post-task updates)
- Before starting a new session
