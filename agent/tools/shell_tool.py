"""Shell tool — execute whitelisted shell commands safely."""

import asyncio
import logging
import shlex

from jarvis.agent.tool_registry import tool

log = logging.getLogger("jarvis.agent.tools.shell_tool")

# Only these commands are allowed — prevents arbitrary code execution
_ALLOWED_COMMANDS = {
    "ls", "cat", "echo", "pwd", "grep", "find", "head", "tail",
    "wc", "sort", "uniq", "cut", "awk", "sed", "date", "env",
    "python", "python3", "pip", "pip3", "npm", "node",
    "git", "curl", "wget",
}


def _is_safe(command: str) -> bool:
    """Check if the first token of the command is in the whitelist."""
    try:
        parts = shlex.split(command)
    except ValueError:
        return False
    if not parts:
        return False
    base = parts[0].split("/")[-1]  # strip path prefix (e.g. /usr/bin/ls → ls)
    return base in _ALLOWED_COMMANDS


@tool(
    name="run_shell",
    description=(
        "Run a whitelisted shell command and return its output. "
        "Allowed commands: ls, cat, grep, find, head, tail, wc, python, pip, git, curl, etc."
    ),
    parameters={
        "command": {
            "type": "string",
            "description": "Shell command to execute.",
            "required": True,
        },
        "timeout": {
            "type": "integer",
            "description": "Timeout in seconds (default 30).",
            "required": False,
        },
    },
)
async def run_shell(command: str, timeout: int = 30) -> str:
    """Execute a whitelisted shell command asynchronously."""
    if not _is_safe(command):
        first = shlex.split(command)[0] if command.strip() else command
        return (
            f"🔒 Command blocked: `{first}` is not in the allowed list.\n"
            f"Allowed: {', '.join(sorted(_ALLOWED_COMMANDS))}"
        )

    log.info("Running shell command: %s", command)
    try:
        proc = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(), timeout=timeout
            )
        except asyncio.TimeoutError:
            proc.kill()
            return f"⏱️ Command timed out after {timeout}s: `{command}`"

        output = stdout.decode("utf-8", errors="replace")
        errors = stderr.decode("utf-8", errors="replace")

        result = []
        if output.strip():
            result.append(f"```\n{output.strip()}\n```")
        if errors.strip():
            result.append(f"⚠️ stderr:\n```\n{errors.strip()}\n```")
        if not result:
            result.append("✅ Command completed with no output.")

        return "\n".join(result)
    except Exception as exc:
        log.exception("Shell command failed: %s", command)
        return f"❌ Shell error: {exc}"
