import pytest
from fastapi.testclient import TestClient

from app.api import app
from app.config import settings
from app.storage import store


@pytest.fixture
def client():
    """FastAPI test client for API tests."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_store():
    """Ensure the in-memory store is empty before each test."""
    store._events.clear()
    yield
    store._events.clear()
