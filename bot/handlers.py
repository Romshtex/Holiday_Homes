"""
bot/handlers.py — Обработчики команд и callback-кнопок.

Роутеры:
  • user_router   — публичные команды (/start, /help, /ask, /news, /image).
  • admin_router  — административные команды (/digest, /broadcast).
"""

from __future__ import annotations

import logging

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message, URLInputFile

from ai_engine.openai_client import (
    analyze_property_query,
    generate_digest,
    generate_news_cover,
    generate_property_image,
)
from bot.keyboards import (
    back_to_menu_keyboard,
    main_menu_keyboard,
    property_type_keyboard,
)
from bot.middlewares import AdminOnlyMiddleware, LoggingMiddleware
from config.settings import settings
from parser.news_parser import NewsItem, fetch_all_feeds

logger = logging.getLogger(__name__)

# ─── Роутер пользователей ────────────────────────────────────────────────────
user_router = Router(name="user")
user_router.message.middleware(LoggingMiddleware())

# ─── Роутер администраторов ──────────────────────────────────────────────────
admin_router = Router(name="admin")
admin_router.message.middleware(LoggingMiddleware())
admin_router.message.middleware(AdminOnlyMiddleware())


# ─────────────────────────────────────────────────────────────────────────────
# FSM: состояния для диалоговых сценариев
# ─────────────────────────────────────────────────────────────────────────────


class PropertySearch(StatesGroup):
    waiting_for_description = State()


class ImageGen(StatesGroup):
    waiting_for_prompt = State()


# ─────────────────────────────────────────────────────────────────────────────
# Публичные хэндлеры
# ─────────────────────────────────────────────────────────────────────────────


@user_router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    name = message.from_user.first_name if message.from_user else "друг"
    await message.answer(
        f"👋 Привет, *{name}*\\!\n\n"
        "Я — *Алания Агент* 🤖\n"
        "Твой персональный помощник по рынку недвижимости в Алании, Турция\\.\n\n"
        "Что тебя интересует?",
        reply_markup=main_menu_keyboard(),
        parse_mode="MarkdownV2",
    )


@user_router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    help_text = (
        "📋 *Команды агента:*\n\n"
        "/start — Главное меню\n"
        "/ask — Задать вопрос о недвижимости\n"
        "/news — Последние новости Алании\n"
        "/image — Сгенерировать изображение объекта\n"
        "/help — Эта справка\n\n"
        "Или просто напиши свой вопрос — я отвечу\\!"
    )
    await message.answer(help_text, parse_mode="MarkdownV2")


@user_router.message(Command("ask"))
async def cmd_ask(message: Message, state: FSMContext) -> None:
    await state.set_state(PropertySearch.waiting_for_description)
    await message.answer(
        "🏠 Опиши, что ищешь:\n\n"
        "_Например: «Апартаменты 2+1 до 100к€ в Обе, желательно близко к морю»_",
        reply_markup=back_to_menu_keyboard(),
        parse_mode="Markdown",
    )


@user_router.message(PropertySearch.waiting_for_description)
async def handle_property_description(message: Message, state: FSMContext) -> None:
    await state.clear()
    user_text = message.text or ""
    if not user_text.strip():
        await message.answer("Пожалуйста, опиши параметры поиска текстом.")
        return

    thinking = await message.answer("🔍 Анализирую запрос…")
    try:
        response = await analyze_property_query(user_text)
        await thinking.delete()
        await message.answer(response, reply_markup=main_menu_keyboard())
    except Exception as exc:
        logger.error("Ошибка GPT-4o: %s", exc)
        await thinking.edit_text("⚠️ Произошла ошибка при обращении к ИИ. Попробуй позже.")


@user_router.message(Command("news"))
async def cmd_news(message: Message) -> None:
    thinking = await message.answer("📡 Синхронизирую данные с лентами…")
    try:
        items: list[NewsItem] = await fetch_all_feeds()
        if not items:
            await thinking.edit_text("😔 Новостей пока нет. Попробуй позже.")
            return

        news_dicts = [{"title": it.title, "summary": it.summary} for it in items]
        digest = await generate_digest(news_dicts)
        await thinking.delete()
        await message.answer(digest, reply_markup=main_menu_keyboard())
    except Exception as exc:
        logger.error("Ошибка при получении новостей: %s", exc)
        await thinking.edit_text("⚠️ Не удалось загрузить новости. Попробуй позже.")


@user_router.message(Command("image"))
async def cmd_image(message: Message, state: FSMContext) -> None:
    await state.set_state(ImageGen.waiting_for_prompt)
    await message.answer(
        "🖼 Опиши объект или сцену для генерации изображения:\n\n"
        "_Например: «Апартаменты с панорамным видом на море, бассейн, закат»_",
        reply_markup=back_to_menu_keyboard(),
        parse_mode="Markdown",
    )


@user_router.message(ImageGen.waiting_for_prompt)
async def handle_image_prompt(message: Message, state: FSMContext) -> None:
    await state.clear()
    prompt = message.text or ""
    if not prompt.strip():
        await message.answer("Пожалуйста, опиши объект текстом.")
        return

    thinking = await message.answer("🎨 Генерирую изображение через DALL-E 3…")
    try:
        image_url = await generate_property_image(prompt)
        await thinking.delete()
        await message.answer_photo(
            photo=URLInputFile(image_url),
            caption=f"🖼 *{prompt[:80]}*",
            parse_mode="Markdown",
            reply_markup=main_menu_keyboard(),
        )
    except Exception as exc:
        logger.error("Ошибка DALL-E 3: %s", exc)
        await thinking.edit_text("⚠️ Ошибка генерации изображения. Попробуй позже.")


@user_router.message(F.text & ~F.text.startswith("/"))
async def handle_free_text(message: Message) -> None:
    """Отвечает на произвольный текст пользователя как консультант."""
    user_text = message.text or ""
    thinking = await message.answer("💭 Думаю…")
    try:
        response = await analyze_property_query(user_text)
        await thinking.delete()
        await message.answer(response, reply_markup=main_menu_keyboard())
    except Exception as exc:
        logger.error("Ошибка GPT-4o free text: %s", exc)
        await thinking.edit_text("⚠️ Произошла ошибка. Попробуй позже.")


# ─────────────────────────────────────────────────────────────────────────────
# Callback-хэндлеры (inline-кнопки)
# ─────────────────────────────────────────────────────────────────────────────


@user_router.callback_query(F.data == "action:menu")
async def cb_menu(call: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.answer(
        "Главное меню:", reply_markup=main_menu_keyboard()
    )
    await call.answer()


@user_router.callback_query(F.data == "action:find_property")
async def cb_find_property(call: CallbackQuery) -> None:
    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.answer(
        "Выбери тип недвижимости:", reply_markup=property_type_keyboard()
    )
    await call.answer()


@user_router.callback_query(F.data.startswith("prop_type:"))
async def cb_property_type(call: CallbackQuery, state: FSMContext) -> None:
    prop_type_map = {
        "apartment": "апартаменты",
        "villa": "виллу",
        "new_build": "новострой",
        "beachfront": "недвижимость у моря",
    }
    key = call.data.split(":", 1)[1]
    label = prop_type_map.get(key, key)

    await state.set_state(PropertySearch.waiting_for_description)
    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.answer(
        f"🏠 Ищем *{label}*. Уточни параметры:\n\n"
        "_Например: бюджет, район, площадь, этаж, вид…_",
        parse_mode="Markdown",
        reply_markup=back_to_menu_keyboard(),
    )
    await call.answer()


@user_router.callback_query(F.data == "action:latest_news")
async def cb_latest_news(call: CallbackQuery) -> None:
    await call.answer("📡 Загружаю новости…")
    await call.message.edit_reply_markup(reply_markup=None)
    thinking = await call.message.answer("📡 Синхронизирую данные с лентами…")
    try:
        items: list[NewsItem] = await fetch_all_feeds()
        if not items:
            await thinking.edit_text("😔 Новостей пока нет. Попробуй позже.")
            return
        news_dicts = [{"title": it.title, "summary": it.summary} for it in items]
        digest = await generate_digest(news_dicts)
        await thinking.delete()
        await call.message.answer(digest, reply_markup=main_menu_keyboard())
    except Exception as exc:
        logger.error("Ошибка при получении новостей: %s", exc)
        await thinking.edit_text("⚠️ Не удалось загрузить новости.")


@user_router.callback_query(F.data == "action:gen_image")
async def cb_gen_image(call: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(ImageGen.waiting_for_prompt)
    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.answer(
        "🖼 Опиши объект для генерации изображения:\n\n"
        "_Например: «Пентхаус с видом на Средиземное море, рассвет»_",
        parse_mode="Markdown",
        reply_markup=back_to_menu_keyboard(),
    )
    await call.answer()


@user_router.callback_query(F.data == "action:contact_manager")
async def cb_contact_manager(call: CallbackQuery) -> None:
    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.answer(
        "📞 *Связаться с менеджером*\n\n"
        "Наш менеджер ответит вам в рабочее время (09:00–18:00 GMT+3).\n\n"
        "✉️ Email: info@holiday-homes.ru\n"
        "💬 WhatsApp/Telegram: +90 XXX XXX XX XX",
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard(),
    )
    await call.answer()


# ─────────────────────────────────────────────────────────────────────────────
# Административные хэндлеры
# ─────────────────────────────────────────────────────────────────────────────


@admin_router.message(Command("digest"))
async def cmd_digest(message: Message) -> None:
    """Вручную публикует дайджест новостей в канале (только для админов)."""
    thinking = await message.answer("🔄 Формирую дайджест…")
    try:
        items: list[NewsItem] = await fetch_all_feeds()
        news_dicts = [{"title": it.title, "summary": it.summary} for it in items]
        digest = await generate_digest(news_dicts)

        # Генерируем обложку для дайджеста по первой новости
        if items:
            cover_url = await generate_news_cover(items[0].title)
            await message.bot.send_photo(
                chat_id=settings.target_channel_id,
                photo=URLInputFile(cover_url),
                caption=digest,
            )
        else:
            await message.bot.send_message(
                chat_id=settings.target_channel_id, text=digest
            )

        await thinking.edit_text("✅ Дайджест опубликован в канале.")
    except Exception as exc:
        logger.error("Ошибка при публикации дайджеста: %s", exc)
        await thinking.edit_text(f"⚠️ Ошибка публикации: {exc}")


@admin_router.message(Command("broadcast"))
async def cmd_broadcast(message: Message) -> None:
    """
    Рассылает текст из команды в канал.
    Использование: /broadcast Текст сообщения
    """
    text = message.text or ""
    payload = text.removeprefix("/broadcast").strip()
    if not payload:
        await message.answer("Использование: /broadcast Текст сообщения")
        return

    try:
        await message.bot.send_message(
            chat_id=settings.target_channel_id, text=payload
        )
        await message.answer("✅ Сообщение отправлено в канал.")
    except Exception as exc:
        logger.error("Ошибка broadcast: %s", exc)
        await message.answer(f"⚠️ Ошибка: {exc}")
