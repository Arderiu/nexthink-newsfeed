from typing import List

from app.sources.ars_technica import ArsTechnicaITSource
from app.sources.base import FeedNewsSource
from app.sources.reddit import RedditSysadminSource
from app.sources.toms_hardware import TomsHardwareSource


def get_all_sources() -> List[FeedNewsSource]:
    """Return the list of news source instances used by the fetcher."""
    return [ArsTechnicaITSource(), TomsHardwareSource()]  # ADD RedditSysadminSource
