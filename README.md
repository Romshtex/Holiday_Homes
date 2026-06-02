# Holiday Homes AI Agent

Автономный AI-агент для агентства недвижимости в Аланье (Турция), который собирает новости, генерирует контент и публикует посты в Telegram-канал.

## Возможности

- Асинхронный Telegram-бот на **aiogram 3.x**.
- Сбор актуальных новостей через RSS и парсинг HTML.
- Генерация текстов постов через **GPT-4o**.
- Генерация изображений через **DALL-E 3**.
- Автоматическая публикация по расписанию (ежедневно в 09:00, Europe/Istanbul).

## Установка и запуск

```bash
git clone https://github.com/Romshtex/Holiday_Homes.git
cd Holiday_Homes
python -m venv venv
source venv/bin/activate  # Windows: venv\\Scripts\\activate
pip install -r requirements.txt
cp .env.example .env
```

Заполните `.env`:

```env
TG_TOKEN=your_telegram_bot_token_here
OPENAI_API_KEY=your_openai_api_key_here
CHANNEL_ID=@your_channel_id_here
```

Запуск:

```bash
python main.py
```

## Структура проекта

```text
Holiday_Homes/
├── .env.example
├── .gitignore
├── requirements.txt
├── README.md
├── main.py
├── config/
│   ├── __init__.py
│   └── settings.py
├── parser/
│   ├── __init__.py
│   └── news_scraper.py
├── ai_engine/
│   ├── __init__.py
│   ├── prompt.py
│   └── openai_client.py
└── bot/
    ├── __init__.py
    ├── handlers.py
    └── sender.py
```

## Деплой через systemd

Пример unit-файла (`/etc/systemd/system/alanya_agent.service`):

```ini
[Unit]
Description=Holiday Homes AI Agent
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/Holiday_Homes
ExecStart=/home/ubuntu/Holiday_Homes/venv/bin/python /home/ubuntu/Holiday_Homes/main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Команды управления:

```bash
sudo systemctl daemon-reload
sudo systemctl enable alanya_agent
sudo systemctl restart alanya_agent
sudo systemctl status alanya_agent
```
