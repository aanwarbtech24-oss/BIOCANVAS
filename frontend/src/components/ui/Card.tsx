import React from 'react'
import { cn } from '@/lib/cn'

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'glass' | 'bordered'
}

export const Card = React.forwardRef<HTMLDivElement, CardProps>(
  ({ className, variant = 'default', ...props }, ref) => {
    const variants = {
      default: 'bg-surface border border-surface-border rounded-lg',
      glass: 'bg-surface/50 backdrop-blur-sm border border-surface-border/50 rounded-lg',
      bordered: 'bg-surface border-2 border-primary rounded-lg',
    }

    return (
      <div
        className={cn(variants[variant], className)}
        ref={ref}
        {...props}
      />
    )
  }
)

Card.displayName = 'Card'

export const CardContent = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div
      className={cn('p-6', className)}
      ref={ref}
      {...props}
    />
  )
)

CardContent.displayName = 'CardContent'
