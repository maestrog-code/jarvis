import { useState, useEffect } from 'react'
import { jarvisAPI } from '@/services/api'
import { HealthStatus } from '@/types/jarvis'

export function useSystemStatus(pollInterval: number = 5000) {
  const [status, setStatus] = useState<HealthStatus | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const data = await jarvisAPI.getHealth()
        setStatus(data)
        setError(null)
      } catch (err) {
        const error = err instanceof Error ? err : new Error('Unknown error')
        setError(error)
        console.error('[v0] Status fetch error:', error)
      } finally {
        setLoading(false)
      }
    }

    // Initial fetch
    fetchStatus()

    // Poll for updates
    const interval = setInterval(fetchStatus, pollInterval)

    return () => clearInterval(interval)
  }, [pollInterval])

  return { status, loading, error }
}
