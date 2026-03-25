"""Tool Registry — decorator-based registration of agentic tools.

Usage::

    from jarvis.agent.tool_registry import tool, get_tools, call_tool

    @tool(
        name="web_search",
        description="Search the web using DuckDuckGo.",
        parameters={
            "query": {"type": "string", "description": "Search query", "required": True}
        }
    )
    async def web_search(query: str) -> str:
        ...
"""

from __future__ import annotations

import json
import logging
from typing import Any, Callable, Awaitable

log = logging.getLogger("jarvis.agent.tool_registry")

# Registry: name → {fn, description, parameters}
_tools: dict[str, dict] = {}


def tool(name: str, description: str, parameters: dict[str, dict]):
    """Decorator to register an async function as an agentic tool.

    Parameters
    ----------
    name : str
        Unique tool name (e.g. ``"web_search"``).
    description : str
        Human/LLM-readable description of what the tool does.
    parameters : dict
        Schema of expected arguments: ``{param_name: {type, description, required}}``.
    """

    def decorator(fn: Callable[..., Awaitable[str]]):
        _tools[name] = {
            "fn": fn,
            "description": description,
            "parameters": parameters,
        }
        log.debug("Registered tool: %s", name)
        return fn

    return decorator


def get_tools() -> list[dict]:
    """Return tool schemas (without the fn) for feeding to the LLM."""
    return [
        {
            "name": name,
            "description": info["description"],
            "parameters": info["parameters"],
        }
        for name, info in _tools.items()
    ]


def format_tools_for_prompt() -> str:
    """Render the tool list as a compact string for the system prompt."""
    lines = []
    for t in get_tools():
        params = ", ".join(
            f"{k}: {v['type']} ({'required' if v.get('required') else 'optional'})"
            for k, v in t["parameters"].items()
        )
        lines.append(f"  • {t['name']}({params}) — {t['description']}")
    return "\n".join(lines)


async def call_tool(name: str, arguments: dict[str, Any]) -> str:
    """Look up a registered tool by name and invoke it.

    Returns the tool's string result, or an error message on failure.
    """
    entry = _tools.get(name)
    if entry is None:
        return f"❌ Unknown tool: {name!r}. Available: {', '.join(_tools)}"
    try:
        result = await entry["fn"](**arguments)
        return str(result)
    except Exception as exc:
        log.exception("Tool %s raised an error.", name)
        return f"❌ Tool {name!r} error: {exc}"
