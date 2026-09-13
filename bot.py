import logging
import os

import groq
from dotenv import load_dotenv
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

load_dotenv()

TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
GROQ_API_KEY = os.environ["GROQ_API_KEY"]
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
MAX_HISTORY_MESSAGES = 20
TELEGRAM_MESSAGE_LIMIT = 4096

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

groq_client = groq.Groq(api_key=GROQ_API_KEY)

# chat_id -> list of {"role": "user"|"assistant", "content": str}
conversations: dict[int, list[dict[str, str]]] = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    conversations.pop(update.effective_chat.id, None)
    await update.message.reply_text(
        "Salom! Men AI botman. Menga xabar yozing, javob beraman. "
        "Suhbat tarixini tozalash uchun /reset buyrug'ini yuboring."
    )


async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    conversations.pop(update.effective_chat.id, None)
    await update.message.reply_text("Suhbat tarixi tozalandi.")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    user_text = update.message.text
    history = conversations.setdefault(chat_id, [])
    history.append({"role": "user", "content": user_text})

    await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)

    try:
        response = groq_client.chat.completions.create(
            model=GROQ_MODEL,
            max_tokens=4096,
            messages=history,
        )
        reply_text = response.choices[0].message.content
    except groq.RateLimitError:
        logger.exception("Groq rate limit hit")
        history.pop()
        await update.message.reply_text(
            "Hozir so'rovlar ko'p, birozdan so'ng qayta urinib ko'ring."
        )
        return
    except groq.APIStatusError:
        logger.exception("Groq API request failed")
        history.pop()
        await update.message.reply_text(
            "Kechirasiz, so'rov yuborishda xatolik yuz berdi. "
            "Birozdan so'ng qayta urinib ko'ring."
        )
        return
    except groq.APIConnectionError:
        logger.exception("Network error while calling Groq API")
        history.pop()
        await update.message.reply_text(
            "Tarmoq xatoligi yuz berdi, birozdan so'ng qayta urinib ko'ring."
        )
        return

    history.append({"role": "assistant", "content": reply_text})
    del conversations[chat_id][:-MAX_HISTORY_MESSAGES]

    for offset in range(0, len(reply_text), TELEGRAM_MESSAGE_LIMIT):
        await update.message.reply_text(reply_text[offset : offset + TELEGRAM_MESSAGE_LIMIT])


def main() -> None:
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("reset", reset))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Bot ishga tushdi (model: %s)", GROQ_MODEL)
    application.run_polling()


if __name__ == "__main__":
    main()
