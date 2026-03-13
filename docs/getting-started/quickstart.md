# Quick Start

This guide walks you through a complete interview-to-content workflow.

## 1. Analyze Your Writing Style

Before generating content, teach the system your writing style:

```bash
# Place 3-5 writing samples in persona/samples/
mkdir -p persona/samples
# Copy your LinkedIn posts, blog articles, etc. as .txt or .md files

# Run analysis
ai-interviewer persona-analyze
```

This creates `persona/fingerprint.json` with your linguistic fingerprint.

## 2. Prepare Interview Questions

Generate tailored questions for your topic:

```bash
ai-interviewer prepare \
  --topic "How CRM data drives personalization" \
  --pillar crm_intelligence \
  --audience "marketing leaders" \
  --suggest
```

This creates `interviews/prep_how_crm_data_drives_personalizat.md` with AI-generated questions.

Open the file and edit the questions — add, remove, or reword as needed:

```markdown
---
topic: How CRM data drives personalization
pillar: crm_intelligence
audience: marketing leaders
language: en
---

# Interview Prep: How CRM data drives personalization

## Questions

- How do you turn raw CRM data into actionable insights?
- What segmentation approach actually drives results for you?
- Where do most teams get CRM metrics wrong?

## Notes

_Add notes here._
```

## 3. Run the Interview

Start a voice interview using your prepared questions:

```bash
ai-interviewer interview \
  --topic "How CRM data drives personalization" \
  --prep interviews/prep_how_crm_data_drives_personalizat.md
```

The interviewer will use your questions as a guide, adapting naturally to the conversation. Speak into your microphone — the AI responds in real-time via your speakers.

Press `Ctrl+C` to end the interview.

## 4. Generate Content

After the interview, generate content from the transcript:

```bash
# List your sessions to find the session ID
ai-interviewer sessions-list

# Generate a LinkedIn post
ai-interviewer write --session-id <id> --format linkedin

# Generate a blog article
ai-interviewer write --session-id <id> --format blog

# Generate with a specific architecture
ai-interviewer write --session-id <id> --format narrative_arc
```

## 5. Export the Transcript

Save the raw transcript for reference:

```bash
ai-interviewer export --session-id <id> --format markdown
```

## Running Without Preparation

You can skip the preparation step and run a direct interview:

```bash
ai-interviewer interview \
  --topic "The future of marketing automation" \
  --pillar building_smart \
  --language en
```

The interviewer will use built-in pillar questions as inspiration instead.
