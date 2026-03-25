"""Web search tool — free DuckDuckGo search, no API key needed."""

import logging
from jarvis.agent.tool_registry import tool

log = logging.getLogger("jarvis.agent.tools.web_search")


@tool(
    name="web_search",
    description="Search the web using DuckDuckGo. Returns top results with titles, URLs, and snippets.",
    parameters={
        "query": {
            "type": "string",
            "description": "The search query to look up.",
            "required": True,
        },
        "max_results": {
            "type": "integer",
            "description": "Maximum number of results to return (default 5).",
            "required": False,
        },
    },
)
async def web_search(query: str, max_results: int = 5) -> str:
    """Search DuckDuckGo and return formatted results."""
    try:
        from duckduckgo_search import DDGS
    except ImportError:
        return "❌ duckduckgo-search not installed. Run: pip install duckduckgo-search"

    log.info("Web search: %s (max %d results)", query, max_results)
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))

        if not results:
            return f"🔍 No results found for: {query}"

        lines = [f"🔍 Search results for: **{query}**\n"]
        for i, r in enumerate(results, 1):
            title = r.get("title", "No title")
            href = r.get("href", "")
            body = r.get("body", "")[:300]
            lines.append(f"{i}. **{title}**\n   {href}\n   {body}\n")

        return "\n".join(lines)
    except Exception as exc:
        log.exception("DuckDuckGo search failed.")
        return f"❌ Search failed: {exc}"
