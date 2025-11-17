from datetime import datetime, timedelta, timezone

from app.storage import StoredEvent, store
from app.config import settings


def _make_event(eid: str, published_at: datetime, score: float, accepted: bool) -> StoredEvent:
    return StoredEvent(
        id=eid,
        source="x",
        title="test",
        body=None,
        published_at=published_at,
        relevance_score=score,
        accepted=accepted,
        ingested_at=published_at,
    )


def test_get_filtered_ranked_respects_accepted():
    now = datetime.now(timezone.utc)
    high = _make_event("high", now, score=1.0, accepted=True)
    low = _make_event("low", now, score=0.1, accepted=False)

    store.ingest([high, low])
    ranked = store.get_filtered_ranked()

    ids = [e.id for e in ranked]
    assert "high" in ids
    assert "low" not in ids


def test_pruning_respects_retention_period():
    now = datetime.now(timezone.utc)
    old_time = now - (settings.retention_period + timedelta(seconds=1))
    recent_time = now

    old_ev = _make_event("old", old_time, score=1.0, accepted=True)
    new_ev = _make_event("new", recent_time, score=1.0, accepted=True)

    store.ingest([old_ev, new_ev])
    ranked = store.get_filtered_ranked()
    ids = [e.id for e in ranked]

    assert "new" in ids
    assert "old" not in ids
