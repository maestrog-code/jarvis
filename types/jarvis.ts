export interface CommandResponse {
  command: string
  response: string
  timestamp: string
  status: 'success' | 'error'
}

export interface HealthStatus {
  status: string
  service: string
  version: string
  uptime: number
  connections: {
    telegram: boolean
    x: boolean
    linkedin: boolean
  }
}

export interface SocialPost {
  id: string
  platform: 'x' | 'linkedin'
  content: string
  status: 'draft' | 'scheduled' | 'published'
  created_at: string
  published_at?: string
}

export interface MemoryEntry {
  id: string
  timestamp: string
  type: 'action' | 'event' | 'error'
  description: string
  metadata?: Record<string, any>
}

export interface JarvisConfig {
  name: string
  version: string
  capabilities: string[]
  safety_protocols: {
    daily_limits: Record<string, number>
    review_enabled: boolean
    engagement_filters: boolean
  }
}

export interface CommandRequest {
  command: string
  args?: Record<string, any>
}
