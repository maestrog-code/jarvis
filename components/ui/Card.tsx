import { ReactNode } from 'react'

interface CardProps {
  children: ReactNode
  className?: string
  variant?: 'default' | 'cyan' | 'gold' | 'pink'
}

export default function Card({ children, className = '', variant = 'default' }: CardProps) {
  const variantStyles = {
    default: 'glass',
    cyan: 'glass glow-cyan',
    gold: 'glass glow-gold',
    pink: 'glass glow-pink',
  }

  return (
    <div className={`rounded-lg p-6 ${variantStyles[variant]} ${className}`}>
      {children}
    </div>
  )
}
