# 🤖 Jarvis — Personal AI Assistant

> **Project Jarvis** is a sophisticated, self-regulating AI assistant that manages your social media, reads your emails, and operates across X (Twitter), LinkedIn, and Instagram with human-in-the-loop safety gates.

## 📋 Quick Overview

| Component | Status | Purpose |
|-----------|--------|---------|
| **Python Backend** | ✅ Complete | Clawdbot, Skills, Safety layer |
| **HTTP API Bridge** | ✅ NEW | Exposes commands to React frontend |
| **React Client** | 🔧 Template | Ready-to-use TypeScript hooks & components |
| **Telegram Bot** | ✅ Complete | Primary UI for commands |
| **Social Media Publishing** | ✅ Complete | X, LinkedIn with Selenium automation |
| **HITL (Human-in-the-loop)** | ✅ Complete | Approval workflow for all posts |

---

## 🚀 Quick Start (< 5 minutes)

### Option 1: Automatic (Recommended)

```bash
# macOS / Linux
chmod +x start.sh
./start.sh

# Windows
start.bat

# Or cross-platform
python start.py
```

### Option 2: Manual

**Terminal 1 — Telegram Bot + Background Tasks:**
```bash
python -m jarvis.main
```

**Terminal 2 — HTTP API Bridge:**
```bash
python -m jarvis.api_bridge
```

**Terminal 3 — Test the API:**
```bash
curl http://localhost:8000/api/command \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"command": "/status"}'
```

✅ **You should see a response with status info!**

---

## 📦 What's Included

### Backend Services

- **`main.py`** — Orchestrator (Telegram polling + background tasks)
- **`clawdbot/`** — Command router & Telegram adapter
- **`skills/`** — Publisher, Newsroom, Sentinel, Ghostwriter
- **`safety/`** — HITL approval, killswitch, anomaly detection
- **`memory/`** — Context store (Chroma + JSON)
- **`browser/`** — Stealth Chrome automation (Selenium)

### New Integration Files

- **`api_bridge.py`** ← HTTP/WebSocket API for web UI
- **`frontend-client.ts`** ← React hook for commands
- **`CommandTerminal-example.tsx`** ← React component template
- **`start.sh` / `start.bat` / `start.py`** ← Launcher scripts
- **`test-commands.sh`** ← API test suite
- **`.env.example`** ← Environment configuration template

### Documentation

- **`SETUP.md`** — Complete setup guide with troubleshooting
- **`INTEGRATION_SUMMARY.md`** — Integration overview & architecture
- **`SOUL.md`** — Jarvis's core identity & directives
- **`README.md`** ← You are here

---

## 🎮 Available Commands

The **Command Terminal** responds to these slash commands:

```
/help                    List all commands
/status                  System health report
/briefing                Fetch and summarize news (morning)
/post <platform> <text>  Queue a post (X, LinkedIn)
/drafts                  Show pending posts awaiting approval
/approve <id>            Approve and publish a post
/reject <id>             Reject a queued post
/sentinel on|off         Toggle Instagram monitoring
/keywords add|remove <word>  Manage alert keywords
/kill                    Emergency shutdown (AUTO-KILL)
```

### Example Workflow

```bash
# Get system status
$ /status
📊 **Jarvis Status Report**
**Status:** 🟢 Active
**Uptime:** 2h 34m 10s
**Active tasks:** sentinel, briefing, hitl-expiry

# Queue a post
$ /post x "Excited to announce Jarvis! 🤖 #AI #Assistant"
📝 Post queued (ID `post_abc123`). Reply `/approve post_abc123` to publish.

# Show drafts
$ /drafts
📋 **Pending Drafts**
• `post_abc123` — **x**: Excited to announce Jarvis! 🤖 #AI...

# Approve it
$ /approve post_abc123
✅ Post published to x.
```

---

## 🔗 API Endpoints

All endpoints return JSON with `status: "ok"` or `"error"`.

### Health Check
```bash
GET /api/health
```
Response: `{"status":"ok","service":"jarvis-api-bridge","last_command":"/status"}`

### Send Command
```bash
POST /api/command
Content-Type: application/json

{"command": "/status"}
```
Response:
```json
{
  "response": "📊 **Jarvis Status Report**...",
  "status": "ok",
  "command": "/status"
}
```

### List Commands
```bash
GET /api/commands
```
Response:
```json
{
  "commands": {
    "/help": "List all commands",
    "/status": "System health report",
    ...
  },
  "count": 11
}
```

### WebSocket (Real-time)
```
WS ws://localhost:8000/ws

Send: {"type": "command", "command": "/status"}
Receive: {"type": "response", "data": "...", "command": "/status"}
```

---

## 🎨 Using with React

### 1. Copy Files to Your React Project

```bash
# Copy client hook
cp frontend-client.ts src/hooks/useJarvisCommand.ts

# Copy example component (optional)
cp CommandTerminal-example.tsx src/components/CommandTerminal.tsx
```

### 2. Set Environment Variable

```env
# In your React .env
REACT_APP_JARVIS_API_URL=http://localhost:8000
```

### 3. Use the Hook

```tsx
import { useJarvisCommand } from './hooks/useJarvisCommand'

export function MyComponent() {
  const { sendCommand, response, loading, error } = useJarvisCommand()

  return (
    <div>
      <input 
        onKeyDown={(e) => {
          if (e.key === 'Enter') {
            sendCommand(e.currentTarget.value)
            e.currentTarget.value = ''
          }
        }}
      />
      {loading && <p>Sending...</p>}
      {error && <p style={{color:'red'}}>{error}</p>}
      {response && <pre>{response}</pre>}
    </div>
  )
}
```

### 4. Run React App

```bash
npm run dev    # Next.js
# or
yarn start     # Create React App
```

Open http://localhost:3000 and start commanding! 🎉

---

## 🧪 Test the Integration

Run the automated test suite:

```bash
chmod +x test-commands.sh
./test-commands.sh        # Run all tests
./test-commands.sh status # Test /status only
VERBOSE=true ./test-commands.sh  # Detailed output
```

Expected output:
```
✅ API is reachable
✅ PASS (health)
✅ PASS (commands list)
✅ PASS (help)
✅ PASS (status)
...
🎉 Test Suite Complete!
```

---

## ⚙️ Configuration

### Minimum Setup

```env
# .env
TELEGRAM_BOT_TOKEN=your_token_from_botfather
API_BRIDGE_PORT=8000
API_BRIDGE_HOST=127.0.0.1
```

### Full Setup (with social media)

See **`.env.example`** for complete configuration including:
- X (Twitter) credentials
- LinkedIn credentials
- Google Workspace access
- Ollama (local LLM)
- Memory/Vector DB settings
- Safety parameters

---

## 🛡️ Safety Features

### Human-in-the-Loop (HITL)

Every post must be explicitly approved before publishing:

1. User: `/post x "Tweet text"`
2. Jarvis: "📝 Post queued (ID 123)"
3. User reviews: `/drafts`
4. User: `/approve 123` ✅ or `/reject 123` ❌

### AUTO-KILL Emergency Brake

If suspicious activity detected:
```bash
/kill
```

This immediately halts all sessions and disables publishing. Only manual restart will resume operations.

### Anomaly Detection

Automatically flags unusual patterns (e.g., too many requests, failed auth, locked accounts).

---

## 📊 Architecture

```
┌─────────────────────────────────────────┐
│        React Frontend (Port 3000)       │
│    useJarvisCommand hook + component    │
└────────────────┬────────────────────────┘
                 │ HTTP/JSON (Port 8000)
                 ▼
        ┌──────────────────┐
        │  api_bridge.py   │ ◄─ NEW
        │  (FastAPI/aiohttp)
        └────────┬─────────┘
                 │
    ┌────────────┼────────────┐
    ▼            ▼            ▼
┌─────────┬──────────┬───────────────────┐
│ Router  │ HITL     │ Skills Execution  │
│Dispatch │ Approval │ (Publisher, etc)  │
└─────────┴──────────┴───────────────────┘
    │        │              │
    └────────┼──────────────┘
             │
    ┌────────▼────────────────┐
    │  Telegram Bot           │
    │ (Background Task)       │
    │ + Scheduled Briefing    │
    │ + Sentinel (IG Monitor) │
    └─────────────────────────┘
```

---

## 🧠 How It Works

### Command Flow

1. **User sends command** via React terminal: `/post x "Hello"`
2. **React calls API:** `POST http://localhost:8000/api/command`
3. **api_bridge.py receives** and calls `router.dispatch()`
4. **router.py parses** command: `/post` → `post_cmd` handler
5. **Handler executes:** Queues post, generates approval ID
6. **Response returned:** JSON with queued post info
7. **React displays** response in terminal
8. **User can approve** via Telegram OR React: `/approve post_123`
9. **Publisher executes:** Opens browser, posts to platform

### Background Processes

- **Telegram bot** — Always polling for messages (primary UI)
- **Sentinel** — Monitors Instagram DMs for urgent keywords
- **Morning briefing** — Fetches news daily at 08:00
- **HITL expiry** — Cleans up old drafts after 24h

---

## 🐛 Troubleshooting

### Connection Refused
```bash
# Check if API is running
curl http://localhost:8000/api/health

# If not, start it
python -m jarvis.api_bridge
```

### React Cannot Connect
```bash
# Verify .env in React project
cat .env | grep JARVIS_API_URL

# Check CORS headers
curl -i http://localhost:8000/api/health
# Should see: Access-Control-Allow-Origin: *
```

### Port Already in Use
```bash
# Find what's using port 8000
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Use different port
export API_BRIDGE_PORT=8001
```

### Command Fails
```bash
# Check backend logs
tail -f logs/main.log
tail -f logs/api_bridge.log

# Test with curl
curl -X POST http://localhost:8000/api/command \
  -H "Content-Type: application/json" \
  -d '{"command": "/help"}'
```

See **`SETUP.md`** for detailed troubleshooting.

---

## 📚 Documentation

- **`SETUP.md`** — Complete setup & configuration guide
- **`INTEGRATION_SUMMARY.md`** — Architecture & integration details
- **`SOUL.md`** — Jarvis's core personality & directives
- **`api_bridge.py`** — HTTP bridge implementation (with docstrings)
- **`frontend-client.ts`** — React integration code (well-commented)

---

## 📈 Project Status

### ✅ Completed

- Python backend (all skills)
- Telegram bot integration
- Command router with 11 commands
- Safety gates (HITL, anomaly detection, killswitch)
- HTTP API bridge (NEW)
- React client library (NEW)
- React component template (NEW)
- Launcher scripts (NEW)
- Environment template (NEW)

### 🔄 Next Steps

1. **Copy frontend files** to your React project
2. **Run the stack** locally (`./start.sh` or `start.bat`)
3. **Test commands** via React terminal
4. **Add credentials** for social media (X, LinkedIn)
5. **Deploy** to production (update `API_BRIDGE_HOST` to `0.0.0.0`)

---

## 🎯 Key Features

✅ **Multi-platform publishing** — X, LinkedIn, Instagram (with HITL approval)
✅ **Browser automation** — Selenium + undetected-chromedriver (anti-detection)
✅ **Human-in-the-loop** — Approve/reject before posting
✅ **Memory layer** — 30+ days conversation context (Chroma)
✅ **Anomaly detection** — Flags suspicious activity
✅ **Emergency kill switch** — `/kill` stops all sessions
✅ **Telegram bot** — Native interface for commands
✅ **HTTP API** — Web UI integration (NEW)
✅ **WebSocket support** — Real-time streaming (NEW)
✅ **CORS enabled** — React frontend compatibility (NEW)

---

## 🚀 Deployment

### Local Development
```bash
./start.sh          # Unix/Mac
start.bat           # Windows
python start.py     # Cross-platform
```

### Production Readiness Checklist

- [ ] Set `API_BRIDGE_HOST=0.0.0.0` (external access)
- [ ] Enable HTTPS on API bridge
- [ ] Set up proper logging to files/CloudWatch
- [ ] Configure environment variables via CI/CD
- [ ] Test AUTO-KILL mechanism
- [ ] Set up database backups
- [ ] Configure alerts for anomalies
- [ ] Add API rate limiting
- [ ] Use OAuth for credentials (not hardcoded)

---

## 📝 License

Project Jarvis — Built with ❤️ and maintained by [Your Team]

---

## 🤝 Support

If you encounter issues:

1. Check **`SETUP.md`** troubleshooting section
2. Run test suite: `./test-commands.sh`
3. Check logs: `tail -f logs/main.log` & `tail -f logs/api_bridge.log`
4. Verify `.env` configuration
5. Ensure both services are running

---

## 🎉 Ready to Launch?

```bash
# Quick start
./start.sh          # macOS/Linux
# or
start.bat           # Windows
# or
python start.py     # Any platform

# Test it
./test-commands.sh

# Open React app
# http://localhost:3000

# Start commanding! 🚀
```

**Happy commanding!** 🤖✨
