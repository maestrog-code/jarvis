'use client'

import { useState } from 'react'
import { Brain, Clock } from 'lucide-react'
import Card from '@/components/ui/Card'

interface MemoryLog {
  timestamp: string
  action: string
  status: string
}

const mockMemoryLogs: MemoryLog[] = [
  {
    timestamp: '2024-03-14 14:32:15',
    action: 'Posted to X: Market update thread',
    status: 'success',
  },
  {
    timestamp: '2024-03-14 13:15:42',
    action: 'Analyzed LinkedIn engagement metrics',
    status: 'success',
  },
  {
    timestamp: '2024-03-14 12:08:33',
    action: 'Generated briefing document',
    status: 'success',
  },
  {
    timestamp: '2024-03-14 11:45:12',
    action: 'Parsed social media feed',
    status: 'success',
  },
  {
    timestamp: '2024-03-14 10:22:55',
    action: 'System initialized',
    status: 'success',
  },
]

const soulConfig = `# J.A.R.V.I.S SOUL Configuration
## Version: 1.0.0

### Identity
- Name: J.A.R.V.I.S (Just Another Remarkably Versatile Intelligence System)
- Purpose: Autonomous social media management & content orchestration
- Platform: X (Twitter) & LinkedIn

### Capabilities
- Real-time social listening
- Autonomous content generation
- Engagement optimization
- Sentiment analysis
- Trend forecasting

### Safety Protocols
- Daily message limits: 50
- Content review enabled: true
- Engagement filters: active
- Rate limiting: 10 requests/min

### Memory Management
- Retention period: 30 days
- Archive strategy: compression
- Backup frequency: daily
`

export default function SoulMemory() {
  const [activeTab, setActiveTab] = useState<'soul' | 'memory'>('soul')

  return (
    <Card className="col-span-full">
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Brain size={20} className="text-secondary" />
            <h2 className="text-lg font-bold text-gold">SOUL & Memory</h2>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex gap-2 border-b border-secondary/20">
          <button
            onClick={() => setActiveTab('soul')}
            className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
              activeTab === 'soul'
                ? 'border-secondary text-secondary'
                : 'border-transparent text-muted hover:text-foreground'
            }`}
          >
            SOUL.md
          </button>
          <button
            onClick={() => setActiveTab('memory')}
            className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
              activeTab === 'memory'
                ? 'border-secondary text-secondary'
                : 'border-transparent text-muted hover:text-foreground'
            }`}
          >
            Memory Logs
          </button>
        </div>

        {/* Tab Content */}
        {activeTab === 'soul' ? (
          <div className="space-y-2">
            <pre className="rounded border border-secondary/20 bg-background/50 p-4 font-mono text-xs text-foreground overflow-x-auto max-h-96 overflow-y-auto">
              {soulConfig}
            </pre>
            <button className="rounded border border-secondary/30 bg-secondary/10 px-4 py-2 text-xs text-secondary hover:bg-secondary/20 transition-colors">
              Edit Configuration
            </button>
          </div>
        ) : (
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {mockMemoryLogs.map((log, idx) => (
              <div
                key={idx}
                className="flex items-start gap-3 rounded border border-secondary/20 bg-secondary/5 p-3 hover:bg-secondary/10 transition-colors"
              >
                <Clock size={16} className="text-secondary flex-shrink-0 mt-0.5" />
                <div className="flex-1">
                  <div className="flex items-center justify-between">
                    <p className="text-sm text-foreground">{log.action}</p>
                    <span className="text-xs text-green-400 bg-green-900/30 px-2 py-1 rounded border border-green-500/20">
                      {log.status}
                    </span>
                  </div>
                  <p className="text-xs text-muted mt-1">{log.timestamp}</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </Card>
  )
}
