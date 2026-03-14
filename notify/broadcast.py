"""Broadcast — forward messages to all configured user channels."""

import os
import logging
import aiohttp

log = logging.getLogger("jarvis.notify.broadcast")

# Telegram is the primary channel; others can be added here.
TELEGRAM_API = "https://api.telegram.org/bot{token}/sendMessage"


async def forward_to_clawdbot(message: str) -> None:
    """Send a message to the user via the primary Telegram channel.

    Requires ``TELEGRAM_BOT_TOKEN`` and ``TELEGRAM_CHAT_ID``
    environment variables to be set.
    """
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        log.warning(
            "Telegram credentials not set — message dropped: %.100s",
            message,
        )
        return

    url = TELEGRAM_API.format(token=token)
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown",
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as resp:
                if resp.status != 200:
                    body = await resp.text()
                    log.error(
                        "Telegram API error %d: %s", resp.status, body
                    )
                else:
                    log.info("Message forwarded to Telegram.")
    except Exception:
        log.exception("Failed to forward message to Telegram.")


async def broadcast(message: str) -> None:
    """Forward a message to ALL configured channels.

    Currently only Telegram is implemented. Add Discord / WhatsApp
    adapters here as they are built.
    """
    await forward_to_clawdbot(message)
    # TODO: await forward_to_discord(message)
    # TODO: await forward_to_whatsapp(message)
