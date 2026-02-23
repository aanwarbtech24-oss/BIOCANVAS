import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Toaster } from 'sonner'
import { Navbar } from '@/components/layout/Navbar'
import { VisualizePage } from '@/components/features/VisualizePage'
import { DockingPipeline } from '@/components/features/DockingPipeline'
import { ErrorBoundary } from '@/components/ErrorBoundary'
import { useUIStore } from '@/stores/useUIStore'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { staleTime: 30_000, retry: 2 },
  },
})

function PageContent() {
  const activeTab = useUIStore((s) => s.activeTab)
  return activeTab === 'visualize' ? <VisualizePage /> : <DockingPipeline />
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <div className="min-h-screen bg-background text-foreground">
        <Navbar />
        <main className="mx-auto max-w-5xl px-4 py-10 sm:px-6 lg:px-8">
          <ErrorBoundary>
            <PageContent />
          </ErrorBoundary>
        </main>
      </div>
      <Toaster
        theme="dark"
        position="bottom-right"
        richColors
        closeButton
        toastOptions={{
          classNames: {
            toast: 'bg-surface border border-surface-border',
            title: 'text-white',
            description: 'text-muted-foreground',
          },
        }}
      />
    </QueryClientProvider>
  )
}
