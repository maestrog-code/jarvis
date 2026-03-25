"""Skill tools — list and invoke existing Jarvis skills from the agent."""

import logging

from jarvis.agent.tool_registry import tool

log = logging.getLogger("jarvis.agent.tools.skill_tools")

# Map of skill names to their runnable coroutine functions
_SKILL_MAP = {
    "newsroom": "jarvis.skills.newsroom:run_newsroom",
    "ghostwriter": "jarvis.skills.ghostwriter:run_ghostwriter",
    "publisher": "jarvis.skills.publisher:run_publisher",
}


@tool(
    name="list_skills",
    description="List all available Jarvis skills that can be invoked by the agent.",
    parameters={},
)
async def list_skills() -> str:
    """Return a list of available skills."""
    lines = ["🛠️ **Available Jarvis Skills**:\n"]
    descriptions = {
        "newsroom": "Scrape X/Twitter for keyword mentions and summarise into a briefing.",
        "ghostwriter": "Fetch unread LinkedIn DMs and draft replies in your writing style.",
        "publisher": "Queue and publish approved content to social platforms.",
    }
    for name, desc in descriptions.items():
        lines.append(f"  • **{name}** — {desc}")
    return "\n".join(lines)


@tool(
    name="run_skill",
    description=(
        "Invoke a Jarvis skill by name. "
        "Use list_skills first to see what's available."
    ),
    parameters={
        "skill_name": {
            "type": "string",
            "description": "Name of the skill to run (e.g. 'newsroom', 'ghostwriter').",
            "required": True,
        },
    },
)
async def run_skill(skill_name: str) -> str:
    """Dynamically import and run a Jarvis skill."""
    skill_name = skill_name.lower().strip()
    entry = _SKILL_MAP.get(skill_name)

    if entry is None:
        available = ", ".join(f"`{s}`" for s in _SKILL_MAP)
        return f"❌ Unknown skill: `{skill_name}`. Available: {available}"

    module_path, fn_name = entry.rsplit(":", 1)
    log.info("Running skill: %s (%s)", skill_name, module_path)

    try:
        import importlib
        module = importlib.import_module(module_path)
        fn = getattr(module, fn_name)
        result = await fn()

        # Skills can return str or list[dict]; normalise to str
        if isinstance(result, list):
            lines = []
            for item in result:
                if isinstance(item, dict):
                    lines.append(
                        f"• **{item.get('sender', 'Unknown')}**: {item.get('draft', str(item))[:300]}"
                    )
                else:
                    lines.append(str(item))
            return f"✅ Skill `{skill_name}` complete:\n" + "\n".join(lines)
        return f"✅ Skill `{skill_name}` complete:\n{result}"
    except Exception as exc:
        log.exception("Skill %s failed.", skill_name)
        return f"❌ Skill `{skill_name}` error: {exc}"
