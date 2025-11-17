from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

from pydantic import BaseModel, field_validator


class EventIn(BaseModel):
    """Incoming event from an external news source."""

    id: str
    source: str
    title: str
    body: Optional[str] = None
    published_at: datetime

    # Ensure Assume ISO-8601 / RFC 3339 and UTC timezone
    @field_validator("published_at")
    def ensure_utc(cls, value):
        if value.tzinfo is None or value.utcoffset() != timedelta(0):
            raise ValueError("published_at must be a UTC ISO-8601 timestamp.")
        return value


class EventOut(EventIn):
    """Event returned in API responses."""

    pass


@dataclass
class StoredEvent:
    """Internal representation of a news event after filtering and scoring."""

    id: str
    source: str
    title: str
    body: Optional[str]
    published_at: datetime
    relevance_score: float
    accepted: bool
    ingested_at: datetime
