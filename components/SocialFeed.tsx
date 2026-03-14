'use client'

import { Twitter, Linkedin, Heart, MessageCircle, Share2 } from 'lucide-react'
import Card from '@/components/ui/Card'
import Badge from '@/components/ui/Badge'

interface FeedItem {
  id: string
  source: 'x' | 'linkedin'
  author: string
  handle: string
  text: string
  timestamp: string
  likes: number
  replies: number
}

const mockFeed: FeedItem[] = [
  {
    id: '1',
    source: 'x',
    author: 'Tech News Daily',
    handle: '@technewsdaily',
    text: 'Breaking: AI systems now passing advanced reasoning benchmarks. What does this mean for the future?',
    timestamp: '2 hours ago',
    likes: 1250,
    replies: 340,
  },
  {
    id: '2',
    source: 'linkedin',
    author: 'AI Research Team',
    handle: 'AIResearchTeam',
    text: 'Excited to announce our latest paper on autonomous agent optimization. The results are promising for real-world applications.',
    timestamp: '4 hours ago',
    likes: 890,
    replies: 120,
  },
  {
    id: '3',
    source: 'x',
    author: 'Code Masters',
    handle: '@codemasters_io',
    text: 'Your reminder: API documentation is your best friend. Document early, document often.',
    timestamp: '6 hours ago',
    likes: 2100,
    replies: 560,
  },
]

export default function SocialFeed() {
  return (
    <Card variant="gold">
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-bold text-gold">Social Feed</h2>
          <span className="text-xs text-muted">Live Stream</span>
        </div>

        <div className="space-y-3 max-h-96 overflow-y-auto">
          {mockFeed.map((item) => (
            <div
              key={item.id}
              className="rounded border border-secondary/20 bg-secondary/5 p-3 hover:bg-secondary/10 transition-colors"
            >
              <div className="flex items-start justify-between gap-2">
                <div className="flex items-center gap-2">
                  {item.source === 'x' ? (
                    <Twitter size={16} className="text-secondary flex-shrink-0" />
                  ) : (
                    <Linkedin size={16} className="text-secondary flex-shrink-0" />
                  )}
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-bold text-foreground">{item.author}</span>
                      <span className="text-xs text-muted">{item.handle}</span>
                    </div>
                    <span className="text-xs text-muted">{item.timestamp}</span>
                  </div>
                </div>
                <Badge label={item.source.toUpperCase()} variant="gold" />
              </div>

              <p className="mt-2 text-sm text-foreground leading-relaxed">{item.text}</p>

              <div className="mt-3 flex items-center gap-4 border-t border-secondary/10 pt-2">
                <div className="flex items-center gap-1 text-xs text-muted hover:text-secondary cursor-pointer">
                  <Heart size={14} />
                  <span>{item.likes}</span>
                </div>
                <div className="flex items-center gap-1 text-xs text-muted hover:text-secondary cursor-pointer">
                  <MessageCircle size={14} />
                  <span>{item.replies}</span>
                </div>
                <div className="flex items-center gap-1 text-xs text-muted hover:text-secondary cursor-pointer ml-auto">
                  <Share2 size={14} />
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </Card>
  )
}
