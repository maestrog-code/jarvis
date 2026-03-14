"""Command Router — parses incoming Clawdbot messages and dispatches."""

import asyncio
import shlex
import logging
from dataclasses import dataclass
from typing import Callable, Awaitable

log = logging.getLogger("jarvis.clawdbot.router")


@dataclass
class Command:
    """Parsed user command."""

    name: str
    args: list[str]
    raw: str


# ── Handler Registry ────────────────────────────────────────────────
_handlers: dict[str, Callable[[Command], Awaitable[str]]] = {}


def command(name: str):
    """Decorator to register a command handler.

    Usage::

        @command("/status")
        async def status_cmd(cmd: Command) -> str:
            return "All systems nominal."
    """

    def decorator(fn: Callable[[Command], Awaitable[str]]):
        _handlers[name] = fn
        return fn

    return decorator


async def dispatch(raw_text: str) -> str:
    """Parse raw text and invoke the matching handler.

    Returns the handler's response string, or an error message if the
    command is unknown.
    """
    raw_text = raw_text.strip()
    if not raw_text.startswith("/"):
        return "💬 I only respond to slash-commands. Try /help."

    try:
        parts = shlex.split(raw_text)
    except ValueError:
        parts = raw_text.split()

    cmd = Command(name=parts[0].lower(), args=parts[1:], raw=raw_text)

    handler = _handlers.get(cmd.name)
    if handler is None:
        return f"❓ Unknown command `{cmd.name}`. Try /help."

    log.info("Dispatching %s with args %s", cmd.name, cmd.args)
    try:
        return await handler(cmd)
    except Exception as exc:
        log.exception("Handler for %s failed.", cmd.name)
        return f"❌ Error executing `{cmd.name}`: {exc}"


# ── Built-in Handlers ──────────────────────────────────────────────


@command("/help")
async def help_cmd(_: Command) -> str:
    return (
        "📖 **Jarvis Commands**\n"
        "`/status` — system health\n"
        "`/briefing` — morning briefing\n"
        "`/post <platform> <content>` — queue a post\n"
        "`/drafts` — pending reply drafts\n"
        "`/approve <id>` — approve queued item\n"
        "`/reject <id>` — reject queued item\n"
        "`/sentinel on|off` — toggle IG monitor\n"
        "`/keywords add|remove <word>` — manage keywords\n"
        "`/kill` — emergency shutdown\n"
        "`/help` — this message"
    )


@command("/status")
async def status_cmd(_: Command) -> str:
    from jarvis.health import get_health_report

    return await get_health_report()


@command("/briefing")
async def briefing_cmd(_: Command) -> str:
    from jarvis.skills.newsroom import run_newsroom

    return await run_newsroom()


@command("/post")
async def post_cmd(cmd: Command) -> str:
    if len(cmd.args) < 2:
        return "⚠️ Usage: `/post <platform> <content>`"
    platform = cmd.args[0]
    content = " ".join(cmd.args[1:])

    from jarvis.safety import queue_for_approval

    item_id = await queue_for_approval(platform, content)
    return (
        f"📝 Post queued (ID `{item_id}`). "
        f"Reply `/approve {item_id}` to publish."
    )


@command("/drafts")
async def drafts_cmd(_: Command) -> str:
    from jarvis.safety.hitl import list_pending

    pending = list_pending()
    if not pending:
        return "📭 No pending drafts."
    lines = ["📋 **Pending Drafts**\n"]
    for item_id, item in pending.items():
        lines.append(
            f"• `{item_id}` — **{item['platform']}**: "
            f"{item['content'][:80]}…"
        )
    return "\n".join(lines)


@command("/approve")
async def approve_cmd(cmd: Command) -> str:
    if not cmd.args:
        return "⚠️ Usage: `/approve <id>`"
    from jarvis.safety import approve_item

    return await approve_item(cmd.args[0])


@command("/reject")
async def reject_cmd(cmd: Command) -> str:
    if not cmd.args:
        return "⚠️ Usage: `/reject <id>`"
    from jarvis.safety import reject_item

    return await reject_item(cmd.args[0])


@command("/sentinel")
async def sentinel_cmd(cmd: Command) -> str:
    if not cmd.args or cmd.args[0].lower() not in ("on", "off"):
        return "⚠️ Usage: `/sentinel on|off`"

    action = cmd.args[0].lower()
    if action == "on":
        # Start the sentinel as a background task if not already running
        from jarvis.skills.sentinel import sentinel_loop

        loop = asyncio.get_event_loop()
        for task in asyncio.all_tasks(loop):
            if task.get_name() == "sentinel":
                return "🟢 Sentinel is already running."
        asyncio.create_task(sentinel_loop(), name="sentinel")
        return "🟢 Sentinel started."
    else:
        # Cancel the sentinel task
        loop = asyncio.get_event_loop()
        for task in asyncio.all_tasks(loop):
            if task.get_name() == "sentinel":
                task.cancel()
                return "🔴 Sentinel stopped."
        return "🔴 Sentinel was not running."


@command("/keywords")
async def keywords_cmd(cmd: Command) -> str:
    if len(cmd.args) < 2 or cmd.args[0].lower() not in ("add", "remove"):
        return "⚠️ Usage: `/keywords add|remove <word>`"
    # This modifies the in-memory config; for persistence, update directives.yaml
    action = cmd.args[0].lower()
    word = " ".join(cmd.args[1:])

    import yaml, os

    config_path = os.path.join(
        os.path.dirname(__file__), "..", "config", "directives.yaml"
    )
    with open(config_path, "r") as f:
        cfg = yaml.safe_load(f)

    keywords = cfg.setdefault("sentinel", {}).setdefault("urgent_keywords", [])

    if action == "add":
        if word in keywords:
            return f"ℹ️ `{word}` is already in the keyword list."
        keywords.append(word)
        with open(config_path, "w") as f:
            yaml.safe_dump(cfg, f)
        return f"➕ Added `{word}` to sentinel keywords."
    else:
        if word not in keywords:
            return f"ℹ️ `{word}` is not in the keyword list."
        keywords.remove(word)
        with open(config_path, "w") as f:
            yaml.safe_dump(cfg, f)
        return f"➖ Removed `{word}` from sentinel keywords."


@command("/kill")
async def kill_cmd(_: Command) -> str:
    from jarvis.safety import engage_auto_kill

    await engage_auto_kill(reason="Manual /kill command")
    return "🛑 **AUTO-KILL engaged.** All sessions terminated. Check logs."
