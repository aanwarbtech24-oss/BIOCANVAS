import { cn } from '@/lib/cn'

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg'
  text?: string
  fullscreen?: boolean
}

/**
 * LoadingSpinner Component
 * Used for lazy-loaded components and async operations
 */
export function LoadingSpinner({
  size = 'md',
  text = 'Loading...',
  fullscreen = false,
}: LoadingSpinnerProps) {
  const sizes = {
    sm: 'w-6 h-6 border-2',
    md: 'w-10 h-10 border-[3px]',
    lg: 'w-16 h-16 border-4',
  }

  const spinnerElement = (
    <div className="flex flex-col items-center gap-4">
      <div
        className={cn(
          'border-surface-border border-t-primary rounded-full animate-spin',
          sizes[size]
        )}
      />
      {text && <p className="text-sm text-muted-foreground">{text}</p>}
    </div>
  )

  if (fullscreen) {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-background/50 backdrop-blur-sm">
        {spinnerElement}
      </div>
    )
  }

  return (
    <div className="flex items-center justify-center py-12">
      {spinnerElement}
    </div>
  )
}

/**
 * Suspend Fallback for React.lazy()
 */
export function LazyLoadingFallback() {
  return <LoadingSpinner text="Loading component..." />
}
