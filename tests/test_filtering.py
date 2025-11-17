from app.events import EventIn
from app.filtering import compute_relevance_score


def test_security_news_scores_higher_than_bug():
    sec = EventIn(
        id="s1",
        source="x",
        title="Critical zero-day vulnerability in Windows",
        body=None,
        published_at="2025-01-01T00:00:00Z",
    )
    bug = EventIn(
        id="b1",
        source="x",
        title="Minor UI bug in settings panel",
        body=None,
        published_at="2025-01-01T00:00:00Z",
    )

    assert compute_relevance_score(sec) > compute_relevance_score(bug)


def test_irrelevant_news_scores_zero():
    e = EventIn(
        id="n1",
        source="news",
        title="Tech stocks rise after market rally",
        body=None,
        published_at="2025-01-01T00:00:00Z",
    )
    assert compute_relevance_score(e) == 0.0
