import { useCallback, useEffect } from 'react'
import { useSubmitDocking, useDockingJob } from '@/hooks/useDockingJob'
import type { SelectedJobData } from '@/hooks/useDockingJob'
import { cn } from '@/lib/cn'
import { toast } from 'sonner'
import type { Protein, Ligand } from '@/types/api'
import { ElapsedTimer } from '../pipeline/ElapsedTimer'

import {
  FlaskConical,
  Atom,
  Play,
  BrainCircuit,
  Zap,
  Loader2,
  AlertTriangle,
  RotateCcw,
  Clock,
  Activity,
  CheckCircle2,
  XCircle,
} from 'lucide-react'

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------

export interface Step3Props {
  /** Step completion flags from parent */
  step1Complete: boolean
  step2Complete: boolean
  /** What's being docked — for summary cards */
  selectedProtein: Protein | null
  customPdbName: string | null
  selectedLigand: Ligand | null
  ligandSmiles: string | null
  /** The PDB viewer data (string) — needed to create the File for submission */
  viewerData: string | null
  /** Docking job id (lifted to parent so it persists across step changes) */
  dockingJobId: string | null
  setDockingJobId: (id: string | null) => void
  /** Navigate to next step */
  goNext: () => void
}

// ---------------------------------------------------------------------------
// Step 3 — Run Docking
// ---------------------------------------------------------------------------

export function Step3_DockingRun({
  step1Complete,
  step2Complete,
  selectedProtein,
  customPdbName,
  selectedLigand,
  ligandSmiles,
  viewerData,
  dockingJobId,
  setDockingJobId,
  goNext,
}: Step3Props) {
  // ── Data hooks ──────────────────────────────────────────────────────
  const submitDocking = useSubmitDocking()
  const jobQuery = useDockingJob(dockingJobId)
  const jobData: SelectedJobData | null | undefined = jobQuery.data
  const jobStatus = jobData?.status ?? null

  // ── Derived state ───────────────────────────────────────────────────
  const isReadyToDock = step1Complete && step2Complete && !dockingJobId && !submitDocking.isPending
  const dockingStatus: string = submitDocking.isPending
    ? 'Uploading files & submitting…'
    : jobStatus === 'queued'
      ? 'Queued — waiting for server…'
      : jobStatus === 'running'
        ? 'Simulation running…'
        : jobStatus === 'completed'
          ? 'Docking complete!'
          : jobStatus === 'failed'
            ? 'Docking failed'
            : 'Ready to dock'

  // ── Handlers ────────────────────────────────────────────────────────
  const handleRunDocking = useCallback(() => {
    if (!viewerData || !ligandSmiles) {
      toast.error('Missing protein or ligand data')
      return
    }
    const pdbBlob = new Blob([viewerData], { type: 'chemical/x-pdb' })
    const pdbFile = new File([pdbBlob], 'protein.pdb', { type: 'chemical/x-pdb' })
    submitDocking.mutate(
      { file: pdbFile, smiles: ligandSmiles },
      { onSuccess: (data) => setDockingJobId(data.job_id) },
    )
  }, [viewerData, ligandSmiles, submitDocking, setDockingJobId])

  const handleResetDocking = useCallback(() => {
    setDockingJobId(null)
    submitDocking.reset()
  }, [setDockingJobId, submitDocking])

  // ── Auto-toast on terminal states ───────────────────────────────────
  useEffect(() => {
    if (jobStatus === 'completed') {
      toast.success('Docking complete!', {
        description: jobData?.result?.affinity
          ? `Binding affinity: ${jobData.result.affinity} kcal/mol`
          : 'Results are ready for review.',
      })
    }
    if (jobStatus === 'failed') {
      toast.error('Docking failed', {
        description: jobData?.error ?? 'Check the server logs for details.',
      })
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [jobStatus])

  // ── JSX ─────────────────────────────────────────────────────────────
  return (
    <div className="min-h-[400px] animate-in fade-in slide-in-from-right-4 duration-300">
      <div className="mb-5">
        <h2 className="text-xl font-semibold text-white">Run Docking</h2>
        <p className="mt-1 text-sm text-muted-foreground">
          Submit your docking job and monitor its progress
        </p>
      </div>

      {/* Summary cards: what's being docked */}
      <div className="mb-6 grid grid-cols-1 gap-3 sm:grid-cols-2">
        {/* Protein card */}
        <div className="flex items-start gap-3 rounded-xl border border-surface-border bg-surface/40 p-4">
          <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-primary/10">
            <FlaskConical className="h-4.5 w-4.5 text-primary" />
          </div>
          <div className="min-w-0">
            <p className="text-[11px] font-semibold uppercase tracking-wider text-muted">Protein</p>
            <p className="mt-0.5 truncate text-sm font-medium text-white">
              {selectedProtein?.name ?? customPdbName ?? 'Custom PDB'}
            </p>
            {selectedProtein && (
              <p className="mt-0.5 font-mono text-[11px] text-muted-foreground">
                {selectedProtein.uniprot_id}
              </p>
            )}
          </div>
        </div>

        {/* Ligand card */}
        <div className="flex items-start gap-3 rounded-xl border border-surface-border bg-surface/40 p-4">
          <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-secondary/10">
            <Atom className="h-4.5 w-4.5 text-secondary" />
          </div>
          <div className="min-w-0">
            <p className="text-[11px] font-semibold uppercase tracking-wider text-muted">Ligand</p>
            <p className="mt-0.5 truncate text-sm font-medium text-white">
              {selectedLigand?.name ?? 'Custom SMILES'}
            </p>
            <p className="mt-0.5 truncate font-mono text-[11px] text-muted-foreground">
              {ligandSmiles && ligandSmiles.length > 40 ? ligandSmiles.slice(0, 40) + '…' : ligandSmiles}
            </p>
          </div>
        </div>
      </div>

      {/* Pre-submission state: launch button */}
      {!dockingJobId && !submitDocking.isPending && !submitDocking.isError && (
        <div className="rounded-xl border border-surface-border bg-surface/40 p-6 text-center">
          <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-primary/10 ring-1 ring-primary/20">
            <Zap className="h-8 w-8 text-primary" />
          </div>
          <h3 className="text-base font-semibold text-white">Ready to Dock</h3>
          <p className="mx-auto mt-2 max-w-md text-sm text-muted-foreground">
            Your protein and ligand are prepared. Submit the job to run molecular
            docking via AutoDock Vina on the server.
          </p>
          <button
            type="button"
            onClick={handleRunDocking}
            disabled={!isReadyToDock}
            className={cn(
              'mt-6 inline-flex items-center gap-2 rounded-lg px-6 py-2.5 text-sm font-semibold transition-all active:scale-[0.98]',
              isReadyToDock
                ? 'bg-primary text-white shadow-lg shadow-primary/25 hover:bg-primary/90 hover:shadow-primary/35'
                : 'cursor-not-allowed bg-surface-highlight text-muted',
            )}
          >
            <Play className="h-4 w-4" />
            Run Docking
          </button>
        </div>
      )}

      {/* Submitting state */}
      {submitDocking.isPending && (
        <div className="rounded-xl border border-amber-500/30 bg-amber-500/5 p-6 text-center">
          <Loader2 className="mx-auto mb-3 h-10 w-10 animate-spin text-amber-400" />
          <p className="text-sm font-medium text-amber-300">{dockingStatus}</p>
          <p className="mt-1 text-xs text-muted-foreground animate-pulse">
            Sending PDB file and SMILES to the server
          </p>
        </div>
      )}

      {/* Submission error */}
      {submitDocking.isError && !dockingJobId && (
        <div className="rounded-xl border border-destructive/30 bg-destructive/5 p-6 text-center">
          <XCircle className="mx-auto mb-3 h-10 w-10 text-destructive" />
          <p className="text-sm font-medium text-destructive">Submission Failed</p>
          <p className="mx-auto mt-1 max-w-sm text-xs text-muted-foreground">
            {(submitDocking.error as any)?.response?.data?.detail ??
              'Could not submit the docking job. Check that the backend is running.'}
          </p>
          <button
            type="button"
            onClick={handleRunDocking}
            className="mt-4 inline-flex items-center gap-1.5 rounded-lg border border-destructive/30
                       bg-destructive/10 px-4 py-2 text-xs font-medium text-destructive
                       transition-colors hover:bg-destructive/20"
          >
            <RotateCcw className="h-3 w-3" /> Retry
          </button>
        </div>
      )}

      {/* Job progress tracker */}
      {dockingJobId && (
        <div className="space-y-4">
          {/* Status bar */}
          <div
            className={cn(
              'rounded-xl border p-5',
              jobStatus === 'completed'
                ? 'border-emerald-500/30 bg-emerald-500/5'
                : jobStatus === 'failed'
                  ? 'border-destructive/30 bg-destructive/5'
                  : 'border-amber-500/30 bg-amber-500/5',
            )}
          >
            <div className="flex items-center gap-3">
              {/* Status icon */}
              {jobStatus === 'completed' ? (
                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-emerald-500/20">
                  <CheckCircle2 className="h-5 w-5 text-emerald-400" />
                </div>
              ) : jobStatus === 'failed' ? (
                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-destructive/20">
                  <XCircle className="h-5 w-5 text-destructive" />
                </div>
              ) : (
                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-amber-500/20">
                  <Loader2 className="h-5 w-5 animate-spin text-amber-400" />
                </div>
              )}

              {/* Status text */}
              <div className="flex-1">
                <p
                  className={cn(
                    'text-sm font-semibold',
                    jobStatus === 'completed'
                      ? 'text-emerald-300'
                      : jobStatus === 'failed'
                        ? 'text-destructive'
                        : 'text-amber-300',
                  )}
                >
                  {dockingStatus}
                </p>
                <p className="mt-0.5 font-mono text-[11px] text-muted-foreground">
                  Job ID: {dockingJobId.slice(0, 8)}…
                </p>
              </div>

              {/* Elapsed timer */}
              {jobData?.submitted_at && (
                <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
                  <Clock className="h-3.5 w-3.5" />
                  <ElapsedTimer startTs={jobData.submitted_at} running={jobStatus === 'queued' || jobStatus === 'running'} />
                </div>
              )}
            </div>

            {/* Error message */}
            {jobStatus === 'failed' && jobData?.error && (
              <div className="mt-3 flex items-start gap-2 rounded-lg bg-destructive/10 px-3 py-2">
                <AlertTriangle className="mt-0.5 h-3.5 w-3.5 shrink-0 text-destructive" />
                <p className="text-xs leading-relaxed text-destructive/90">{jobData.error}</p>
              </div>
            )}

            {/* Progress stages */}
            <div className="mt-4 flex gap-2">
              {(['queued', 'running', 'completed'] as const).map((stage) => {
                const stageIdx = stage === 'queued' ? 0 : stage === 'running' ? 1 : 2
                const currentIdx = jobStatus === 'queued' ? 0 : jobStatus === 'running' ? 1 : jobStatus === 'completed' ? 2 : -1
                const isActive = stageIdx === currentIdx
                const isDone = stageIdx < currentIdx
                const isFailed = jobStatus === 'failed'

                return (
                  <div key={stage} className="flex flex-1 flex-col items-center gap-1.5">
                    <div
                      className={cn(
                        'h-1.5 w-full rounded-full transition-all duration-500',
                        isDone
                          ? 'bg-emerald-500'
                          : isActive && !isFailed
                            ? 'bg-amber-500 animate-pulse'
                            : isFailed && isActive
                              ? 'bg-destructive'
                              : 'bg-surface-highlight',
                      )}
                    />
                    <span className="text-[10px] uppercase tracking-wider text-muted-foreground">
                      {stage}
                    </span>
                  </div>
                )
              })}
            </div>
          </div>

          {/* Quick results preview when completed */}
          {jobStatus === 'completed' && jobData && (
            <div className="rounded-xl border border-emerald-500/20 bg-surface/40 p-5">
              <div className="mb-3 flex items-center justify-between">
                <h4 className="flex items-center gap-2 text-sm font-semibold text-white">
                  <Activity className="h-4 w-4 text-emerald-400" />
                  Quick Results
                </h4>
                {jobData.result?.simulated && (
                  <span className="inline-flex items-center gap-1 rounded-full border border-amber-500/30 bg-amber-500/10 px-2.5 py-0.5 text-[10px] font-semibold uppercase tracking-wider text-amber-400">
                    <Zap className="h-2.5 w-2.5" /> Simulated
                  </span>
                )}
              </div>
              <div className="grid grid-cols-3 gap-3">
                <div className="rounded-lg bg-surface-highlight/40 px-3 py-2.5 text-center">
                  <p className="text-[10px] font-semibold uppercase tracking-wider text-muted">Affinity</p>
                  <p className="mt-1 text-lg font-bold text-emerald-400">
                    {jobData.result?.affinity != null ? `${jobData.result.affinity}` : '—'}
                  </p>
                  <p className="text-[10px] text-muted-foreground">kcal/mol</p>
                </div>
                <div className="rounded-lg bg-surface-highlight/40 px-3 py-2.5 text-center">
                  <p className="text-[10px] font-semibold uppercase tracking-wider text-muted">RMSD</p>
                  <p className="mt-1 text-lg font-bold text-sky-400">
                    {jobData.result?.rmsd != null ? `${jobData.result.rmsd}` : '—'}
                  </p>
                  <p className="text-[10px] text-muted-foreground">Å</p>
                </div>
                <div className="rounded-lg bg-surface-highlight/40 px-3 py-2.5 text-center">
                  <p className="text-[10px] font-semibold uppercase tracking-wider text-muted">Poses</p>
                  <p className="mt-1 text-lg font-bold text-violet-400">
                    {jobData.result?.poses != null ? `${jobData.result.poses}` : '—'}
                  </p>
                  <p className="text-[10px] text-muted-foreground">found</p>
                </div>
              </div>

              <button
                type="button"
                onClick={goNext}
                className="mt-4 inline-flex w-full items-center justify-center gap-2 rounded-lg
                           bg-emerald-600 py-2.5 text-sm font-semibold text-white
                           shadow-lg shadow-emerald-600/20 transition-all hover:bg-emerald-500
                           active:scale-[0.98]"
              >
                <BrainCircuit className="h-4 w-4" />
                View Full Results &amp; AI Analysis →
              </button>
            </div>
          )}

          {/* Re-run button on failure */}
          {jobStatus === 'failed' && (
            <div className="flex justify-center gap-3">
              <button
                type="button"
                onClick={handleResetDocking}
                className="inline-flex items-center gap-1.5 rounded-lg border border-surface-border
                           bg-surface/60 px-4 py-2 text-xs font-medium text-muted-foreground
                           transition-colors hover:bg-surface hover:text-white"
              >
                <RotateCcw className="h-3 w-3" /> Reset &amp; Try Again
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
