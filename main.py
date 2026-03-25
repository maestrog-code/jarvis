#!/usr/bin/env python3
"""Project Jarvis — Main Orchestrator.

This is the entry-point for the entire Jarvis system. It boots up
background tasks (Sentinel, scheduled briefing, HITL expiry) and
then starts the Telegram bot polling loop.

Usage::

    python -m jarvis.main
"""

import sys
import os
from pathlib import Path

# Fix import paths - ensure the parent directory is in sys.path
# This allows 'from jarvis.xxx' to work regardless of how the script is launched.
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import asyncio
import datetime
import logging
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
log = logging.getLogger("jarvis")


async def scheduled_briefing() -> None:
    """Send the morning briefing at 08:00 local time every day."""
    from jarvis.skills.newsroom import run_newsroom
    from jarvis.notify import forward_to_clawdbot

    while True:
        now = datetime.datetime.now()
        target = now.replace(hour=8, minute=0, second=0, microsecond=0)
        if now >= target:
            target += datetime.timedelta(days=1)

        wait = (target - now).total_seconds()
        log.info("⏰ Next briefing in %.0f seconds (at %s).", wait, target)
        await asyncio.sleep(wait)

        try:
            briefing = await run_newsroom()
            await forward_to_clawdbot(briefing)
            log.info("Morning briefing delivered.")
        except asyncio.CancelledError:
            raise
        except Exception:
            log.exception("Scheduled briefing failed.")


async def main() -> None:
    """Boot Jarvis — launch background tasks and start the Telegram bot."""
    # Load environment variables from .env
    load_dotenv()

    # Load SOUL.md for logging / future reference
    soul_path = os.path.join(os.path.dirname(__file__), "soul", "SOUL.md")
    if os.path.exists(soul_path):
        with open(soul_path, "r") as f:
            soul = f.read()
        log.info("Loaded SOUL.md (%d chars).", len(soul))
    else:
        log.warning("SOUL.md not found at %s.", soul_path)

    log.info("🚀 Jarvis is booting up…")

    # Launch background tasks
    from jarvis.skills.sentinel import sentinel_loop
    from jarvis.safety.hitl import expire_stale

    asyncio.create_task(sentinel_loop(), name="sentinel")
    asyncio.create_task(scheduled_briefing(), name="briefing")
    asyncio.create_task(expire_stale(), name="hitl-expiry")

    log.info(
        "Background tasks launched: sentinel, briefing, hitl-expiry."
    )

    # Start the Telegram bot (blocking polling loop)
    from jarvis.clawdbot.telegram_adapter import start_telegram_bot

    await start_telegram_bot()
    
    # Stay alive forever (or until CTRL+C)
    log.info("Jarvis is fully operational and alive.")
    while True:
        await asyncio.sleep(3600)



if __name__ == "__main__":
    asyncio.run(main())
