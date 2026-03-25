'use client'

import { useState, useRef, useEffect } from 'react'
import { Send, Terminal } from 'lucide-react'
import Card from '@/components/ui/Card'
import { useJarvis } from '@/hooks/useJarvisContext'

interface CommandLog {
  id: string
  input: string
  output: string
  timestamp: string
  status: 'pending' | 'success' | 'error'
}

export default function CommandTerminal() {
  const [input, setInput] = useState('')
  const [logs, setLogs] = useState<CommandLog[]>([])
  const { executeCommand, status, error } = useJarvis()
  const outputRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (outputRef.current) {
      outputRef.current.scrollTop = outputRef.current.scrollHeight
    }
  }, [logs])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim()) return

    const logId = Date.now().toString()
    const newLog: CommandLog = {
      id: logId,
      input,
      output: '',
      timestamp: new Date().toLocaleTimeString(),
      status: 'pending',
    }

    setLogs((prev) => [...prev, newLog])
    const commandInput = input
    setInput('')

    try {
      await executeCommand(commandInput)
      setLogs((prev) =>
        prev.map((log) =>
          log.id === logId
            ? {
                ...log,
                output: `Command executed successfully`,
                status: 'success',
              }
            : log
        )
      )
    } catch (err) {
      setLogs((prev) =>
        prev.map((log) =>
          log.id === logId
            ? {
                ...log,
                output: `Error: ${err instanceof Error ? err.message : 'Unknown error'}`,
                status: 'error',
              }
            : log
        )
      )
    }
  }

  return (
    <Card variant="pink">
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Terminal size={20} className="text-accent" />
            <h2 className="text-lg font-bold text-pink">Command Terminal</h2>
          </div>
          <span className="text-xs text-muted">v1.0</span>
        </div>

        {/* Output Terminal */}
        <div
          ref={outputRef}
          className="space-y-2 rounded border border-accent/30 bg-background/50 p-4 font-mono text-sm h-64 overflow-y-auto"
        >
          {logs.map((log) => (
            <div key={log.id} className="space-y-1">
              <div className="flex items-center gap-2">
                <span className="text-accent">$</span>
                <span className="text-foreground">{log.input}</span>
              </div>
              <div
                className={`ml-6 text-xs ${
                  log.status === 'success'
                    ? 'text-green-400'
                    : log.status === 'error'
                      ? 'text-red-400'
                      : 'text-muted'
                }`}
              >
                {log.output}
              </div>
            </div>
          ))}
          {status === 'executing' && (
            <div className="flex items-center gap-2 text-muted">
              <span className="text-accent">$</span>
              <span className="animate-pulse">Processing...</span>
            </div>
          )}
          {error && (
            <div className="flex items-center gap-2 text-red-400">
              <span className="text-accent">$</span>
              <span>{error}</span>
            </div>
          )}
        </div>

        {/* Input */}
        <form onSubmit={handleSubmit} className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Enter command (e.g., /status, /help, /post x 'Hello')"
            disabled={status === 'executing'}
            className="flex-1 rounded border border-accent/30 bg-background/50 px-3 py-2 font-mono text-sm text-foreground placeholder-muted focus:border-accent focus:outline-none focus:ring-1 focus:ring-accent/50 disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={status === 'executing' || !input.trim()}
            className="rounded border border-accent/30 bg-accent/10 px-4 py-2 text-accent hover:bg-accent/20 disabled:opacity-50 transition-colors flex items-center gap-2"
          >
            <Send size={16} />
            <span className="hidden sm:inline">Send</span>
          </button>
        </form>

        {/* Info */}
        <div className="border-t border-accent/20 pt-2 text-xs text-muted">
          <p>Commands: /help, /status, /drafts, /post, /memory, /keywords, /kill</p>
        </div>
      </div>
    </Card>
  )
}
