from app.sources.base import FeedNewsSource


class ArsTechnicaITSource(FeedNewsSource):
    name = "ars-technica"
    feed_url = "https://feeds.arstechnica.com/arstechnica/technology-lab"
