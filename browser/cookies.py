"""Cookie management — load, save, encrypt, rotate, and format-convert session cookies."""

import os
import base64
import json
import logging
from cryptography.fernet import Fernet

log = logging.getLogger("jarvis.browser.cookies")


def _get_cipher() -> Fernet:
    """Return a Fernet cipher from the ENCRYPTION_KEY env var."""
    key = os.environ.get("ENCRYPTION_KEY")
    if not key:
        raise RuntimeError("ENCRYPTION_KEY environment variable is not set.")
    return Fernet(key.encode())


def load_cookies(env_var: str) -> list[dict]:
    """Decode a base64-encoded cookie jar from an environment variable.

    The value is expected to be: base64(Fernet-encrypted(json-cookies)).
    If ENCRYPTION_KEY is not set, falls back to plain base64.
    """
    raw_b64 = os.environ.get(env_var)
    if not raw_b64:
        log.warning("Cookie env var %s is empty — returning empty jar.", env_var)
        return []

    decoded = base64.b64decode(raw_b64)

    try:
        cipher = _get_cipher()
        decrypted = cipher.decrypt(decoded)
        return json.loads(decrypted)
    except Exception:
        # Fallback: assume plain JSON (useful during dev)
        log.warning("Decryption failed for %s — trying plain JSON.", env_var)
        return json.loads(decoded)


def save_cookies(cookies: list[dict], env_var: str) -> str:
    """Encrypt and base64-encode cookies; return the encoded string.

    The caller is responsible for persisting this value back into
    the environment or a secrets manager.
    """
    raw_json = json.dumps(cookies).encode()
    try:
        cipher = _get_cipher()
        encrypted = cipher.encrypt(raw_json)
    except RuntimeError:
        log.warning("No ENCRYPTION_KEY — storing cookies in plain base64.")
        encrypted = raw_json

    encoded = base64.b64encode(encrypted).decode()
    log.info("Cookies for %s encoded (%d bytes).", env_var, len(encoded))
    return encoded


# ── Format converters ──────────────────────────────────────────────


def convert_cookies_to_selenium(cookies: list[dict]) -> list[dict]:
    """Convert Playwright-format cookies to Selenium-compatible dicts.

    Playwright uses camelCase keys and slightly different sameSite
    values; Selenium expects different casing and field names.
    """
    converted: list[dict] = []
    for c in cookies:
        sc: dict = {
            "name": c.get("name", ""),
            "value": c.get("value", ""),
            "domain": c.get("domain", ""),
            "path": c.get("path", "/"),
        }

        # sameSite: Playwright uses "Strict"/"Lax"/"None";
        # Selenium expects the same strings but some cookies
        # may omit it entirely.
        same_site = c.get("sameSite", "")
        if same_site and same_site != "None":
            sc["sameSite"] = same_site

        if c.get("secure"):
            sc["secure"] = True

        if c.get("httpOnly"):
            sc["httpOnly"] = True

        # Expiry: Playwright uses "expires" (float epoch);
        # Selenium expects "expiry" (int epoch).
        if c.get("expires") and c["expires"] > 0:
            sc["expiry"] = int(c["expires"])

        converted.append(sc)

    return converted


def convert_cookies_from_selenium(cookies: list[dict]) -> list[dict]:
    """Convert Selenium ``driver.get_cookies()`` output to a generic format
    suitable for JSON storage and later re-injection.
    """
    converted: list[dict] = []
    for c in cookies:
        gc: dict = {
            "name": c.get("name", ""),
            "value": c.get("value", ""),
            "domain": c.get("domain", ""),
            "path": c.get("path", "/"),
            "secure": c.get("secure", False),
            "httpOnly": c.get("httpOnly", False),
        }

        if c.get("sameSite"):
            gc["sameSite"] = c["sameSite"]

        if c.get("expiry"):
            gc["expires"] = float(c["expiry"])

        converted.append(gc)

    return converted
