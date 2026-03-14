"""Core browser primitives — undetected Chrome context factory and human-like delays."""

import asyncio
import random
import logging
import functools

import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options

from jarvis.browser.cookies import load_cookies, convert_cookies_to_selenium
from jarvis.browser.ua_pool import pick_ua

log = logging.getLogger("jarvis.browser.core")


async def human_delay(low: float = 1.2, high: float = 4.5) -> None:
    """Sleep a random interval to mimic a real user."""
    delay = random.uniform(low, high)
    await asyncio.sleep(delay)


def _create_driver(headless: bool = True) -> uc.Chrome:
    """Build an undetected-chromedriver instance with stealth options.

    Uses a real Chrome installation so Google doesn't flag it as
    an automation browser.
    """
    options = uc.ChromeOptions()

    if headless:
        options.add_argument("--headless=new")

    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument(f"--user-agent={pick_ua()}")

    # Suppress unhelpful logs
    options.add_argument("--log-level=3")
    options.add_argument("--disable-logging")

    driver = uc.Chrome(
        options=options,
        use_subprocess=True,
        version_main=145,
        browser_executable_path="/home/cuthbert/.local/bin/google-chrome"
    )
    return driver


async def stealth_browser(platform: str, headless: bool = True) -> uc.Chrome:
    """Launch an undetected Chrome session with injected session cookies.

    Parameters
    ----------
    platform : str
        One of ``"X"``, ``"LINKEDIN"``, ``"IG"`` — used to look up the
        corresponding ``<PLATFORM>_COOKIES_B64`` env var.
    headless : bool
        Run headless (default True). Set False for visible login flows.

    Returns
    -------
    uc.Chrome
        A Selenium WebDriver instance.  Caller is responsible for
        calling ``driver.quit()`` when done.
    """
    loop = asyncio.get_running_loop()
    driver = await loop.run_in_executor(
        None, functools.partial(_create_driver, headless=headless)
    )

    # Platform → base URL mapping for cookie injection
    base_urls = {
        "X": "https://x.com",
        "LINKEDIN": "https://www.linkedin.com",
        "IG": "https://www.instagram.com",
    }
    base_url = base_urls.get(platform.upper(), "https://www.google.com")

    # Navigate to the base domain so cookies can be set
    await loop.run_in_executor(None, driver.get, base_url)

    # Inject session cookies
    cookie_var = f"{platform.upper()}_COOKIES_B64"
    cookies = load_cookies(cookie_var)
    if cookies:
        selenium_cookies = convert_cookies_to_selenium(cookies)
        for cookie in selenium_cookies:
            try:
                driver.add_cookie(cookie)
            except Exception as exc:
                log.debug("Skipped cookie %s: %s", cookie.get("name"), exc)
        log.info("Injected %d cookies for %s.", len(selenium_cookies), platform)

        # Refresh to apply cookies
        await loop.run_in_executor(None, driver.refresh)
    else:
        log.warning("No cookies available for %s — session may fail.", platform)

    return driver
