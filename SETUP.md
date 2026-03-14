# 🚀 Jarvis Local Setup & Integration Guide

## Overview

Jarvis is a **full-stack AI assistant** with:
- **Backend:** Python (Clawdbot + skills + safety layer)
- **Frontend:** React (separate repo, to be integrated)
- **Bridge:** HTTP API (`api_bridge.py`) connecting the two

This guide walks you through running the complete local environment.

---

## 📋 Prerequisites

### System Requirements
- Python 3.11+
- Node.js 18+ (for React frontend, when ready)
- Chrome/Chromium (for Selenium-based publishing)

### Accounts Needed
- Telegram Bot Token (from @BotFather)
- X (Twitter) credentials (optional, for publishing)
- LinkedIn credentials (optional, for publishing)
- Google Service Account (optional, for Gmail reading)

---

## 🛠️ Step 1: Python Backend Setup

### 1.1 Clone & Install Dependencies

```bash
# Navigate to project root
cd /path/to/jarvis

# Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # macOS/Linux
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Install aiohttp for API bridge (not in requirements.txt yet)
pip install aiohttp>=3.9
```

### 1.2 Create `.env` File

```bash
# Copy the template
cp .env.example .env

# Edit with your credentials
nano .env
```

**Minimum required for Telegram:**
```env
TELEGRAM_BOT_TOKEN=your_token_here
API_BRIDGE_PORT=8000
API_BRIDGE_HOST=127.0.0.1
```

**To enable social media publishing, also add:**
```env
X_USERNAME=your_handle@example.com
X_PASSWORD=your_password
LINKEDIN_EMAIL=your_email@example.com
LINKEDIN_PASSWORD=your_password
```

---

## ▶️ Step 2: Running the Backend Locally

### Terminal 1: Telegram Bot + Background Tasks

```bash
# Run the main Jarvis orchestrator
# This starts:
# - Telegram bot polling
# - Morning briefing scheduler
# - Sentinel (Instagram monitor)
# - HITL expiry cleanup

python -m jarvis.main
```

**Expected Output:**
```
2026-03-14 10:30:15,123 [jarvis] INFO: 🚀 Jarvis is booting up…
2026-03-14 10:30:15,234 [jarvis] INFO: Background tasks launched: sentinel, briefing, hitl-expiry.
2026-03-14 10:30:15,345 [jarvis.clawdbot.telegram] INFO: 🤖 Telegram adapter online — polling for messages.
```

✅ **Jarvis is now running and listening on Telegram.**

### Terminal 2: HTTP API Bridge

```bash
# In a new terminal, start the API bridge
python -m jarvis.api_bridge
```

**Expected Output:**
```
2026-03-14 10:31:00,000 [jarvis.api_bridge] INFO: 🌐 Jarvis API Bridge running on http://127.0.0.1:8000
[v0] API Bridge listening at http://127.0.0.1:8000
[v0] Available endpoints:
  - GET    http://127.0.0.1:8000/api/health
  - POST   http://127.0.0.1:8000/api/command
  - GET    http://127.0.0.1:8000/api/commands
  - WS     ws://127.0.0.1:8000/ws
```

✅ **API Bridge is now ready to accept commands from the React frontend.**

---

## 🧪 Step 3: Test the Bridge

### 3.1 Test via Terminal

```bash
# Check health
curl http://localhost:8000/api/health

# List available commands
curl http://localhost:8000/api/commands

# Send a command
curl -X POST http://localhost:8000/api/command \
  -H "Content-Type: application/json" \
  -d '{"command": "/status"}'
```

### 3.2 Terminal Test (Watch Both Logs!)

In Terminal 1 (main.py), you should see:
```
[v0] API command received: /status
[v0] API response: 📊 **Jarvis Status Report**...
```

---

## 🎨 Step 4: React Frontend Integration

### 4.1 Import the Client Hook

Copy `frontend-client.ts` to your React project:

```bash
# In your React app
cp frontend-client.ts src/hooks/useJarvisCommand.ts
```

### 4.2 Example Command Terminal Component

```tsx
// src/components/CommandTerminal.tsx
import React, { useState } from 'react'
import { useJarvisCommand } from '../hooks/useJarvisCommand'

export function CommandTerminal() {
  const { sendCommand, response, loading, error, history } = useJarvisCommand()
  const [input, setInput] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim()) return

    await sendCommand(input)
    setInput('')
  }

  return (
    <div style={{ fontFamily: 'monospace', padding: '1rem' }}>
      <h2>🤖 Jarvis Command Terminal</h2>

      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Enter command (e.g., /status, /help)"
          style={{ width: '100%', padding: '0.5rem' }}
          disabled={loading}
        />
        <button type="submit" disabled={loading}>
          {loading ? 'Sending...' : 'Send'}
        </button>
      </form>

      {error && (
        <div style={{ color: 'red', marginTop: '1rem' }}>
          ❌ {error}
        </div>
      )}

      {response && (
        <pre
          style={{
            background: '#f0f0f0',
            padding: '1rem',
            marginTop: '1rem',
            whiteSpace: 'pre-wrap',
            wordBreak: 'break-word',
          }}
        >
          {response}
        </pre>
      )}

      {history.length > 0 && (
        <div style={{ marginTop: '1rem', fontSize: '0.9rem', color: '#666' }}>
          <strong>History:</strong> {history.join(' → ')}
        </div>
      )}
    </div>
  )
}
```

### 4.3 Add Environment Variable to React

In your React `.env` file:

```env
REACT_APP_JARVIS_API_URL=http://localhost:8000
```

---

## 📡 Command Reference

### Built-in Commands

The Command Terminal responds to these slash commands:

| Command | Description |
|---------|-------------|
| `/help` | List all available commands |
| `/status` | System health report |
| `/briefing` | Run morning briefing (fetch news) |
| `/post <platform> <content>` | Queue a post for approval |
| `/drafts` | List pending drafts for approval |
| `/approve <id>` | Approve a queued draft |
| `/reject <id>` | Reject a queued draft |
| `/sentinel on\|off` | Toggle Instagram monitor |
| `/keywords add\|remove <word>` | Manage urgent keywords |
| `/kill` | Emergency shutdown (AUTO-KILL) |

### Example Terminal Usage

```
> /status
📊 **Jarvis Status Report**

**Status:** 🟢 Active
**Uptime:** 0h 2m 15s
**Requests (5min window):** 3
**Active tasks:** sentinel, briefing, hitl-expiry
**Boot time:** 2026-03-14 10:30 UTC

> /post x "Hello world! This is my first automated post from Jarvis."
📝 Post queued (ID `post_1234567890`). Reply `/approve post_1234567890` to publish.

> /drafts
📋 **Pending Drafts**

• `post_1234567890` — **x**: Hello world! This is my first automated post...

> /approve post_1234567890
✅ Post published to x.
```

---

## 🔗 API Endpoints

All endpoints return JSON with `status: 'ok' | 'error'`.

### Health Check
```
GET /api/health

Response:
{
  "status": "ok",
  "service": "jarvis-api-bridge",
  "last_command": "/status"
}
```

### Send Command
```
POST /api/command
Content-Type: application/json

Request:
{ "command": "/status" }

Response:
{
  "response": "📊 **Jarvis Status Report**...",
  "status": "ok",
  "command": "/status"
}
```

### List Commands
```
GET /api/commands

Response:
{
  "commands": {
    "/help": "List all available commands",
    "/status": "System health report",
    ...
  },
  "count": 11
}
```

### WebSocket Streaming (Optional)
```
WS ws://localhost:8000/ws

Send:
{ "type": "command", "command": "/status" }

Receive:
{ "type": "response", "data": "📊 **Jarvis Status Report**...", "command": "/status" }
```

---

## 🧠 Memory & Context

Jarvis maintains 30+ days of conversation context using:
- **Chroma DB** (local vector database)
- **Conversation Store** (`memory/context_store.json`)

These are automatically managed. No setup needed.

---

## 🛡️ Safety Mechanisms

### HITL (Human-in-the-Loop)
Every post must be approved before publishing. The flow:

1. User sends: `/post x "My tweet"`
2. Jarvis queues it: `post_123`
3. User reviews: `/drafts`
4. User approves: `/approve post_123` ✅ or `/reject post_123` ❌

### AUTO-KILL Emergency Brake
If suspicious activity is detected, run:
```
/kill
```

This immediately halts all sessions and disables publishing.

---

## 🐛 Troubleshooting

### API Bridge Won't Start

```bash
# Check if port 8000 is in use
lsof -i :8000

# Use a different port
export API_BRIDGE_PORT=8001
python -m jarvis.api_bridge
```

### React Can't Connect to Backend

```bash
# Make sure both servers are running
curl http://localhost:8000/api/health

# Check .env in React
cat .env | grep JARVIS_API_URL

# Verify CORS headers (should include Access-Control-Allow-Origin: *)
```

### Commands Return Errors

Check the backend logs:
```bash
# Terminal 1: tail the jarvis.main output
# Terminal 2: tail the jarvis.api_bridge output

# Enable debug logging
export LOG_LEVEL=DEBUG
python -m jarvis.main
```

---

## 📦 Deployment Checklist

Before deploying to production:

- [ ] Set `API_BRIDGE_HOST=0.0.0.0` (allow external connections)
- [ ] Use environment variables for all secrets (never hardcode)
- [ ] Enable HTTPS on the API bridge
- [ ] Set up proper logging and monitoring
- [ ] Test AUTO-KILL mechanism
- [ ] Configure alerts for anomalies
- [ ] Set up database backups (for context store + memory)

---

## 📚 Additional Resources

- **SOUL.md** — Jarvis's core identity and directives
- **clawdbot/router.py** — Command dispatcher logic
- **skills/*.py** — Individual skill implementations
- **safety/*.py** — Safety gates, approval workflows, killswitches

---

## ❓ Support

If you encounter issues:

1. Check the logs (both Terminal 1 and Terminal 2)
2. Verify all `.env` variables are set
3. Run the health check: `curl http://localhost:8000/api/health`
4. Try a simple command: `/help`

**Happy commanding! 🚀**
