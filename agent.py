"""
Nihongo Agent - Week 1 minimal version.
Listens to Telegram, forwards to Claude (via Poe), replies.
This is the gateway. In Week 2 we route to skills instead of always calling the LLM.
"""

import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# --- Setup ---
load_dotenv()

TELEGRAM_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
OWNER_ID = int(os.environ["TELEGRAM_OWNER_ID"])
POE_API_KEY = os.environ["POE_API_KEY"]
POE_MODEL = os.environ.get("POE_MODEL", "Claude-Haiku-4.5")

LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(LOG_DIR / "agent.log"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger("nihongo")

# Poe is OpenAI-compatible: same SDK, different base URL.
client = OpenAI(
    api_key=POE_API_KEY,
    base_url="https://api.poe.com/v1",
)

SYSTEM_PROMPT = (
    "You are Nihongo Sensei, a kind and patient Japanese tutor. "
    "When the user writes in Japanese, reply in Japanese first, then add a brief "
    "English (Chinese) gloss in parentheses with hiragana for kanji. When the user writes in English, answer in "
    "English (Chinese) but include relevant Japanese examples. Keep replies short (≤4 sentences) "
    "unless explicitly asked for more depth."
)

# --- Handlers ---
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        log.warning("Rejected /start from %s", update.effective_user.id)
        return
    await update.message.reply_text(
        "こんにちは！I'm your Nihongo Sensei. Send me anything in Japanese "
        "or English and let's start learning."
    )

async def on_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        log.warning("Rejected message from %s", update.effective_user.id)
        return

    user_text = update.message.text
    log.info("USER: %s", user_text)

    try:
        response = client.chat.completions.create(
            model=POE_MODEL,
            max_tokens=512,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_text},
            ],
        )
        reply = response.choices[0].message.content
    except Exception as e:
        log.exception("Poe call failed")
        reply = f"⚠️ Error talking to Poe: {e}"

    log.info("BOT: %s", reply)
    await update.message.reply_text(reply)

# --- Main ---
def main():
    log.info("Starting agent... (model=%s)", POE_MODEL)
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_message))
    log.info("Polling Telegram. Press Ctrl+C to stop.")
    app.run_polling()

if __name__ == "__main__":
    main()