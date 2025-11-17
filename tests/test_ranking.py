from datetime import datetime, timedelta, timezone

from app.filtering import rank_events
from app.storage import StoredEvent


def test_rank_events_orders_by_relevance_then_recency():
    now = datetime.now(timezone.utc)

    e1 = StoredEvent("1", "s", "t", None, now - timedelta(hours=1), 0.9, True, now)
    e2 = StoredEvent("2", "s", "t", None, now, 0.5, True, now)
    e3 = StoredEvent("3", "s", "t", None, now, 0.9, True, now)

    ranked = rank_events([e1, e2, e3])
    assert [e.id for e in ranked] == ["3", "1", "2"]
