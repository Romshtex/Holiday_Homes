from config.settings import CHANNEL_ID


async def publish_post(bot, text: str, image_url: str) -> None:
    await bot.send_photo(chat_id=CHANNEL_ID, photo=image_url, caption=text)
