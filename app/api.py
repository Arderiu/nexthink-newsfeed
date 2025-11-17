import logging
from datetime import datetime, timezone
from typing import List

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from .config import settings
from .events import EventIn, EventOut
from .filtering import compute_relevance_score
from .logging import configure_logging
from .storage import StoredEvent, store

configure_logging()
logger = logging.getLogger("newsfeed")

app = FastAPI(
    title="Nexthink IT Newsfeed",
    version="0.1.0",
)


@app.post("/ingest", status_code=200)
def ingest_events(events: List[EventIn]):
    """Ingest a JSON array of event objects."""
    stored_events: List[StoredEvent] = []

    # Compute relevance scores
    for event in events:
        score = compute_relevance_score(event)
        accepted = score >= settings.relevance_threshold

        stored_events.append(
            StoredEvent(
                id=event.id,
                source=event.source,
                title=event.title,
                body=event.body,
                published_at=event.published_at,
                relevance_score=score,
                accepted=accepted,
                ingested_at=datetime.now(timezone.utc),
            )
        )

    # Store the events
    store.ingest(stored_events)
    accepted = [e for e in store._events.values() if e.accepted]

    logger.info(
        "Ingested batch: total=%d accepted=%d",
        len(stored_events),
        sum(1 for e in stored_events if e.accepted),
    )

    return {"status": "ok", "ingested": len(stored_events)}


@app.get("/retrieve", response_model=List[EventOut])
def retrieve_events():
    """Retrieve filtered events only, sorted by default ranking (importance × recency)."""
    stored = store.get_filtered_ranked()
    return [
        EventOut(
            id=e.id,
            source=e.source,
            title=e.title,
            body=e.body,
            published_at=e.published_at,
        )
        for e in stored
    ]


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    """Render a simple auto-refreshing HTML dashboard showing the filtered and ranked events."""

    events = store.get_filtered_ranked()

    rows = []
    for ev in events:
        rows.append(
            f"""
            <tr>
                <td>{ev.source}</td>
                <td>{ev.title}</td>
                <td>{(ev.body or "")[:120]}</td>
                <td>{ev.relevance_score:.2f}</td>
                <td>{ev.published_at.isoformat()}</td>
            </tr>
            """
        )

    html = f"""
    <html>
      <head>
        <title>News Dashboard</title>

        <!-- Auto-refresh every 5 seconds -->
        <meta http-equiv="refresh" content="5">

        <style>
          body {{
            font-family: system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
            margin: 2rem;
          }}
          h1 {{
            margin-bottom: 1rem;
          }}
          table {{
            border-collapse: collapse;
            width: 100%;
          }}
          th, td {{
            border: 1px solid #ddd;
            padding: 0.5rem;
            vertical-align: top;
          }}
          th {{
            background-color: #f5f5f5;
          }}
          tr:nth-child(even) {{
            background-color: #fafafa;
          }}
        </style>
      </head>
      <body>
        <h1>Relevant IT news</h1>
        <p>Total events: {len(events)}</p>
        <table>
          <thead>
            <tr>
              <th>Source</th>
              <th>Title</th>
              <th>Content</th>
              <th>Relevance score</th>
              <th>Time of publication (UTC)</th>
            </tr>
          </thead>
          <tbody>
            {''.join(rows)}
          </tbody>
        </table>
      </body>
    </html>
    """
    return HTMLResponse(content=html)
