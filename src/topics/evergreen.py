"""Evergreen topic bank organized by content pillar."""

from __future__ import annotations

EVERGREEN_TOPICS: dict[str, list[str]] = {
    "connected_journey": [
        "How to map the full customer journey across channels",
        "Breaking down data silos between marketing and sales",
        "Cross-channel attribution: what actually works",
        "First-party data strategies for a cookieless world",
        "Connecting online and offline touchpoints in B2B",
        "Building a single customer view from fragmented data",
    ],
    "crm_intelligence": [
        "CRM data hygiene: why clean data beats more data",
        "Turning CRM data into actionable marketing segments",
        "Predictive lead scoring: lessons from real implementations",
        "Automating CRM workflows without losing the human touch",
        "Measuring CRM ROI beyond pipeline attribution",
        "Integrating CRM with your marketing stack",
    ],
    "building_smart": [
        "Evaluating martech tools: build vs buy decisions",
        "Marketing automation pitfalls and how to avoid them",
        "Building a scalable martech stack from scratch",
        "When to consolidate vs when to add another tool",
        "Technical debt in marketing operations",
        "API-first thinking for marketing teams",
    ],
    "people_not_prompts": [
        "AI as a teammate: augmenting not replacing marketers",
        "Upskilling your team for the AI-assisted workplace",
        "The human skills that AI cannot replace in marketing",
        "Building an AI-literate marketing team",
        "Ethical AI usage in customer communications",
        "Balancing automation with authentic human connection",
    ],
    "field_notes": [
        "Lessons learned from a CRM migration gone wrong",
        "What we discovered running our first attribution model",
        "Client spotlight: transforming lead qualification",
        "Behind the scenes of a successful martech audit",
        "Real-world results from marketing automation tuning",
        "Common mistakes in marketing data projects",
    ],
}


def get_topics(pillar: str) -> list[str]:
    """Return evergreen topics for a given content pillar.

    Args:
        pillar: Content pillar key (e.g. "connected_journey").

    Returns:
        List of topic strings.

    Raises:
        ValueError: If the pillar is not recognized.
    """
    if pillar not in EVERGREEN_TOPICS:
        raise ValueError(
            f"Unknown pillar: {pillar!r}. Valid pillars: {', '.join(EVERGREEN_TOPICS.keys())}"
        )
    return EVERGREEN_TOPICS[pillar]


def get_all_topics() -> dict[str, list[str]]:
    """Return the full evergreen topic bank.

    Returns:
        Copy of the topic bank dictionary.
    """
    return dict(EVERGREEN_TOPICS)
