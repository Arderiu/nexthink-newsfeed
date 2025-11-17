import os
import sys
import time
from typing import List

import httpx

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)
import logging

from app.config import settings
from app.events import EventIn
from app.sources import get_all_sources

API_INGEST_URL = settings.api_base_url.rstrip("/") + "/ingest"

log = logging.getLogger(__name__)


def events_to_payload(events: List[EventIn]) -> list[dict]:
    """Convert EventIn objects into JSON-serializable payloads"""
    payload: list[dict] = []
    for ev in events:
        d = ev.model_dump()
        dt = d["published_at"]
        d["published_at"] = dt.isoformat().replace("+00:00", "Z")
        payload.append(d)
    return payload


def main():
    """Continuously poll all news sources, format events, and POST to the ingest API."""
    sources = get_all_sources()
    log.info(f"Polling %d sources, posting to %s", len(sources), API_INGEST_URL)

    while True:
        for source in sources:
            try:
                events = source.fetch_events()
            except Exception as e:
                log.error("[%s] fetch error: %s", source.name, e)
                continue

            if not events:
                continue

            payload = events_to_payload(events)

            try:
                with httpx.Client(timeout=10.0) as client:
                    resp = client.post(API_INGEST_URL, json=payload)
                    log.info(
                        "[%s] sent %d events -> %d",
                        source.name,
                        len(payload),
                        resp.status_code,
                    )
            except Exception as e:
                # 👇 This prevents the script from crashing if the API isn't up yet
                log.error("[%s] ingest error: %s", source.name, e)

        time.sleep(settings.poll_interval_seconds)


if __name__ == "__main__":
    main()
