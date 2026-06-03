import asyncio
from pathlib import Path

from aiogram.types import FSInputFile, URLInputFile

from config.settings import CHANNEL_ID


async def publish_post(bot, text: str, image_source: str | Path | None = None) -> None:
    if image_source is None:
        await bot.send_message(chat_id=CHANNEL_ID, text=text)
        return

    # Динамическая маршрутизация: лимит Telegram для caption — 1024 символа
    caption = text if len(text) <= 1024 else None

    image_path = Path(image_source)
    if await asyncio.to_thread(image_path.exists):
        try:
            await bot.send_photo(
                chat_id=CHANNEL_ID,
                photo=FSInputFile(image_path),
                caption=caption,
            )
            # Если текст превысил лимит, отправляем его следом обычным сообщением
            if caption is None:
                await bot.send_message(chat_id=CHANNEL_ID, text=text)
        finally:
            if image_path.name == "generated_image.png":
                await asyncio.to_thread(image_path.unlink, True)
        return

    if isinstance(image_source, str) and image_source.startswith(("http://", "https://")):
        await bot.send_photo(
            chat_id=CHANNEL_ID,
            photo=URLInputFile(image_source),
            caption=caption,
        )
        if caption is None:
            await bot.send_message(chat_id=CHANNEL_ID, text=text)
        return

    raise FileNotFoundError(f"Image file not found: {image_source}")
        finally:
            if image_path.name == "generated_image.png":
                await asyncio.to_thread(image_path.unlink, True)
        return

    if isinstance(image_source, str) and image_source.startswith(("http://", "https://")):
        await bot.send_photo(
            chat_id=CHANNEL_ID,
            photo=URLInputFile(image_source),
            caption=text,
        )
        return

    raise FileNotFoundError(f"Image file not found: {image_source}")
