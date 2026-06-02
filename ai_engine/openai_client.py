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


async def generate_post_image(prompt: str) -> str:
    response = await client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        quality="hd",
        n=1,
    )
    return response.data[0].url
