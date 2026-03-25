'use client'

import { useState, useRef, useEffect } from 'react'
import { agentService, AgentStep } from '@/services/agentService'

interface AgentState {
  status: 'idle' | 'running' | 'done' | 'error'
  goal: string
  finalAnswer: string
  steps: AgentStep[]
  error: string
}

const initialState: AgentState = {
  status: 'idle',
  goal: '',
  finalAnswer: '',
  steps: [],
  error: '',
}

export default function AgentPanel() {
  const [state, setState] = useState<AgentState>(initialState)
  const [goalInput, setGoalInput] = useState('')
  const [expandedSteps, setExpandedSteps] = useState<Set<number>>(new Set())
  const answerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (state.status === 'done' && answerRef.current) {
      answerRef.current.scrollIntoView({ behavior: 'smooth', block: 'nearest' })
    }
  }, [state.status])

  const handleRun = async () => {
    if (!goalInput.trim() || state.status === 'running') return
    setState({ ...initialState, status: 'running', goal: goalInput.trim() })
    try {
      const result = await agentService.runAgent(goalInput.trim())
      setState({
        status: result.success ? 'done' : 'error',
        goal: result.goal,
        finalAnswer: result.final_answer,
        steps: result.steps ?? [],
        error: result.error ?? '',
      })
    } catch (err: any) {
      setState(prev => ({
        ...prev,
        status: 'error',
        error: err.message ?? 'Unknown error',
      }))
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
      handleRun()
    }
  }

  const toggleStep = (idx: number) => {
    setExpandedSteps(prev => {
      const next = new Set(prev)
      next.has(idx) ? next.delete(idx) : next.add(idx)
      return next
    })
  }

  const statusColor = {
    idle: '#404854',
    running: '#00d4ff',
    done: '#00ff88',
    error: '#ff006e',
  }[state.status]

  const toolIcon: Record<string, string> = {
    web_search: '🔍',
    read_file: '📄',
    write_file: '✍️',
    run_shell: '💻',
    scrape_url: '🌐',
    recall_memory: '🧠',
    store_memory: '💾',
    list_skills: '🛠️',
    run_skill: '⚡',
    DONE: '✅',
  }

  return (
    <div style={{
      background: 'rgba(10, 14, 39, 0.85)',
      backdropFilter: 'blur(12px)',
      WebkitBackdropFilter: 'blur(12px)',
      border: '1px solid rgba(0, 212, 255, 0.2)',
      borderRadius: '16px',
      padding: '24px',
      display: 'flex',
      flexDirection: 'column',
      gap: '20px',
      boxShadow: '0 0 30px rgba(0, 212, 255, 0.08)',
      fontFamily: "'Roboto', sans-serif",
    }}>

      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <div style={{
          width: '10px', height: '10px', borderRadius: '50%',
          background: statusColor,
          boxShadow: `0 0 12px ${statusColor}`,
          transition: 'all 0.3s ease',
          animation: state.status === 'running' ? 'pulse 1s infinite' : 'none',
        }} />
        <h2 style={{
          color: '#00d4ff',
          fontSize: '18px',
          fontWeight: 700,
          letterSpacing: '0.08em',
          textShadow: '0 0 10px rgba(0, 212, 255, 0.6)',
          margin: 0,
        }}>
          🤖 AGENT MODE
        </h2>
        <span style={{
          marginLeft: 'auto',
          fontSize: '11px',
          color: '#404854',
          fontFamily: "'Space Mono', monospace",
          letterSpacing: '0.1em',
        }}>
          REACT · LOCAL · FREE
        </span>
      </div>

      <p style={{ color: '#8892a4', fontSize: '13px', margin: 0, lineHeight: 1.5 }}>
        Give Jarvis a complex goal. It will autonomously plan, pick tools, execute them,
        and loop until done — all using your local Ollama model.
      </p>

      {/* Input */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
        <textarea
          id="agent-goal-input"
          value={goalInput}
          onChange={e => setGoalInput(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={state.status === 'running'}
          placeholder="Enter your goal… e.g. 'Search for the latest AI news and summarise in 5 bullet points'"
          rows={3}
          style={{
            width: '100%',
            background: 'rgba(20, 28, 52, 0.6)',
            border: '1px solid rgba(0, 212, 255, 0.2)',
            borderRadius: '10px',
            color: '#e0e0e0',
            padding: '14px 16px',
            fontSize: '14px',
            fontFamily: 'inherit',
            resize: 'vertical',
            outline: 'none',
            transition: 'border-color 0.2s ease, box-shadow 0.2s ease',
            boxSizing: 'border-box',
            opacity: state.status === 'running' ? 0.6 : 1,
          }}
          onFocus={e => {
            e.target.style.borderColor = 'rgba(0, 212, 255, 0.6)'
            e.target.style.boxShadow = '0 0 0 2px rgba(0, 212, 255, 0.1)'
          }}
          onBlur={e => {
            e.target.style.borderColor = 'rgba(0, 212, 255, 0.2)'
            e.target.style.boxShadow = 'none'
          }}
        />

        <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
          <button
            id="agent-run-button"
            onClick={handleRun}
            disabled={!goalInput.trim() || state.status === 'running'}
            style={{
              background: state.status === 'running'
                ? 'rgba(0, 212, 255, 0.1)'
                : 'linear-gradient(135deg, rgba(0, 212, 255, 0.2), rgba(0, 212, 255, 0.05))',
              border: '1px solid rgba(0, 212, 255, 0.4)',
              borderRadius: '8px',
              color: state.status === 'running' ? '#4a8a9a' : '#00d4ff',
              padding: '10px 24px',
              fontSize: '13px',
              fontWeight: 600,
              letterSpacing: '0.08em',
              cursor: state.status === 'running' || !goalInput.trim() ? 'not-allowed' : 'pointer',
              transition: 'all 0.2s ease',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
            }}
          >
            {state.status === 'running' ? (
              <><span style={{ animation: 'spin 1s linear infinite', display: 'inline-block' }}>⟳</span> RUNNING…</>
            ) : '▶ RUN AGENT'}
          </button>

          {state.status !== 'idle' && state.status !== 'running' && (
            <button
              id="agent-reset-button"
              onClick={() => { setState(initialState); setGoalInput(''); setExpandedSteps(new Set()) }}
              style={{
                background: 'transparent',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                borderRadius: '8px',
                color: '#404854',
                padding: '10px 16px',
                fontSize: '12px',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
              }}
              onMouseEnter={e => (e.currentTarget.style.color = '#e0e0e0')}
              onMouseLeave={e => (e.currentTarget.style.color = '#404854')}
            >
              ✕ CLEAR
            </button>
          )}

          <span style={{
            marginLeft: 'auto',
            fontSize: '11px',
            color: '#404854',
            fontFamily: "'Space Mono', monospace",
          }}>
            Ctrl+Enter to run
          </span>
        </div>
      </div>

      {/* Running indicator */}
      {state.status === 'running' && (
        <div style={{
          background: 'rgba(0, 212, 255, 0.04)',
          border: '1px solid rgba(0, 212, 255, 0.15)',
          borderRadius: '10px',
          padding: '16px',
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
        }}>
          <div style={{
            width: '8px', height: '8px', borderRadius: '50%',
            background: '#00d4ff',
            animation: 'pulse 0.8s ease-in-out infinite',
          }} />
          <span style={{ color: '#00d4ff', fontSize: '13px', fontFamily: "'Space Mono', monospace" }}>
            Agent is reasoning and executing tools…
          </span>
        </div>
      )}

      {/* Step log */}
      {state.steps.length > 0 && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <h3 style={{ color: '#8892a4', fontSize: '12px', fontWeight: 600, letterSpacing: '0.12em', margin: 0, textTransform: 'uppercase' }}>
            Execution Trace · {state.steps.length} step{state.steps.length !== 1 ? 's' : ''}
          </h3>

          {state.steps.map((step, idx) => (
            <div
              key={idx}
              id={`agent-step-${idx}`}
              style={{
                background: 'rgba(20, 28, 52, 0.5)',
                border: `1px solid ${step.is_final ? 'rgba(0, 255, 136, 0.2)' : 'rgba(255, 215, 0, 0.1)'}`,
                borderRadius: '8px',
                overflow: 'hidden',
                transition: 'border-color 0.2s ease',
              }}
            >
              <button
                onClick={() => toggleStep(idx)}
                style={{
                  width: '100%',
                  background: 'transparent',
                  border: 'none',
                  padding: '12px 16px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '10px',
                  cursor: 'pointer',
                  textAlign: 'left',
                }}
              >
                <span style={{ fontSize: '16px' }}>
                  {toolIcon[step.action] ?? '⚙️'}
                </span>
                <span style={{
                  color: step.is_final ? '#00ff88' : '#ffd700',
                  fontFamily: "'Space Mono', monospace",
                  fontSize: '12px',
                  fontWeight: 600,
                }}>
                  {step.is_final ? 'FINAL' : `STEP ${step.step}`}
                </span>
                <span style={{ color: '#8892a4', fontSize: '12px' }}>
                  {step.is_final ? 'Done' : step.action}
                </span>
                {step.thought && (
                  <span style={{
                    marginLeft: 'auto',
                    color: '#404854',
                    fontSize: '11px',
                    maxWidth: '200px',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    whiteSpace: 'nowrap',
                  }}>
                    {step.thought}
                  </span>
                )}
                <span style={{ color: '#404854', fontSize: '11px', marginLeft: step.thought ? '4px' : 'auto' }}>
                  {expandedSteps.has(idx) ? '▲' : '▼'}
                </span>
              </button>

              {expandedSteps.has(idx) && (
                <div style={{ padding: '0 16px 14px', display: 'flex', flexDirection: 'column', gap: '10px' }}>
                  {step.thought && (
                    <div>
                      <div style={{ color: '#404854', fontSize: '10px', letterSpacing: '0.1em', marginBottom: '4px', textTransform: 'uppercase' }}>Thought</div>
                      <p style={{ color: '#8892a4', fontSize: '12px', lineHeight: 1.6, margin: 0 }}>{step.thought}</p>
                    </div>
                  )}

                  {step.action && !step.is_final && (
                    <div>
                      <div style={{ color: '#404854', fontSize: '10px', letterSpacing: '0.1em', marginBottom: '4px', textTransform: 'uppercase' }}>Tool Call</div>
                      <code style={{
                        display: 'block',
                        background: 'rgba(0,0,0,0.3)',
                        borderRadius: '6px',
                        padding: '8px 12px',
                        color: '#ffd700',
                        fontSize: '12px',
                        fontFamily: "'Space Mono', monospace",
                        whiteSpace: 'pre-wrap',
                        wordBreak: 'break-all',
                      }}>
                        {step.action}({JSON.stringify(step.action_input)})
                      </code>
                    </div>
                  )}

                  {step.observation && !step.is_final && (
                    <div>
                      <div style={{ color: '#404854', fontSize: '10px', letterSpacing: '0.1em', marginBottom: '4px', textTransform: 'uppercase' }}>Result</div>
                      <pre style={{
                        background: 'rgba(0,0,0,0.3)',
                        borderRadius: '6px',
                        padding: '8px 12px',
                        color: '#e0e0e0',
                        fontSize: '11px',
                        fontFamily: "'Space Mono', monospace",
                        whiteSpace: 'pre-wrap',
                        wordBreak: 'break-word',
                        margin: 0,
                        maxHeight: '200px',
                        overflowY: 'auto',
                      }}>
                        {step.observation}
                      </pre>
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Final answer */}
      {state.status === 'done' && state.finalAnswer && (
        <div
          ref={answerRef}
          id="agent-final-answer"
          style={{
            background: 'rgba(0, 255, 136, 0.04)',
            border: '1px solid rgba(0, 255, 136, 0.2)',
            borderRadius: '10px',
            padding: '18px',
            boxShadow: '0 0 20px rgba(0, 255, 136, 0.05)',
          }}
        >
          <div style={{ color: '#00ff88', fontSize: '12px', letterSpacing: '0.12em', fontWeight: 600, marginBottom: '10px', textTransform: 'uppercase' }}>
            ✅ Final Answer
          </div>
          <div style={{
            color: '#e0e0e0',
            fontSize: '14px',
            lineHeight: 1.7,
            whiteSpace: 'pre-wrap',
          }}>
            {state.finalAnswer}
          </div>
        </div>
      )}

      {/* Error state */}
      {state.status === 'error' && (
        <div style={{
          background: 'rgba(255, 0, 110, 0.06)',
          border: '1px solid rgba(255, 0, 110, 0.25)',
          borderRadius: '10px',
          padding: '16px',
        }}>
          <div style={{ color: '#ff006e', fontSize: '12px', letterSpacing: '0.1em', fontWeight: 600, marginBottom: '8px', textTransform: 'uppercase' }}>
            ❌ Agent Error
          </div>
          <p style={{ color: '#cc4465', fontSize: '13px', margin: 0, lineHeight: 1.5 }}>
            {state.error || state.finalAnswer || 'An unknown error occurred.'}
          </p>
          <p style={{ color: '#404854', fontSize: '12px', marginTop: '8px', margin: '8px 0 0' }}>
            Make sure Ollama is running: <code style={{ color: '#ffd700', fontFamily: "'Space Mono', monospace" }}>ollama serve</code>
          </p>
        </div>
      )}

      <style jsx global>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; transform: scale(1); }
          50% { opacity: 0.5; transform: scale(0.9); }
        }
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  )
}
