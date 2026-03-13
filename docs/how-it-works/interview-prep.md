# Interview Preparation

The preparation workflow lets you generate, review, and customize interview questions before starting a session.

## Workflow

```
prepare → edit markdown → interview --prep
```

### Step 1: Generate a Prep File

```bash
ai-interviewer prepare \
  --topic "AI in CRM" \
  --pillar crm_intelligence \
  --suggest
```

The `--suggest` flag uses Claude to generate contextual questions. Without it, the prep file is created with an empty questions section for you to fill in manually.

### Step 2: Edit the Prep File

The generated file is a simple markdown document:

```markdown
---
topic: AI in CRM
pillar: crm_intelligence
audience:
architecture:
language: en
interviewee:
---

# Interview Prep: AI in CRM

## Questions

- How do you turn raw CRM data into actionable insights?
- What segmentation approach actually drives results?
- How do you measure the real ROI of your CRM strategy?
- What CRM metrics do most teams get wrong?
- How do you handle data quality issues in your CRM?
- What surprised you most about implementing AI in CRM?
- Where do you see CRM intelligence heading in the next 3 years?
- What advice would you give someone just starting with CRM analytics?

## Notes

_Add notes here._
```

Edit freely:

- Add, remove, or reorder questions
- Update metadata (interviewee name, audience, etc.)
- Add notes for context the interviewer should know

### Step 3: Start the Interview

```bash
ai-interviewer interview \
  --topic "AI in CRM" \
  --prep interviews/prep_ai_in_crm.md
```

The interviewer loads your questions and uses them as the interview guide, adapting naturally based on the conversation.

## How Prepared Questions Work

When `--prep` is used, the system:

1. Parses the markdown file with `parse_prep_file()`
2. Extracts the questions list from the `## Questions` section
3. Passes them as `prepared_questions` to `build_system_prompt()`
4. The prompt includes a `## Prepared Questions` section that instructs the LLM to follow the question order but adapt naturally

### Priority Rules

- **Prepared questions override pillar questions** — When a prep file is loaded, the built-in pillar question bank is suppressed
- **CLI flags override prep file metadata** — If you pass `--language nl` on the CLI, it overrides the language in the prep file
- **The interviewer can skip or add** — Questions are a guide, not a rigid script. The LLM may skip covered topics or add follow-ups

## File Format

### Frontmatter

YAML-style frontmatter between `---` markers:

| Field | Required | Description |
|-------|----------|-------------|
| `topic` | Yes | Interview topic |
| `pillar` | No | Content pillar (e.g., `crm_intelligence`) |
| `audience` | No | Target audience |
| `architecture` | No | Article architecture type |
| `language` | No | Language code (`en` or `nl`, default `en`) |
| `interviewee` | No | Interviewee name |

### Questions Section

Questions are listed under `## Questions` as markdown bullet points:

```markdown
## Questions

- First question here
- Second question here
```

### Notes Section

Free-form text under `## Notes`. Use this for context, background info, or reminders:

```markdown
## Notes

The interviewee has 10 years of CRM experience at enterprise scale.
Focus on practical lessons, not theory.
```

## Question Generator

The `QuestionGenerator` class generates questions using Claude:

```python
from src.interview.prep import QuestionGenerator

gen = QuestionGenerator(anthropic_api_key="sk-...")
questions = gen.generate(
    topic="AI in CRM",
    pillar="crm_intelligence",   # optional: includes pillar examples
    audience="marketing leaders", # optional: adjusts tone
    language="en",                # "en" or "nl"
    count=8,                      # number of questions
)
```

When a pillar is specified, the generator includes the built-in pillar questions as examples in its prompt, producing questions that align with the pillar's themes.

## CLI Options

```bash
ai-interviewer prepare [OPTIONS]
```

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--topic` | TEXT | Required | Interview topic |
| `--pillar` | TEXT | None | Content pillar |
| `--audience` | TEXT | None | Target audience |
| `--architecture` | TEXT | None | Article architecture |
| `--language` | TEXT | `en` | Language (`en` or `nl`) |
| `--interviewee` | TEXT | None | Interviewee name |
| `--suggest` | FLAG | False | Use AI to generate questions |
| `--output-dir` | TEXT | `interviews` | Output directory |
