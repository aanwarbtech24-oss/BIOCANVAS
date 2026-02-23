import { cn } from '@/lib/cn'
import {
  Check,
  Lock,
  FlaskConical,
  Atom,
  Play,
  BrainCircuit,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react'

// ---------------------------------------------------------------------------
// Step metadata
// ---------------------------------------------------------------------------

export type StepStatus = 'completed' | 'active' | 'locked'

export const STEPS = [
  { number: 1, title: 'Protein Target',   icon: FlaskConical },
  { number: 2, title: 'Ligand Selection', icon: Atom },
  { number: 3, title: 'Run Docking',      icon: Play },
  { number: 4, title: 'Results & AI',     icon: BrainCircuit },
] as const

// ---------------------------------------------------------------------------
// Horizontal progress bar (top of page)
// ---------------------------------------------------------------------------

export function ProgressBar({
  activeStep,
  maxUnlocked,
  onStepClick,
}: {
  activeStep: number
  maxUnlocked: number
  onStepClick: (step: number) => void
}) {
  return (
    <div className="mb-8">
      <div className="flex items-center justify-between">
        {STEPS.map(({ number, title, icon: Icon }, idx) => {
          const status: StepStatus =
            number < maxUnlocked ? 'completed' : number === maxUnlocked ? 'active' : 'locked'
          const isCurrent = number === activeStep
          const clickable = number <= maxUnlocked

          return (
            <div key={number} className="flex items-center flex-1 last:flex-none">
              <button
                type="button"
                disabled={!clickable}
                onClick={() => clickable && onStepClick(number)}
                className={cn(
                  'group flex flex-col items-center gap-1.5 transition-all',
                  clickable ? 'cursor-pointer' : 'cursor-not-allowed',
                )}
              >
                <div
                  className={cn(
                    'flex h-10 w-10 items-center justify-center rounded-full border-2 transition-all duration-300',
                    status === 'completed'
                      ? 'border-emerald-500 bg-emerald-500/20 text-emerald-400'
                      : isCurrent
                        ? 'border-primary bg-primary/15 text-primary shadow-lg shadow-primary/10 ring-4 ring-primary/10'
                        : 'border-surface-border bg-surface-highlight text-muted',
                  )}
                >
                  {status === 'completed' ? (
                    <Check className="h-4 w-4" />
                  ) : status === 'locked' ? (
                    <Lock className="h-3.5 w-3.5" />
                  ) : (
                    <Icon className="h-4 w-4" />
                  )}
                </div>
                <span
                  className={cn(
                    'text-[11px] font-semibold leading-none transition-colors',
                    isCurrent ? 'text-white' : status === 'completed' ? 'text-emerald-400' : 'text-muted',
                  )}
                >
                  {title}
                </span>
              </button>

              {idx < STEPS.length - 1 && (
                <div className="relative mx-2 h-0.5 flex-1 rounded-full bg-surface-border/60 mb-5">
                  <div
                    className={cn(
                      'absolute inset-y-0 left-0 rounded-full transition-all duration-500',
                      number < maxUnlocked ? 'bg-emerald-500/60 w-full' : 'bg-surface-border/60 w-0',
                    )}
                  />
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}

// ---------------------------------------------------------------------------
// Bottom navigation bar (fixed)
// ---------------------------------------------------------------------------

export function BottomNav({
  activeStep,
  maxUnlocked,
  canProceed,
  onBack,
  onNext,
}: {
  activeStep: number
  maxUnlocked: number
  canProceed: boolean
  onBack: () => void
  onNext: () => void
}) {
  const isFirst = activeStep === 1
  const isLast = activeStep === STEPS.length
  const nextDisabled = !canProceed || activeStep >= maxUnlocked

  return (
    <div className="fixed bottom-0 left-0 right-0 z-40 border-t border-surface-border bg-surface/90 backdrop-blur-md">
      <div className="mx-auto flex max-w-5xl items-center justify-between px-4 py-3 sm:px-6 lg:px-8">
        <button
          type="button"
          disabled={isFirst}
          onClick={onBack}
          className={cn(
            'inline-flex items-center gap-2 rounded-xl px-5 py-2.5 text-sm font-medium transition-all',
            isFirst
              ? 'text-muted cursor-not-allowed'
              : 'text-muted-foreground hover:text-white hover:bg-surface-highlight',
          )}
        >
          <ChevronLeft className="h-4 w-4" />
          Back
        </button>

        <span className="text-xs font-bold uppercase tracking-widest text-muted">
          Step {activeStep} of {STEPS.length}
        </span>

        {isLast ? (
          <span className="w-[100px]" />
        ) : (
          <button
            type="button"
            disabled={nextDisabled}
            onClick={onNext}
            className={cn(
              'inline-flex items-center gap-2 rounded-xl px-5 py-2.5 text-sm font-semibold transition-all',
              nextDisabled
                ? 'bg-surface-highlight text-muted cursor-not-allowed'
                : 'bg-primary text-white hover:bg-primary/90 shadow-lg shadow-primary/20',
            )}
          >
            Next
            <ChevronRight className="h-4 w-4" />
          </button>
        )}
      </div>
    </div>
  )
}
