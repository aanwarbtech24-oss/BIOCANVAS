import { useState, useMemo, useCallback, memo } from 'react'
import { useDockingStore } from '@/stores/useDockingStore'
import { useDockingJob } from '@/hooks/useDockingJob'
import { DockingViewer3D } from '@/components/science/DockingViewer3D'
import { cn } from '@/lib/cn'
import type { DockingPose, LipinskiProfile } from '@/types/api'

import {
  Sparkles,
  FlaskConical,
  Atom,
  Activity,
  ArrowUpDown,
  ArrowUp,
  ArrowDown,
  Zap,
  ShieldCheck,
  ShieldAlert,
  Layers,
  TrendingDown,
  AlertTriangle,
} from 'lucide-react'

// ---------------------------------------------------------------------------
// Step 4 — Results Dashboard (Wired to Zustand Store)
// ---------------------------------------------------------------------------

export function ResultsStep() {
  // ── Zustand Store State ───────────────────────────────────────────────
  const {
    customPdbData,
    selectedProtein,
    customPdbName,
    selectedLigand,
    dockingJobId,
    proteinPdbData,
  } = useDockingStore()

  // ── Job Data from API ────────────────────────────────────────────────
  const jobQuery = useDockingJob(dockingJobId)
  const jobData = jobQuery.data

  // ── Derived Data ────────────────────────────────────────────────────
  const poses = jobData?.dockingPoses ?? []
  const lipinski = jobData?.lipinski ?? null
  const activePoseIndex = useDockingStore((s) => s.activePoseIndex)
  const setActivePose = useDockingStore((s) => s.setActivePose)

  const activePose = poses[activePoseIndex] ?? poses[0] ?? null
  const isSimulated = jobData?.result?.simulated ?? false
  const ligandPdbqt = jobData?.output_pdbqt ?? null
  const activeInteractions = activePose?.interactions ?? null

  const proteinLabel = selectedProtein?.name ?? customPdbName ?? 'Protein'
  const ligandLabel = selectedLigand?.name ?? 'Custom SMILES'

  // Get viewer data (protein PDB) — prefer custom upload, then AlphaFold fetch
  const viewerData = customPdbData ?? proteinPdbData

  return (
    <div className="min-h-[400px] animate-in fade-in slide-in-from-right-4 duration-300">
      {/* ── Top Row: Run Summary Header ──────────────────────────────── */}
      <ResultsHeader
        proteinLabel={proteinLabel}
        ligandLabel={ligandLabel}
        poseCount={poses.length}
        isSimulated={isSimulated}
      />

      {/* ── SIMULATED WARNING BANNER ─────────────────────────────── */}
      {isSimulated && (
        <div className="mt-4 rounded-xl border-2 border-amber-500/40 bg-amber-500/10 px-5 py-4">
          <div className="flex items-center gap-3">
            <AlertTriangle className="h-6 w-6 shrink-0 text-amber-400" />
            <div>
              <p className="text-lg font-bold uppercase tracking-wide text-amber-400">
                Simulated Results — AutoDock Vina Not Installed
              </p>
              <p className="mt-1 text-sm text-amber-300/70">
                These docking scores and poses are <span className="font-semibold text-amber-300">artificially generated</span> for
                demonstration purposes only. Install AutoDock Vina to get real molecular docking results.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* ── Bento Grid ───────────────────────────────────────────────── */}
      <div className="mt-5 grid grid-cols-12 gap-4">
        {/* Main Left — Hero (3D Docked Complex Viewer) */}
        <div className="col-span-12 lg:col-span-8">
          <DockingViewer3D
            proteinPdb={viewerData}
            ligandPdbqt={ligandPdbqt}
            activePoseIndex={activePoseIndex}
            interactions={activeInteractions}
            height={600}
          />
        </div>

        {/* Main Right — Data Column */}
        <div className="col-span-12 space-y-4 lg:col-span-4">
          {/* Lead Card: Binding Affinity + LE */}
          <LeadCard pose={activePose} poseIndex={activePoseIndex} isSimulated={isSimulated} />

          {/* Lipinski Pulse */}
          <LipinskiPulse lipinski={lipinski} />

          {/* AI Analysis placeholder */}
          <AIAnalysisTeaser />
        </div>

        {/* Full-Width: Pose Table */}
        <div className="col-span-12">
          <PoseTable
            poses={poses}
            activePoseIndex={activePoseIndex}
            onSelectPose={setActivePose}
          />
        </div>
      </div>
    </div>
  )
}

// ═══════════════════════════════════════════════════════════════════════════
//  Sub-Components
// ═══════════════════════════════════════════════════════════════════════════

// ---------------------------------------------------------------------------
// Results Header
// ---------------------------------------------------------------------------

const ResultsHeader = memo(function ResultsHeader({
  proteinLabel,
  ligandLabel,
  poseCount,
  isSimulated,
}: {
  proteinLabel: string
  ligandLabel: string
  poseCount: number
  isSimulated: boolean
}) {
  return (
    <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h2 className="text-xl font-semibold text-white">Docking Results</h2>
        <p className="mt-1 flex items-center gap-2 text-sm text-muted-foreground">
          <FlaskConical className="h-3.5 w-3.5 text-primary" />
          <span className="font-medium text-white">{ligandLabel}</span>
          <span>docked into</span>
          <span className="font-medium text-white">{proteinLabel}</span>
        </p>
      </div>

      <div className="flex items-center gap-2">
        {isSimulated && (
          <span className="inline-flex items-center gap-1.5 rounded-full border-2 border-amber-500/40 bg-amber-500/10 px-3.5 py-1.5 text-xs font-bold uppercase tracking-wider text-amber-400">
            <Zap className="h-3.5 w-3.5" /> Simulated
          </span>
        )}
        <span className="inline-flex items-center gap-1.5 rounded-full border border-surface-border bg-surface-highlight/60 px-3 py-1 text-xs text-muted-foreground">
          <Layers className="h-3 w-3" />
          {poseCount} pose{poseCount !== 1 ? 's' : ''}
        </span>
      </div>
    </div>
  )
})

ResultsHeader.displayName = 'ResultsHeader'

// ---------------------------------------------------------------------------
// Lead Card — Binding Affinity + Ligand Efficiency
// ---------------------------------------------------------------------------

const LeadCard = memo(function LeadCard({ pose, poseIndex, isSimulated }: { pose: DockingPose | null; poseIndex: number; isSimulated: boolean }) {
  if (!pose) {
    return (
      <div className="rounded-2xl border border-surface-border bg-surface/40 p-5 text-center">
        <p className="text-sm text-muted-foreground">No pose data available</p>
      </div>
    )
  }

  // Color coding: more negative = stronger binding = greener
  const affinityColor =
    pose.affinity <= -8
      ? 'text-emerald-400'
      : pose.affinity <= -6
        ? 'text-sky-400'
        : pose.affinity <= -4
          ? 'text-amber-400'
          : 'text-red-400'

  const leColor =
    pose.ligand_efficiency <= -0.4
      ? 'text-emerald-400'
      : pose.ligand_efficiency <= -0.25
        ? 'text-sky-400'
        : 'text-amber-400'

  return (
    <div className="relative overflow-hidden rounded-2xl border border-surface-border bg-gradient-to-br from-surface/60 to-primary/5">
      {/* Simulated watermark */}
      {isSimulated && (
        <div className="pointer-events-none absolute inset-0 z-10 flex items-center justify-center">
          <span className="-rotate-12 select-none text-3xl font-black uppercase tracking-[0.25em] text-amber-500/15">
            SIMULATED
          </span>
        </div>
      )}
      {/* Header */}
      <div className="flex items-center justify-between border-b border-surface-border/50 px-5 py-3">
        <div className="flex items-center gap-2">
          <Activity className="h-4 w-4 text-primary" />
          <span className="text-xs font-bold uppercase tracking-wider text-muted">Lead Compound</span>
        </div>
        <span className="rounded-full bg-primary/10 px-2.5 py-0.5 text-[10px] font-bold text-primary">
          Pose #{poseIndex + 1}
        </span>
      </div>

      {/* Body */}
      <div className="px-5 py-4">
        {/* Binding Affinity — hero number */}
        <div className="text-center">
          <p className="text-[10px] font-semibold uppercase tracking-widest text-muted">Binding Affinity</p>
          <p className={cn('mt-1 text-4xl font-extrabold tabular-nums tracking-tight', affinityColor)}>
            {pose.affinity.toFixed(1)}
          </p>
          <p className="mt-0.5 text-xs text-muted-foreground">kcal/mol</p>
        </div>

        {/* Divider */}
        <div className="my-3 h-px bg-surface-border/50" />

        {/* Ligand Efficiency + RMSD row */}
        <div className="grid grid-cols-2 gap-3">
          <div className="rounded-lg bg-surface-highlight/40 px-3 py-2 text-center">
            <p className="text-[9px] font-semibold uppercase tracking-wider text-muted">Ligand Eff.</p>
            <p className={cn('mt-0.5 text-lg font-bold tabular-nums', leColor)}>
              {pose.ligand_efficiency.toFixed(2)}
            </p>
            <p className="text-[9px] text-muted">kcal/mol/HA</p>
          </div>
          <div className="rounded-lg bg-surface-highlight/40 px-3 py-2 text-center">
            <p className="text-[9px] font-semibold uppercase tracking-wider text-muted">RMSD (UB)</p>
            <p className="mt-0.5 text-lg font-bold tabular-nums text-sky-400">
              {pose.rmsd_ub.toFixed(1)}
            </p>
            <p className="text-[9px] text-muted">Å</p>
          </div>
        </div>
      </div>
    </div>
  )
})

LeadCard.displayName = 'LeadCard'

// ---------------------------------------------------------------------------
// Lipinski Pulse — RO5 Badge Row
// ---------------------------------------------------------------------------

const LIPINSKI_RULES: {
  key: keyof Pick<LipinskiProfile, 'mw' | 'logp' | 'hbd' | 'hba'>
  label: string
  threshold: number
  comparator: 'lte' | 'gte'
  unit: string
}[] = [
  { key: 'mw',   label: 'MW',   threshold: 500, comparator: 'lte', unit: 'Da' },
  { key: 'logp', label: 'LogP', threshold: 5,   comparator: 'lte', unit: '' },
  { key: 'hbd',  label: 'HBD',  threshold: 5,   comparator: 'lte', unit: '' },
  { key: 'hba',  label: 'HBA',  threshold: 10,  comparator: 'lte', unit: '' },
]

const LipinskiPulse = memo(function LipinskiPulse({ lipinski }: { lipinski: LipinskiProfile | null }) {
  if (!lipinski) {
    return (
      <div className="rounded-2xl border border-surface-border bg-surface/40 p-5 text-center">
        <p className="text-sm text-muted-foreground">Lipinski data unavailable</p>
      </div>
    )
  }

  const allPass = lipinski.pass_rule_of_five

  return (
    <div className="overflow-hidden rounded-2xl border border-surface-border bg-surface/40">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-surface-border/50 px-5 py-3">
        <div className="flex items-center gap-2">
          {allPass ? (
            <ShieldCheck className="h-4 w-4 text-emerald-400" />
          ) : (
            <ShieldAlert className="h-4 w-4 text-amber-400" />
          )}
          <span className="text-xs font-bold uppercase tracking-wider text-muted">Rule of Five</span>
        </div>
        <span
          className={cn(
            'rounded-full px-2.5 py-0.5 text-[10px] font-bold uppercase',
            allPass
              ? 'bg-emerald-500/10 text-emerald-400'
              : 'bg-amber-500/10 text-amber-400',
          )}
        >
          {allPass ? 'PASS' : 'VIOLATION'}
        </span>
      </div>

      {/* Pills */}
      <div className="grid grid-cols-2 gap-2 p-4">
        {LIPINSKI_RULES.map((rule) => {
          const value = lipinski[rule.key]
          const passes = rule.comparator === 'lte' ? value <= rule.threshold : value >= rule.threshold

          return (
            <div
              key={rule.key}
              className={cn(
                'flex items-center justify-between rounded-lg border px-3 py-2',
                passes
                  ? 'border-emerald-500/20 bg-emerald-500/5'
                  : 'border-red-500/20 bg-red-500/5',
              )}
            >
              <div>
                <p className="text-[10px] font-bold uppercase tracking-wider text-muted">
                  {rule.label}
                </p>
                <p
                  className={cn(
                    'text-sm font-bold tabular-nums',
                    passes ? 'text-emerald-400' : 'text-red-400',
                  )}
                >
                  {typeof value === 'number' ? (rule.key === 'logp' || rule.key === 'mw' ? value.toFixed(1) : value) : '—'}
                </p>
              </div>
              <span
                className={cn(
                  'text-[9px] font-semibold',
                  passes ? 'text-emerald-500/60' : 'text-red-500/60',
                )}
              >
                {passes ? '✓' : '✗'} {rule.comparator === 'lte' ? '≤' : '≥'} {rule.threshold}
              </span>
            </div>
          )
        })}
      </div>
    </div>
  )
})

LipinskiPulse.displayName = 'LipinskiPulse'

// ---------------------------------------------------------------------------
// AI Analysis Teaser
// ---------------------------------------------------------------------------

const AIAnalysisTeaser = memo(function AIAnalysisTeaser() {
  return (
    <div className="overflow-hidden rounded-2xl border border-surface-border bg-gradient-to-br from-surface/60 to-secondary/10">
      <div className="px-5 py-6 text-center">
        <div className="mx-auto mb-3 flex h-10 w-10 items-center justify-center rounded-xl bg-secondary/10 ring-1 ring-secondary/20">
          <Sparkles className="h-5 w-5 text-secondary" />
        </div>
        <h4 className="text-sm font-semibold text-secondary-foreground">AI Binding Analysis</h4>
        <p className="mx-auto mt-1.5 max-w-[220px] text-[11px] leading-relaxed text-muted-foreground">
          GPT-powered binding interpretation and interaction analysis.
        </p>
        <div className="mt-3 inline-flex items-center gap-1.5 rounded-full border border-secondary/20 bg-secondary/5 px-3 py-1">
          <span className="relative flex h-1.5 w-1.5">
            <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-secondary opacity-75" />
            <span className="relative inline-flex h-1.5 w-1.5 rounded-full bg-secondary" />
          </span>
          <span className="text-[10px] font-semibold text-secondary">Coming Soon</span>
        </div>
      </div>
    </div>
  )
})

AIAnalysisTeaser.displayName = 'AIAnalysisTeaser'

// ---------------------------------------------------------------------------
// SortIcon — extracted from PoseTable for stable reference
// ---------------------------------------------------------------------------

const SortIcon = memo(function SortIcon({
  column,
  sortKey,
  sortDir,
}: {
  column: SortKey
  sortKey: SortKey
  sortDir: SortDir
}) {
  if (sortKey !== column) return <ArrowUpDown className="h-3 w-3 text-muted" />
  return sortDir === 'asc' ? (
    <ArrowUp className="h-3 w-3 text-primary" />
  ) : (
    <ArrowDown className="h-3 w-3 text-primary" />
  )
})

SortIcon.displayName = 'SortIcon'

// ---------------------------------------------------------------------------
// Pose Table — sortable, interactive
// ---------------------------------------------------------------------------

type SortKey = 'pose_rank' | 'affinity' | 'rmsd_ub'
type SortDir = 'asc' | 'desc'

const PoseTable = memo(function PoseTable({
  poses,
  activePoseIndex,
  onSelectPose,
}: {
  poses: DockingPose[]
  activePoseIndex: number
  onSelectPose: (index: number) => void
}) {
  const [sortKey, setSortKey] = useState<SortKey>('pose_rank')
  const [sortDir, setSortDir] = useState<SortDir>('asc')

  const handleSort = useCallback(
    (key: SortKey) => {
      if (sortKey === key) {
        setSortDir((d) => (d === 'asc' ? 'desc' : 'asc'))
      } else {
        setSortKey(key)
        setSortDir(key === 'affinity' ? 'asc' : 'asc')
      }
    },
    [sortKey],
  )

  // Sorted poses with original index preserved for onSelectPose
  const sortedPoses = useMemo(() => {
    const indexed = poses.map((p, i) => ({ pose: p, originalIndex: i }))
    indexed.sort((a, b) => {
      const aVal = a.pose[sortKey]
      const bVal = b.pose[sortKey]
      return sortDir === 'asc' ? aVal - bVal : bVal - aVal
    })
    return indexed
  }, [poses, sortKey, sortDir])

  if (poses.length === 0) {
    return (
      <div className="rounded-2xl border border-surface-border bg-surface/40 p-6 text-center">
        <p className="text-sm text-muted-foreground">No pose data available</p>
      </div>
    )
  }

  return (
    <div className="overflow-hidden rounded-2xl border border-surface-border bg-surface/40">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-surface-border/50 px-5 py-3">
        <div className="flex items-center gap-2">
          <TrendingDown className="h-4 w-4 text-primary" />
          <span className="text-xs font-bold uppercase tracking-wider text-muted">All Poses</span>
        </div>
        <span className="text-[10px] text-muted-foreground">Click a row to inspect</span>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm">
          <thead>
            <tr className="border-b border-surface-border/50 bg-surface-highlight/30">
              {([
                ['pose_rank', 'Rank'],
                ['affinity', 'Affinity (kcal/mol)'],
                ['rmsd_ub', 'RMSD (Å)'],
              ] as [SortKey, string][]).map(([key, label]) => (
                <th
                  key={key}
                  onClick={() => handleSort(key)}
                  className="cursor-pointer select-none px-5 py-2.5 text-[10px] font-bold uppercase tracking-wider text-muted transition-colors hover:text-white"
                >
                  <span className="inline-flex items-center gap-1.5">
                    {label}
                    <SortIcon column={key} sortKey={sortKey} sortDir={sortDir} />
                  </span>
                </th>
              ))}
              <th className="px-5 py-2.5 text-[10px] font-bold uppercase tracking-wider text-muted">
                LE
              </th>
              <th className="px-5 py-2.5 text-[10px] font-bold uppercase tracking-wider text-muted">
                Interactions
              </th>
            </tr>
          </thead>
          <tbody>
            {sortedPoses.map(({ pose, originalIndex }) => {
              const isActive = originalIndex === activePoseIndex
              const totalInteractions =
                (pose.interactions?.hydrogen_bonds?.length ?? 0) +
                (pose.interactions?.hydrophobic?.length ?? 0) +
                (pose.interactions?.pi_stacking?.length ?? 0) +
                (pose.interactions?.salt_bridges?.length ?? 0)

              return (
                <tr
                  key={pose.pose_rank}
                  onClick={() => onSelectPose(originalIndex)}
                  className={cn(
                    'cursor-pointer border-b border-surface-border/30 transition-colors',
                    isActive
                      ? 'bg-primary/10 hover:bg-primary/15'
                      : 'hover:bg-surface-highlight/50',
                  )}
                >
                  {/* Rank */}
                  <td className="px-5 py-3">
                    <span
                      className={cn(
                        'inline-flex h-6 w-6 items-center justify-center rounded-full text-[10px] font-bold',
                        isActive
                          ? 'bg-primary/20 text-primary ring-1 ring-primary/30'
                          : 'bg-surface-highlight text-muted-foreground',
                      )}
                    >
                      {pose.pose_rank}
                    </span>
                  </td>

                  {/* Affinity */}
                  <td className="px-5 py-3">
                    <span
                      className={cn(
                        'font-bold tabular-nums',
                        pose.affinity <= -8
                          ? 'text-emerald-400'
                          : pose.affinity <= -6
                            ? 'text-sky-400'
                            : pose.affinity <= -4
                              ? 'text-amber-400'
                              : 'text-red-400',
                      )}
                    >
                      {pose.affinity.toFixed(1)}
                    </span>
                  </td>

                  {/* RMSD */}
                  <td className="px-5 py-3 tabular-nums text-muted-foreground">
                    {pose.rmsd_ub.toFixed(2)}
                  </td>

                  {/* LE */}
                  <td className="px-5 py-3 tabular-nums text-muted-foreground">
                    {pose.ligand_efficiency.toFixed(2)}
                  </td>

                  {/* Interactions count */}
                  <td className="px-5 py-3">
                    <span className="inline-flex items-center gap-1 text-xs text-muted-foreground">
                      <Atom className="h-3 w-3" />
                      {totalInteractions}
                    </span>
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </div>
  )
})

PoseTable.displayName = 'PoseTable'
