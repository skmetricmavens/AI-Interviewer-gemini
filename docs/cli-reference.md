# CLI Reference

All commands are available via the `ai-interviewer` CLI.

## `interview`

Start a voice interview session.

```bash
ai-interviewer interview [OPTIONS]
```

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--topic` | TEXT | Required | Interview topic |
| `--context` | TEXT | None | Path to a context file |
| `--language` | TEXT | `auto` | Language: `en`, `nl`, or `auto` |
| `--interviewee` | TEXT | None | Interviewee name |
| `--pillar` | TEXT | None | Content pillar |
| `--architecture` | TEXT | None | Article architecture |
| `--audience` | TEXT | None | Target audience |
| `--prep` | TEXT | None | Path to a prep file with prepared questions |

**Examples:**

```bash
# Basic interview
ai-interviewer interview --topic "Marketing automation trends"

# With prepared questions
ai-interviewer interview --topic "CRM strategy" --prep interviews/prep_crm_strategy.md

# Full metadata
ai-interviewer interview \
  --topic "Customer journey mapping" \
  --pillar connected_journey \
  --audience marketing_leaders \
  --architecture narrative_arc \
  --interviewee "Jane Doe" \
  --language en
```

---

## `prepare`

Create an interview preparation file with optional AI-generated questions.

```bash
ai-interviewer prepare [OPTIONS]
```

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--topic` | TEXT | Required | Interview topic |
| `--pillar` | TEXT | None | Content pillar |
| `--audience` | TEXT | None | Target audience |
| `--architecture` | TEXT | None | Article architecture |
| `--language` | TEXT | `en` | Language: `en` or `nl` |
| `--interviewee` | TEXT | None | Interviewee name |
| `--suggest` | FLAG | False | Use AI to generate questions |
| `--output-dir` | TEXT | `interviews` | Output directory for prep files |

**Examples:**

```bash
# Create empty prep file
ai-interviewer prepare --topic "Data-driven marketing"

# Generate AI-suggested questions
ai-interviewer prepare --topic "CRM ROI" --pillar crm_intelligence --suggest

# Dutch interview prep
ai-interviewer prepare --topic "Klantreizen optimaliseren" --language nl --suggest
```

---

## `write`

Generate content from a past interview session.

```bash
ai-interviewer write [OPTIONS]
```

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--session-id` | TEXT | Required | Session ID to generate from |
| `--format` | TEXT | `linkedin` | Output format |
| `--language` | TEXT | `en` | Output language |

Available formats: `linkedin`, `blog`, `inverted_pyramid`, `narrative_arc`, `pillar_cluster`

---

## `blueprint`

Generate an article blueprint (structural outline) from a past interview.

```bash
ai-interviewer blueprint [OPTIONS]
```

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--session-id` | TEXT | Required | Session ID |
| `--architecture` | TEXT | `inverted_pyramid` | Architecture type |
| `--pillar` | TEXT | None | Content pillar |
| `--audience` | TEXT | None | Target audience |
| `--language` | TEXT | `en` | Language |

---

## `export`

Export a session transcript to a file.

```bash
ai-interviewer export [OPTIONS]
```

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--session-id` | TEXT | Required | Session ID |
| `--output-dir` | TEXT | `exports` | Output directory |
| `--format` | TEXT | `markdown` | Format: `markdown`, `plain_text`, or `json` |

---

## `topics`

List or suggest interview topics for a content pillar.

```bash
ai-interviewer topics [OPTIONS]
```

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--pillar` | TEXT | Required | Content pillar |
| `--count` | INT | `3` | Number of topics to suggest |
| `--language` | TEXT | `en` | Language |
| `--suggest` | FLAG | False | Use AI to suggest new topics |

**Examples:**

```bash
# List evergreen topics
ai-interviewer topics --pillar connected_journey

# AI-suggested topics
ai-interviewer topics --pillar field_notes --suggest --count 5
```

---

## `persona-analyze`

Analyze writing samples and generate a style fingerprint.

```bash
ai-interviewer persona-analyze [OPTIONS]
```

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--samples-dir` | TEXT | `persona/samples` | Directory with writing samples |
| `--output` | TEXT | `persona/fingerprint.json` | Output path for fingerprint |

---

## `sessions-list`

List past interview sessions.

```bash
ai-interviewer sessions-list
```

No options. Displays a table of all sessions with ID, topic, language, and timestamps.

---

## Content Pillars

These values can be used with `--pillar`:

| Value | Description |
|-------|-------------|
| `connected_journey` | Customer journey mapping and orchestration |
| `crm_intelligence` | CRM data, segmentation, and ROI |
| `building_smart` | Martech stack decisions and integration |
| `people_not_prompts` | Human element in AI-driven marketing |
| `field_notes` | Practical experiments and lessons learned |

## Target Audiences

These values can be used with `--audience`:

| Value | Description |
|-------|-------------|
| `crm_managers` | CRM managers and specialists |
| `performance_marketers` | Performance and growth marketers |
| `marketing_leaders` | Marketing directors and VPs |
| `c_suite` | CMOs, CTOs, and C-level executives |

## Article Architectures

These values can be used with `--architecture`:

| Value | Description |
|-------|-------------|
| `inverted_pyramid` | Lead with key info, then details |
| `narrative_arc` | Story-driven structure |
| `pillar_cluster` | Hub-and-spoke SEO structure |
