"""
bot/middlewares.py — Middleware-слой Telegram-бота.

LoggingMiddleware: логирует каждое входящее обновление.
AdminOnlyMiddleware: блокирует не-администраторов для приватных команд.
"""

from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject

from config.settings import settings

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseMiddleware):
    """Логирует каждое входящее сообщение."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        if isinstance(event, Message):
            user = event.from_user
            logger.info(
                "Входящее сообщение | user_id=%s | username=@%s | text=%.80r",
                user.id if user else "?",
                user.username if user else "?",
                event.text or event.caption or "",
            )
        return await handler(event, data)


class AdminOnlyMiddleware(BaseMiddleware):
    """
    Пропускает обновление только если отправитель входит в ADMIN_IDS.
    Применяется к роутеру с административными командами.
    """

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        if isinstance(event, Message) and event.from_user:
            if event.from_user.id not in settings.admin_ids:
                await event.answer("⛔ Доступ запрещён. Только для администраторов.")
                return None
        return await handler(event, data)
