from app.sources.base import FeedNewsSource


class RedditSysadminSource(FeedNewsSource):
    name = "reddit/r/sysadmin"
    feed_url = "https://www.reddit.com/r/sysadmin/new/.rss"
