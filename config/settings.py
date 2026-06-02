"""
config/settings.py — Ядро конфигурации системы.

Загружает переменные окружения из .env и экспортирует единый
объект Settings, используемый во всех модулях агента.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

# Загружаем .env из корня проекта
_BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(_BASE_DIR / ".env")


def _require(key: str) -> str:
    """Читает обязательную переменную окружения; падает с понятной ошибкой."""
    value = os.getenv(key)
    if not value:
        raise RuntimeError(
            f"[config] Обязательная переменная окружения '{key}' не задана. "
            "Проверь файл .env."
        )
    return value


def _int_list(key: str) -> list[int]:
    """Читает переменную как список целых чисел через запятую."""
    raw = os.getenv(key, "")
    return [int(x.strip()) for x in raw.split(",") if x.strip().isdigit()]


def _str_list(key: str) -> list[str]:
    """Читает переменную как список строк через запятую."""
    raw = os.getenv(key, "")
    return [x.strip() for x in raw.split(",") if x.strip()]


@dataclass(frozen=True)
class Settings:
    # ── Telegram ──────────────────────────────────────────────────────────
    telegram_bot_token: str
    admin_ids: list[int]
    target_channel_id: str

    # ── OpenAI ────────────────────────────────────────────────────────────
    openai_api_key: str
    openai_text_model: str
    openai_image_model: str

    # ── Scheduler ─────────────────────────────────────────────────────────
    scheduler_timezone: str
    news_publish_hour: int
    news_publish_minute: int

    # ── Parser ────────────────────────────────────────────────────────────
    rss_feeds: list[str]
    max_news_items: int

    # ── Служебные ─────────────────────────────────────────────────────────
    base_dir: Path = field(default_factory=lambda: _BASE_DIR)


def load_settings() -> Settings:
    """Фабрика: читает .env и возвращает иммутабельный объект Settings."""
    return Settings(
        telegram_bot_token=_require("TELEGRAM_BOT_TOKEN"),
        admin_ids=_int_list("ADMIN_IDS"),
        target_channel_id=os.getenv("TARGET_CHANNEL_ID", ""),
        openai_api_key=_require("OPENAI_API_KEY"),
        openai_text_model=os.getenv("OPENAI_TEXT_MODEL", "gpt-4o"),
        openai_image_model=os.getenv("OPENAI_IMAGE_MODEL", "dall-e-3"),
        scheduler_timezone=os.getenv("SCHEDULER_TIMEZONE", "Europe/Istanbul"),
        news_publish_hour=int(os.getenv("NEWS_PUBLISH_HOUR", "9")),
        news_publish_minute=int(os.getenv("NEWS_PUBLISH_MINUTE", "0")),
        rss_feeds=_str_list("RSS_FEEDS"),
        max_news_items=int(os.getenv("MAX_NEWS_ITEMS", "5")),
    )


# Синглтон — импортируется остальными модулями
settings: Settings = load_settings()
