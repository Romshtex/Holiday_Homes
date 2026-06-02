"""
ai_engine/openai_client.py — Ядро интеллекта агента.

Асинхронный клиент для:
  • GPT-4o  — аналитика текста, перевод, саммаризация, генерация постов.
  • DALL-E 3 — создание фотореалистичных изображений для публикаций.
"""

from __future__ import annotations

import logging

from openai import AsyncOpenAI

from config.settings import settings

logger = logging.getLogger(__name__)

# Единственный экземпляр асинхронного клиента — создаётся один раз при импорте
_client = AsyncOpenAI(api_key=settings.openai_api_key)


# ─────────────────────────────────────────────────────────────────────────────
# Текстовая аналитика — GPT-4o
# ─────────────────────────────────────────────────────────────────────────────


async def summarize_news(title: str, body: str) -> str:
    """
    Создаёт короткий аналитический пост на русском языке
    на основе заголовка и тела новости.
    Возвращает готовый текст для публикации в Telegram-канале.
    """
    prompt = (
        "Ты — эксперт по рынку недвижимости и туризму в Алании, Турция. "
        "На основе приведённой новости напиши лаконичный аналитический пост "
        "для Telegram-канала агентства недвижимости. "
        "Структура:\n"
        "1. Заголовок (эмодзи + тема)\n"
        "2. Суть (2-3 предложения)\n"
        "3. Влияние на рынок недвижимости Алании (1-2 предложения)\n"
        "4. Вывод / призыв к действию\n\n"
        f"Заголовок оригинала: {title}\n\n"
        f"Текст: {body}"
    )

    response = await _client.chat.completions.create(
        model=settings.openai_text_model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=600,
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()


async def translate_to_russian(text: str) -> str:
    """Переводит произвольный текст на русский язык."""
    response = await _client.chat.completions.create(
        model=settings.openai_text_model,
        messages=[
            {
                "role": "system",
                "content": "Ты профессиональный переводчик. Переводи точно, без добавлений.",
            },
            {
                "role": "user",
                "content": f"Переведи на русский язык:\n\n{text}",
            },
        ],
        max_tokens=1000,
        temperature=0.3,
    )
    return response.choices[0].message.content.strip()


async def analyze_property_query(user_message: str) -> str:
    """
    Отвечает на вопрос пользователя о недвижимости в Алании.
    Выступает в роли консультанта агентства.
    """
    system_prompt = (
        "Ты — опытный консультант агентства недвижимости в Алание (Турция). "
        "Ты знаешь местный рынок: районы (Оба, Махмутлар, Авсаллар, Кестель, Центр), "
        "юридические нюансы покупки для иностранцев, популярные ЖК, ценовые диапазоны. "
        "Общайся дружелюбно, профессионально и по делу. "
        "Если нужна дополнительная информация — уточняй. "
        "Отвечай на языке вопроса пользователя."
    )

    response = await _client.chat.completions.create(
        model=settings.openai_text_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        max_tokens=800,
        temperature=0.6,
    )
    return response.choices[0].message.content.strip()


async def generate_digest(news_items: list[dict]) -> str:
    """
    Генерирует ежедневный дайджест новостей Алании на русском языке.

    Args:
        news_items: список словарей с ключами 'title' и 'summary'.

    Returns:
        Готовый текст дайджеста для Telegram.
    """
    if not news_items:
        return "📭 Новостей для дайджеста нет."

    items_text = "\n\n".join(
        f"{i + 1}. {item['title']}\n{item['summary']}"
        for i, item in enumerate(news_items)
    )

    prompt = (
        "Ты — аналитик рынка недвижимости Алании, Турция. "
        "Составь ежедневный дайджест на русском языке для Telegram-канала. "
        "Формат:\n"
        "🗞 *Дайджест Алании — [дата]*\n\n"
        "Краткое вступление (1-2 предложения о дне).\n\n"
        "Затем по каждой новости:\n"
        "• Эмодзи + тема — 1-2 предложения сути.\n\n"
        "В конце: вывод о влиянии на рынок недвижимости (2-3 предложения).\n\n"
        f"Новости:\n{items_text}"
    )

    response = await _client.chat.completions.create(
        model=settings.openai_text_model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=900,
        temperature=0.65,
    )
    return response.choices[0].message.content.strip()


# ─────────────────────────────────────────────────────────────────────────────
# Генерация изображений — DALL-E 3
# ─────────────────────────────────────────────────────────────────────────────


async def generate_property_image(description: str) -> str:
    """
    Генерирует фотореалистичное изображение недвижимости через DALL-E 3.

    Args:
        description: текстовое описание объекта / сцены на английском.

    Returns:
        URL изображения (действителен ~60 минут).
    """
    # DALL-E лучше работает с промптами на английском
    dalle_prompt = (
        f"Photorealistic luxury real estate photo: {description}. "
        "Mediterranean style, Alanya Turkey, bright sunny day, "
        "high quality architectural photography, 8K resolution."
    )

    logger.info("Генерация изображения DALL-E 3: %.80s…", description)

    response = await _client.images.generate(
        model=settings.openai_image_model,
        prompt=dalle_prompt,
        n=1,
        size="1024x1024",
        quality="hd",
        style="natural",
    )

    url = response.data[0].url
    logger.info("Изображение сгенерировано: %s", url)
    return url


async def generate_news_cover(news_title: str) -> str:
    """
    Генерирует обложку для новостного поста (1:1, фотореализм).

    Args:
        news_title: заголовок новости на русском.

    Returns:
        URL изображения.
    """
    dalle_prompt = (
        f"Photorealistic news cover image related to: '{news_title}'. "
        "Set in Alanya, Turkey. Mediterranean coast, modern architecture, "
        "vibrant colors. Professional news photography style."
    )

    response = await _client.images.generate(
        model=settings.openai_image_model,
        prompt=dalle_prompt,
        n=1,
        size="1024x1024",
        quality="standard",
        style="natural",
    )

    return response.data[0].url
