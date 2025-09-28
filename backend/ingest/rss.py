from __future__ import annotations

from datetime import datetime
from typing import Iterable

import feedparser
from dateutil import parser as date_parser, tz

from backend.utils.url import normalize_url


class RSSItem:
    def __init__(self, title: str, url: str, published_at: datetime | None):
        self.title = title
        self.url = url
        self.published_at = published_at


class RSSFetcher:
    def __init__(self, feed_url: str):
        self.feed_url = feed_url

    def fetch(self, limit: int = 50) -> Iterable[RSSItem]:
        feed = feedparser.parse(self.feed_url)
        for entry in feed.entries[:limit]:
            link = entry.get("link")
            if not link:
                continue
            title = entry.get("title", "")
            published_at = None
            if entry.get("published"):
                try:
                    published_at = date_parser.parse(entry.published)
                    if published_at and published_at.tzinfo is None:
                        published_at = published_at.replace(tzinfo=tz.UTC)
                except (ValueError, TypeError):
                    published_at = None
            yield RSSItem(title=title, url=normalize_url(link), published_at=published_at)
