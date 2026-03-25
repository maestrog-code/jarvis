"""Memory tools — store and recall facts using Jarvis's ChromaDB memory layer."""

import logging

from jarvis.agent.tool_registry import tool

log = logging.getLogger("jarvis.agent.tools.memory_tools")


@tool(
    name="recall_memory",
    description="Search Jarvis long-term memory for relevant information about a topic.",
    parameters={
        "query": {
            "type": "string",
            "description": "What to search for in memory.",
            "required": True,
        },
        "max_results": {
            "type": "integer",
            "description": "Max number of memory entries to retrieve (default 5).",
            "required": False,
        },
    },
)
async def recall_memory(query: str, max_results: int = 5) -> str:
    """Query ChromaDB for relevant memories."""
    try:
        from jarvis.memory import recall
        results = await recall(query, n_results=max_results)

        if not results:
            return f"🧠 No memories found for: {query!r}"

        lines = [f"🧠 **Memory recall — '{query}'**:\n"]
        for i, entry in enumerate(results, 1):
            lines.append(f"{i}. {entry}")
        return "\n".join(lines)
    except ImportError:
        return "❌ Memory module not available (jarvis.memory not found)."
    except Exception as exc:
        log.exception("recall_memory failed for query: %s", query)
        return f"❌ Memory recall error: {exc}"


@tool(
    name="store_memory",
    description="Save an important fact or piece of information to Jarvis long-term memory.",
    parameters={
        "fact": {
            "type": "string",
            "description": "The information to store in memory.",
            "required": True,
        },
        "category": {
            "type": "string",
            "description": "Optional category/tag for the memory (e.g. 'research', 'task').",
            "required": False,
        },
    },
)
async def store_memory(fact: str, category: str = "general") -> str:
    """Store a fact in ChromaDB memory."""
    try:
        from jarvis.memory import remember
        await remember(fact, metadata={"category": category})
        log.info("Stored memory (category=%s): %s…", category, fact[:80])
        return f"✅ Stored in memory [{category}]: {fact[:200]}"
    except ImportError:
        return "❌ Memory module not available (jarvis.memory not found)."
    except Exception as exc:
        log.exception("store_memory failed.")
        return f"❌ Memory store error: {exc}"
