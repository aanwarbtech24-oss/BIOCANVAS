import { Beaker, Eye, FlaskConical } from 'lucide-react'
import { useUIStore } from '@/stores/useUIStore'
import { useHealthCheck } from '@/hooks/useDockingJob'
import { cn } from '@/lib/cn'

const TABS = [
  { id: 'visualize', label: 'Visualize', icon: Eye },
  { id: 'docking',   label: 'Docking',   icon: FlaskConical },
] as const

export function Navbar() {
  const { activeTab, setActiveTab } = useUIStore()
  const health = useHealthCheck()
  const isOnline = health.data?.status === 'active'

  return (
    <nav className="sticky top-0 z-50 bg-surface/80 backdrop-blur-sm border-b border-surface-border">
      <div className="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo & Brand */}
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center">
              <Beaker className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-lg font-bold text-white tracking-tight">BIOCANVAS</h1>
              <p className="text-[10px] font-semibold uppercase tracking-widest text-muted-foreground">Molecular Docking Platform</p>
            </div>
          </div>

          {/* Tabs */}
          <div className="flex items-center gap-1">
            {TABS.map(({ id, label, icon: Icon }) => (
              <button
                key={id}
                type="button"
                onClick={() => setActiveTab(id)}
                className={cn(
                  'inline-flex items-center gap-1.5 rounded-lg px-4 py-2 text-sm font-medium transition-all',
                  activeTab === id
                    ? 'bg-primary/15 text-primary border border-primary/30'
                    : 'text-muted-foreground hover:text-white hover:bg-surface-highlight',
                )}
              >
                <Icon className="h-4 w-4" />
                {label}
              </button>
            ))}
          </div>

          {/* Status pill — live health check */}
          <div className="hidden sm:flex items-center gap-2 rounded-full border border-surface-border bg-surface-highlight/60 px-3 py-1.5">
            <span className="relative flex h-2 w-2">
              {isOnline && <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-success opacity-75" />}
              <span className={cn(
                'relative inline-flex h-2 w-2 rounded-full',
                isOnline ? 'bg-success' : 'bg-destructive',
              )} />
            </span>
            <span className="text-[11px] font-medium text-muted-foreground">
              {isOnline ? 'Server Online' : 'Server Offline'}
            </span>
          </div>
        </div>
      </div>
    </nav>
  )
}
