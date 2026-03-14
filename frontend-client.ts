/**
 * Jarvis API Client — React/TypeScript frontend bridge
 *
 * Usage in React component:
 *
 *   import { useJarvisCommand } from './jarvis-client'
 *
 *   export function CommandTerminal() {
 *     const { sendCommand, response, loading, error } = useJarvisCommand()
 *
 *     return (
 *       <div>
 *         <input 
 *           onKeyDown={(e) => {
 *             if (e.key === 'Enter') {
 *               sendCommand(e.currentTarget.value)
 *               e.currentTarget.value = ''
 *             }
 *           }}
 *         />
 *         {loading && <p>Loading...</p>}
 *         {error && <p style={{color: 'red'}}>{error}</p>}
 *         {response && <pre>{response}</pre>}
 *       </div>
 *     )
 *   }
 */

import { useState, useCallback, useRef } from 'react'

const API_BASE_URL = process.env.REACT_APP_JARVIS_API_URL || 'http://localhost:8000'

export interface JarvisResponse {
  response: string
  status: 'ok' | 'error'
  command?: string
  error?: string
}

export interface UseJarvisCommandReturn {
  sendCommand: (command: string) => Promise<void>
  response: string | null
  loading: boolean
  error: string | null
  history: string[]
  clearHistory: () => void
}

/**
 * React hook for dispatching commands to Jarvis API
 */
export function useJarvisCommand(): UseJarvisCommandReturn {
  const [response, setResponse] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [history, setHistory] = useState<string[]>([])
  const abortController = useRef<AbortController | null>(null)

  const sendCommand = useCallback(async (command: string): Promise<void> => {
    console.log('[v0] Sending command:', command)

    if (!command.trim()) {
      setError('Command cannot be empty')
      return
    }

    setLoading(true)
    setError(null)
    setResponse(null)

    // Cancel previous request if still in flight
    if (abortController.current) {
      abortController.current.abort()
    }

    abortController.current = new AbortController()

    try {
      const res = await fetch(`${API_BASE_URL}/api/command`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ command }),
        signal: abortController.current.signal,
      })

      if (!res.ok) {
        const errorData = (await res.json()) as JarvisResponse
        throw new Error(errorData.error || `HTTP ${res.status}`)
      }

      const data = (await res.json()) as JarvisResponse

      if (data.status === 'error') {
        setError(data.error || 'Unknown error')
      } else {
        setResponse(data.response)
        setHistory((prev) => [...prev, command])
        console.log('[v0] Command succeeded:', data.response.slice(0, 100))
      }
    } catch (err) {
      if (err instanceof Error) {
        if (err.name === 'AbortError') {
          console.log('[v0] Request cancelled')
        } else {
          console.error('[v0] Command error:', err.message)
          setError(err.message)
        }
      } else {
        setError('Unknown error occurred')
      }
    } finally {
      setLoading(false)
    }
  }, [])

  const clearHistory = useCallback(() => {
    setHistory([])
    setResponse(null)
    setError(null)
  }, [])

  return {
    sendCommand,
    response,
    loading,
    error,
    history,
    clearHistory,
  }
}

/**
 * Fetch available commands from the API
 */
export async function getAvailableCommands(): Promise<Record<string, string>> {
  try {
    const res = await fetch(`${API_BASE_URL}/api/commands`)
    if (!res.ok) throw new Error(`HTTP ${res.status}`)

    const data = (await res.json()) as { commands: Record<string, string>; count: number }
    console.log('[v0] Available commands:', data.count)
    return data.commands
  } catch (err) {
    console.error('[v0] Failed to fetch commands:', err)
    return {}
  }
}

/**
 * Check API health
 */
export async function checkHealth(): Promise<boolean> {
  try {
    const res = await fetch(`${API_BASE_URL}/api/health`)
    return res.ok
  } catch {
    console.error('[v0] API health check failed')
    return false
  }
}

/**
 * WebSocket client for streaming (optional)
 */
export function useJarvisWebSocket() {
  const [isConnected, setIsConnected] = useState(false)
  const [response, setResponse] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const wsRef = useRef<WebSocket | null>(null)

  const connect = useCallback(() => {
    const wsUrl = `${API_BASE_URL.replace('http://', 'ws://').replace('https://', 'wss://')}/ws`
    console.log('[v0] Connecting to WebSocket:', wsUrl)

    const ws = new WebSocket(wsUrl)

    ws.onopen = () => {
      console.log('[v0] WebSocket connected')
      setIsConnected(true)
    }

    ws.onmessage = (event: MessageEvent) => {
      try {
        const data = JSON.parse(event.data)
        if (data.type === 'response') {
          setResponse(data.data)
        } else if (data.type === 'error') {
          setError(data.data)
        }
      } catch (err) {
        console.error('[v0] Failed to parse WebSocket message:', err)
      }
    }

    ws.onerror = (event: Event) => {
      console.error('[v0] WebSocket error:', event)
      setError('WebSocket error')
    }

    ws.onclose = () => {
      console.log('[v0] WebSocket disconnected')
      setIsConnected(false)
    }

    wsRef.current = ws
  }, [])

  const sendCommand = useCallback((command: string) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ command }))
      console.log('[v0] WebSocket command sent:', command)
    } else {
      setError('WebSocket not connected')
    }
  }, [])

  const disconnect = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close()
      wsRef.current = null
    }
  }, [])

  return {
    connect,
    disconnect,
    sendCommand,
    isConnected,
    response,
    error,
  }
}
