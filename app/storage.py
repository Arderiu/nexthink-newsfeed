from __future__ import annotations

from datetime import datetime, timezone
from threading import RLock
from typing import Dict, List

from .config import settings
from .events import StoredEvent
from .filtering import rank_events


class InMemoryEventStore:
    """Simple in-memory store."""

    def __init__(self) -> None:
        self._events: Dict[str, StoredEvent] = {}
        self._lock = RLock()

    def ingest(self, events: List[StoredEvent]) -> None:
        """Ingest events by timestamping, storing by ID, and pruning old entries."""
        now = datetime.now(timezone.utc)
        with self._lock:
            # Store or overwrite by ID (deterministic behavior)
            for e in events:
                e.ingested_at = now
                self._events[e.id] = e

            self._prune(now)

    def _prune(self, now: datetime) -> None:
        """Drop stored events older than the configured retention period."""
        cutoff = now - settings.retention_period
        to_delete = [
            eid for eid, ev in self._events.items() if ev.published_at < cutoff
        ]
        for eid in to_delete:
            del self._events[eid]

    def get_filtered_ranked(self) -> List[StoredEvent]:
        """Return all accepted events sorted by relevance and recency."""
        with self._lock:
            accepted = [e for e in self._events.values() if e.accepted]
            return rank_events(accepted)  # rank them here


store = InMemoryEventStore()
