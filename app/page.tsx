'use client'

import { useState, useEffect } from 'react'
import Layout from '@/components/Layout'
import StatusPulse from '@/components/StatusPulse'
import SocialFeed from '@/components/SocialFeed'
import CommandTerminal from '@/components/CommandTerminal'
import SoulMemory from '@/components/SoulMemory'

export default function Home() {
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // Simulate loading
    const timer = setTimeout(() => setIsLoading(false), 500)
    return () => clearTimeout(timer)
  }, [])

  return (
    <Layout>
      <div className="min-h-screen bg-background">
        {/* Header */}
        <div className="border-b border-primary/20 bg-card-bg glass sticky top-0 z-40">
          <div className="mx-auto max-w-7xl px-4 py-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-3xl font-bold text-cyan">J.A.R.V.I.S</h1>
                <p className="text-sm text-muted">Command Center v1.0</p>
              </div>
              <div className="flex items-center gap-4">
                <div className="flex h-3 w-3 items-center justify-center">
                  <div className="h-2 w-2 rounded-full bg-primary animate-pulse"></div>
                </div>
                <span className="text-xs text-primary">SYSTEM ACTIVE</span>
              </div>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
          {isLoading ? (
            <div className="flex items-center justify-center py-20">
              <div className="text-center">
                <div className="mb-4 inline-block">
                  <div className="h-12 w-12 animate-spin rounded-full border-4 border-primary/20 border-t-primary"></div>
                </div>
                <p className="text-muted">Initializing systems...</p>
              </div>
            </div>
          ) : (
            <div className="grid gap-6">
              {/* Top Row: Status & Social */}
              <div className="grid gap-6 lg:grid-cols-3">
                <div className="lg:col-span-1">
                  <StatusPulse />
                </div>
                <div className="lg:col-span-2">
                  <SocialFeed />
                </div>
              </div>

              {/* Middle Row: Command Terminal */}
              <div className="grid gap-6">
                <CommandTerminal />
              </div>

              {/* Bottom Row: SOUL Memory */}
              <div className="grid gap-6">
                <SoulMemory />
              </div>
            </div>
          )}
        </main>
      </div>
    </Layout>
  )
}
