"""
parser/news_parser.py — Агент сбора данных.

Асинхронно забирает записи из RSS-лент и при необходимости
дополнительно парсит HTML-страницы через BeautifulSoup.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import AsyncIterator

import aiohttp
import feedparser
from bs4 import BeautifulSoup

from config.settings import settings

logger = logging.getLogger(__name__)


@dataclass
class NewsItem:
    title: str
    link: str
    summary: str
    published: datetime | None = None
    source: str = ""


async def _fetch_html(session: aiohttp.ClientSession, url: str) -> str:
    """Загружает HTML-страницу; при ошибке возвращает пустую строку."""
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as resp:
            resp.raise_for_status()
            return await resp.text()
    except Exception as exc:
        logger.warning("Не удалось загрузить %s: %s", url, exc)
        return ""


def _parse_feed(raw_xml: str, source_url: str) -> list[NewsItem]:
    """Парсит RSS/Atom XML через feedparser и возвращает список NewsItem."""
    feed = feedparser.parse(raw_xml)
    items: list[NewsItem] = []

    for entry in feed.entries:
        title = entry.get("title", "").strip()
        link = entry.get("link", "").strip()
        summary = BeautifulSoup(
            entry.get("summary", entry.get("description", "")), "lxml"
        ).get_text(separator=" ", strip=True)

        published: datetime | None = None
        if hasattr(entry, "published_parsed") and entry.published_parsed:
            published = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)

        if title and link:
            items.append(
                NewsItem(
                    title=title,
                    link=link,
                    summary=summary[:500],
                    published=published,
                    source=source_url,
                )
            )

    return items


async def _fetch_feed(
    session: aiohttp.ClientSession, feed_url: str
) -> list[NewsItem]:
    """Загружает одну RSS-ленту и парсит её."""
    raw = await _fetch_html(session, feed_url)
    if not raw:
        return []
    return _parse_feed(raw, feed_url)


async def fetch_all_feeds() -> list[NewsItem]:
    """
    Параллельно забирает все RSS-ленты из конфига.
    Возвращает объединённый список, отсортированный по дате (новые первые),
    обрезанный до MAX_NEWS_ITEMS.
    """
    if not settings.rss_feeds:
        logger.warning("Список RSS-лент пуст. Проверь RSS_FEEDS в .env")
        return []

    async with aiohttp.ClientSession() as session:
        tasks = [_fetch_feed(session, url) for url in settings.rss_feeds]
        results = await asyncio.gather(*tasks, return_exceptions=True)

    all_items: list[NewsItem] = []
    for result in results:
        if isinstance(result, Exception):
            logger.error("Ошибка при парсинге ленты: %s", result)
            continue
        all_items.extend(result)

    # Сортируем: без даты — в конец
    all_items.sort(
        key=lambda x: x.published or datetime.min.replace(tzinfo=timezone.utc),
        reverse=True,
    )

    return all_items[: settings.max_news_items]


async def scrape_page_text(url: str) -> str:
    """
    Вспомогательная функция: скачивает произвольную веб-страницу
    и возвращает чистый текст (без тегов).
    Используется для дополнительного анализа полной статьи.
    """
    async with aiohttp.ClientSession() as session:
        html = await _fetch_html(session, url)

    if not html:
        return ""

    soup = BeautifulSoup(html, "lxml")
    # Удаляем служебные теги
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()

    return soup.get_text(separator="\n", strip=True)[:3000]
