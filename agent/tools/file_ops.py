"""File operations tool — sandboxed read/write within the Jarvis project."""

import logging
import os
from pathlib import Path

from jarvis.agent.tool_registry import tool

log = logging.getLogger("jarvis.agent.tools.file_ops")

# Sandbox root — only allow access within the Jarvis project directory
_SANDBOX_ROOT = Path(__file__).resolve().parent.parent.parent


def _safe_path(relative_path: str) -> Path:
    """Resolve a path and ensure it stays inside the sandbox."""
    resolved = (_SANDBOX_ROOT / relative_path).resolve()
    if not str(resolved).startswith(str(_SANDBOX_ROOT)):
        raise PermissionError(f"Access denied: {relative_path!r} is outside the Jarvis directory.")
    return resolved


@tool(
    name="read_file",
    description="Read a file's contents from the Jarvis project directory.",
    parameters={
        "path": {
            "type": "string",
            "description": "Relative path to the file (from the Jarvis project root).",
            "required": True,
        },
        "max_chars": {
            "type": "integer",
            "description": "Max characters to return (default 4000).",
            "required": False,
        },
    },
)
async def read_file(path: str, max_chars: int = 4000) -> str:
    """Read a file and return its content."""
    try:
        full_path = _safe_path(path)
        if not full_path.exists():
            return f"❌ File not found: {path}"
        if not full_path.is_file():
            return f"❌ Not a file: {path}"
        content = full_path.read_text(encoding="utf-8", errors="replace")
        if len(content) > max_chars:
            content = content[:max_chars] + f"\n…[truncated at {max_chars} chars]"
        log.info("Read file: %s (%d chars)", path, len(content))
        return f"📄 **{path}**:\n```\n{content}\n```"
    except PermissionError as e:
        return f"🔒 {e}"
    except Exception as exc:
        log.exception("read_file failed for %s", path)
        return f"❌ Error reading file: {exc}"


@tool(
    name="write_file",
    description="Write or append text to a file in the Jarvis project directory.",
    parameters={
        "path": {
            "type": "string",
            "description": "Relative path to the file (from the Jarvis project root).",
            "required": True,
        },
        "content": {
            "type": "string",
            "description": "The text content to write.",
            "required": True,
        },
        "mode": {
            "type": "string",
            "description": "Write mode: 'write' (overwrite) or 'append'. Default: 'write'.",
            "required": False,
        },
    },
)
async def write_file(path: str, content: str, mode: str = "write") -> str:
    """Write or append to a file."""
    try:
        full_path = _safe_path(path)
        full_path.parent.mkdir(parents=True, exist_ok=True)
        file_mode = "a" if mode == "append" else "w"
        full_path.write_text(content, encoding="utf-8") if file_mode == "w" else \
            open(full_path, "a", encoding="utf-8").write(content)
        log.info("Wrote file: %s (%s, %d chars)", path, mode, len(content))
        return f"✅ File {'appended' if mode == 'append' else 'written'}: {path} ({len(content)} chars)"
    except PermissionError as e:
        return f"🔒 {e}"
    except Exception as exc:
        log.exception("write_file failed for %s", path)
        return f"❌ Error writing file: {exc}"
