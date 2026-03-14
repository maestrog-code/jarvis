"""Publisher — post content to social media platforms after HITL approval."""

import asyncio
import logging
import random

from jarvis.browser import stealth_browser, human_delay

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

log = logging.getLogger("jarvis.skills.publisher")


async def publish(platform: str, content: str) -> None:
    """Publish ``content`` to the specified ``platform``.

    Currently supports: ``x``, ``linkedin``, ``instagram``.
    Raises ``ValueError`` for unknown platforms.
    """
    platform = platform.lower().strip()
    publishers = {
        "x": _publish_to_x,
        "twitter": _publish_to_x,
        "linkedin": _publish_to_linkedin,
        "instagram": _publish_to_instagram,
    }

    handler = publishers.get(platform)
    if handler is None:
        raise ValueError(
            f"Unknown platform '{platform}'. "
            f"Supported: {', '.join(publishers)}"
        )

    await handler(content)
    log.info("Published to %s: %.80s…", platform, content)


# ── Platform-specific publishers ───────────────────────────────────


async def _publish_to_x(content: str) -> None:
    """Post a tweet via the X/Twitter web compose UI."""
    driver = await stealth_browser("X")
    loop = asyncio.get_running_loop()
    try:
        await loop.run_in_executor(
            None, driver.get, "https://x.com/compose/tweet"
        )
        await human_delay(2.0, 4.0)

        editor = await loop.run_in_executor(
            None,
            lambda: WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, '[data-testid="tweetTextarea_0"]')
                )
            ),
        )
        await loop.run_in_executor(None, editor.click)
        await human_delay(0.5, 1.0)

        # Type character-by-character for realism
        for char in content:
            await loop.run_in_executor(None, editor.send_keys, char)
            await asyncio.sleep(0.05 + random.random() * 0.08)
        await human_delay(1.0, 2.0)

        post_btn = await loop.run_in_executor(
            None,
            lambda: WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, '[data-testid="tweetButton"]')
                )
            ),
        )
        await loop.run_in_executor(None, post_btn.click)
        await human_delay(2.0, 4.0)
        log.info("Tweet posted successfully.")
    finally:
        await loop.run_in_executor(None, driver.quit)


async def _publish_to_linkedin(content: str) -> None:
    """Create a LinkedIn post via the web compose UI."""
    driver = await stealth_browser("LINKEDIN")
    loop = asyncio.get_running_loop()
    try:
        await loop.run_in_executor(
            None, driver.get, "https://www.linkedin.com/feed/"
        )
        await human_delay(2.0, 4.0)

        # Click "Start a post"
        start_btn = await loop.run_in_executor(
            None,
            lambda: WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "button.share-box-feed-entry__trigger")
                )
            ),
        )
        await loop.run_in_executor(None, start_btn.click)
        await human_delay(1.5, 3.0)

        editor = await loop.run_in_executor(
            None,
            lambda: WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, ".ql-editor[data-placeholder]")
                )
            ),
        )
        await loop.run_in_executor(None, editor.click)
        await human_delay(0.5, 1.0)
        await loop.run_in_executor(None, editor.send_keys, content)
        await human_delay(1.0, 2.0)

        post_btn = await loop.run_in_executor(
            None,
            lambda: WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "button.share-actions__primary-action")
                )
            ),
        )
        await loop.run_in_executor(None, post_btn.click)
        await human_delay(2.0, 4.0)
        log.info("LinkedIn post published successfully.")
    finally:
        await loop.run_in_executor(None, driver.quit)


async def _publish_to_instagram(content: str) -> None:
    """Stub — Instagram web does not support post compose.

    This would require mobile emulation or the Instagram Graph API.
    For now, log a warning and instruct the user.
    """
    log.warning(
        "Instagram web publishing is not supported. "
        "Use the Instagram Graph API or post manually. "
        "Content was: %.200s",
        content,
    )
    raise NotImplementedError(
        "Instagram web publishing is not yet supported. "
        "Please use the Graph API integration or post manually."
    )
