from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

from ai_engine.openai_client import generate_post_text, generate_post_image
from bot.sender import publish_post
from parser.news_scraper import fetch_latest_news

router = Router()


def main_menu() -> ReplyKeyboardMarkup:
    """Генерирует системную клавиатуру в нижней части экрана."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📢 POST")]
        ],
        resize_keyboard=True,
        input_field_placeholder="Ожидаю команды..."
    )


@router.message(Command("start"))
async def cmd_start(message: Message) -> None:
    await message.answer(
        "👋 Я AI-агент Holiday Homes по недвижимости в Аланье.\n\nВыбери действие:",
        reply_markup=main_menu()
    )


@router.message(Command("status"))
async def cmd_status(message: Message) -> None:
    await message.answer("✅ Агент активен и готов к публикациям.", reply_markup=main_menu())


@router.message(Command("post"))
async def cmd_post(message: Message) -> None:
    await _do_publish(message.bot, message)


@router.message(F.text == "📢 POST")
async def msg_post(message: Message) -> None:
    # Перехват текстового сигнала от Reply-клавиатуры
    await _do_publish(message.bot, message)


async def _do_publish(bot, message: Message) -> None:
    await message.answer("⏳ Генерирую пост и изображение, подожди 20-30 секунд...")
    try:
        news = await fetch_latest_news()
        topic = news[0]["title"] if news else "Недвижимость в Аланье: актуальные тренды"
        post_text = await generate_post_text(topic)
        image_path = await generate_post_image(topic)
        await publish_post(bot, post_text, image_path)
        await message.answer("✅ Пост опубликован в канал!", reply_markup=main_menu())
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}", reply_markup=main_menu())
