"""Output format templates for content generation (LinkedIn, Blog)."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class LinkedInPost:
    """LinkedIn post format."""

    hook: str
    body: str
    cta: str
    max_chars: int = 3000


@dataclass
class BlogPost:
    """Blog post format."""

    title: str
    intro: str
    sections: list[str] = field(default_factory=list)
    conclusion: str = ""


@dataclass
class InvertedPyramidArticle:
    """Inverted Pyramid article format — most important info first."""

    headline: str
    lead: str
    body: list[str] = field(default_factory=list)
    background: str = ""
    cta: str = ""


@dataclass
class NarrativeArcArticle:
    """Narrative Arc article format — storytelling structure."""

    headline: str
    setup: str
    rising_action: list[str] = field(default_factory=list)
    climax: str = ""
    resolution: str = ""
    cta: str = ""


@dataclass
class PillarClusterArticle:
    """Pillar-Cluster article format — SEO hub-and-spoke structure."""

    headline: str
    pillar_summary: str
    clusters: list[str] = field(default_factory=list)
    internal_links: list[str] = field(default_factory=list)
    cta: str = ""


CTA_PATTERNS: dict[str, list[str]] = {
    "engagement": [
        "What's your take? Share in the comments.",
        "Have you experienced this? I'd love to hear your story.",
        "Tag someone who needs to see this.",
    ],
    "conversion": [
        "Want to dive deeper? Download our free guide.",
        "Ready to get started? Book a free consultation.",
        "Subscribe for weekly insights like this.",
    ],
    "sharing": [
        "Found this useful? Share it with your network.",
        "Know someone who'd benefit? Pass it along.",
        "Repost if this resonated with you.",
    ],
}


def format_instructions(format_type: str) -> str:
    """Return Claude-ready formatting rules for the given format type.

    Args:
        format_type: "linkedin", "blog", "inverted_pyramid",
            "narrative_arc", or "pillar_cluster".

    Returns:
        Formatting instructions string.

    Raises:
        ValueError: If format_type is not recognized.
    """
    if format_type == "linkedin":
        return (
            "Format as a LinkedIn post with these elements:\n"
            "1. Hook — a compelling opening line that grabs attention\n"
            "2. Body — the main content, using short paragraphs and line breaks\n"
            "3. CTA (Call to Action) — end with a question or invitation to engage\n"
            "Keep the total length under 3000 characters.\n"
            "Use line breaks between paragraphs for readability."
        )
    if format_type == "blog":
        return (
            "Format as a blog post with these elements:\n"
            "1. Title — a clear, engaging headline\n"
            "2. Intro — a brief introduction that sets the context\n"
            "3. Sections — multiple sections with subheadings covering key points\n"
            "4. Conclusion — a summary with a takeaway or call to action\n"
            "Use markdown formatting for headings and emphasis."
        )
    if format_type == "inverted_pyramid":
        return (
            "Format as an Inverted Pyramid article with these elements:\n"
            "1. Headline — a clear, attention-grabbing headline\n"
            "2. Lead — the most important information first "
            "(who, what, when, where, why)\n"
            "3. Body — supporting details in decreasing order of importance\n"
            "4. Background — additional context and background information\n"
            "5. CTA — a call to action or next step for the reader\n"
            "Front-load the most critical insights so readers get value "
            "even if they stop reading early."
        )
    if format_type == "narrative_arc":
        return (
            "Format as a Narrative Arc article with these elements:\n"
            "1. Headline — a compelling headline that hints at the story\n"
            "2. Setup — set the scene with context and stakes\n"
            "3. Rising Action — build tension with challenges, "
            "obstacles, or discoveries\n"
            "4. Climax — the turning point or key insight\n"
            "5. Resolution — what changed, lessons learned, outcomes\n"
            "6. CTA — a call to action that connects to the narrative\n"
            "Tell the story in a way that keeps readers engaged "
            "and delivers a clear takeaway."
        )
    if format_type == "pillar_cluster":
        return (
            "Format as a Pillar-Cluster article with these elements:\n"
            "1. Headline — a broad headline covering the pillar topic\n"
            "2. Pillar Summary — a comprehensive overview of the topic\n"
            "3. Clusters — subtopic sections that link to deeper content\n"
            "4. Internal Links — cross-references to related articles\n"
            "5. CTA — a call to action for the reader\n"
            "Structure for SEO: the pillar page links to cluster "
            "articles and vice versa."
        )
    raise ValueError(
        f"Unknown format type: {format_type!r}."
        " Use 'linkedin', 'blog', 'inverted_pyramid',"
        " 'narrative_arc', or 'pillar_cluster'."
    )
