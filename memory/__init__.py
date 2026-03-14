"""Jarvis Memory — long-term recall and writing-style retrieval."""

import json
import os
import logging

log = logging.getLogger("jarvis.memory")

_STORE_PATH = os.path.join(
    os.path.dirname(__file__), "context_store.json"
)


def _load_store() -> dict:
    """Load the JSON-LD context store from disk."""
    if not os.path.exists(_STORE_PATH):
        return {}
    with open(_STORE_PATH, "r") as f:
        return json.load(f)


def _save_store(store: dict) -> None:
    """Persist the context store to disk."""
    with open(_STORE_PATH, "w") as f:
        json.dump(store, f, indent=2)


async def recall_writing_style() -> str:
    """Return a text summary of the user's writing style for the Ghostwriter.

    Reads ``writing_style`` from ``context_store.json`` and formats it
    as a human-readable style guide string.
    """
    store = _load_store()
    style = store.get("writing_style", {})

    parts = [
        f"Tone: {style.get('tone', 'professional yet approachable')}",
        f"Formality: {style.get('formality', 'semi-formal')}",
    ]
    phrases = style.get("sample_phrases", [])
    if phrases:
        parts.append("Sample phrases: " + "; ".join(phrases))
    vocab = style.get("vocabulary_preferences", [])
    if vocab:
        parts.append("Preferred vocabulary: " + ", ".join(vocab))

    guide = "\n".join(parts)
    log.info("Recalled writing style (%d chars).", len(guide))
    return guide


async def store_conversation(role: str, content: str) -> None:
    """Append a message to the conversation history in the context store."""
    store = _load_store()
    convos = store.setdefault("conversations", [])
    convos.append({"role": role, "content": content[:2000]})

    # Keep only the last 500 messages to avoid unbounded growth
    if len(convos) > 500:
        store["conversations"] = convos[-500:]

    _save_store(store)
    log.debug("Stored %s message (%d chars).", role, len(content))


async def get_recent_context(n: int = 20) -> list[dict]:
    """Return the last ``n`` conversation entries."""
    store = _load_store()
    return store.get("conversations", [])[-n:]
