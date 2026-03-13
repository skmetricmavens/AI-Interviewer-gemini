# Discovery Prompt Template

Use this prompt in Repoprompt to create a discovery document for your project.

---

## Prompt

```
You are a senior software architect. Analyze the following project idea and create
a comprehensive discovery document.

## Project Idea

[PASTE YOUR PROJECT IDEA HERE]

## Discovery Output Requirements

Create a structured discovery document with the following sections:

### 1. Project Scope

Define clear boundaries:
- **In Scope**: What this project will deliver
- **Out of Scope**: What is explicitly excluded
- **Target Users**: Who will use this
- **Success Criteria**: How we know it's done

### 2. Architecture Overview

Provide a system diagram using Mermaid:

```mermaid
graph TB
    [Component relationships]
```

Include:
- Main components
- Data flow direction
- External dependencies
- Technology stack choices with rationale

### 3. Module Breakdown

For EACH module in the system, provide:

| Module | Purpose | Public API | Dependencies | Location |
|--------|---------|------------|--------------|----------|
| name | what it does | functions/classes | other modules | file path |

Detail the public API for each module:
- Classes with key methods
- Functions with signatures
- What it exports

### 4. Data Models

Define core data structures:

```python
class ModelName:
    field: type  # description
```

Include:
- Required vs optional fields
- Relationships between models
- Validation rules

### 5. External Dependencies

List all third-party requirements:

| Dependency | Version | Purpose |
|------------|---------|---------|
| library | ^x.y.z | why needed |

### 6. MVP Definition

Minimum viable product criteria:

- [ ] Feature 1: [acceptance criteria]
- [ ] Feature 2: [acceptance criteria]
- [ ] Feature 3: [acceptance criteria]

**What can be deferred:**
- Enhancement 1
- Enhancement 2

### 7. Risks and Unknowns

| Risk | Impact | Mitigation |
|------|--------|------------|
| description | high/medium/low | how to address |

---

## Output Format

Output the discovery as structured markdown that can be saved directly to
`agent_memory/architecture.md`.

Start the output with:
# Architecture - [Project Name]

Make it comprehensive but focused. This document will guide all implementation.
```

---

## Example Output

See `examples/discovery-output.md` for a complete example.

## Next Step

After generating the discovery, use the Plan prompt to create an executable task list.
