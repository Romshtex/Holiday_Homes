import asyncio
import base64
from pathlib import Path

from openai import AsyncOpenAI

from ai_engine.prompt import SYSTEM_PROMPT
from config.settings import OPENAI_API_KEY


client = AsyncOpenAI(api_key=OPENAI_API_KEY)
GENERATED_IMAGE_PATH = Path("generated_image.png")


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


async def generate_post_image(prompt: str) -> Path:
    response = await client.images.generate(
        model="gpt-image-1",
        prompt=prompt,
        size="1024x1024",
        quality="standard",
        n=1,
    )
    image_base64 = response.data[0].b64_json
    if not image_base64:
        raise ValueError("OpenAI did not return image data")

    image_bytes = base64.b64decode(image_base64)
    await asyncio.to_thread(GENERATED_IMAGE_PATH.write_bytes, image_bytes)
    return GENERATED_IMAGE_PATH
