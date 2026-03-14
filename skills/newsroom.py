"""The Newsroom — scrape X/Twitter for keyword mentions and summarise."""

import asyncio
import logging
import yaml
import os

from jarvis.browser import stealth_browser, human_delay

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

log = logging.getLogger("jarvis.skills.newsroom")

SEARCH_URL = "https://x.com/search?q={query}&src=typed_query&f=live"


def _load_config() -> dict:
    """Load newsroom settings from directives.yaml."""
    config_path = os.path.join(
        os.path.dirname(__file__), "..", "config", "directives.yaml"
    )
    with open(config_path, "r") as f:
        cfg = yaml.safe_load(f)
    return cfg.get("newsroom", {})


async def scrape_tweets(
    keywords: list[str] | None = None,
    max_per_kw: int | None = None,
) -> dict[str, list[str]]:
    """Return ``{keyword: [tweet_text, …]}`` for each keyword.

    Parameters default to values in ``directives.yaml`` if not supplied.
    """
    cfg = _load_config()
    keywords = keywords or cfg.get("keywords", [])
    max_per_kw = max_per_kw or cfg.get("max_tweets_per_keyword", 10)

    driver = await stealth_browser("X")
    results: dict[str, list[str]] = {}
    loop = asyncio.get_running_loop()

    try:
        for kw in keywords:
            encoded_kw = kw.replace(" ", "%20")
            url = SEARCH_URL.format(query=encoded_kw)
            log.info("Searching X for: %s", kw)
            await loop.run_in_executor(None, driver.get, url)
            await human_delay(2.0, 5.0)

            # Wait for tweet elements to render
            try:
                await loop.run_in_executor(
                    None,
                    lambda: WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR, 'article [data-testid="tweetText"]')
                        )
                    ),
                )
            except Exception:
                log.warning("No tweets found for '%s' — timeout.", kw)
                results[kw] = []
                continue

            tweet_els = await loop.run_in_executor(
                None,
                driver.find_elements,
                By.CSS_SELECTOR,
                'article [data-testid="tweetText"]',
            )
            texts: list[str] = []
            for el in tweet_els[:max_per_kw]:
                texts.append(el.text)
                await human_delay(0.3, 0.8)
            results[kw] = texts
            log.info("Collected %d tweets for '%s'.", len(texts), kw)
    finally:
        await loop.run_in_executor(None, driver.quit)

    return results


async def summarise(results: dict[str, list[str]]) -> str:
    """Produce a bullet-point briefing from raw tweets."""
    lines = ["📰 **Newsroom Briefing**\n"]
    for kw, tweets in results.items():
        lines.append(f"### {kw}")
        if not tweets:
            lines.append("  _No results._")
        else:
            for i, t in enumerate(tweets, 1):
                # Truncate long tweets for readability
                lines.append(f"  {i}. {t[:200]}")
        lines.append("")
    return "\n".join(lines)


async def run_newsroom() -> str:
    """Full pipeline: scrape → summarise → return formatted briefing."""
    log.info("Running Newsroom briefing…")
    data = await scrape_tweets()
    briefing = await summarise(data)
    log.info("Newsroom briefing complete.")
    return briefing
