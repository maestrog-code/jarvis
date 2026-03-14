import { CommandResponse, HealthStatus, CommandRequest } from '@/types/jarvis'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

class JarvisAPI {
  private baseUrl: string

  constructor(baseUrl: string = API_URL) {
    this.baseUrl = baseUrl
  }

  async sendCommand(command: string): Promise<CommandResponse> {
    const response = await fetch(`${this.baseUrl}/api/command`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ command } as CommandRequest),
    })

    if (!response.ok) {
      throw new Error(`Command failed: ${response.statusText}`)
    }

    return response.json()
  }

  async getHealth(): Promise<HealthStatus> {
    const response = await fetch(`${this.baseUrl}/api/health`)

    if (!response.ok) {
      throw new Error(`Health check failed: ${response.statusText}`)
    }

    return response.json()
  }

  async getFeed(limit: number = 10) {
    const response = await fetch(`${this.baseUrl}/api/feed?limit=${limit}`)

    if (!response.ok) {
      throw new Error(`Feed fetch failed: ${response.statusText}`)
    }

    return response.json()
  }

  async getMemory() {
    const response = await fetch(`${this.baseUrl}/api/memory`)

    if (!response.ok) {
      throw new Error(`Memory fetch failed: ${response.statusText}`)
    }

    return response.json()
  }

  async getSoulConfig() {
    const response = await fetch(`${this.baseUrl}/api/soul`)

    if (!response.ok) {
      throw new Error(`SOUL config fetch failed: ${response.statusText}`)
    }

    return response.json()
  }

  async updateSoulConfig(config: string) {
    const response = await fetch(`${this.baseUrl}/api/soul`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ config }),
    })

    if (!response.ok) {
      throw new Error(`SOUL update failed: ${response.statusText}`)
    }

    return response.json()
  }
}

export const jarvisAPI = new JarvisAPI()
