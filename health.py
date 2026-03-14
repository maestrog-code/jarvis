"""Jarvis Health — system health report for the /status command."""

import asyncio
import logging
import datetime

from jarvis.safety.anomaly import get_request_count
from jarvis.safety.killswitch import is_killed

log = logging.getLogger("jarvis.health")

_boot_time = datetime.datetime.utcnow()


async def get_health_report() -> str:
    """Return a formatted health report string."""
    uptime = datetime.datetime.utcnow() - _boot_time
    hours, remainder = divmod(int(uptime.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)

    kill_status = "🔴 KILLED" if is_killed() else "🟢 Active"
    req_count = get_request_count()

    # Check which background tasks are running
    running_tasks = []
    for task in asyncio.all_tasks():
        name = task.get_name()
        if name in ("sentinel", "briefing", "hitl-expiry"):
            running_tasks.append(name)

    tasks_str = ", ".join(running_tasks) if running_tasks else "_none_"

    report = (
        "📊 **Jarvis Status Report**\n\n"
        f"**Status:** {kill_status}\n"
        f"**Uptime:** {hours}h {minutes}m {seconds}s\n"
        f"**Requests (5min window):** {req_count}\n"
        f"**Active tasks:** {tasks_str}\n"
        f"**Boot time:** {_boot_time.strftime('%Y-%m-%d %H:%M UTC')}"
    )
    return report
