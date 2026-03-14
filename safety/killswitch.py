"""Auto-Kill switch — immediately halt all Jarvis activity."""

import asyncio
import logging
import sys

log = logging.getLogger("jarvis.safety.killswitch")

_killed = False


async def engage_auto_kill(reason: str) -> None:
    """Immediately cancel all asyncio tasks, notify the user, and exit.

    Exit code 42 is used to signal to the process supervisor (systemd /
    Antigravity Process Guard) that this was a deliberate safety halt and
    the process should **not** be auto-restarted.
    """
    global _killed
    _killed = True
    log.critical("🛑 AUTO-KILL ENGAGED — reason: %s", reason)

    # 1. Cancel every running asyncio task except ourselves
    current = asyncio.current_task()
    for task in asyncio.all_tasks():
        if task is not current:
            task.cancel()

    # 2. Notify user via every available channel
    try:
        from jarvis.notify import broadcast

        await broadcast(
            f"🛑 **AUTO-KILL** engaged.\n"
            f"Reason: {reason}\n"
            f"All browser sessions & skills have been halted.\n"
            f"Manual restart required."
        )
    except Exception:
        log.exception("Failed to broadcast kill notification.")

    # 3. Exit with safety code
    sys.exit(42)


def is_killed() -> bool:
    """Return ``True`` if the kill switch has been engaged."""
    return _killed
