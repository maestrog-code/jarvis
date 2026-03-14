"""The Ghostwriter — draft LinkedIn DM replies in the user's voice."""

import asyncio
import logging
import os

import aiohttp
import yaml

from jarvis.browser import stealth_browser, human_delay
from jarvis.memory import recall_writing_style

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

log = logging.getLogger("jarvis.skills.ghostwriter")

LI_DM_URL = "https://www.linkedin.com/messaging/"


async def fetch_unread_dms(max_threads: int = 5) -> list[dict]:
    """Scrape unread LinkedIn DMs and return ``[{sender, message}]``.

    Parameters
    ----------
    max_threads : int
        Maximum number of unread threads to inspect.
    """
    driver = await stealth_browser("LINKEDIN")
    dms: list[dict] = []
    loop = asyncio.get_running_loop()

    try:
        await loop.run_in_executor(None, driver.get, LI_DM_URL)
        await human_delay(3.0, 6.0)

        threads = await loop.run_in_executor(
            None,
            driver.find_elements,
            By.CSS_SELECTOR,
            ".msg-conversation-listitem--unread",
        )
        log.info("Found %d unread LinkedIn threads.", len(threads))

        for thread in threads[:max_threads]:
            await loop.run_in_executor(None, thread.click)
            await human_delay(1.5, 3.0)

            msgs = await loop.run_in_executor(
                None,
                driver.find_elements,
                By.CSS_SELECTOR,
                ".msg-s-event-listitem__body",
            )
            if msgs:
                last_msg = await loop.run_in_executor(
                    None, getattr, msgs[-1], "text"
                )
                try:
                    sender_el = await loop.run_in_executor(
                        None,
                        driver.find_element,
                        By.CSS_SELECTOR,
                        ".msg-entity-lockup__entity-title",
                    )
                    sender = sender_el.text
                except Exception:
                    sender = "Unknown"
                dms.append({"sender": sender, "message": last_msg})
                log.info("Read DM from %s.", sender)
    finally:
        await loop.run_in_executor(None, driver.quit)

    return dms


async def draft_reply(dm: dict) -> str:
    """Use a local Ollama model to draft a reply matching the user's writing style."""
    style_guide = await recall_writing_style()

    # Load model name from config (defaults to llama3.2)
    config_path = os.path.join(
        os.path.dirname(__file__), "..", "config", "directives.yaml"
    )
    with open(config_path, "r") as f:
        cfg = yaml.safe_load(f)
    model = cfg.get("ghostwriter", {}).get("model", "llama3.2")

    ollama_url = os.environ.get("OLLAMA_URL", "http://localhost:11434")
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a ghostwriter. Match this style guide:\n"
                    f"{style_guide}\n\n"
                    "Draft a concise, professional LinkedIn reply. "
                    "Do NOT include a subject line or greeting beyond "
                    "the first name."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Incoming DM from {dm['sender']}:\n\n"
                    f"{dm['message']}"
                ),
            },
        ],
        "stream": False,
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{ollama_url}/api/chat", json=payload
        ) as resp:
            if resp.status != 200:
                body = await resp.text()
                raise RuntimeError(f"Ollama error {resp.status}: {body}")
            data = await resp.json()
            return data["message"]["content"]


async def run_ghostwriter() -> list[dict]:
    """Return ``[{sender, original, draft}]`` for each unread DM."""
    log.info("Running Ghostwriter…")
    dms = await fetch_unread_dms()
    output: list[dict] = []

    for dm in dms:
        draft = await draft_reply(dm)
        output.append(
            {
                "sender": dm["sender"],
                "original": dm["message"],
                "draft": draft,
            }
        )
        log.info("Drafted reply for %s.", dm["sender"])

    log.info("Ghostwriter complete — %d drafts.", len(output))
    return output
