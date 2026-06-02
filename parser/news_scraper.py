import asyncio

import feedparser
from bs4 import BeautifulSoup


RSS_FEEDS = [
    "https://www.trthaber.com/kategori/ekonomi.rss",
    "https://www.aa.com.tr/tr/rss/default?cat=ekonomi",
]


def _parse_feed(url: str):
    return feedparser.parse(url)


async def fetch_latest_news() -> list[dict]:
    items: list[dict] = []
    for feed_url in RSS_FEEDS:
        parsed = await asyncio.to_thread(_parse_feed, feed_url)
        for entry in parsed.entries[:5]:
            summary_html = entry.get("summary", "")
            summary = BeautifulSoup(summary_html, "lxml").get_text(" ", strip=True)
            items.append(
                {
                    "title": entry.get("title", ""),
                    "summary": summary,
                    "link": entry.get("link", ""),
                }
            )

    return items
