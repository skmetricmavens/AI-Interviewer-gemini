# Content Pipeline

After an interview, the content pipeline transforms the transcript into styled, publication-ready content.

## Overview

```
Transcript → Persona Fingerprint → Format Template → Claude → Styled Content
```

## Persona Analysis

The persona engine analyzes your writing samples to create a linguistic fingerprint that Claude uses to match your style.

### How It Works

1. Place writing samples (LinkedIn posts, blog articles, etc.) in `persona/samples/`
2. Run `ai-interviewer persona-analyze`
3. Claude analyzes vocabulary, sentence structure, tone, and patterns
4. Results are saved to `persona/fingerprint.json`

The fingerprint captures:

- Vocabulary preferences and frequently used phrases
- Sentence length and structure patterns
- Tone markers (casual vs. formal, assertive vs. reflective)
- Anti-AI vocabulary (words to avoid that sound AI-generated)

## Content Humanizer

The `ContentHumanizer` combines the transcript, fingerprint, and format template to generate content:

```python
humanizer = ContentHumanizer(
    anthropic_api_key=settings.anthropic_api_key,
    model=settings.claude_model,
)

content = humanizer.generate(
    transcript=transcript,
    fingerprint=fingerprint,
    format_type="linkedin",  # or blog, inverted_pyramid, etc.
    language="en",
)
```

## Output Formats

### LinkedIn Post

Short-form content with a hook, body, and CTA. Optimized for the LinkedIn feed.

### Blog Post

Long-form content with title, intro, sections, and conclusion.

### Inverted Pyramid

News-style article: lead with the most important information, then supporting details, then background.

### Narrative Arc

Story-driven article: setup, rising action, climax, resolution. Works well for case studies and experience-based content.

### Pillar-Cluster

Hub-and-spoke structure: one pillar piece with linked cluster topics. Ideal for SEO-focused content strategies.

## Article Blueprints

Before writing a full article, you can generate a blueprint — a structural outline with key points and source quotes:

```bash
ai-interviewer blueprint \
  --session-id <id> \
  --architecture narrative_arc \
  --pillar crm_intelligence \
  --audience marketing_leaders
```

The blueprint includes:

- Headline suggestion
- Section breakdown with key points
- Source quotes from the transcript
- Estimated word count

## CTA Patterns

Each output format includes contextual call-to-action patterns:

| Format | CTA Style |
|--------|----------|
| LinkedIn | Engagement question ("What's your take?") |
| Blog | Newsletter signup or related reading |
| Inverted Pyramid | Expert quote or further reading |
| Narrative Arc | Reflection prompt |
| Pillar-Cluster | Links to cluster articles |
