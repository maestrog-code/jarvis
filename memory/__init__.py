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


# ── Vector Memory (ChromaDB) ──────────────────────────────────────────────────

_CHROMA_CLIENT = None
_COLLECTION = None


def _get_chroma():
    """Lazy initialize ChromaDB client and collection."""
    global _CHROMA_CLIENT, _COLLECTION
    if _CHROMA_CLIENT is None:
        try:
            import chromadb
            path = os.environ.get("CHROMA_DB_PATH", "./memory/chroma_db")
            name = os.environ.get("CHROMA_COLLECTION_NAME", "jarvis-context")
            _CHROMA_CLIENT = chromadb.PersistentClient(path=path)
            _COLLECTION = _CHROMA_CLIENT.get_or_create_collection(name=name)
        except Exception as e:
            log.error("Failed to init ChromaDB: %s", e)
            return None, None
    return _CHROMA_CLIENT, _COLLECTION


async def remember(text: str, metadata: dict = None) -> None:
    """Store a text snippet in the vector database."""
    _, collection = _get_chroma()
    if not collection:
        log.warning("ChromaDB not available, skipping remember.")
        return

    import uuid
    collection.add(
        documents=[text],
        metadatas=[metadata or {}],
        ids=[str(uuid.uuid4())]
    )
    log.info("Memory stored: %s...", text[:50])


async def recall(query: str, n_results: int = 5) -> list[str]:
    """Search for relevant past memories using vector similarity."""
    _, collection = _get_chroma()
    if not collection:
        log.warning("ChromaDB not available, skipping recall.")
        return []

    results = collection.query(
        query_texts=[query],
        n_results=n_results
    )
    # Chroma query returns list of lists for documents
    return results.get("documents", [[]])[0]
