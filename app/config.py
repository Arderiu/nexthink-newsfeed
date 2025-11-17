from datetime import timedelta

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuration values controlling retention, filtering, polling, and API endpoints."""

    # Retain events for this duration
    retention_period: timedelta = timedelta(days=14)

    # Minimum relevance score to keep an event
    relevance_threshold: float = 0.4

    # How often to poll external sources (seconds)
    poll_interval_seconds: int = 300  # 5 minutes

    # Base URL of the API we post ingested events to
    api_base_url: str = "http://127.0.0.1:8000"  # default uvicorn address


settings = Settings()
