from app.sources.base import FeedNewsSource


class TomsHardwareSource(FeedNewsSource):
    name = "toms-hardware"
    feed_url = "https://www.tomshardware.com/feeds.xml"
