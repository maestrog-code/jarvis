# Jarvis — Vercel Deployment Guide

## Fixed Issues

✅ **Error**: `No python entrypoint found`
✅ **Solution**: Created proper Vercel-compatible ASGI app in `api/app.py`

---

## What Changed

### New Files
- **`api/app.py`** — FastAPI entrypoint that Vercel will discover
- **`api/__init__.py`** — Python module init
- **`pyproject.toml`** — Python project config with dependencies
- **`vercel.json`** — Explicit Vercel configuration

### Updated Files
- **`requirements.txt`** — Added FastAPI, uvicorn, pydantic

---

## Architecture

### Local Development
```
main.py (long-running bot + scheduled tasks)
  ↓
api_bridge.py (aiohttp, port 8000)
  ↓
React frontend (localhost:3000)
```

### Vercel Deployment
```
api/app.py (FastAPI, auto-imported by Vercel)
  ↓
HTTP requests to /api/command
  ↓
Routes to clawdbot/router.py → dispatch()
  ↓
JSON response back to client
```

---

## Environment Variables (Set in Vercel Dashboard)

```env
TELEGRAM_BOT_TOKEN=your_token_from_botfather
API_BRIDGE_PORT=8000
API_BRIDGE_HOST=127.0.0.1
```

The bot (Telegram polling) **won't run on Vercel** (no persistent background processes).
Only the API server runs on Vercel.

---

## Deployment Steps

### 1. Push to GitHub
```bash
git add -A
git commit -m "Fix Vercel deployment entrypoint"
git push origin project-recovery-and-integration
```

### 2. Connect to Vercel (if not already done)
- Go to https://vercel.com
- Import `maestrog-code/jarvis` repo
- Set environment variables in "Settings → Environment Variables"
- Click "Deploy"

### 3. Verify Deployment
```bash
# After deployment, test the API:
curl https://your-vercel-url.vercel.app/api/health
# Should return: {"status":"ok","service":"jarvis-api","version":"1.0.0"}
```

---

## API Endpoints (Live on Vercel)

| Method | Endpoint | Body |
|--------|----------|------|
| GET | `/api/health` | — |
| POST | `/api/command` | `{"command": "/status"}` |
| GET | `/api/commands` | — |
| GET | `/` | — |
| GET | `/docs` | — (Swagger UI) |

---

## Testing Endpoints

```bash
# Health check
curl https://your-vercel-url.vercel.app/api/health

# Run command
curl -X POST https://your-vercel-url.vercel.app/api/command \
  -H "Content-Type: application/json" \
  -d '{"command": "/status"}'

# List available commands
curl https://your-vercel-url.vercel.app/api/commands

# View API docs
# Open: https://your-vercel-url.vercel.app/docs
```

---

## Local vs. Vercel

| Feature | Local | Vercel |
|---------|-------|--------|
| API endpoints | ✅ Yes | ✅ Yes |
| Telegram bot polling | ✅ Yes | ❌ No (serverless) |
| Scheduled briefing | ✅ Yes | ❌ No (needs queue) |
| Sentinel monitoring | ✅ Yes | ❌ No (needs queue) |

**For background jobs on Vercel**, consider:
- Vercel Cron Functions
- AWS Lambda + EventBridge
- External job queue (Bull, Celery)

---

## Running Locally (After Vercel Fix)

```bash
# Terminal 1: Main bot
python -m jarvis.main

# Terminal 2: API bridge (alternative to Vercel)
python -m jarvis.api_bridge

# Terminal 3: React frontend
npm start
```

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'api'"
- Check that `api/__init__.py` exists
- Run: `pip install -e .` (editable install)

### "No module named 'jarvis'"
- Ensure you're in the project root
- Run: `pip install -e .`

### Vercel says "No Python entrypoint"
- Check that `api/app.py` exists
- Check that `pyproject.toml` lists FastAPI in dependencies
- Try deleting `.vercel/` cache and redeploy

### Deployment timeout
- Increase build timeout in `vercel.json` or dashboard
- Remove heavy dependencies if not needed locally

---

## Next: Frontend Integration

Update your React `.env`:
```env
REACT_APP_API_URL=https://your-vercel-url.vercel.app
```

Then use in React:
```tsx
const response = await fetch(
  `${process.env.REACT_APP_API_URL}/api/command`,
  {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ command: '/status' })
  }
)
```

---

## Support

- Vercel docs: https://vercel.com/docs/frameworks/backend/python
- FastAPI docs: https://fastapi.tiangolo.com
- GitHub issues: maestrog-code/jarvis
