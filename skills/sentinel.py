"""The Sentinel — monitor Instagram DMs for urgent keyword alerts."""

import asyncio
import logging
import os
import yaml

from jarvis.browser import stealth_browser, human_delay
from jarvis.notify import forward_to_clawdbot

from selenium.webdriver.common.by import By

log = logging.getLogger("jarvis.skills.sentinel")

IG_DM_URL = "https://www.instagram.com/direct/inbox/"


def _load_config() -> dict:
    """Load sentinel settings from directives.yaml."""
    config_path = os.path.join(
        os.path.dirname(__file__), "..", "config", "directives.yaml"
    )
    with open(config_path, "r") as f:
        cfg = yaml.safe_load(f)
    return cfg.get("sentinel", {})


async def check_dms_once(
    keywords: list[str] | None = None,
) -> list[dict]:
    """Scan Instagram DMs for urgent keyword matches.

    Returns a list of ``{keyword, snippet}`` dicts for every match.
    """
    cfg = _load_config()
    keywords = keywords or cfg.get("urgent_keywords", [])

    driver = await stealth_browser("IG")
    alerts: list[dict] = []
    loop = asyncio.get_running_loop()

    try:
        await loop.run_in_executor(None, driver.get, IG_DM_URL)
        await human_delay(3.0, 6.0)

        threads = await loop.run_in_executor(
            None,
            driver.find_elements,
            By.CSS_SELECTOR,
            '[aria-label="Direct messaging"] a',
        )
        log.info("Found %d IG DM threads.", len(threads))

        for thread in threads[:10]:
            await loop.run_in_executor(None, thread.click)
            await human_delay(1.5, 3.0)

            messages = await loop.run_in_executor(
                None,
                driver.find_elements,
                By.CSS_SELECTOR,
                'div[role="row"] span',
            )
            for msg_el in messages[-5:]:
                text = msg_el.text
                for kw in keywords:
                    if kw.lower() in text.lower():
                        alerts.append(
                            {"keyword": kw, "snippet": text[:300]}
                        )
                        log.warning(
                            "Sentinel match: keyword '%s' in IG DM.", kw
                        )
                        break   # one match per message is enough
    finally:
        await loop.run_in_executor(None, driver.quit)

    return alerts


async def sentinel_loop() -> None:
    """Continuous polling loop — runs until the task is cancelled."""
    cfg = _load_config()
    poll_interval = cfg.get("poll_interval_seconds", 60)
    log.info(
        "Sentinel loop started (poll every %ds).", poll_interval
    )

    while True:
        try:
            alerts = await check_dms_once()
            for alert in alerts:
                await forward_to_clawdbot(
                    f"🚨 **Sentinel Alert** — keyword "
                    f"*{alert['keyword']}* detected:\n"
                    f"> {alert['snippet']}"
                )
        except asyncio.CancelledError:
            log.info("Sentinel loop cancelled.")
            raise
        except Exception:
            log.exception("Sentinel loop error — will retry next cycle.")

        await asyncio.sleep(poll_interval)
