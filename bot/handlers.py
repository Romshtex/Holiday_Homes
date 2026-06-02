from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from ai_engine.openai_client import generate_post_text, generate_post_image
from bot.sender import publish_post
from parser.news_scraper import fetch_latest_news

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message) -> None:
    await message.answer("Привет! Я AI-агент Holiday Homes по недвижимости в Аланье.")


@router.message(Command("status"))
async def cmd_status(message: Message) -> None:
    await message.answer("Агент активен и готов к публикациям.")


@router.message(Command("post"))
async def cmd_post(message: Message) -> None:
    await message.answer("⏳ Генерирую пост и изображение, подожди 20-30 секунд...")
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
            await message.answer("⚠️ Не удалось сгенерировать изображение, публикую только текст.")

        await publish_post(message.bot, post_text, image_path)
        await message.answer("✅ Пост опубликован в канал!")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")
