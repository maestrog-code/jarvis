"""Anomaly detector — rate-limit tracking and automatic kill trigger."""

import time
import logging

from jarvis.safety.killswitch import engage_auto_kill

log = logging.getLogger("jarvis.safety.anomaly")

_request_log: list[float] = []
RATE_LIMIT = 100  # max requests per window
WINDOW_SECONDS = 300  # 5-minute sliding window


async def record_request() -> None:
    """Record a browser/API request and check the rate limit.

    If the number of requests in the sliding window exceeds
    ``RATE_LIMIT``, the Auto-Kill switch is engaged immediately.
    """
    now = time.time()
    _request_log.append(now)

    # Trim entries outside the window
    cutoff = now - WINDOW_SECONDS
    while _request_log and _request_log[0] < cutoff:
        _request_log.pop(0)

    if len(_request_log) > RATE_LIMIT:
        log.error(
            "Rate limit exceeded: %d requests in %ds.",
            len(_request_log),
            WINDOW_SECONDS,
        )
        await engage_auto_kill(
            f"Anomaly: {len(_request_log)} requests in {WINDOW_SECONDS}s "
            f"(limit: {RATE_LIMIT})"
        )


def get_request_count() -> int:
    """Return the current number of requests in the sliding window."""
    now = time.time()
    cutoff = now - WINDOW_SECONDS
    while _request_log and _request_log[0] < cutoff:
        _request_log.pop(0)
    return len(_request_log)
