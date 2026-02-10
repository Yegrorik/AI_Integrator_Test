import logging
import aiohttp
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.client.default import DefaultBotProperties

from config import settings


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


# Системный промпт — именно под него будет работать бот.
SYSTEM_PROMPT = (
    "Ты — AI-интегратор, который помогает кандидату проходить "
    "тестовые задания по интеграции ИИ в продукты. "
    "Отвечай кратко, по делу, на русском языке. "
    "Если нужно, можешь предлагать варианты архитектуры, кода и комментарии."
)


# ==========================
# Взаимодействие с LLM (сырая работа с API через aiohttp)
# ==========================

async def call_llm(user_message: str) -> str:
    if not settings.groq_api_key:
        return (
            "Ошибка конфигурации: не задан API‑ключ Groq. "
            "Установите переменную окружения GROQ_API_KEY или заполните `.env`."
        )

    headers = {
        "Authorization": f"Bearer {settings.groq_api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": settings.groq_model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        "temperature": 0.3,
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                settings.groq_api_url,
                json=payload,
                headers=headers,
                timeout=60,
            ) as response:
                if response.status != 200:
                    text = await response.text()
                    logger.error(
                        "Ошибка запроса к LLM: статус %s, тело ответа: %s",
                        response.status,
                        text,
                    )
                    return f"Произошла ошибка при обращении к модели (HTTP {response.status})."

                data = await response.json()

        # Классический формат Chat Completions
        content = data["choices"][0]["message"]["content"]
        return content.strip()
    except aiohttp.ClientError as e:
        logger.exception("Ошибка сети при запросе к LLM")
        return f"Сетевая ошибка при обращении к модели: {e}"
    except (KeyError, IndexError) as e:
        logger.exception("Неожиданный формат ответа LLM")
        return f"Не удалось распарсить ответ модели: {e}"


# ==========================
# Обработчики Telegram-бота (aiogram)
# ==========================


async def cmd_start(message: Message) -> None:
    user_name = message.from_user.full_name if message.from_user else "друг"
    text = (
        f"Привет, {user_name}!\n\n"
        "Я AI-интегратор‑бот (Groq + aiogram).\n"
        "Напиши мне любой вопрос по ИИ/коду, "
        "а я отправлю его в LLM с заданным системным промптом и верну ответ."
    )
    await message.answer(text, reply_markup=ReplyKeyboardRemove())


async def cmd_help(message: Message) -> None:
    text = (
        "Просто напишите сообщение — я отправлю его в Groq‑LLM.\n\n"
        "/start — краткое приветствие\n"
        "/help — это сообщение"
    )
    await message.answer(text)


async def handle_text(message: Message) -> None:
    user_text = message.text or ""
    chat_id = message.chat.id
    logger.info("Новое сообщение от %s: %s", chat_id, user_text)

    await message.bot.send_chat_action(chat_id=chat_id, action="typing")

    reply = await call_llm(user_text)
    await message.answer(reply, parse_mode=ParseMode.MARKDOWN)


async def main() -> None:
    """
    Точка входа для aiogram-бота.
    """

    bot = Bot(token=settings.telegram_bot_token,
              default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()

    # Регистрация хендлеров
    dp.message.register(cmd_start, CommandStart())
    dp.message.register(cmd_help, Command("help"))
    dp.message.register(handle_text, F.text & ~F.via_bot)

    logger.info("Бот запущен (aiogram + Groq). Ожидание сообщений...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())


