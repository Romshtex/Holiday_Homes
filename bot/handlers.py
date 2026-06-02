import logging
from pathlib import Path

from aiogram import Bot
from aiogram.types import FSInputFile, URLInputFile

from config.settings import CHANNEL_ID


async def publish_post(bot: Bot, text: str, image: Path | str | None = None) -> None:
    try:
        if isinstance(image, Path) and image.exists():
            # Локальный файл (gpt-image-1)
            photo = FSInputFile(image)
            await bot.send_photo(chat_id=CHANNEL_ID, photo=photo, caption=text)
            image.unlink(missing_ok=True)  # удаляем временный файл
        elif isinstance(image, str) and image.startswith("http"):
            # URL (на случай будущих моделей)
            await bot.send_photo(chat_id=CHANNEL_ID, photo=URLInputFile(image), caption=text)
        else:
            # Только текст если картинка не сгенерировалась
            await bot.send_message(chat_id=CHANNEL_ID, text=text)
    except Exception:
        logging.exception("Ошибка при отправке поста")
