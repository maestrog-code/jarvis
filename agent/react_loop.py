"""ReAct (Reason + Act) Agent Loop — the agentic planning engine for Jarvis.

This module powers Kimi-style autonomous tool use. Given a goal, it asks
the local Ollama model to reason and choose the next tool, executes that
tool, feeds the result back, and loops until the goal is achieved.

Usage::

    from jarvis.agent.react_loop import run_agent

    result = await run_agent("Search the web for AI trends and summarise in 5 bullets")
    print(result.final_answer)
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import re
from dataclasses import dataclass, field
from typing import Optional

import aiohttp

# Auto-import all tools so they register themselves
import jarvis.agent.tools  # noqa: F401

from jarvis.agent.tool_registry import call_tool, format_tools_for_prompt

log = logging.getLogger("jarvis.agent.react_loop")

# Align with Jarvis defaults from .env
OLLAMA_URL = os.environ.get("OLLAMA_URL") or os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
DEFAULT_MODEL = os.environ.get("AGENT_MODEL") or os.environ.get("OLLAMA_MODEL", "llama3.2:latest")
MAX_STEPS = int(os.environ.get("AGENT_MAX_STEPS", "10"))


# ── Data Structures ────────────────────────────────────────────────────────────


@dataclass
class AgentStep:
    """One step in the agent's execution trace."""

    step: int
    thought: str = ""
    action: str = ""       # tool name
    action_input: dict = field(default_factory=dict)
    observation: str = ""
    is_final: bool = False


@dataclass
class AgentResult:
    """The final result of a run_agent call."""

    goal: str
    final_answer: str
    steps: list[AgentStep] = field(default_factory=list)
    success: bool = True
    error: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "goal": self.goal,
            "final_answer": self.final_answer,
            "steps": [
                {
                    "step": s.step,
                    "thought": s.thought,
                    "action": s.action,
                    "action_input": s.action_input,
                    "observation": s.observation[:500],  # truncate for JSON
                    "is_final": s.is_final,
                }
                for s in self.steps
            ],
            "success": self.success,
            "error": self.error,
        }


# ── System Prompt ──────────────────────────────────────────────────────────────


def _build_system_prompt() -> str:
    tools_str = format_tools_for_prompt()
    return f"""You are Jarvis. Complete the goal using tools.
{tools_str}

FORMAT:
THOUGHT: <reasoning>
ACTION: <tool_name>
INPUT: <JSON>
-- OR --
THOUGHT: <reasoning>
DONE: <final answer>

RULES:
- Start with THOUGHT. Valid JSON in INPUT.
- Max {MAX_STEPS} steps.
"""


# ── LLM Call ──────────────────────────────────────────────────────────────────


async def _call_ollama(messages: list[dict], model: str) -> str:
    """Send messages to Ollama and return the assistant's text response."""
    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{OLLAMA_URL}/api/chat",
            json=payload,
            timeout=aiohttp.ClientTimeout(total=300),
        ) as resp:
            if resp.status != 200:
                body = await resp.text()
                raise RuntimeError(f"Ollama error {resp.status}: {body[:300]}")
            data = await resp.json()
            return data["message"]["content"]


# ── Response Parser ────────────────────────────────────────────────────────────


@dataclass
class _ParsedResponse:
    thought: str
    is_done: bool
    done_text: str = ""
    action: str = ""
    action_input: dict = field(default_factory=dict)
    parse_error: str = ""


def _parse_response(text: str) -> _ParsedResponse:
    """Parse the model's raw text into a structured response."""
    thought = ""
    thought_match = re.search(r"THOUGHT:\s*(.+?)(?=\n(?:ACTION|DONE):|$)", text, re.DOTALL)
    if thought_match:
        thought = thought_match.group(1).strip()

    # Check for DONE
    done_match = re.search(r"DONE:\s*(.+)", text, re.DOTALL)
    if done_match:
        return _ParsedResponse(thought=thought, is_done=True, done_text=done_match.group(1).strip())

    # Check for ACTION
    action_match = re.search(r"ACTION:\s*(\S+)", text)
    input_match = re.search(r"INPUT:\s*(\{.+?\}|\[.+?\])", text, re.DOTALL)

    if not action_match:
        return _ParsedResponse(
            thought=thought,
            is_done=False,
            parse_error=f"Could not find ACTION or DONE in response:\n{text[:400]}",
        )

    action = action_match.group(1).strip()
    action_input: dict = {}

    if input_match:
        try:
            action_input = json.loads(input_match.group(1))
        except json.JSONDecodeError as e:
            return _ParsedResponse(
                thought=thought,
                is_done=False,
                parse_error=f"Invalid JSON in INPUT: {e}",
            )

    return _ParsedResponse(thought=thought, is_done=False, action=action, action_input=action_input)


# ── Main Agent Loop ────────────────────────────────────────────────────────────


async def run_agent(
    goal: str,
    model: str = DEFAULT_MODEL,
    max_steps: int = MAX_STEPS,
) -> AgentResult:
    """Run the ReAct agentic loop for a given goal.

    Parameters
    ----------
    goal : str
        The natural language goal for the agent.
    model : str
        Ollama model name (default: ``llama3.2`` or ``AGENT_MODEL`` env var).
    max_steps : int
        Maximum number of tool-use cycles before forcing a final answer.

    Returns
    -------
    AgentResult
        Contains the final answer, all steps taken, and success/error info.
    """
    log.info("🤖 Agent starting — goal: %s", goal[:100])

    messages: list[dict] = [
        {"role": "system", "content": _build_system_prompt()},
        {"role": "user", "content": f"GOAL: {goal}"},
    ]
    steps: list[AgentStep] = []

    for step_num in range(1, max_steps + 1):
        log.info("Agent step %d/%d", step_num, max_steps)

        try:
            raw_response = await _call_ollama(messages, model)
        except Exception as exc:
            log.exception("Ollama call failed at step %d.", step_num)
            return AgentResult(
                goal=goal,
                final_answer=f"❌ Agent failed: could not reach Ollama — {exc}",
                steps=steps,
                success=False,
                error=str(exc),
            )

        log.debug("Model response:\n%s", raw_response[:500])
        parsed = _parse_response(raw_response)

        if parsed.parse_error:
            log.warning("Parse error at step %d: %s", step_num, parsed.parse_error)
            # Feed the error back so the model can correct itself
            messages.append({"role": "assistant", "content": raw_response})
            messages.append({
                "role": "user",
                "content": (
                    f"⚠️ Parse error: {parsed.parse_error}\n"
                    "Please respond again in the correct format (THOUGHT / ACTION / INPUT or DONE)."
                ),
            })
            continue

        step = AgentStep(step=step_num, thought=parsed.thought)

        if parsed.is_done:
            step.is_final = True
            step.action = "DONE"
            steps.append(step)
            log.info("✅ Agent complete after %d steps.", step_num)
            return AgentResult(
                goal=goal,
                final_answer=parsed.done_text,
                steps=steps,
                success=True,
            )

        # Execute the tool
        step.action = parsed.action
        step.action_input = parsed.action_input
        log.info("Calling tool: %s(%s)", parsed.action, parsed.action_input)

        observation = await call_tool(parsed.action, parsed.action_input)
        step.observation = observation
        steps.append(step)
        log.info("Tool result: %s…", observation[:150])

        # Append the turn to the conversation history
        messages.append({"role": "assistant", "content": raw_response})
        messages.append({
            "role": "user",
            "content": f"OBSERVATION:\n{observation}\n\nContinue. What is your next step?",
        })

    # Max steps reached — ask for a final answer based on what's been gathered
    log.warning("Max steps (%d) reached. Requesting final answer.", max_steps)
    messages.append({
        "role": "user",
        "content": (
            "You have reached the maximum number of steps. "
            "Based on everything gathered so far, provide your FINAL answer now using: "
            "THOUGHT: <reasoning>\nDONE: <answer>"
        ),
    })
    try:
        raw = await _call_ollama(messages, model)
        parsed = _parse_response(raw)
        final = parsed.done_text or parsed.thought or raw[:500]
    except Exception:
        final = "⚠️ Agent reached max steps and could not produce a final answer."

    return AgentResult(
        goal=goal,
        final_answer=final,
        steps=steps,
        success=True,
    )
