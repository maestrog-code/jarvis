'use client'

import { useState, useEffect } from 'react'
import CommandTerminal from '@/components/CommandTerminal'
import AgentPanel from '@/components/AgentPanel'

// ── Types ──────────────────────────────────────────────────────────────
type NavId = 'dashboard' | 'agent' | 'feed' | 'memory' | 'soul'

interface StatCard {
  label: string
  value: string
  sub?: string
  icon: string
  color: 'cyan' | 'gold' | 'green' | 'pink'
  progress?: number
}

interface FeedItem {
  id: string
  source: 'X' | 'LI'
  author: string
  handle: string
  text: string
  time: string
  likes: number
}

// ── Static data ────────────────────────────────────────────────────────
const STAT_CARDS: StatCard[] = [
  { label: 'System Status', value: 'ONLINE',  sub: 'All systems nominal',         icon: '⚡', color: 'green', progress: 100 },
  { label: 'Active Tasks',  value: '3',        sub: 'Sentinel · Briefing · HITL', icon: '🔄', color: 'cyan',  progress: 60  },
  { label: 'Memory Used',   value: '1.2 GB',  sub: '30 days retention',           icon: '🧠', color: 'gold',  progress: 40  },
  { label: 'Posts Queued',  value: '7',        sub: '2 awaiting approval',        icon: '📬', color: 'pink',  progress: 25  },
]

const MOCK_FEED: FeedItem[] = [
  { id:'1', source:'X',  author:'AI Research',   handle:'@airesearch',   text:'GPT-5 benchmark results are in. Reasoning scores up 40% over previous generation.',              time:'2m ago',  likes:2410 },
  { id:'2', source:'LI', author:'Tech Ventures', handle:'TechVentures',  text:'Excited to share our Q1 AI investment thesis — autonomous agents are the next frontier.',       time:'18m ago', likes:891  },
  { id:'3', source:'X',  author:'Dev Dispatch',  handle:'@devdispatch',  text:'DuckDuckGo now returns structured results for code queries. Big win for local AI agents.',      time:'1h ago',  likes:543  },
  { id:'4', source:'LI', author:'Sarah Mitchell',handle:'SarahMitchell', text:'Published: "Building reliable multi-step AI agents" — lessons from 6 months in production.',  time:'3h ago',  likes:1200 },
]

const NAV_ITEMS: { id: NavId; label: string }[] = [
  { id: 'dashboard', label: 'Dashboard'   },
  { id: 'agent',     label: 'Agent Mode'  },
  { id: 'feed',      label: 'Social Feed' },
  { id: 'memory',    label: 'Memory'      },
  { id: 'soul',      label: 'Soul Config' },
]

const COLOR_MAP = {
  cyan:  { text: '#00d4ff', bg: 'rgba(0,212,255,0.08)',  border: 'rgba(0,212,255,0.2)'  },
  gold:  { text: '#ffd700', bg: 'rgba(255,215,0,0.08)',  border: 'rgba(255,215,0,0.2)'  },
  green: { text: '#00ff88', bg: 'rgba(0,255,136,0.08)',  border: 'rgba(0,255,136,0.2)'  },
  pink:  { text: '#ff006e', bg: 'rgba(255,0,110,0.08)',  border: 'rgba(255,0,110,0.2)'  },
}

// ── StatCard sub-component ──────────────────────────────────────────────
function StatCardUI({ card, idx }: { card: StatCard; idx: number }) {
  const [width, setWidth] = useState(0)
  const c = COLOR_MAP[card.color]
  useEffect(() => {
    const t = setTimeout(() => setWidth(card.progress ?? 0), 300 + idx * 120)
    return () => clearTimeout(t)
  }, [card.progress, idx])
  return (
    <div className="stat-card">
      <div style={{ display:'flex', justifyContent:'space-between', alignItems:'flex-start', marginBottom:'14px' }}>
        <div>
          <p className="section-label" style={{ marginBottom:'6px' }}>{card.label}</p>
          <p style={{ fontSize:'26px', fontWeight:800, color:c.text, fontFamily:'var(--font-display)', letterSpacing:'0.05em', lineHeight:1 }}>
            {card.value}
          </p>
        </div>
        <div style={{ width:'40px', height:'40px', display:'flex', alignItems:'center', justifyContent:'center',
                      background:c.bg, border:`1px solid ${c.border}`, borderRadius:'10px', fontSize:'18px' }}>
          {card.icon}
        </div>
      </div>
      {card.sub && <p className="text-muted" style={{ fontSize:'11px', marginBottom:'12px' }}>{card.sub}</p>}
      {card.progress !== undefined && (
        <div className="progress-bar">
          <div className="progress-fill" style={{ width:`${width}%`, background:`linear-gradient(90deg, ${c.text}88, ${c.text})`, transition:'width 1.2s ease' }} />
        </div>
      )}
    </div>
  )
}

// ── Feed list ──────────────────────────────────────────────────────────
function FeedList() {
  return (
    <div>
      {MOCK_FEED.map(item => (
        <div key={item.id} className="feed-item">
          <div style={{ display:'flex', gap:'10px', alignItems:'flex-start' }}>
            <div style={{
              width:'32px', height:'32px', borderRadius:'8px', flexShrink:0,
              background: item.source === 'X' ? 'rgba(255,255,255,0.08)' : 'rgba(0,119,181,0.15)',
              border:`1px solid ${item.source === 'X' ? 'rgba(255,255,255,0.1)' : 'rgba(0,119,181,0.3)'}`,
              display:'flex', alignItems:'center', justifyContent:'center',
              fontSize:'12px', fontWeight:700, color: item.source === 'X' ? '#e0e0e0' : '#0ea5e9',
              fontFamily:'var(--font-mono)',
            }}>
              {item.source}
            </div>
            <div style={{ flex:1, minWidth:0 }}>
              <div style={{ display:'flex', gap:'6px', alignItems:'center', marginBottom:'4px', flexWrap:'wrap' }}>
                <span style={{ fontSize:'13px', fontWeight:600, color:'var(--text)' }}>{item.author}</span>
                <span style={{ fontSize:'11px', color:'var(--muted)', fontFamily:'var(--font-mono)' }}>{item.handle}</span>
                <span style={{ marginLeft:'auto', fontSize:'11px', color:'var(--muted)' }}>{item.time}</span>
              </div>
              <p style={{ fontSize:'13px', color:'var(--text2)', lineHeight:1.55, margin:'0 0 6px' }}>{item.text}</p>
              <span style={{ fontSize:'11px', color:'var(--muted)' }}>♥ {item.likes.toLocaleString()}</span>
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}

// ── Terminal log ───────────────────────────────────────────────────────
function TerminalLog() {
  const lines = [
    ['prompt','jarvis@core'], ['cmd','./start.sh --full'],
    ['out','[OK] SOUL.md loaded (3,241 chars)'],
    ['out','[OK] Sentinel loop started (60s)'],
    ['out','[OK] API Bridge → http://127.0.0.1:8000'],
    ['out','[OK] Telegram bot polling active'],
    ['prompt','jarvis@agent'], ['cmd','/agent "Search AI trends 2026"'],
    ['out','[1] web_search("AI trends 2026")'],
    ['out','[2] scrape_url("techcrunch.com/ai")'],
    ['out','[DONE] Final answer ready ✓'],
  ]
  return (
    <div className="terminal-block" style={{ maxHeight:'200px', overflowY:'auto' }}>
      {lines.map(([t, v], i) => (
        <div key={i} style={{ display:'flex', gap:'8px', lineHeight:'1.8' }}>
          {t === 'prompt' && <><span className="prompt">❯</span><span className="cmd">{v}</span></>}
          {t === 'cmd'    && <><span style={{ opacity:0 }}>❯</span><span style={{ color:'#e2e8f0' }}>{v}</span></>}
          {t === 'out'    && <><span style={{ opacity:0 }}>❯</span><span className="out">{v}</span></>}
        </div>
      ))}
      <div style={{ display:'flex', gap:'8px' }}>
        <span className="prompt">❯</span>
        <span className="cmd" style={{ borderRight:'2px solid var(--cyan)', paddingRight:'2px', animation:'blink 1s step-end infinite' }}>_</span>
      </div>
    </div>
  )
}

// ── Section header helper ──────────────────────────────────────────────
function SectionHeader({ icon, title, badge, badgeColor }: { icon:string; title:string; badge?:string; badgeColor?:string }) {
  return (
    <>
      <div style={{ display:'flex', alignItems:'center', gap:'8px', marginBottom:'16px' }}>
        <span style={{ fontSize:'14px' }}>{icon}</span>
        <h2 style={{ fontSize:'12px', fontWeight:700, letterSpacing:'0.12em', textTransform:'uppercase', color:'var(--text)' }}>{title}</h2>
        {badge && (
          <span style={{
            marginLeft:'auto', fontSize:'9px', padding:'3px 8px', borderRadius:'100px',
            fontWeight:700, letterSpacing:'0.1em', textTransform:'uppercase',
            background: badgeColor === 'green' ? 'rgba(0,255,136,0.08)' : 'rgba(0,212,255,0.08)',
            border:     badgeColor === 'green' ? '1px solid rgba(0,255,136,0.25)' : '1px solid rgba(0,212,255,0.25)',
            color:      badgeColor === 'green' ? 'var(--green)' : 'var(--cyan)',
          }}>{badge}</span>
        )}
      </div>
      <div className="divider" style={{ marginBottom:'16px' }} />
    </>
  )
}

// ── Main Page ──────────────────────────────────────────────────────────
export default function Home() {
  const [activeNav, setActiveNav] = useState<NavId>('dashboard')
  const [mounted, setMounted]     = useState(false)
  const [time, setTime]           = useState('')

  useEffect(() => {
    setMounted(true)
    const tick = () => setTime(new Date().toLocaleTimeString('en-US', { hour12:false }))
    tick()
    const id = setInterval(tick, 1000)
    return () => clearInterval(id)
  }, [])

  return (
    <div className="bg-grid" style={{ minHeight:'100vh', position:'relative' }}>
      {/* Ambient glow orbs */}
      <div className="orb orb-cyan" />
      <div className="orb orb-gold" />
      <div className="orb orb-pink" />

      {/* ── Top Nav ─────────────────────────────────────── */}
      <header style={{
        position:'sticky', top:0, zIndex:50,
        background:'rgba(4,6,15,0.88)',
        backdropFilter:'blur(20px)',
        WebkitBackdropFilter:'blur(20px)',
        borderBottom:'1px solid var(--border)',
      }}>
        <div style={{ maxWidth:'1400px', margin:'0 auto', padding:'0 28px', height:'64px', display:'flex', alignItems:'center', gap:'20px' }}>

          {/* Logo */}
          <div style={{ display:'flex', alignItems:'center', gap:'12px', flexShrink:0, marginRight:'8px' }}>
            <div style={{
              width:'38px', height:'38px', borderRadius:'10px',
              background:'rgba(0,212,255,0.1)', border:'1px solid rgba(0,212,255,0.3)',
              display:'flex', alignItems:'center', justifyContent:'center', fontSize:'20px',
            }}>⬡</div>
            <div>
              <p style={{ fontFamily:'var(--font-display)', fontWeight:900, fontSize:'15px', color:'var(--cyan)', letterSpacing:'0.2em', lineHeight:1 }}>JARVIS</p>
              <p style={{ fontFamily:'var(--font-mono)', fontSize:'9px', color:'var(--muted)', letterSpacing:'0.15em', marginTop:'2px' }}>COMMAND CENTER</p>
            </div>
          </div>

          {/* Nav tabs */}
          <nav style={{ display:'flex', gap:'2px' }}>
            {NAV_ITEMS.map(n => (
              <button key={n.id} onClick={() => setActiveNav(n.id)} style={{
                padding:'8px 16px', borderRadius:'6px',
                border:'none', borderBottom: activeNav === n.id ? '2px solid var(--cyan)' : '2px solid transparent',
                background: activeNav === n.id ? 'rgba(0,212,255,0.08)' : 'transparent',
                color:      activeNav === n.id ? 'var(--cyan)' : 'var(--text2)',
                fontSize:'12px', fontWeight:500, letterSpacing:'0.04em',
                cursor:'pointer', transition:'all 0.2s ease', fontFamily:'var(--font-sans)',
              }}>
                {n.label}
              </button>
            ))}
          </nav>

          {/* Right side */}
          <div style={{ marginLeft:'auto', display:'flex', alignItems:'center', gap:'20px' }}>
            <div style={{ display:'flex', alignItems:'center', gap:'6px' }}>
              <span style={{ width:'7px', height:'7px', borderRadius:'50%', background:'var(--green)', boxShadow:'0 0 8px var(--green)', display:'block', animation:'pulse-dot 2s infinite' }} />
              <span style={{ fontSize:'11px', fontWeight:600, letterSpacing:'0.1em', color:'var(--green)' }}>ONLINE</span>
            </div>
            {mounted && (
              <span style={{ fontFamily:'var(--font-mono)', fontSize:'12px', color:'var(--muted)' }}>{time}</span>
            )}
          </div>
        </div>
      </header>

      {/* ── Main Content ─────────────────────────────────── */}
      <main style={{ maxWidth:'1400px', margin:'0 auto', padding:'32px 28px', position:'relative', zIndex:1 }}>

        {/* ─── DASHBOARD VIEW ─── */}
        {activeNav === 'dashboard' && (
          <>
            {/* Hero banner */}
            <div style={{
              background:'linear-gradient(135deg, rgba(0,212,255,0.06) 0%, transparent 55%, rgba(255,215,0,0.04) 100%)',
              border:'1px solid var(--border)',
              borderRadius:'20px',
              padding:'40px 48px',
              marginBottom:'28px',
              position:'relative', overflow:'hidden',
            }}>
              {/* Subtle scan line */}
              <div style={{ position:'absolute', inset:0, pointerEvents:'none',
                background:'linear-gradient(180deg, transparent 45%, rgba(0,212,255,0.025) 50%, transparent 55%)',
                animation:'scanVertical 8s linear infinite', zIndex:0 }} />
              <div style={{ position:'relative', zIndex:1, display:'flex', justifyContent:'space-between', alignItems:'center', flexWrap:'wrap', gap:'32px' }}>
                <div>
                  <div style={{ display:'inline-flex', alignItems:'center', gap:'6px', padding:'4px 12px',
                    background:'rgba(0,212,255,0.08)', border:'1px solid rgba(0,212,255,0.2)', borderRadius:'100px',
                    marginBottom:'16px' }}>
                    <span style={{ width:'6px', height:'6px', borderRadius:'50%', background:'var(--green)', boxShadow:'0 0 6px var(--green)', display:'block' }} />
                    <span style={{ fontSize:'10px', fontWeight:700, letterSpacing:'0.12em', color:'var(--cyan)' }}>AUTONOMOUS AI AGENT · REACT POWERED</span>
                  </div>
                  <h1 style={{ fontFamily:'var(--font-display)', fontWeight:900, fontSize:'clamp(36px,4vw,58px)',
                    color:'var(--cyan)', letterSpacing:'0.15em', lineHeight:1.05, marginBottom:'14px',
                    textShadow:'0 0 40px rgba(0,212,255,0.4)' }}>
                    J.A.R.V.I.S
                  </h1>
                  <p style={{ fontSize:'15px', color:'var(--text2)', maxWidth:'460px', lineHeight:1.65 }}>
                    Your personal AI command center. Monitors social feeds, drafts content, runs autonomous agents, and keeps your digital presence alive — 24/7.
                  </p>
                  <div style={{ display:'flex', gap:'12px', marginTop:'24px', flexWrap:'wrap' }}>
                    <button className="btn btn-primary" onClick={() => setActiveNav('agent')}>▶ Run Agent</button>
                    <button className="btn btn-ghost"   onClick={() => setActiveNav('feed')}>📡 View Feed</button>
                  </div>
                </div>
                <div className="card" style={{ padding:'20px', minWidth:'260px', maxWidth:'340px', flex:'1' }}>
                  <p className="section-label" style={{ marginBottom:'12px' }}>Live System Log</p>
                  <TerminalLog />
                </div>
              </div>
            </div>

            {/* Stat cards */}
            <div style={{ display:'grid', gridTemplateColumns:'repeat(4, 1fr)', gap:'16px', marginBottom:'28px' }}>
              {STAT_CARDS.map((c, i) => <StatCardUI key={c.label} card={c} idx={i} />)}
            </div>

            {/* 2-col grid */}
            <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:'20px' }}>

              {/* Command Terminal */}
              <div className="card" style={{ padding:'24px' }}>
                <SectionHeader icon="💻" title="Command Terminal" badge="LIVE" badgeColor="cyan" />
                <CommandTerminal />
              </div>

              {/* Social Feed */}
              <div className="card" style={{ padding:'24px' }}>
                <SectionHeader icon="📡" title="Social Feed" badge="LIVE" badgeColor="green" />
                <FeedList />
              </div>

              {/* Agent Mode — full width */}
              <div className="card" style={{ padding:'24px', gridColumn:'1 / -1' }}>
                <div style={{ display:'flex', alignItems:'center', gap:'8px', marginBottom:'16px' }}>
                  <span style={{ fontSize:'14px' }}>🤖</span>
                  <h2 style={{ fontSize:'12px', fontWeight:700, letterSpacing:'0.12em', textTransform:'uppercase', color:'var(--text)' }}>Agent Mode</h2>
                  <div style={{ marginLeft:'12px', display:'flex', gap:'5px', flexWrap:'wrap' }}>
                    {['web_search', 'run_shell', 'scrape_url', 'recall_memory'].map(t => (
                      <span key={t} style={{ fontSize:'9px', padding:'2px 7px', borderRadius:'100px', fontWeight:700, letterSpacing:'0.08em',
                        background:'rgba(0,212,255,0.06)', border:'1px solid rgba(0,212,255,0.15)', color:'var(--muted)' }}>{t}</span>
                    ))}
                  </div>
                </div>
                <div className="divider" style={{ marginBottom:'20px' }} />
                <AgentPanel />
              </div>
            </div>
          </>
        )}

        {/* ─── AGENT VIEW ─── */}
        {activeNav === 'agent' && (
          <div className="card animate-fade-up" style={{ padding:'32px' }}>
            <div style={{ marginBottom:'24px' }}>
              <h1 style={{ fontFamily:'var(--font-display)', fontSize:'22px', color:'var(--cyan)', letterSpacing:'0.15em', marginBottom:'6px' }}>AGENT MODE</h1>
              <p style={{ color:'var(--text2)', fontSize:'13px' }}>Give Jarvis a complex goal. It will plan, use tools, and loop until done.</p>
            </div>
            <div className="divider" style={{ marginBottom:'24px' }} />
            <AgentPanel />
          </div>
        )}

        {/* ─── FEED VIEW ─── */}
        {activeNav === 'feed' && (
          <div className="card animate-fade-up" style={{ padding:'32px' }}>
            <SectionHeader icon="📡" title="Social Feed" badge="LIVE" badgeColor="green" />
            <FeedList />
          </div>
        )}

        {/* ─── MEMORY VIEW ─── */}
        {activeNav === 'memory' && (
          <div style={{ display:'flex', flexDirection:'column', gap:'20px' }} className="animate-fade-up">
            <div style={{ display:'grid', gridTemplateColumns:'repeat(4,1fr)', gap:'16px' }}>
              {[
                { label:'Total Entries', value:'1,842', icon:'📦', c:'cyan'  as const },
                { label:'Avg Recall',    value:'0.87',  icon:'🎯', c:'green' as const },
                { label:'Retention',     value:'30d',   icon:'🗓️', c:'gold'  as const },
                { label:'Archive',       value:'Zip',   icon:'💾', c:'pink'  as const },
              ].map(s => <StatCardUI key={s.label} card={{ label:s.label, value:s.value, icon:s.icon, color:s.c }} idx={0} />)}
            </div>
            <div className="card" style={{ padding:'24px' }}>
              <SectionHeader icon="🧠" title="Memory Store" badge="ChromaDB" />
              <div className="terminal-block">
                <div><span className="prompt">❯ </span><span className="cmd">recall_memory("AI trends")</span></div>
                <div className="out" style={{ marginTop:'10px', lineHeight:2 }}>
                  1. AI agents are the dominant automation pattern (2025-03)<br/>
                  2. DuckDuckGo returns JSON for agentic code queries<br/>
                  3. Ollama v0.3 supports parallel inference for local models
                </div>
              </div>
            </div>
          </div>
        )}

        {/* ─── SOUL VIEW ─── */}
        {activeNav === 'soul' && (
          <div className="card animate-fade-up" style={{ padding:'32px' }}>
            <SectionHeader icon="✦" title="Soul Configuration" />
            <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:'32px' }}>
              <div>
                <p className="section-label" style={{ marginBottom:'14px' }}>Identity</p>
                {[
                  { k:'Name',      v:'J.A.R.V.I.S'                              },
                  { k:'Version',   v:'1.0.0'                                    },
                  { k:'Purpose',   v:'Autonomous social media orchestration'    },
                  { k:'Platforms', v:'X · LinkedIn · Instagram'                 },
                ].map(r => (
                  <div key={r.k} style={{ display:'flex', gap:'16px', marginBottom:'12px', fontSize:'13px', alignItems:'flex-start' }}>
                    <span style={{ color:'var(--muted)', width:'80px', flexShrink:0 }}>{r.k}</span>
                    <span style={{ color:'var(--text)' }}>{r.v}</span>
                  </div>
                ))}
              </div>
              <div>
                <p className="section-label" style={{ marginBottom:'14px' }}>Safety Protocols</p>
                {[
                  { k:'Daily Limit',    v:'50 posts',   pct:50  },
                  { k:'Content Review', v:'Enabled',    pct:100 },
                  { k:'Rate Limiting',  v:'10 req/min', pct:10  },
                ].map(r => (
                  <div key={r.k} style={{ marginBottom:'18px' }}>
                    <div style={{ display:'flex', justifyContent:'space-between', marginBottom:'6px', fontSize:'12px' }}>
                      <span style={{ color:'var(--muted)' }}>{r.k}</span>
                      <span style={{ color:'var(--cyan)' }}>{r.v}</span>
                    </div>
                    <div className="progress-bar"><div className="progress-fill" style={{ width:`${r.pct}%` }} /></div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

      </main>

      {/* ── Footer ─────────────────────────────────────────── */}
      <footer style={{ borderTop:'1px solid var(--border)', marginTop:'60px', padding:'20px 28px', textAlign:'center' }}>
        <p style={{ fontFamily:'var(--font-mono)', fontSize:'10px', color:'var(--muted)', letterSpacing:'0.15em' }}>
          J.A.R.V.I.S · COMMAND CENTER v1.0 · {mounted ? time : '––:––:––'} · ALL SYSTEMS NOMINAL
        </p>
      </footer>

      <style jsx global>{`
        @keyframes blink        { 0%,100%{ opacity:1; } 50%{ opacity:0; } }
        @keyframes scanVertical { 0%{ transform:translateY(-100%); } 100%{ transform:translateY(200%); } }
      `}</style>
    </div>
  )
}
