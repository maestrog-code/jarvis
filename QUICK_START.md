# Quick Start — Vercel Fix Applied ✅

## What Was Wrong
Vercel couldn't find a Python ASGI/WSGI entrypoint for deployment.

## What's Fixed
Created `api/app.py` with FastAPI—Vercel's Python runtime will auto-detect it.

---

## Deploy Now (5 Minutes)

### Step 1: Check Files
Verify these new files exist in your repo:
```
✅ api/app.py               (157 lines)
✅ api/__init__.py          (6 lines)
✅ pyproject.toml           (55 lines)
✅ vercel.json              (18 lines)
```

Check requirements.txt has:
```
✅ fastapi>=0.104
✅ uvicorn>=0.24
✅ pydantic>=2.0
```

### Step 2: Push to GitHub
```bash
git add -A
git commit -m "Fix Vercel deployment: add FastAPI entrypoint"
git push origin project-recovery-and-integration
```

### Step 3: Vercel Dashboard
1. Go to https://vercel.com/dashboard
2. Find your `jarvis` project
3. Click "Redeploy" or wait for auto-deployment from git push
4. Set environment variables if not set:
   - `TELEGRAM_BOT_TOKEN` = your bot token

### Step 4: Wait & Test
Deployment takes ~2-3 minutes. Then:
```bash
# Test health endpoint
curl https://your-deployment-url.vercel.app/api/health

# Should return:
# {"status":"ok","service":"jarvis-api","version":"1.0.0"}
```

---

## Verify Deployment

### Option 1: Browser
```
https://your-app.vercel.app/api/health
```
Should show JSON: `{"status":"ok",...}`

### Option 2: Terminal
```bash
curl https://your-app.vercel.app/api/health
```

### Option 3: Swagger UI (Interactive)
```
https://your-app.vercel.app/docs
```
Test endpoints directly in the UI.

---

## Use in React

Update your React `.env`:
```env
REACT_APP_API_URL=https://your-app.vercel.app
```

Then fetch commands:
```tsx
const response = await fetch(
  `${process.env.REACT_APP_API_URL}/api/command`,
  {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ command: '/status' })
  }
)
const data = await response.json()
console.log(data.response) // Command output
```

---

## Local Development (Unchanged)

Your local setup still works exactly the same:
```bash
# Terminal 1
python -m jarvis.main

# Terminal 2
python -m jarvis.api_bridge

# Terminal 3
npm start
```

---

## Endpoints Available

| Method | URL | Purpose |
|--------|-----|---------|
| GET | `/api/health` | Health check |
| POST | `/api/command` | Send command |
| GET | `/api/commands` | List available |
| GET | `/docs` | Interactive UI |
| GET | `/` | Root info |

---

## Example Commands

```bash
# Get system status
curl -X POST https://your-app.vercel.app/api/command \
  -H "Content-Type: application/json" \
  -d '{"command": "/status"}'

# Get help
curl -X POST https://your-app.vercel.app/api/command \
  -H "Content-Type: application/json" \
  -d '{"command": "/help"}'

# Queue a post
curl -X POST https://your-app.vercel.app/api/command \
  -H "Content-Type: application/json" \
  -d '{"command": "/post x Hello from Jarvis"}'
```

---

## If Deployment Fails

Check these in order:

1. **Git push succeeded?**
   ```bash
   git status  # Should show nothing
   ```

2. **Vercel has latest code?**
   - Check Vercel dashboard → click project → "Deployments"
   - Should show recent deployment from your commit

3. **Build log has errors?**
   - Click the failed deployment
   - Check "Build Logs" tab
   - Look for "ERROR" messages

4. **Dependencies installed?**
   - Should see `Installed dependencies` in build logs
   - Verify `fastapi` and `uvicorn` are listed

5. **Python version compatible?**
   - Vercel uses Python 3.11 by default
   - Project requires Python 3.10+
   - ✅ Compatible

---

## Common Issues

### "ModuleNotFoundError: No module named 'jarvis'"
- This happens at runtime, not build time
- Check that your project structure is correct
- Ensure `__init__.py` files exist in `jarvis/` subdirectories

### "No Python entrypoint found"
- This means `api/app.py` wasn't deployed
- Check: `git log --oneline` (see your commit?)
- Check Vercel dashboard → Deployments (see new build?)
- Try: Hard refresh dashboard or reconnect repo

### 502 Bad Gateway
- API is running but timeout
- Check Vercel logs for which endpoint failed
- Verify router.dispatch() is working locally first

### CORS errors in browser
- The API sets `Access-Control-Allow-Origin: *`
- If still getting CORS error, check browser console for real error
- Might be wrong API URL in React .env

---

## Need Help?

1. **Vercel docs**: https://vercel.com/docs/frameworks/backend/python
2. **FastAPI docs**: https://fastapi.tiangolo.com
3. **Check logs**:
   - Vercel dashboard → Deployments → click deployment → Logs
   - GitHub Actions (if set up)
   - Local terminal (for local dev)

---

## Success Indicators

✅ Deployment completed (Vercel dashboard shows "Ready")  
✅ `/api/health` returns status 200  
✅ `/api/command` with valid command returns 200  
✅ Swagger UI at `/docs` loads  
✅ React can fetch from API  

**You're ready to go! 🚀**
