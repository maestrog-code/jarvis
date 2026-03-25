"""URL scraper tool — fetch a URL and return its readable text content."""

import logging

import aiohttp

from jarvis.agent.tool_registry import tool

log = logging.getLogger("jarvis.agent.tools.scraper")

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
}


def _strip_html(html: str) -> str:
    """Naive HTML stripper — removes tags, condenses whitespace."""
    import re
    text = re.sub(r"<style[^>]*>.*?</style>", " ", html, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<script[^>]*>.*?</script>", " ", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s{2,}", " ", text)
    return text.strip()


@tool(
    name="scrape_url",
    description="Fetch a URL and return its readable text content (HTML tags stripped).",
    parameters={
        "url": {
            "type": "string",
            "description": "The full URL to fetch (must start with http:// or https://).",
            "required": True,
        },
        "max_chars": {
            "type": "integer",
            "description": "Max characters to return (default 3000).",
            "required": False,
        },
    },
)
async def scrape_url(url: str, max_chars: int = 3000) -> str:
    """Fetch a URL and return its stripped text."""
    if not url.startswith(("http://", "https://")):
        return f"❌ Invalid URL: must start with http:// or https://"

    log.info("Scraping URL: %s", url)
    try:
        async with aiohttp.ClientSession(headers=_HEADERS) as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                if resp.status != 200:
                    return f"❌ HTTP {resp.status} for {url}"
                html = await resp.text(errors="replace")

        text = _strip_html(html)
        if len(text) > max_chars:
            text = text[:max_chars] + f"\n…[truncated at {max_chars} chars]"

        return f"🌐 **Content from {url}**:\n\n{text}"
    except asyncio.TimeoutError:
        return f"⏱️ Timeout fetching: {url}"
    except Exception as exc:
        log.exception("scrape_url failed for %s", url)
        return f"❌ Scrape error: {exc}"


import asyncio  # noqa: E402 — needed in the handler above
