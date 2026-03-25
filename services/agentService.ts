/**
 * Jarvis Agent Service - Central API Communication Layer
 * Handles all communication between React UI and Antigravity backend
 */

import axios, { AxiosInstance, AxiosResponse } from 'axios'

// API Configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
const API_TIMEOUT = 30000 // 30 seconds

// Agent Status Types
export type AgentStatus = 'idle' | 'thinking' | 'executing' | 'success' | 'error' | 'offline'

// Agentic Tool Use Types
export interface AgentStep {
  step: number
  thought: string
  action: string
  action_input: Record<string, any>
  observation: string
  is_final: boolean
}

export interface AgentResult {
  goal: string
  final_answer: string
  steps: AgentStep[]
  success: boolean
  error?: string | null
}

// API Response Types
export interface ApiResponse<T = any> {
  status: 'ok' | 'error'
  data?: T
  error?: string
  command?: string
}

export interface HealthResponse {
  status: string
  service: string
  last_command?: string
  uptime?: string
  active_tasks?: string[]
}

export interface CommandResponse {
  response: string
  status: string
  command: string
}

export interface FeedItem {
  id: string
  source: 'x' | 'linkedin'
  author: string
  handle: string
  text: string
  timestamp: string
  likes: number
  replies: number
}

export interface MemoryLog {
  timestamp: string
  action: string
  status: string
}

export interface SoulConfig {
  version: string
  identity: {
    name: string
    purpose: string
    platforms: string[]
  }
  capabilities: string[]
  safety_protocols: {
    daily_limits: number
    content_review: boolean
    engagement_filters: boolean
    rate_limiting: number
  }
  memory_management: {
    retention_period: string
    archive_strategy: string
    backup_frequency: string
  }
}

class AgentService {
  private client: AxiosInstance
  private wsConnection: WebSocket | null = null
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: API_TIMEOUT,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    // Request interceptor for debugging
    this.client.interceptors.request.use(
      (config) => {
        console.log(`[AgentService] ${config.method?.toUpperCase()} ${config.url}`)
        return config
      },
      (error) => {
        console.error('[AgentService] Request error:', error)
        return Promise.reject(error)
      }
    )

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response: AxiosResponse) => {
        return response
      },
      (error) => {
        console.error('[AgentService] Response error:', error)
        if (error.code === 'ECONNABORTED') {
          throw new Error('Request timeout - Jarvis may be busy')
        }
        if (error.response?.status === 503) {
          throw new Error('Jarvis service unavailable')
        }
        throw error
      }
    )
  }

  // Health Check
  async getHealth(): Promise<HealthResponse> {
    try {
      const response = await this.client.get<ApiResponse<HealthResponse>>('/api/health')
      return (response.data.data || response.data) as HealthResponse
    } catch (error) {
      throw new Error(`Health check failed: ${error instanceof Error ? error.message : 'Unknown error'}`)
    }
  }

  // Command Execution
  async executeCommand(command: string): Promise<CommandResponse> {
    try {
      const response = await this.client.post<ApiResponse<CommandResponse>>('/api/command', {
        command,
      })
      return (response.data.data || response.data) as CommandResponse
    } catch (error) {
      throw new Error(`Command execution failed: ${error instanceof Error ? error.message : 'Unknown error'}`)
    }
  }

  // Get Available Commands
  async getCommands(): Promise<Record<string, string>> {
    try {
      const response = await this.client.get<ApiResponse<{ commands: Record<string, string>; count: number }>>('/api/commands')
      return response.data.data?.commands || {}
    } catch (error) {
      throw new Error(`Failed to fetch commands: ${error instanceof Error ? error.message : 'Unknown error'}`)
    }
  }

  // Get Social Feed
  async getFeed(): Promise<FeedItem[]> {
    try {
      const response = await this.client.get<ApiResponse<FeedItem[]>>('/api/feed')
      return (response.data.data || []) as FeedItem[]
    } catch (error) {
      console.warn('Feed fetch failed, using mock data:', error)
      return this.getMockFeed()
    }
  }

  // Get Memory Logs
  async getMemoryLogs(): Promise<MemoryLog[]> {
    try {
      const response = await this.client.get<ApiResponse<MemoryLog[]>>('/api/memory')
      return (response.data.data || []) as MemoryLog[]
    } catch (error) {
      console.warn('Memory logs fetch failed, using mock data:', error)
      return this.getMockMemoryLogs()
    }
  }

  // Get SOUL Configuration
  async getSoulConfig(): Promise<SoulConfig> {
    try {
      const response = await this.client.get<ApiResponse<SoulConfig>>('/api/soul')
      return (response.data.data || this.getMockSoulConfig()) as SoulConfig
    } catch (error) {
      console.warn('SOUL config fetch failed, using mock data:', error)
      return this.getMockSoulConfig()
    }
  }

  // Update SOUL Configuration
  async updateSoulConfig(config: Partial<SoulConfig>): Promise<void> {
    try {
      await this.client.put('/api/soul', config)
    } catch (error) {
      throw new Error(`Failed to update SOUL config: ${error instanceof Error ? error.message : 'Unknown error'}`)
    }
  }

  // WebSocket Connection for Real-time Updates
  connectWebSocket(onMessage: (data: any) => void, onError?: (error: Event) => void): void {
    if (this.wsConnection?.readyState === WebSocket.OPEN) {
      return
    }

    try {
      const wsUrl = API_BASE_URL.replace('http', 'ws') + '/ws'
      this.wsConnection = new WebSocket(wsUrl)

      this.wsConnection.onopen = () => {
        console.log('[AgentService] WebSocket connected')
        this.reconnectAttempts = 0
      }

      this.wsConnection.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          onMessage(data)
        } catch (error) {
          console.error('[AgentService] WebSocket message parse error:', error)
        }
      }

      this.wsConnection.onerror = (error) => {
        console.error('[AgentService] WebSocket error:', error)
        onError?.(error)
      }

      this.wsConnection.onclose = () => {
        console.log('[AgentService] WebSocket closed')
        this.attemptReconnect(onMessage, onError)
      }
    } catch (error) {
      console.error('[AgentService] WebSocket connection failed:', error)
    }
  }

  // Disconnect WebSocket
  disconnectWebSocket(): void {
    if (this.wsConnection) {
      this.wsConnection.close()
      this.wsConnection = null
    }
  }

  // Private Methods
  private attemptReconnect(onMessage: (data: any) => void, onError?: (error: Event) => void): void {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++
      const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 10000)
      
      console.log(`[AgentService] Attempting WebSocket reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts}) in ${delay}ms`)
      
      setTimeout(() => {
        this.connectWebSocket(onMessage, onError)
      }, delay)
    } else {
      console.error('[AgentService] Max reconnect attempts reached')
    }
  }

  // Run Agentic Task (ReAct loop)
  async runAgent(goal: string, model?: string): Promise<AgentResult> {
    try {
      const body: Record<string, string> = { goal }
      if (model) body.model = model
      const response = await this.client.post<AgentResult>('/api/agent', body)
      return response.data
    } catch (error) {
      throw new Error(`Agent run failed: ${error instanceof Error ? error.message : 'Unknown error'}`)
    }
  }

  // Mock Data Fallbacks
  private getMockFeed(): FeedItem[] {
    return [
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
    ]
  }

  private getMockMemoryLogs(): MemoryLog[] {
    return [
      {
        timestamp: new Date().toISOString(),
        action: 'System initialized',
        status: 'success',
      },
      {
        timestamp: new Date(Date.now() - 3600000).toISOString(),
        action: 'Health check completed',
        status: 'success',
      },
    ]
  }

  private getMockSoulConfig(): SoulConfig {
    return {
      version: '1.0.0',
      identity: {
        name: 'J.A.R.V.I.S',
        purpose: 'Autonomous social media management & content orchestration',
        platforms: ['X (Twitter)', 'LinkedIn'],
      },
      capabilities: [
        'Real-time social listening',
        'Autonomous content generation',
        'Engagement optimization',
        'Sentiment analysis',
        'Trend forecasting',
      ],
      safety_protocols: {
        daily_limits: 50,
        content_review: true,
        engagement_filters: true,
        rate_limiting: 10,
      },
      memory_management: {
        retention_period: '30 days',
        archive_strategy: 'compression',
        backup_frequency: 'daily',
      },
    }
  }
}

// Singleton Instance
export const agentService = new AgentService()

export default agentService
