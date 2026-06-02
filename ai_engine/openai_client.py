import base64
from pathlib import Path

from openai import AsyncOpenAI

from ai_engine.prompt import SYSTEM_PROMPT
from config.settings import OPENAI_API_KEY


client = AsyncOpenAI(api_key=OPENAI_API_KEY)


async def generate_post_text(topic: str) -> str:
    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Подготовь пост для Telegram-канала на тему: {topic}",
            },
        ],
        temperature=0.7,
    )
    return (response.choices[0].message.content or "").strip()


async def generate_post_image(prompt: str) -> Path | None:
    try:
        response = await client.images.generate(
            model="gpt-image-1",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        image_b64 = response.data[0].b64_json
        image_bytes = base64.b64decode(image_b64)
        path = Path("generated_image.png")
        path.write_bytes(image_bytes)
        return path
    except Exception as e:
        import logging
        logging.error(f"Ошибка генерации изображения: {e}")
        return None
