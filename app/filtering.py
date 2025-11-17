from .events import EventIn, StoredEvent

SECURITY_TERMS = {
    "vulnerability",
    "vulnerabilities",
    "cve-",
    "zero-day",
    "zero day",
    "exploit",
    "exploited in the wild",
    "ransomware",
    "malware",
    "trojan",
    "spyware",
    "data breach",
    "data leak",
    "credential theft",
    "phishing",
    "privilege escalation",
    "remote code execution",
    "security advisory",
    "critical security update",
    "bypass",
}

OUTAGE_TERMS = {
    "outage",
    "downtime",
    "disruption",
    "degradation",
    "sev-1",
    "sev1",
    "incident",
}

BUG_TERMS = {
    "bug",
    "breaking change",
    "data loss",
    "data corruption",
    "crash",
    "blue screen",
    "stop",
    "kernel panic",
    "hang",
    "login failure",
    "sign-in failure",
    "high cpu",
    "memory leak",
    "io spike",
    "performance degradation",
    "slow startup",
    "slow logon",
}

IT_CONTEXT_TERMS = {
    "endpoint",
    "endpoints",
    "device",
    "laptop",
    "workstation",
    "windows 10",
    "windows 11",
    "macos",
    "vpn",
    "proxy",
    "firewall",
    "microsoft teams",
    "teams",
    "zoom",
    "webex",
    "slack",
    "outlook",
    "exchange",
    "sharepoint",
    "google workspace",
    "gmail",
    "google meet",
    "sccm",
    "intune",
    "endpoint manager",
    "patch management",
    "software deployment",
    "service desk",
    "it service",
    "ticket volume",
}


def _contains_any(text: str, terms: set[str]) -> bool:
    """Return True if the text contains any of the given terms."""
    return any(term in text for term in terms)


def compute_relevance_score(event: EventIn) -> float:
    """Compute a relevance score for an event based on category matches and contextual signals."""
    title = event.title.lower()
    body = (event.body or "").lower()
    text = title + " " + body

    # Primary category hits
    has_security = _contains_any(text, SECURITY_TERMS)
    has_outage = _contains_any(text, OUTAGE_TERMS)
    has_bug = _contains_any(text, BUG_TERMS)

    # Base score from strongest primary category
    base_score = 0.0
    if has_security:
        base_score = max(base_score, 0.7)
    if has_outage:
        base_score = max(base_score, 0.7)
    if has_bug:
        base_score = max(base_score, 0.5)

    # If no primary signal at all, probably not relevant
    if base_score == 0.0:
        return 0.0

    # Combo bonus for multiple primary categories
    num_primary = sum([has_security, has_outage, has_bug])
    combo_bonus = 0.1 * max(0, num_primary - 1)

    # IT-context bonus
    it_context_bonus = 0.0
    if _contains_any(text, IT_CONTEXT_TERMS):
        it_context_bonus = 0.15

    # Title emphasis bonus if main terms are in title
    title_bonus = 0.0
    if _contains_any(title, SECURITY_TERMS | OUTAGE_TERMS | BUG_TERMS):
        title_bonus = 0.15

    # Body length bonus: detailed news gets a small boost
    body_length_bonus = 0.0
    if len(body) > 500:
        body_length_bonus = 0.1
    elif len(body) > 200:
        body_length_bonus = 0.05

    score = (
        base_score + combo_bonus + it_context_bonus + title_bonus + body_length_bonus
    )
    return score


def rank_events(events: list[StoredEvent]) -> list[StoredEvent]:
    """Return events sorted by relevance, recency, and ID for stable ordering."""
    return sorted(
        events,
        key=lambda e: (
            -e.relevance_score,
            -e.published_at.timestamp(),
            e.id,
        ),
    )
