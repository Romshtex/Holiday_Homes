"""
bot/keyboards.py — Inline-клавиатуры Telegram-бота.
"""

from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def main_menu_keyboard() -> InlineKeyboardMarkup:
    """Главное меню агента."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="🏠 Подобрать недвижимость",
            callback_data="action:find_property",
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="🗞 Последние новости Алании",
            callback_data="action:latest_news",
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="🖼 Сгенерировать изображение",
            callback_data="action:gen_image",
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="📞 Связаться с менеджером",
            callback_data="action:contact_manager",
        )
    )
    return builder.as_markup()


def back_to_menu_keyboard() -> InlineKeyboardMarkup:
    """Кнопка возврата в главное меню."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="◀️ Главное меню", callback_data="action:menu")
    )
    return builder.as_markup()


def property_type_keyboard() -> InlineKeyboardMarkup:
    """Выбор типа недвижимости."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🏢 Апартаменты", callback_data="prop_type:apartment"),
        InlineKeyboardButton(text="🏡 Вилла", callback_data="prop_type:villa"),
    )
    builder.row(
        InlineKeyboardButton(text="🏗 Новострой", callback_data="prop_type:new_build"),
        InlineKeyboardButton(text="🏖 У моря", callback_data="prop_type:beachfront"),
    )
    builder.row(
        InlineKeyboardButton(text="◀️ Назад", callback_data="action:menu")
    )
    return builder.as_markup()
