"""
main.py — Точка входа. Синхронизирует все потоки Системы.

Запускает:
  • aiogram Dispatcher (Telegram-бот, long-polling)
  • APScheduler (ежедневная публикация дайджеста новостей)
"""

from __future__ import annotations

import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import URLInputFile
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from bot.handlers import admin_router, user_router
from config.settings import settings
from ai_engine.openai_client import generate_digest, generate_news_cover
from parser.news_parser import NewsItem, fetch_all_feeds

# ─── Настройка логирования ────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Scheduled job: ежедневный дайджест
# ─────────────────────────────────────────────────────────────────────────────


async def job_publish_news(bot: Bot) -> None:
    """
    Плановая задача: собирает новости, генерирует дайджест через GPT-4o,
    создаёт обложку через DALL-E 3 и публикует в TARGET_CHANNEL_ID.
    """
    logger.info("▶ job_publish_news: старт")

    if not settings.target_channel_id:
        logger.warning("TARGET_CHANNEL_ID не задан — публикация пропущена.")
        return

    try:
        items: list[NewsItem] = await fetch_all_feeds()
        if not items:
            logger.warning("Нет новостей для публикации.")
            return

        news_dicts = [{"title": it.title, "summary": it.summary} for it in items]
        digest = await generate_digest(news_dicts)

        # Обложка — по заголовку первой новости
        cover_url = await generate_news_cover(items[0].title)

        await bot.send_photo(
            chat_id=settings.target_channel_id,
            photo=URLInputFile(cover_url),
            caption=digest,
        )
        logger.info("✅ Дайджест опубликован в %s", settings.target_channel_id)

    except Exception as exc:
        logger.error("❌ Ошибка в job_publish_news: %s", exc, exc_info=True)


# ─────────────────────────────────────────────────────────────────────────────
# Инициализация и запуск
# ─────────────────────────────────────────────────────────────────────────────


async def main() -> None:
    logger.info("🚀 Алания Агент запускается…")

    # ── Telegram Bot & Dispatcher ──────────────────────────────────────────
    bot = Bot(
        token=settings.telegram_bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=MemoryStorage())

    # Регистрируем роутеры (порядок важен: сначала admin, потом user)
    dp.include_router(admin_router)
    dp.include_router(user_router)

    # ── APScheduler ────────────────────────────────────────────────────────
    scheduler = AsyncIOScheduler(timezone=settings.scheduler_timezone)
    scheduler.add_job(
        job_publish_news,
        trigger="cron",
        hour=settings.news_publish_hour,
        minute=settings.news_publish_minute,
        kwargs={"bot": bot},
        id="daily_news_digest",
        replace_existing=True,
    )
    scheduler.start()
    logger.info(
        "⏰ Планировщик запущен. Дайджест — %02d:%02d (%s)",
        settings.news_publish_hour,
        settings.news_publish_minute,
        settings.scheduler_timezone,
    )

    # ── Запуск polling ─────────────────────────────────────────────────────
    try:
        logger.info("📡 Бот запущен. Ожидаю обновления…")
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        scheduler.shutdown(wait=False)
        await bot.session.close()
        logger.info("🔴 Агент остановлен.")


if __name__ == "__main__":
    asyncio.run(main())
