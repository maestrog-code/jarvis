/**
 * CommandTerminal Component (React Example)
 * 
 * This is a fully functional example that integrates with the Jarvis API bridge.
 * 
 * To use in your React app:
 * 1. Copy frontend-client.ts to your src/hooks/ folder
 * 2. Copy this file to your src/components/ folder (rename to CommandTerminal.tsx)
 * 3. Import and use in your page/app
 * 4. Ensure REACT_APP_JARVIS_API_URL=http://localhost:8000 in your .env
 */

'use client' // If using Next.js App Router

import React, { useState, useEffect, useRef } from 'react'
import { useJarvisCommand, getAvailableCommands, checkHealth } from '../hooks/useJarvisCommand'

interface TerminalMessage {
  type: 'input' | 'output' | 'error' | 'system'
  content: string
  timestamp: Date
}

export function CommandTerminal() {
  const { sendCommand, response, loading, error, history } = useJarvisCommand()
  const [input, setInput] = useState('')
  const [messages, setMessages] = useState<TerminalMessage[]>([])
  const [suggestions, setSuggestions] = useState<string[]>([])
  const [apiHealthy, setApiHealthy] = useState<boolean>(false)
  const terminalEndRef = useRef<HTMLDivElement>(null)

  // Check API health on mount
  useEffect(() => {
    const checkAPI = async () => {
      const healthy = await checkHealth()
      setApiHealthy(healthy)
      if (!healthy) {
        addMessage('system', '⚠️ API Bridge is offline. Make sure to run: python -m jarvis.api_bridge')
      } else {
        addMessage('system', '✅ Connected to Jarvis API')
      }
    }
    checkAPI()
  }, [])

  // Load command suggestions
  useEffect(() => {
    const loadCommands = async () => {
      const commands = await getAvailableCommands()
      setSuggestions(Object.keys(commands))
    }
    loadCommands()
  }, [])

  // Auto-scroll to bottom
  useEffect(() => {
    terminalEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // Handle responses from API
  useEffect(() => {
    if (response) {
      addMessage('output', response)
    }
  }, [response])

  // Handle errors
  useEffect(() => {
    if (error) {
      addMessage('error', `❌ ${error}`)
    }
  }, [error])

  const addMessage = (type: TerminalMessage['type'], content: string) => {
    setMessages((prev) => [...prev, { type, content, timestamp: new Date() }])
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || !apiHealthy) return

    const cmd = input.trim()
    addMessage('input', `$ ${cmd}`)
    setInput('')

    await sendCommand(cmd)
  }

  const handleCommandSuggestion = async (cmd: string) => {
    addMessage('input', `$ ${cmd}`)
    setInput('')
    await sendCommand(cmd)
  }

  const clearTerminal = () => {
    setMessages([])
  }

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h2 style={styles.title}>🤖 Jarvis Command Terminal</h2>
        <div style={styles.statusBar}>
          <span style={apiHealthy ? styles.statusOnline : styles.statusOffline}>
            {apiHealthy ? '🟢 Online' : '🔴 Offline'}
          </span>
          <button onClick={clearTerminal} style={styles.clearBtn}>
            Clear
          </button>
        </div>
      </div>

      {/* Quick Commands */}
      {suggestions.length > 0 && (
        <div style={styles.quickCommands}>
          <label style={styles.suggestionsLabel}>Quick Commands:</label>
          <div style={styles.suggestionsGrid}>
            {['/help', '/status', '/drafts', '/briefing'].map((cmd) => (
              suggestions.includes(cmd) && (
                <button
                  key={cmd}
                  onClick={() => handleCommandSuggestion(cmd)}
                  disabled={loading || !apiHealthy}
                  style={styles.suggestionBtn}
                >
                  {cmd}
                </button>
              )
            ))}
          </div>
        </div>
      )}

      {/* Terminal Output */}
      <div style={styles.terminalBox}>
        {messages.length === 0 ? (
          <div style={styles.emptyState}>
            <p>💡 Type a command and press Enter</p>
            <p style={styles.help}>/help for available commands</p>
          </div>
        ) : (
          messages.map((msg, idx) => (
            <div key={idx} style={styles.messageLine}>
              <span style={styles.timestamp}>
                {msg.timestamp.toLocaleTimeString()}
              </span>
              <pre
                style={{
                  ...styles.messageContent,
                  ...(msg.type === 'input' && styles.inputLine),
                  ...(msg.type === 'output' && styles.outputLine),
                  ...(msg.type === 'error' && styles.errorLine),
                  ...(msg.type === 'system' && styles.systemLine),
                }}
              >
                {msg.content}
              </pre>
            </div>
          ))
        )}
        <div ref={terminalEndRef} />
      </div>

      {/* Command Input */}
      <form onSubmit={handleSubmit} style={styles.form}>
        <span style={styles.prompt}>$</span>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Enter command (e.g., /status, /post x Hello)"
          disabled={loading || !apiHealthy}
          style={styles.input}
          autoFocus
          list="commands"
        />
        <datalist id="commands">
          {suggestions.map((cmd) => (
            <option key={cmd} value={cmd} />
          ))}
        </datalist>
        <button
          type="submit"
          disabled={loading || !apiHealthy || !input.trim()}
          style={styles.submitBtn}
        >
          {loading ? '⏳' : '→'}
        </button>
      </form>

      {/* Footer Info */}
      <div style={styles.footer}>
        <small>
          Commands executed: {history.length} | Last: {history[history.length - 1] || 'none'}
        </small>
      </div>
    </div>
  )
}

// ─────────────────────────────────────────────────────────────────
// Styles
// ─────────────────────────────────────────────────────────────────

const styles: Record<string, React.CSSProperties> = {
  container: {
    display: 'flex',
    flexDirection: 'column',
    height: '100vh',
    background: '#1e1e1e',
    color: '#e0e0e0',
    fontFamily: '"Fira Code", "Courier New", monospace',
    fontSize: '14px',
    lineHeight: '1.6',
    padding: '1rem',
    gap: '1rem',
  },

  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    borderBottom: '2px solid #404040',
    paddingBottom: '0.5rem',
  },

  title: {
    margin: 0,
    fontSize: '1.5rem',
    fontWeight: 'bold',
    color: '#00ff88',
  },

  statusBar: {
    display: 'flex',
    gap: '1rem',
    alignItems: 'center',
  },

  statusOnline: {
    color: '#00ff88',
    fontWeight: 'bold',
  },

  statusOffline: {
    color: '#ff4444',
    fontWeight: 'bold',
  },

  clearBtn: {
    padding: '0.25rem 0.75rem',
    background: '#404040',
    color: '#e0e0e0',
    border: '1px solid #606060',
    borderRadius: '4px',
    cursor: 'pointer',
    fontSize: '12px',
  },

  quickCommands: {
    background: '#262626',
    padding: '0.75rem',
    borderRadius: '4px',
    borderLeft: '3px solid #00ff88',
  },

  suggestionsLabel: {
    display: 'block',
    fontSize: '12px',
    color: '#888',
    marginBottom: '0.5rem',
    textTransform: 'uppercase',
  },

  suggestionsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(100px, 1fr))',
    gap: '0.5rem',
  },

  suggestionBtn: {
    padding: '0.5rem',
    background: '#333',
    border: '1px solid #00ff88',
    color: '#00ff88',
    borderRadius: '4px',
    cursor: 'pointer',
    fontSize: '12px',
    transition: 'all 0.2s',
  },

  terminalBox: {
    flex: 1,
    background: '#000',
    border: '1px solid #404040',
    borderRadius: '4px',
    padding: '1rem',
    overflowY: 'auto',
    fontFamily: 'inherit',
  },

  emptyState: {
    textAlign: 'center',
    color: '#666',
    paddingTop: '2rem',
  },

  help: {
    fontSize: '12px',
    marginTop: '0.5rem',
  },

  messageLine: {
    display: 'flex',
    gap: '0.5rem',
    marginBottom: '0.5rem',
  },

  timestamp: {
    color: '#666',
    fontSize: '11px',
    minWidth: '60px',
  },

  messageContent: {
    margin: 0,
    padding: 0,
    whiteSpace: 'pre-wrap',
    wordBreak: 'break-word',
    fontFamily: 'inherit',
  },

  inputLine: {
    color: '#00ff88',
  },

  outputLine: {
    color: '#e0e0e0',
  },

  errorLine: {
    color: '#ff6b6b',
  },

  systemLine: {
    color: '#ffaa00',
    fontStyle: 'italic',
  },

  form: {
    display: 'flex',
    gap: '0.5rem',
    alignItems: 'center',
    background: '#262626',
    padding: '0.75rem',
    borderRadius: '4px',
    borderTop: '1px solid #404040',
  },

  prompt: {
    color: '#00ff88',
    fontWeight: 'bold',
  },

  input: {
    flex: 1,
    background: 'transparent',
    border: 'none',
    color: '#e0e0e0',
    fontFamily: 'inherit',
    fontSize: 'inherit',
    outline: 'none',
    padding: '0.25rem',
  },

  submitBtn: {
    padding: '0.5rem 0.75rem',
    background: '#00ff88',
    color: '#000',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    fontWeight: 'bold',
    transition: 'all 0.2s',
  },

  footer: {
    textAlign: 'right',
    color: '#666',
    fontSize: '12px',
    paddingTop: '0.5rem',
    borderTop: '1px solid #404040',
  },
}
