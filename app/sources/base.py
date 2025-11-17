# app/sources/base.py
from abc import ABC, abstractmethod
from datetime import datetime, timedelta, timezone
from typing import Any, List, Optional, Set

import feedparser

from app.config import settings  # wherever your retention lives
from app.events import EventIn


def _parse_published(entry) -> Optional[datetime]:
    """Convert an RSS/Feedparser time tuple into a UTC datetime, or return None if missing."""
    ts = entry.get("published_parsed") or entry.get("updated_parsed")
    if not ts:
        return None
    return datetime(*ts[:6], tzinfo=timezone.utc)


class FeedNewsSource(ABC):
    """Base class for RSS/Atom-backed news sources with de-duplication and retention filtering."""

    #: URL of the RSS/Atom feed to poll.
    feed_url: str

    #: Source identifier to store on EventIn.sources.
    name: str

    def __init__(self) -> None:
        """Initialize the source with an in-memory set to track already-seen entries."""
        self._seen_ids: Set[str] = set()

    def fetch_events(self) -> List[EventIn]:
        """Fetch new feed entries within the retention window and map them to EventIn objects."""
        feed = feedparser.parse(self.feed_url)
        new_events: List[EventIn] = []

        for entry in feed.entries:

            # Skip entries without a timestamp or outside the retention window
            published_at = _parse_published(entry)
            if not published_at or not is_within_retention(published_at):
                continue

            # Skip if we cannot uniquely identify this entry
            raw_id = self._extract_id(entry)
            if not raw_id:
                continue

            # Skip if already processed in a previous poll
            if raw_id in self._seen_ids:
                continue

            # Create a new EventIn object with the fetched new
            self._seen_ids.add(raw_id)
            event = self._entry_to_event(entry, raw_id, published_at)
            if event:
                new_events.append(event)

        return new_events

    def _extract_id(self, entry: Any) -> str | None:
        """Extract a stable identifier (Atom id preferred, fallback to link)."""
        return entry.get("id") or entry.get("link")

    def parse_title(self, entry: Any) -> str:
        """Extract the title from a feed entry."""
        return (entry.get("title") or "").strip()

    def parse_body(self, entry: Any) -> Optional[str]:
        """Extract the body/summary from a feed entry."""
        return (entry.get("summary") or "").strip() or None

    def _entry_to_event(
        self,
        entry: Any,
        raw_id: str,
        published_at: datetime,
    ) -> Optional[EventIn]:
        """Generic mapping of a feed entry to an EventIn."""
        title = self.parse_title(entry)
        body = self.parse_body(entry)

        if not title:
            return None

        return EventIn(
            id=raw_id,
            source=self.name,
            title=title,
            body=body,
            published_at=published_at,
        )


def is_within_retention(published_at: datetime) -> bool:
    """Return True if the date is within the retention period."""
    cutoff = datetime.now(timezone.utc) - settings.retention_period
    return published_at >= cutoff
