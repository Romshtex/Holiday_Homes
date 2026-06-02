import asyncio
import logging

from aiogram import Bot, Dispatcher
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from zoneinfo import ZoneInfo

from ai_engine.openai_client import generate_post_image, generate_post_text
from bot.handlers import router
from bot.sender import publish_post
from config.settings import TG_TOKEN
from parser.news_scraper import fetch_latest_news


async def scheduled_publication(bot: Bot) -> None:
    try:
        news = await fetch_latest_news()
        topic = news[0]["title"] if news else "Недвижимость в Аланье: актуальные тренды"
        post_text = await generate_post_text(topic)
        image_path = None
        try:
            image_path = await generate_post_image(
                f"Современная недвижимость в Аланье, тема: {topic}"
            )
        except Exception:
            logging.exception("Ошибка при генерации изображения, публикуем только текст")

        await publish_post(bot, post_text, image_path)
    except Exception:
        logging.exception("Ошибка при публикации поста")


async def main() -> None:
    logging.basicConfig(level=logging.INFO)

    bot = Bot(token=TG_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)

    scheduler = AsyncIOScheduler(timezone=ZoneInfo("Europe/Istanbul"))
    scheduler.add_job(
        scheduled_publication,
        trigger=CronTrigger(hour=9, minute=0, timezone=ZoneInfo("Europe/Istanbul")),
        args=[bot],
    )
    scheduler.start()

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
