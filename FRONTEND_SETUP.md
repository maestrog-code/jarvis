# Jarvis Command Center - Frontend Setup Guide

## Overview

This is a Next.js 15 + React 18 web dashboard for controlling the Jarvis AI assistant. It provides real-time monitoring, command execution, social feed integration, and memory management through a beautiful cyberpunk-themed interface.

## Technology Stack

- **Framework:** Next.js 15
- **UI:** React 18 with Tailwind CSS 3
- **Animations:** Framer Motion
- **Icons:** Lucide React
- **Language:** TypeScript
- **API Client:** Fetch API with custom hooks

## Project Structure

```
├── app/
│   ├── layout.tsx          # Root layout with metadata
│   ├── page.tsx            # Dashboard homepage
│   ├── globals.css         # Tailwind + custom cyberpunk styles
│   └── favicon.ico         # Browser tab icon
├── components/
│   ├── Layout.tsx          # Main layout wrapper (gradients, grid overlay)
│   ├── CommandTerminal.tsx # Command input/output terminal
│   ├── StatusPulse.tsx     # System health monitor
│   ├── SocialFeed.tsx      # X/LinkedIn unified stream
│   ├── SoulMemory.tsx      # SOUL.md config + memory logs
│   └── ui/
│       ├── Card.tsx        # Glassmorphic card component
│       └── Badge.tsx       # Status badge component
├── hooks/
│   ├── useJarvisCommand.ts # Command dispatch hook
│   └── useSystemStatus.ts  # Health polling hook
├── services/
│   └── api.ts              # Centralized API client
├── types/
│   └── jarvis.ts           # TypeScript interfaces
├── package.json            # Dependencies
├── tailwind.config.js      # Tailwind configuration
├── next.config.js          # Next.js configuration
├── tsconfig.json           # TypeScript configuration
└── .env.example            # Environment template
```

## Installation & Setup

### Prerequisites

- Node.js 18+ ([download](https://nodejs.org))
- npm, yarn, or bun package manager
- Python backend running on `http://localhost:8000` (or configured URL)

### Step 1: Clone or Navigate to Project

```bash
cd /path/to/jarvis
```

### Step 2: Install Dependencies

```bash
npm install
# or
yarn install
# or
bun install
```

### Step 3: Configure Environment

```bash
# Copy the environment template
cp .env.example .env.local

# Edit .env.local and set your API URL
# For local development:
# NEXT_PUBLIC_API_URL=http://localhost:8000

# For Vercel deployment:
# NEXT_PUBLIC_API_URL=https://your-deployed-api.vercel.app
```

### Step 4: Start Backend (in separate terminal)

The React frontend requires the Python backend to be running:

```bash
# Terminal 1: Start main Jarvis bot
python -m jarvis.main

# Terminal 2: Start API bridge (web server)
python -m jarvis.api_bridge

# Terminal 3: You'll start the React dev server here
```

### Step 5: Start Development Server

```bash
npm run dev
# or
yarn dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser. You should see the Jarvis Command Center dashboard.

## Development

### File Structure Guidelines

- **Components:** Place reusable UI components in `components/` folder
- **Hooks:** Custom React hooks go in `hooks/` folder
- **Services:** API calls and utilities go in `services/` folder
- **Types:** TypeScript interfaces go in `types/` folder
- **Styles:** Global styles in `app/globals.css`, Tailwind config in `tailwind.config.js`

### Adding New Components

```tsx
// components/MyComponent.tsx
'use client'

import { ReactNode } from 'react'
import Card from '@/components/ui/Card'

interface MyComponentProps {
  title: string
  children: ReactNode
}

export default function MyComponent({ title, children }: MyComponentProps) {
  return (
    <Card variant="cyan">
      <h2 className="text-lg font-bold text-cyan">{title}</h2>
      {children}
    </Card>
  )
}
```

### Using the API Client

```tsx
import { jarvisAPI } from '@/services/api'

// Send a command
const response = await jarvisAPI.sendCommand('/status')

// Get system health
const health = await jarvisAPI.getHealth()

// Get social feed
const feed = await jarvisAPI.getFeed(limit: 20)
```

### Using Custom Hooks

```tsx
import { useJarvisCommand } from '@/hooks/useJarvisCommand'
import { useSystemStatus } from '@/hooks/useSystemStatus'

export function MyPage() {
  const { sendCommand, loading, error, response } = useJarvisCommand()
  const { status, loading: statusLoading } = useSystemStatus(pollInterval: 5000)

  return (
    <div>
      <button onClick={() => sendCommand('/help')}>
        Get Help
      </button>
    </div>
  )
}
```

## Styling & Design

### Color System

The dashboard uses a cyberpunk theme with neon colors:

- **Primary:** Cyan (`#00d4ff`)
- **Secondary:** Gold (`#ffd700`)
- **Accent:** Pink/Magenta (`#ff006e`)
- **Background:** Dark Blue (`#0a0e27`)
- **Muted:** Gray (`#404854`)

### CSS Classes

- `.glass` - Glassmorphic effect with backdrop blur
- `.glow-cyan`, `.glow-gold`, `.glow-pink` - Neon glow effects
- `.text-cyan`, `.text-gold`, `.text-pink` - Colored text with glow
- `.terminal` - Terminal-style font (monospace)
- `.animate-scan-line`, `.animate-flicker` - Sci-fi animations

### Tailwind Configuration

Custom Tailwind extensions in `tailwind.config.js`:

```js
colors: {
  primary: '#00d4ff',
  secondary: '#ffd700',
  accent: '#ff006e',
  background: '#0a0e27',
  foreground: '#e0e0e0',
}

boxShadow: {
  'neon-cyan': '0 0 20px rgba(0, 212, 255, 0.5)',
  'neon-gold': '0 0 20px rgba(255, 215, 0, 0.5)',
  'neon-pink': '0 0 20px rgba(255, 0, 110, 0.5)',
}
```

## API Endpoints

The frontend communicates with these backend endpoints:

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/health` | System health check |
| POST | `/api/command` | Send command to Jarvis |
| GET | `/api/feed` | Get social feed (X/LinkedIn) |
| GET | `/api/memory` | Get memory logs |
| GET | `/api/soul` | Get SOUL.md config |
| PUT | `/api/soul` | Update SOUL.md config |

## Production Deployment

### Vercel Deployment

1. **Connect GitHub Repository:**
   - Push code to GitHub
   - Import repository in Vercel dashboard

2. **Set Environment Variables:**
   - In Vercel Settings → Environment Variables
   - Add `NEXT_PUBLIC_API_URL` pointing to your deployed backend

3. **Deploy:**
   - Vercel automatically builds and deploys on git push
   - Your site will be live at `https://jarvis-xyz.vercel.app`

### Custom Domain

1. In Vercel dashboard → Domains
2. Add your custom domain
3. Update DNS records according to Vercel's instructions

### Backend Deployment

Deploy your Python backend separately (e.g., on Render, Railway, or a VPS):

1. Update `NEXT_PUBLIC_API_URL` in Vercel to point to deployed backend
2. Ensure CORS is enabled on backend for your frontend domain
3. Test `/api/health` endpoint is accessible from browser

## Troubleshooting

### Issue: "Cannot connect to API"

**Solution:**
- Verify backend is running: `curl http://localhost:8000/api/health`
- Check `NEXT_PUBLIC_API_URL` in `.env.local`
- Ensure CORS headers are correct on backend

### Issue: Dashboard shows "OFFLINE"

**Solution:**
- Check backend status
- Verify network connectivity
- Check browser console for error messages

### Issue: Commands not executing

**Solution:**
- Verify backend is responding to `/api/command` endpoint
- Check terminal output for errors
- Ensure Telegram bot token is set in backend `.env`

### Issue: Tailwind styles not applying

**Solution:**
```bash
# Rebuild Tailwind cache
rm -rf .next
npm run dev
```

## Performance Tips

1. **Image Optimization:** Use Next.js `Image` component for automatic optimization
2. **Code Splitting:** Next.js automatically splits code per page
3. **Caching:** Leverage `SWR` hooks for data caching
4. **Lazy Loading:** Use dynamic imports for heavy components

## Security

- Never commit `.env.local` to git
- Use `NEXT_PUBLIC_` prefix only for public variables
- Sensitive data (API keys) should not be exposed to frontend
- Always validate API responses on the client side

## Contributing

1. Create a new branch: `git checkout -b feature/my-feature`
2. Make changes and test locally
3. Commit with descriptive message: `git commit -m "Add my feature"`
4. Push to GitHub: `git push origin feature/my-feature`
5. Create Pull Request

## Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [React Documentation](https://react.dev)
- [Tailwind CSS](https://tailwindcss.com)
- [Lucide Icons](https://lucide.dev)
- [Framer Motion](https://www.framer.com/motion)

## Support

For issues or questions:

1. Check existing GitHub issues
2. Review backend API documentation
3. Check browser console for error messages
4. Review network tab in browser DevTools

---

**Version:** 1.0.0  
**Last Updated:** March 2024  
**Status:** Ready for Development
