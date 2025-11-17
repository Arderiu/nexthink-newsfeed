from datetime import datetime, timezone


def test_ingest_valid_event(client):
    payload = [
        {
            "id": "e1",
            "source": "reddit",
            "title": "Teams outage impacts users globally",
            "body": "Details…",
            "published_at": "2025-01-01T10:00:00Z",
        }
    ]

    resp = client.post("/ingest", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["ingested"] == 1


def test_ingest_endpoint_accepts_batch(client):
    payload = [
        {
            "id": "x1",
            "source": "test",
            "title": "Security update released",
            "body": "Patch available",
            "published_at": datetime.now(timezone.utc).isoformat(),
        }
    ]

    resp = client.post("/ingest", json=payload)
    assert resp.status_code == 200


def test_ingest_missing_id_is_rejected(client):
    payload = [
        {
            "source": "reddit",
            "title": "Missing id",
            "published_at": "2025-01-01T10:00:00Z",
        }
    ]

    resp = client.post("/ingest", json=payload)
    assert resp.status_code in (400, 422)


def test_retrieve_returns_relevant_events(client):
    from datetime import datetime, timezone

    # Ingest one relevant and one irrelevant
    payload = [
        {
            "id": "rel",
            "source": "test",
            "title": "Critical outage impacts SSO login",
            "body": "",
            "published_at": datetime.now(timezone.utc).isoformat(),
        },
        {
            "id": "irr",
            "source": "test",
            "title": "Nice weather today",
            "body": "",
            "published_at": datetime.now(timezone.utc).isoformat(),
        },
    ]

    client.post("/ingest", json=payload)

    resp = client.get("/retrieve")
    assert resp.status_code == 200

    ids = [item["id"] for item in resp.json()]
    assert "rel" in ids
    assert "irr" not in ids  # because irrelevant score = 0 by default
