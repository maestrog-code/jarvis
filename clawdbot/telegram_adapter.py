"""Thin adapter: Telegram Bot API → Jarvis Command Router."""

import os
import logging
import socket

# Force IPv4 to prevent httpx from hanging on IPv6 blackholes
old_getaddrinfo = socket.getaddrinfo
def new_getaddrinfo(*args, **kwargs):
    res = old_getaddrinfo(*args, **kwargs)
    return [r for r in res if r[0] == socket.AF_INET]
socket.getaddrinfo = new_getaddrinfo

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    ContextTypes,
    filters,
)

from jarvis.clawdbot.router import dispatch

log = logging.getLogger("jarvis.clawdbot.telegram")


async def handle_message(
    update: Update, ctx: ContextTypes.DEFAULT_TYPE
) -> None:
    """Route every incoming text message through the command dispatcher."""
    if update.message is None or update.message.text is None:
        return

    reply = await dispatch(update.message.text)
    await update.message.reply_text(reply, parse_mode="Markdown")


async def start_telegram_bot() -> None:
    """Build and run the Telegram bot (async).

    Requires the ``TELEGRAM_BOT_TOKEN`` environment variable.
    """
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        log.error("TELEGRAM_BOT_TOKEN is not set — cannot start bot.")
        return

    app = ApplicationBuilder().token(token).build()

    # Catch both plain text and /command-style messages
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )
    app.add_handler(MessageHandler(filters.COMMAND, handle_message))

    log.info("🤖 Telegram adapter online — polling for messages.")
    
    # In PTB v20+, to run within an existing loop:
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    
    # We don't call idle() or run_polling() here because those try to 
    # manage the loop. We just return, and the bot runs in the background.
