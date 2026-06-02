# Holiday Homes — Алания Агент 🤖

**Автономный ИИ-Агент** для агентства недвижимости в Алание (Турция).

Telegram-бот, работающий на GPT-4o и DALL-E 3, который:
- Консультирует клиентов по рынку недвижимости Алании.
- Собирает и анализирует актуальные новости через RSS-ленты.
- Ежедневно публикует новостной дайджест в Telegram-канал.
- Генерирует фотореалистичные изображения объектов через DALL-E 3.

---

## Стек

| Слой | Технология |
|------|-----------|
| Язык | Python 3.10+ (asyncio) |
| Telegram | aiogram 3.x |
| ИИ | OpenAI API (GPT-4o + DALL-E 3) |
| Планировщик | APScheduler 3.x |
| Парсинг | feedparser + BeautifulSoup |
| Деплой | Linux VPS + systemd |

---

## Структура проекта

```
Holiday_Homes/
├── main.py                  # Точка входа
├── alanya_agent.service     # systemd unit
├── requirements.txt
├── .env.example             # Шаблон переменных окружения
├── config/
│   └── settings.py          # Загрузка конфигурации из .env
├── parser/
│   └── news_parser.py       # Async RSS/HTML парсер
├── ai_engine/
│   └── openai_client.py     # GPT-4o + DALL-E 3 клиент
└── bot/
    ├── handlers.py          # Команды и callback-кнопки
    ├── keyboards.py         # Inline-клавиатуры
    └── middlewares.py       # Logging & Admin middleware
```

---

## Быстрый старт (локальная разработка)

```bash
# 1. Клонируй репозиторий
git clone https://github.com/Romshtex/Holiday_Homes.git
cd Holiday_Homes

# 2. Создай виртуальное окружение
python3 -m venv venv
source venv/bin/activate

# 3. Установи зависимости
pip install -r requirements.txt

# 4. Создай .env из шаблона и заполни значения
cp .env.example .env
nano .env

# 5. Запусти агента
python main.py
```

---

## Деплой на VPS (Production)

### Первичная настройка

```bash
# На сервере — клонируем репозиторий
cd /home/ubuntu
git clone https://github.com/Romshtex/Holiday_Homes.git
cd Holiday_Homes

# Создаём и активируем venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Копируем и настраиваем .env
cp .env.example .env
nano .env   # заполни все переменные реальными значениями

# Копируем systemd unit
sudo cp alanya_agent.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable alanya_agent
sudo systemctl start alanya_agent
```

### Обновление кода (шпаргалка деплоя)

```bash
cd /home/ubuntu/Holiday_Homes
git pull origin main
sudo systemctl restart alanya_agent
```

### Мониторинг логов

```bash
# Потоковые логи
journalctl -u alanya_agent -f

# Последние 100 строк
journalctl -u alanya_agent -n 100
```

---

## Переменные окружения

Все переменные описаны в [`.env.example`](.env.example).

| Переменная | Описание |
|-----------|---------|
| `TELEGRAM_BOT_TOKEN` | Токен бота от @BotFather |
| `ADMIN_IDS` | Telegram ID администраторов (через запятую) |
| `TARGET_CHANNEL_ID` | ID/username канала для публикаций |
| `OPENAI_API_KEY` | Ключ OpenAI API |
| `OPENAI_TEXT_MODEL` | Модель для текста (по умолчанию `gpt-4o`) |
| `OPENAI_IMAGE_MODEL` | Модель для изображений (по умолчанию `dall-e-3`) |
| `SCHEDULER_TIMEZONE` | Часовой пояс планировщика (`Europe/Istanbul`) |
| `NEWS_PUBLISH_HOUR` | Час публикации дайджеста (0–23) |
| `NEWS_PUBLISH_MINUTE` | Минута публикации дайджеста (0–59) |
| `RSS_FEEDS` | Список RSS-лент через запятую |
| `MAX_NEWS_ITEMS` | Максимум новостей в дайджесте |

---

## Команды бота

| Команда | Описание | Роль |
|---------|---------|------|
| `/start` | Запуск, главное меню | Все |
| `/help` | Справка по командам | Все |
| `/ask` | Вопрос консультанту | Все |
| `/news` | Последние новости | Все |
| `/image` | Генерация изображения | Все |
| `/digest` | Ручная публикация дайджеста | Только админы |
| `/broadcast` | Рассылка в канал | Только админы |

---

## Безопасность

- Все API-ключи хранятся **только** в `.env` (не в коде).
- Файл `.env` добавлен в `.gitignore` — никогда не попадёт в репозиторий.
- Административные команды защищены `AdminOnlyMiddleware`.