import logging
from pathlib import Path

from aiogram import Bot
from aiogram.types import FSInputFile

from config.settings import CHANNEL_ID


async def publish_post(bot: Bot, text: str, image: Path | None = None) -> None:
    try:
        if isinstance(image, Path) and image.exists():
            photo = FSInputFile(image)
            await bot.send_photo(chat_id=CHANNEL_ID, photo=photo, caption=text)
            image.unlink(missing_ok=True)
        else:
            await bot.send_message(chat_id=CHANNEL_ID, text=text)
    except Exception:
        logging.exception("Ошибка при отправке поста")
