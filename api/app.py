#!/usr/bin/env python3
"""Vercel-compatible ASGI entrypoint for Jarvis API.

This module exports the FastAPI app that Vercel will deploy.
It's separate from api_bridge.py (which runs aiohttp locally).

For local development, use: python -m jarvis.api_bridge
For Vercel deployment, Vercel will load this app.py
"""

import os
from typing import Any

# Use FastAPI for Vercel (ASGI-compatible)
try:
    from fastapi import FastAPI, HTTPException, WebSocketException
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse
except ImportError:
    print("ERROR: FastAPI not installed. Run: pip install fastapi uvicorn")
    exit(1)

# Create the FastAPI app
app = FastAPI(
    title="Jarvis API",
    description="Command dispatch and API bridge for Jarvis assistant",
    version="1.0.0"
)

# Add CORS middleware for web UI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Health Check ───────────────────────────────────────────────────


@app.get("/api/health")
async def health_check() -> dict[str, Any]:
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": "jarvis-api",
        "version": "1.0.0"
    }


# ── Command Dispatch ────────────────────────────────────────────────


@app.post("/api/command")
async def dispatch_command(request: dict[str, Any]) -> dict[str, Any]:
    """Dispatch a command to the Jarvis router.
    
    Expected JSON body:
        {"command": "/status"}
    
    Returns:
        {"success": bool, "response": str, "error": str | None}
    """
    command = request.get("command", "").strip()
    
    if not command:
        raise HTTPException(status_code=400, detail="command is required")
    
    try:
        from jarvis.clawdbot.router import dispatch
        
        print(f"[v0] API command received: {command}")
        
        # Dispatch command to router (sync wrapper)
        response = await dispatch(command)
        
        print(f"[v0] API response: {response}")
        
        return {
            "success": True,
            "response": response,
            "error": None
        }
    
    except Exception as e:
        error_msg = str(e)
        print(f"[v0] API error: {error_msg}")
        return {
            "success": False,
            "response": None,
            "error": error_msg
        }


# ── Command List ───────────────────────────────────────────────────


@app.get("/api/commands")
async def list_commands() -> dict[str, Any]:
    """List all available Jarvis commands."""
    try:
        from jarvis.clawdbot.router import list_available_commands
        
        commands = await list_available_commands()
        
        return {
            "success": True,
            "commands": commands,
            "error": None
        }
    
    except Exception as e:
        return {
            "success": False,
            "commands": [],
            "error": str(e)
        }


# ── Root Redirect ──────────────────────────────────────────────────


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint - redirects to docs."""
    return {
        "message": "Jarvis API is running",
        "docs": "/docs",
        "endpoints": {
            "health": "GET /api/health",
            "command": "POST /api/command",
            "commands": "GET /api/commands"
        }
    }


# ── Vercel Compatibility ───────────────────────────────────────────


# Vercel's serverless functions need specific patterns
# This is already compatible as a standard ASGI app

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    
    uvicorn.run(
        "api.app:app",
        host=host,
        port=port,
        reload=True
    )
