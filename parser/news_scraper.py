import asyncio
import logging

import feedparser
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# Профильные RSS-источники по недвижимости Турции и Аланьи
RSS_FEEDS = [
    # Англоязычные новости по недвижимости Турции
    "https://www.dailysabah.com/rss/real-estate",
    "https://www.propertyturkey.com/blog-turkey-property?format=feed&type=rss",
    # Турецкая экономика и рынок недвижимости
    "https://www.hurriyetdailynews.com/rss.aspx?pageID=238&nID=132950&NewsCatID=344",
    # Общие новости Турции (экономика, инвестиции)
    "https://www.aa.com.tr/en/rss/default?cat=economy",
    "https://www.trthaber.com/kategori/ekonomi.rss",
]

# Если RSS недоступен — используем резервные темы для генерации постов
FALLBACK_TOPICS = [
    "Рынок недвижимости Аланьи: тенденции и прогнозы",
    "Почему инвесторы выбирают Аланью в 2026 году",
    "Топ-5 районов Аланьи для покупки апартаментов",
    "Аренда vs покупка недвижимости в Турции: что выгоднее",
    "Как получить ВНЖ через покупку недвижимости в Турции",
    "Инфраструктура Аланьи: школы, больницы, транспорт",
    "Сезонность рынка аренды в Аланье: когда выгоднее покупать",
    "Турецкий рынок недвижимости: рост цен и инвестиционный потенциал",
]


def _parse_feed(url: str):
    return feedparser.parse(url)


async def fetch_latest_news() -> list[dict]:
    """
    Асинхронно парсит RSS-ленты профильных источников.
    Если все источники недоступны — возвращает резервные темы.
    """
    items: list[dict] = []

    for feed_url in RSS_FEEDS:
        try:
            parsed = await asyncio.to_thread(_parse_feed, feed_url)
            if not parsed.entries:
                logger.warning(f"Пустая лента: {feed_url}")
                continue
            for entry in parsed.entries[:3]:
                summary_html = entry.get("summary", "")
                summary = BeautifulSoup(summary_html, "lxml").get_text(" ", strip=True)
                items.append(
                    {
                        "title": entry.get("title", ""),
                        "summary": summary,
                        "link": entry.get("link", ""),
                        "source": feed_url,
                    }
                )
            logger.info(f"Получено {len(parsed.entries[:3])} новостей из: {feed_url}")
        except Exception as e:
            logger.error(f"Ошибка парсинга {feed_url}: {e}")
            continue

    # Если новостей не получили — используем резервные темы
    if not items:
        logger.warning("Все RSS недоступны. Используем резервные темы.")
        import random
        topic = random.choice(FALLBACK_TOPICS)
        items.append({
            "title": topic,
            "summary": "",
            "link": "",
            "source": "fallback",
        })

    return items
