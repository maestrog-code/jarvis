"""Human-in-the-Loop (HITL) gate — queue, approve, reject public posts."""

import asyncio
import uuid
import logging
from datetime import datetime, timedelta

log = logging.getLogger("jarvis.safety.hitl")

# In-memory pending queue: id → {platform, content, created_at}
_pending: dict[str, dict] = {}
EXPIRY = timedelta(hours=1)


async def queue_for_approval(platform: str, content: str) -> str:
    """Queue a post for human approval; return the item ID."""
    item_id = uuid.uuid4().hex[:8]
    _pending[item_id] = {
        "platform": platform,
        "content": content,
        "created_at": datetime.utcnow(),
    }
    log.info(
        "Queued item %s for HITL approval (platform=%s).", item_id, platform
    )
    return item_id


async def approve_item(item_id: str) -> str:
    """Approve and publish a queued item.

    Returns a user-facing status message.
    """
    item = _pending.pop(item_id, None)
    if item is None:
        return f"❌ Item `{item_id}` not found or expired."

    from jarvis.skills.publisher import publish

    try:
        await publish(item["platform"], item["content"])
    except NotImplementedError as exc:
        return f"⚠️ {exc}"
    except Exception as exc:
        log.exception("Publish failed for item %s.", item_id)
        return f"❌ Publish failed: {exc}"

    return f"✅ Published to **{item['platform']}**."


async def reject_item(item_id: str) -> str:
    """Reject and discard a queued item."""
    item = _pending.pop(item_id, None)
    if item is None:
        return f"❌ Item `{item_id}` not found."
    log.info("Rejected item %s.", item_id)
    return f"🗑️ Item `{item_id}` rejected and discarded."


def list_pending() -> dict[str, dict]:
    """Return a snapshot of the pending queue (for /drafts)."""
    return dict(_pending)


async def expire_stale() -> None:
    """Background task — purge unconfirmed items older than EXPIRY."""
    while True:
        now = datetime.utcnow()
        expired = [
            k
            for k, v in _pending.items()
            if now - v["created_at"] > EXPIRY
        ]
        for k in expired:
            _pending.pop(k)
            log.warning("HITL item %s expired without approval.", k)
        await asyncio.sleep(300)
