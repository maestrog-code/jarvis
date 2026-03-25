import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { JarvisProvider } from '@/hooks/useJarvisContext'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Jarvis Command Center',
  description: 'AI Assistant Command & Control Dashboard',
}

export const viewport = {
  width: 'device-width',
  initialScale: 1,
  maximumScale: 1,
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="scroll-smooth">
      <body className={`${inter.className} bg-background text-foreground`}>
        <JarvisProvider>
          {children}
        </JarvisProvider>
      </body>
    </html>
  )
}
