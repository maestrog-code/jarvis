'use client'

import { createContext, useContext, useReducer, useEffect, ReactNode } from 'react'
import React from 'react'
import { AgentStatus, agentService, HealthResponse, MemoryLog, FeedItem } from '@/services/agentService'

interface State {
  status: AgentStatus
  health: HealthResponse | null
  logs: MemoryLog[]
  feed: FeedItem[]
  connected: boolean
  error: string | null
}

type Action =
  | { type: 'SET_STATUS'; payload: AgentStatus }
  | { type: 'SET_HEALTH'; payload: HealthResponse }
  | { type: 'ADD_LOG'; payload: MemoryLog }
  | { type: 'SET_FEED'; payload: FeedItem[] }
  | { type: 'SET_CONNECTED'; payload: boolean }
  | { type: 'SET_ERROR'; payload: string | null }
  | { type: 'RESET_ERROR' }

const initialState: State = {
  status: 'idle',
  health: null,
  logs: [],
  feed: [],
  connected: false,
  error: null,
}

function reducer(state: State, action: Action): State {
  switch (action.type) {
    case 'SET_STATUS':
      return { ...state, status: action.payload }
    case 'SET_HEALTH':
      return { ...state, health: action.payload }
    case 'ADD_LOG':
      return { ...state, logs: [action.payload, ...state.logs].slice(0, 100) }
    case 'SET_FEED':
      return { ...state, feed: action.payload }
    case 'SET_CONNECTED':
      return { ...state, connected: action.payload }
    case 'SET_ERROR':
      return { ...state, error: action.payload }
    case 'RESET_ERROR':
      return { ...state, error: null }
    default:
      return state
  }
}

interface ContextType extends State {
  executeCommand: (command: string) => Promise<void>
  refreshHealth: () => Promise<void>
  refreshFeed: () => Promise<void>
  resetError: () => void
}

const JarvisContext = createContext<ContextType | null>(null)

export function JarvisProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(reducer, initialState)

  const executeCommand = async (command: string) => {
    dispatch({ type: 'SET_STATUS', payload: 'executing' })
    dispatch({ type: 'RESET_ERROR' })
    
    try {
      const response = await agentService.executeCommand(command)
      dispatch({ type: 'SET_STATUS', payload: 'success' })
      
      const log: MemoryLog = {
        timestamp: new Date().toISOString(),
        action: `Executed: ${command}`,
        status: 'success',
      }
      dispatch({ type: 'ADD_LOG', payload: log })
      
      setTimeout(() => dispatch({ type: 'SET_STATUS', payload: 'idle' }), 2000)
    } catch (error) {
      dispatch({ type: 'SET_STATUS', payload: 'error' })
      dispatch({ type: 'SET_ERROR', payload: error instanceof Error ? error.message : 'Command failed' })
      setTimeout(() => dispatch({ type: 'SET_STATUS', payload: 'idle' }), 3000)
    }
  }

  const refreshHealth = async () => {
    try {
      const health = await agentService.getHealth()
      dispatch({ type: 'SET_HEALTH', payload: health })
      dispatch({ type: 'SET_CONNECTED', payload: true })
      dispatch({ type: 'SET_STATUS', payload: 'idle' })
    } catch (error) {
      dispatch({ type: 'SET_CONNECTED', payload: false })
      dispatch({ type: 'SET_ERROR', payload: 'Health check failed' })
    }
  }

  const refreshFeed = async () => {
    try {
      const feed = await agentService.getFeed()
      dispatch({ type: 'SET_FEED', payload: feed })
    } catch (error) {
      console.error('Feed refresh failed:', error)
    }
  }

  const resetError = () => dispatch({ type: 'RESET_ERROR' })

  useEffect(() => {
    refreshHealth()
    refreshFeed()
    
    const healthInterval = setInterval(refreshHealth, 5000)
    const feedInterval = setInterval(refreshFeed, 30000)
    
    agentService.connectWebSocket(
      (data) => {
        if (data.type === 'log') {
          dispatch({ type: 'ADD_LOG', payload: data.data })
        } else if (data.type === 'status') {
          dispatch({ type: 'SET_STATUS', payload: data.data })
        }
      },
      () => dispatch({ type: 'SET_CONNECTED', payload: false })
    )

    return () => {
      clearInterval(healthInterval)
      clearInterval(feedInterval)
      agentService.disconnectWebSocket()
    }
  }, [])

  const contextValue = {
    ...state,
    executeCommand,
    refreshHealth,
    refreshFeed,
    resetError,
  }

  return React.createElement(
    JarvisContext.Provider,
    { value: contextValue },
    children
  )
}

export function useJarvis() {
  const context = useContext(JarvisContext)
  if (!context) {
    throw new Error('useJarvis must be used within JarvisProvider')
  }
  return context
}
