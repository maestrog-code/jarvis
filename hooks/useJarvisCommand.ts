import { useState, useCallback } from 'react'
import { jarvisAPI } from '@/services/api'
import { CommandResponse } from '@/types/jarvis'

interface UseJarvisCommandOptions {
  onSuccess?: (response: CommandResponse) => void
  onError?: (error: Error) => void
}

export function useJarvisCommand(options: UseJarvisCommandOptions = {}) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<Error | null>(null)
  const [response, setResponse] = useState<CommandResponse | null>(null)

  const sendCommand = useCallback(
    async (command: string) => {
      setLoading(true)
      setError(null)

      try {
        const result = await jarvisAPI.sendCommand(command)
        setResponse(result)
        options.onSuccess?.(result)
        return result
      } catch (err) {
        const error = err instanceof Error ? err : new Error('Unknown error')
        setError(error)
        options.onError?.(error)
        throw error
      } finally {
        setLoading(false)
      }
    },
    [options]
  )

  return {
    sendCommand,
    loading,
    error,
    response,
  }
}
