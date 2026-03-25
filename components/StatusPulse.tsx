'use client'

import { useState, useEffect } from 'react'
import { Activity, Network, Zap } from 'lucide-react'
import Card from '@/components/ui/Card'
import Badge from '@/components/ui/Badge'
import { useJarvis } from '@/hooks/useJarvisContext'

interface SystemStatus {
  status: string
  connections: number
  health: number
}

export default function StatusPulse() {
  const { status, health, connected, error } = useJarvis()
  
  const systemStatus = {
    status: connected ? (status === 'idle' ? 'ONLINE' : status.toUpperCase()) : 'OFFLINE',
    connections: connected ? 3 : 0,
    health: connected && !error ? 85 : 0,
  }

  return (
    <Card variant="cyan">
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-bold text-cyan">System Status</h2>
          <div className="h-2 w-2 rounded-full bg-primary animate-pulse"></div>
        </div>

        <div className="space-y-3">
          {/* Status */}
          <div className="flex items-center justify-between rounded border border-primary/20 bg-primary/5 px-3 py-2">
            <div className="flex items-center gap-2">
              <Activity size={16} className="text-primary" />
              <span className="text-sm text-muted">Status</span>
            </div>
            <Badge 
              label={systemStatus.status} 
              variant={
                systemStatus.status === 'ONLINE' ? 'success' : 
                systemStatus.status === 'OFFLINE' ? 'error' : 
                'default'
              } 
            />
          </div>

          {/* Connections */}
          <div className="flex items-center justify-between rounded border border-primary/20 bg-primary/5 px-3 py-2">
            <div className="flex items-center gap-2">
              <Network size={16} className="text-primary" />
              <span className="text-sm text-muted">Connections</span>
            </div>
            <span className="font-mono text-sm text-primary">{systemStatus.connections}</span>
          </div>

          {/* Health */}
          <div className="flex items-center justify-between rounded border border-primary/20 bg-primary/5 px-3 py-2">
            <div className="flex items-center gap-2">
              <Zap size={16} className="text-primary" />
              <span className="text-sm text-muted">Health</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="h-2 w-20 rounded-full bg-primary/20">
                <div
                  className="h-full rounded-full bg-primary transition-all duration-300"
                  style={{ width: `${systemStatus.health}%` }}
                ></div>
              </div>
              <span className="font-mono text-xs text-primary">{systemStatus.health}%</span>
            </div>
          </div>
        </div>

        {/* Last Update */}
        <div className="border-t border-primary/20 pt-3">
          <p className="text-xs text-muted/70">
            Last update: {new Date().toLocaleTimeString()}
          </p>
        </div>
      </div>
    </Card>
  )
}
