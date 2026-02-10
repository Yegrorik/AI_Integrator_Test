# AI-интегратор — Telegram-бот с прямым обращением к LLM

## Описание

Этот проект — простой Telegram-бот на **aiogram**, который:

- **принимает сообщения от пользователя**;
- **отправляет их в LLM Groq по системному промпту** (через прямой HTTP-запрос к совместимому с OpenAI API);
- **возвращает ответ модели обратно пользователю в Telegram**.

Используется классический Chat Completions API (без Assistants API и других высокоуровневых абстракций), но через endpoint Groq.

## Подготовка окружения

1. **Создайте виртуальное окружение (рекомендуется)**:

```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
```

2. **Установите зависимости**:

```bash
pip install -r requirements.txt
```

3. **Создайте Telegram-бота и получите токен** у [@BotFather](https://t.me/BotFather).

4. **Получите API-ключ Groq** и сохраните его.

5. **Заполните файл `.env`** в корне проекта (создан шаблон):

```env
TELEGRAM_BOT_TOKEN=ВАШ_TELEGRAM_БОТ_ТОКЕН_ОТ_BOTFATHER
GROQ_API_KEY=ВАШ_GROQ_API_KEY
```

## Запуск бота

Из корня проекта:

```bash
python bot.py
```

После запуска бот начнёт long polling и будет отвечать на текстовые сообщения.