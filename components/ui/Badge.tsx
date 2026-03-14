interface BadgeProps {
  label: string
  variant?: 'default' | 'success' | 'warning' | 'error' | 'cyan' | 'gold'
}

export default function Badge({ label, variant = 'default' }: BadgeProps) {
  const variantStyles = {
    default: 'bg-muted text-foreground',
    success: 'bg-green-900/30 text-green-400 border border-green-500/20',
    warning: 'bg-yellow-900/30 text-yellow-400 border border-yellow-500/20',
    error: 'bg-red-900/30 text-red-400 border border-red-500/20',
    cyan: 'bg-primary/10 text-primary border border-primary/30',
    gold: 'bg-secondary/10 text-secondary border border-secondary/30',
  }

  return (
    <span className={`inline-block rounded px-2 py-1 text-xs font-mono ${variantStyles[variant]}`}>
      {label}
    </span>
  )
}
