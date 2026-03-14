# Jarvis Frontend - Quick Start (5 Minutes)

## TL;DR - Get Running Immediately

### Terminal 1: Start Backend API

```bash
python -m jarvis.api_bridge
```

### Terminal 2: Start Frontend Dev Server

```bash
npm install
npm run dev
```

### Terminal 3: Open in Browser

```bash
open http://localhost:3000
```

Done! You should see the Jarvis dashboard.

---

## What You're Looking At

The dashboard has 4 main sections:

1. **Status Pulse (top-left)** - System health, active connections, last update
2. **Social Feed (top-right)** - Unified X/LinkedIn stream
3. **Command Terminal (middle)** - Type commands like `/status`, `/help`, `/post x "message"`
4. **SOUL & Memory (bottom)** - Configuration and action history

---

## Common Commands

Try these in the Command Terminal:

| Command | What it does |
|---------|---|
| `/help` | Show all available commands |
| `/status` | Get system health report |
| `/drafts` | Show draft posts |
| `/post x "Hello world"` | Post to X (Twitter) |
| `/memory` | Show memory logs |
| `/keywords list` | List tracked keywords |

---

## Configuration

### Backend URL

Edit `.env.local`:

```env
# Local development (default)
NEXT_PUBLIC_API_URL=http://localhost:8000

# For deployed backend
NEXT_PUBLIC_API_URL=https://your-api.vercel.app
```

---

## Deployment (Optional)

### Deploy to Vercel (Free Tier Eligible)

```bash
# 1. Push to GitHub
git add -A
git commit -m "Add Jarvis frontend"
git push origin main

# 2. In Vercel Dashboard:
# - Click "Add New Project"
# - Select your GitHub repository
# - Add environment variable: NEXT_PUBLIC_API_URL=<your-api-url>
# - Click Deploy

# Your site is now live!
```

---

## Troubleshooting

**Dashboard shows "OFFLINE"?**
- Start the backend: `python -m jarvis.api_bridge`
- Check `.env.local` has correct `NEXT_PUBLIC_API_URL`

**Commands not working?**
- Click on Status Pulse to check connection
- Check browser console (F12) for errors

**Styles look broken?**
- Clear Next.js cache: `rm -rf .next && npm run dev`

---

## Next Steps

1. Check [FRONTEND_SETUP.md](./FRONTEND_SETUP.md) for detailed documentation
2. Explore the components in `components/` folder
3. Add new commands to `CommandTerminal.tsx`
4. Customize colors in `tailwind.config.js`

---

**Questions?** See FRONTEND_SETUP.md or check backend logs in other terminal.
