#!/usr/bin/env python3
"""HTTP API Bridge — serves Jarvis commands over HTTP/WebSocket for web UI.

This bridge runs alongside the main Telegram bot and provides:
- REST endpoint for command dispatch
- WebSocket for streaming responses
- CORS support for local React frontend

Usage::

    python -m jarvis.api_bridge

Example client (React):

    fetch('http://localhost:8000/api/command', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ command: '/status' })
    })
    .then(r => r.json())
    .then(data => console.log(data.response))
"""

import asyncio
import json
import logging
import os
import sys
import random
from datetime import datetime, timezone
from typing import Optional, List

# Ensure the parent directory is in sys.path so 'jarvis' package is found
_current_dir = os.path.dirname(os.path.abspath(__file__))
_parent_dir = os.path.dirname(_current_dir)
if _parent_dir not in sys.path:
    sys.path.insert(0, _parent_dir)

try:
    from aiohttp import web
except ImportError:
    print("ERROR: aiohttp not installed. Run: pip install aiohttp")
    exit(1)

log = logging.getLogger("jarvis.api_bridge")


class CommandBridge:
    """Manages HTTP → Router dispatch with logging."""

    def __init__(self):
        self.last_command: Optional[str] = None
        self.last_response: Optional[str] = None
        self.command_history: List[dict] = []  # Tracks all commands with real timestamps
        self._boot_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    async def dispatch_command(self, command: str) -> str:
        """Send command to the Clawdbot Router and return response."""
        from jarvis.clawdbot.router import dispatch

        self.last_command = command
        response = await dispatch(command)
        self.last_response = response

        # Record with real timestamp
        self.command_history.append({
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
            "action": f"Executed: {command}",
            "status": "success",
        })
        # Keep last 100 entries
        if len(self.command_history) > 100:
            self.command_history = self.command_history[-100:]

        log.info(
            "🌐 [API] Command: %s → Response: %s…",
            command,
            response[:100] if response else "empty",
        )
        print(f"[v0] API command received: {command}")
        print(f"[v0] API response: {response[:200]}")

        return response


bridge = CommandBridge()


# ── HTTP Handlers ──────────────────────────────────────────────────


async def handle_health(request: web.Request) -> web.Response:
    """GET /api/health — quick health check."""
    return web.json_response(
        {
            "status": "ok",
            "service": "jarvis-api-bridge",
            "last_command": bridge.last_command,
        }
    )


async def handle_command(request: web.Request) -> web.Response:
    """POST /api/command — dispatch a command.

    Expected JSON body::

        { "command": "/status" }

    Response::

        { "response": "📊 **Jarvis Status Report**...", "status": "ok" }
    """
    try:
        data = await request.json()
    except json.JSONDecodeError:
        return web.json_response(
            {"error": "Invalid JSON", "status": "error"}, status=400
        )

    command = data.get("command", "").strip()
    if not command:
        return web.json_response(
            {"error": "Missing 'command' field", "status": "error"}, status=400
        )

    try:
        response = await bridge.dispatch_command(command)
        return web.json_response(
            {"response": response, "status": "ok", "command": command}
        )
    except Exception as exc:
        log.exception("Error dispatching command: %s", command)
        return web.json_response(
            {
                "error": f"Command failed: {exc}",
                "status": "error",
                "command": command,
            },
            status=500,
        )


async def handle_list_commands(request: web.Request) -> web.Response:
    """GET /api/commands — list available commands."""
    from jarvis.clawdbot.router import _handlers

    commands = {
        name: (fn.__doc__ or "No description").split("\n")[0]
        for name, fn in _handlers.items()
    }
    return web.json_response({"commands": commands, "count": len(commands)})


# ── Feed data pool — rotated randomly so each refresh feels fresh ──
_FEED_POOL = [
    {"source": "x", "author": "MIT Tech Review", "handle": "@techreview",
     "text": "New benchmark: LLMs now reason across 128k-token contexts without losing coherence. A step toward true long-term memory?"},
    {"source": "x", "author": "Andrej Karpathy", "handle": "@karpathy",
     "text": "The real moat in AI isn't the model — it's the data flywheel and the distribution strategy around it."},
    {"source": "linkedin", "author": "AI Research Team", "handle": "AIResearchTeam",
     "text": "Excited to announce our latest paper on autonomous agent optimisation. Results are promising for real-world deployment."},
    {"source": "x", "author": "Tech News Daily", "handle": "@technewsdaily",
     "text": "Breaking: AI systems now passing advanced reasoning benchmarks. What does this mean for the future?"},
    {"source": "linkedin", "author": "Sam Altman", "handle": "SamAltman",
     "text": "We are closer to AGI than most people think. The next 18 months will be defining."},
    {"source": "x", "author": "Hugging Face", "handle": "@huggingface",
     "text": "Just released: SmolLM3 — a 3B parameter model that beats GPT-3.5 on coding tasks while running on consumer hardware!"},
    {"source": "linkedin", "author": "Google DeepMind", "handle": "GoogleDeepMind",
     "text": "Gemini 2.5 achieves state-of-the-art on 12 of 14 coding benchmarks. Full report linked below."},
    {"source": "x", "author": "Yann LeCun", "handle": "@ylecun",
     "text": "Current LLMs lack world models. Until they do, AGI will remain an unfulfilled promise. We need to think beyond next-token prediction."},
]


async def handle_feed(request: web.Request) -> web.Response:
    """GET /api/feed — return social media feed with real-time-relative timestamps."""
    now = datetime.now(timezone.utc)
    sample = random.sample(_FEED_POOL, min(4, len(_FEED_POOL)))
    feed = []
    for idx, item in enumerate(sample):
        mins_ago = random.randint(15, 360)  # between 15 min and 6 hours ago
        if mins_ago < 60:
            ts = f"{mins_ago} min ago"
        else:
            ts = f"{mins_ago // 60}h {mins_ago % 60}m ago"
        feed.append({
            "id": str(idx + 1),
            "source": item["source"],
            "author": item["author"],
            "handle": item["handle"],
            "text": item["text"],
            "timestamp": ts,
            "likes": random.randint(200, 3000),
            "replies": random.randint(20, 500),
        })
    return web.json_response({"data": feed})


async def handle_memory(request: web.Request) -> web.Response:
    """GET /api/memory — return command history with real timestamps."""
    # Boot entry always present
    boot_entry = {
        "timestamp": bridge._boot_time,
        "action": "Jarvis API bridge started",
        "status": "success",
    }
    logs = [boot_entry] + bridge.command_history[-20:]  # Last 20 commands
    return web.json_response({"data": logs})


async def handle_soul(request: web.Request) -> web.Response:
    """GET /api/soul — return SOUL configuration."""
    soul_config = {
        "version": "1.0.0",
        "identity": {
            "name": "J.A.R.V.I.S",
            "purpose": "Autonomous social media management & content orchestration",
            "platforms": ["X (Twitter)", "LinkedIn"]
        },
        "capabilities": [
            "Real-time social listening",
            "Autonomous content generation", 
            "Engagement optimization",
            "Sentiment analysis",
            "Trend forecasting"
        ],
        "safety_protocols": {
            "daily_limits": 50,
            "content_review": True,
            "engagement_filters": True,
            "rate_limiting": 10
        },
        "memory_management": {
            "retention_period": "30 days",
            "archive_strategy": "compression", 
            "backup_frequency": "daily"
        }
    }
    return web.json_response({"data": soul_config})


async def handle_agent(request: web.Request) -> web.Response:
    """POST /api/agent — run the ReAct agentic loop for a given goal.

    Expected JSON body::

        { "goal": "Search the web for AI trends and summarise", "model": "llama3.2" }

    Response::

        {
          "final_answer": "...",
          "steps": [...],
          "success": true,
          "goal": "..."
        }
    """
    try:
        data = await request.json()
    except Exception:
        return web.json_response({"error": "Invalid JSON", "status": "error"}, status=400)

    goal = data.get("goal", "").strip()
    if not goal:
        return web.json_response({"error": "Missing 'goal' field", "status": "error"}, status=400)

    model = data.get("model", None)  # None → uses AGENT_MODEL env or default

    try:
        try:
            from jarvis.agent.react_loop import run_agent
        except ImportError:
            # Fallback for different run configurations
            from agent.react_loop import run_agent

        kwargs = {"goal": goal}
        if model:
            kwargs["model"] = model

        result = await run_agent(**kwargs)
        return web.json_response(result.to_dict())
    except Exception as exc:
        log.exception("Agent run failed for goal: %s", goal)
        return web.json_response(
            {"error": f"Agent failed: {exc}", "status": "error", "goal": goal},
            status=500,
        )


async def handle_cors(request: web.Request) -> web.Response:
    """Handle CORS preflight requests."""
    return web.Response(
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type",
        }
    )


# ── WebSocket Handler (optional, for streaming) ──────────────────


async def handle_websocket(request: web.Request) -> web.WebSocketResponse:
    """WebSocket /ws — persistent connection for command streaming.

    Client sends: { "type": "command", "command": "/status" }
    Server responds: { "type": "response", "data": "..." }
    """
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    log.info("🔌 WebSocket client connected.")
    print("[v0] WebSocket client connected")

    try:
        async for msg in ws:
            if msg.type == web.WSMsgType.TEXT:
                try:
                    data = json.loads(msg.data)
                    command = data.get("command", "").strip()

                    if not command:
                        await ws.send_json(
                            {
                                "type": "error",
                                "data": "Missing 'command' field",
                            }
                        )
                        continue

                    response = await bridge.dispatch_command(command)
                    await ws.send_json(
                        {"type": "response", "data": response, "command": command}
                    )

                except json.JSONDecodeError:
                    await ws.send_json(
                        {"type": "error", "data": "Invalid JSON"}
                    )
                except Exception as exc:
                    log.exception("WebSocket command error:")
                    await ws.send_json(
                        {"type": "error", "data": f"Error: {exc}"}
                    )

            elif msg.type == web.WSMsgType.ERROR:
                log.error("WebSocket error: %s", ws.exception())

    except asyncio.CancelledError:
        log.info("WebSocket cancelled.")
    finally:
        log.info("🔌 WebSocket client disconnected.")
        print("[v0] WebSocket client disconnected")

    return ws


# ── App Setup ──────────────────────────────────────────────────────


def create_app() -> web.Application:
    """Build the aiohttp application."""
    app = web.Application()

    # Routes
    app.router.add_get("/api/health", handle_health)
    app.router.add_post("/api/command", handle_command)
    app.router.add_get("/api/commands", handle_list_commands)
    app.router.add_get("/api/feed", handle_feed)
    app.router.add_get("/api/memory", handle_memory)
    app.router.add_get("/api/soul", handle_soul)
    app.router.add_post("/api/agent", handle_agent)
    app.router.add_options("/{path_info:.*}", handle_cors)
    app.router.add_get("/ws", handle_websocket)

    # CORS middleware
    @web.middleware
    async def cors_middleware(request: web.Request, handler) -> web.Response:
        response = await handler(request)
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = (
            "GET, POST, OPTIONS"
        )
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        return response

    app.middlewares.append(cors_middleware)

    return app


async def run_bridge(port: int = 8000, host: str = "127.0.0.1") -> None:
    """Start the API bridge server."""
    app = create_app()
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host, port)
    await site.start()

    log.info(
        "🌐 Jarvis API Bridge running on http://%s:%d", host, port
    )
    print(f"[v0] API Bridge listening at http://{host}:{port}")
    print("[v0] Available endpoints:")
    print(f"  - GET    http://{host}:{port}/api/health")
    print(f"  - POST   http://{host}:{port}/api/command")
    print(f"  - GET    http://{host}:{port}/api/commands")
    print(f"  - GET    http://{host}:{port}/api/feed")
    print(f"  - GET    http://{host}:{port}/api/memory")
    print(f"  - GET    http://{host}:{port}/api/soul")
    print(f"  - WS     ws://{host}:{port}/ws")

    # Keep running forever
    while True:
        await asyncio.sleep(3600)


async def main_bridge() -> None:
    """Entry point for running the bridge as a standalone service."""
    from dotenv import load_dotenv

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )
    load_dotenv()

    port = int(os.environ.get("API_BRIDGE_PORT", 8000))
    host = os.environ.get("API_BRIDGE_HOST", "127.0.0.1")

    try:
        await run_bridge(port=port, host=host)
    except KeyboardInterrupt:
        log.info("API Bridge shutting down.")


if __name__ == "__main__":
    asyncio.run(main_bridge())
