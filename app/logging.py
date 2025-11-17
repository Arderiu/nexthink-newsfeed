import logging


def configure_logging():
    """Initialize basic logging configuration for the application."""

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
