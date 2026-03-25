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
from typing import Optional

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

    async def dispatch_command(self, command: str) -> str:
        """Send command to the Clawdbot Router and return response."""
        from jarvis.clawdbot.router import dispatch

        self.last_command = command
        response = await dispatch(command)
        self.last_response = response

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


async def handle_feed(request: web.Request) -> web.Response:
    """GET /api/feed — return social media feed."""
    # Mock social media feed data
    mock_feed = [
        {
            "id": "1",
            "source": "x",
            "author": "Tech News Daily",
            "handle": "@technewsdaily",
            "text": "Breaking: AI systems now passing advanced reasoning benchmarks. What does this mean for the future?",
            "timestamp": "2 hours ago",
            "likes": 1250,
            "replies": 340,
        },
        {
            "id": "2", 
            "source": "linkedin",
            "author": "AI Research Team",
            "handle": "AIResearchTeam",
            "text": "Excited to announce our latest paper on autonomous agent optimization. The results are promising for real-world applications.",
            "timestamp": "4 hours ago",
            "likes": 890,
            "replies": 120,
        },
    ]
    return web.json_response({"data": mock_feed})


async def handle_memory(request: web.Request) -> web.Response:
    """GET /api/memory — return memory logs."""
    # Get recent command history from bridge
    memory_logs = []
    if bridge.last_command and bridge.last_response:
        memory_logs.append({
            "timestamp": "2024-03-14 16:00:00",
            "action": f"Executed: {bridge.last_command}",
            "status": "success"
        })
    
    return web.json_response({"data": memory_logs})


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
        from jarvis.agent.react_loop import run_agent

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

    load_dotenv()

    port = int(os.environ.get("API_BRIDGE_PORT", 8000))
    host = os.environ.get("API_BRIDGE_HOST", "127.0.0.1")

    try:
        await run_bridge(port=port, host=host)
    except KeyboardInterrupt:
        log.info("API Bridge shutting down.")


if __name__ == "__main__":
    asyncio.run(main_bridge())
