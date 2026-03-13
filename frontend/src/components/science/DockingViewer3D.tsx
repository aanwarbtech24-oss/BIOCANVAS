import { useEffect, useRef, useCallback, useState, useMemo, memo } from 'react'
import { cn } from '@/lib/cn'
import type { InteractionSet } from '@/types/api'
import {
  RotateCcw, Crosshair, Layers, Atom, Cylinder, Circle,
  Eye, EyeOff, ChevronRight, ChevronLeft,
} from 'lucide-react'

// ═══════════════════════════════════════════════════════════════════════════
// 3Dmol – loaded via CDN <script> tag in index.html.
// window.$3Dmol avoids all Vite CJS interop issues.
// ═══════════════════════════════════════════════════════════════════════════

// eslint-disable-next-line @typescript-eslint/no-explicit-any
function get3Dmol(): any {
  return (window as any).$3Dmol
}

// ═══════════════════════════════════════════════════════════════════════════
// Types
// ═══════════════════════════════════════════════════════════════════════════

export interface DockingViewer3DProps {
  /** Raw PDB string for the protein receptor */
  proteinPdb: string | null
  /** Multi-model PDBQT string containing all docked ligand poses */
  ligandPdbqt: string | null
  /** Index of the currently active pose (0-based) */
  activePoseIndex: number
  /** Interaction data for the active pose (H-bonds, hydrophobic, etc.) */
  interactions: InteractionSet | null
  /** Container height in pixels */
  height?: number
}

// ═══════════════════════════════════════════════════════════════════════════
// Constants – Interaction Color Palette
// ═══════════════════════════════════════════════════════════════════════════

const INTERACTION_COLORS = {
  hydrogen_bond: { line: '#facc15', label: '#fef3c7', bg: '#422006', dot: 'bg-amber-400' },
  hydrophobic:   { line: '#a3e635', label: '#ecfccb', bg: '#1a2e05', dot: 'bg-lime-400' },
  pi_stacking:   { line: '#c084fc', label: '#f3e8ff', bg: '#3b0764', dot: 'bg-purple-400' },
  salt_bridge:   { line: '#22d3ee', label: '#cffafe', bg: '#083344', dot: 'bg-cyan-400' },
} as const

// ═══════════════════════════════════════════════════════════════════════════
// Helpers
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Split a multi-model PDBQT string into individual pose blocks.
 * Vina output: MODEL 1 ... ENDMDL  MODEL 2 ... ENDMDL  ...
 */
function splitPdbqtModels(pdbqt: string): string[] {
  const models: string[] = []
  const lines = pdbqt.split('\n')
  let current: string[] = []
  let inModel = false

  for (const line of lines) {
    if (line.startsWith('MODEL')) {
      inModel = true
      current = [line]
    } else if (line.startsWith('ENDMDL')) {
      current.push(line)
      models.push(current.join('\n'))
      current = []
      inModel = false
    } else if (inModel) {
      current.push(line)
    }
  }

  // If no MODEL/ENDMDL markers, treat whole string as one model
  if (models.length === 0 && pdbqt.trim().length > 0) {
    models.push(pdbqt)
  }

  return models
}

/**
 * Parse a PLIP-style residue string like "TYR-102" into { resn, resi }.
 */
function parseResidue(residueStr: string): { resn: string; resi: number } | null {
  const match = residueStr.match(/^([A-Z]{3})-(\d+)$/)
  if (!match) return null
  return { resn: match[1], resi: parseInt(match[2], 10) }
}

/**
 * Find the closest protein atom (in a residue) to the ligand centroid,
 * and the closest ligand atom to that protein atom.
 */
// eslint-disable-next-line @typescript-eslint/no-explicit-any
function findClosestPair(resAtoms: any[], ligandAtoms: any[], ligandCentroid: { x: number; y: number; z: number }) {
  let bestProtein = resAtoms[0]
  let bestDist = Infinity
  for (const atom of resAtoms) {
    const dx = atom.x - ligandCentroid.x
    const dy = atom.y - ligandCentroid.y
    const dz = atom.z - ligandCentroid.z
    const dist = dx * dx + dy * dy + dz * dz
    if (dist < bestDist) { bestDist = dist; bestProtein = atom }
  }

  let bestLigand = ligandAtoms[0]
  let bestLigDist = Infinity
  for (const la of ligandAtoms) {
    const dx = la.x - bestProtein.x
    const dy = la.y - bestProtein.y
    const dz = la.z - bestProtein.z
    const dist = dx * dx + dy * dy + dz * dz
    if (dist < bestLigDist) { bestLigDist = dist; bestLigand = la }
  }

  return { proteinAtom: bestProtein, ligandAtom: bestLigand }
}

// ═══════════════════════════════════════════════════════════════════════════
// Interaction Panel Sub-Component
// ═══════════════════════════════════════════════════════════════════════════

interface InteractionPanelProps {
  interactions: InteractionSet | null
  visible: boolean
  onToggle: () => void
  onResidueClick: (residue: string) => void
}

function InteractionPanel({ interactions, visible, onToggle, onResidueClick }: InteractionPanelProps) {
  if (!interactions) return null

  const hbonds = interactions.hydrogen_bonds ?? []
  const hydrophobic = interactions.hydrophobic ?? []
  const piStack = interactions.pi_stacking ?? []
  const saltBridges = interactions.salt_bridges ?? []
  const totalCount = hbonds.length + hydrophobic.length + piStack.length + saltBridges.length

  if (totalCount === 0) return null

  return (
    <div className="absolute right-0 top-0 z-20 flex h-full">
      {/* Toggle tab */}
      <button
        type="button"
        onClick={onToggle}
        className="my-auto flex h-20 w-5 items-center justify-center rounded-l-md bg-slate-800/90 text-slate-400 backdrop-blur-sm transition-colors hover:bg-slate-700 hover:text-white"
        title={visible ? 'Hide interactions' : 'Show interactions'}
      >
        {visible ? <ChevronRight className="h-3 w-3" /> : <ChevronLeft className="h-3 w-3" />}
      </button>

      {/* Panel */}
      <div
        className={cn(
          'h-full w-64 overflow-y-auto border-l border-slate-700/50 bg-slate-900/95 backdrop-blur-md transition-all duration-300',
          visible ? 'translate-x-0 opacity-100' : 'pointer-events-none translate-x-full opacity-0',
        )}
      >
        {/* Header */}
        <div className="sticky top-0 z-10 border-b border-slate-700/50 bg-slate-900/95 px-3 py-2.5 backdrop-blur">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-bold uppercase tracking-widest text-slate-300">
              Interactions
            </span>
            <span className="rounded-full bg-primary/20 px-1.5 py-0.5 text-[9px] font-bold text-primary">
              {totalCount}
            </span>
          </div>
        </div>

        <div className="space-y-1 p-2">
          {/* H-Bonds section */}
          {hbonds.length > 0 && (
            <InteractionSection
              title="Hydrogen Bonds"
              dotClass={INTERACTION_COLORS.hydrogen_bond.dot}
              items={hbonds.map((h) => ({
                residue: h.residue,
                detail: `${h.distance.toFixed(1)}Å`,
              }))}
              onResidueClick={onResidueClick}
            />
          )}

          {/* Hydrophobic section */}
          {hydrophobic.length > 0 && (
            <InteractionSection
              title="Hydrophobic"
              dotClass={INTERACTION_COLORS.hydrophobic.dot}
              items={hydrophobic.map((h) => ({
                residue: h.residue,
                detail: h.distance ? `${h.distance.toFixed(1)}Å` : '',
              }))}
              onResidueClick={onResidueClick}
            />
          )}

          {/* Pi-stacking section */}
          {piStack.length > 0 && (
            <InteractionSection
              title="π-Stacking"
              dotClass={INTERACTION_COLORS.pi_stacking.dot}
              items={piStack.map((p) => ({
                residue: p.residue,
                detail: p.type === 'T' ? 'T-shaped' : p.type === 'P' ? 'Parallel' : '',
              }))}
              onResidueClick={onResidueClick}
            />
          )}

          {/* Salt bridges section */}
          {saltBridges.length > 0 && (
            <InteractionSection
              title="Salt Bridges"
              dotClass={INTERACTION_COLORS.salt_bridge.dot}
              items={saltBridges.map((s) => ({
                residue: s.residue,
                detail: s.distance ? `${s.distance.toFixed(1)}Å` : '',
              }))}
              onResidueClick={onResidueClick}
            />
          )}
        </div>
      </div>
    </div>
  )
}

function InteractionSection({
  title,
  dotClass,
  items,
  onResidueClick,
}: {
  title: string
  dotClass: string
  items: { residue: string; detail: string }[]
  onResidueClick: (r: string) => void
}) {
  return (
    <div className="rounded-lg bg-slate-800/50 p-2">
      <div className="mb-1.5 flex items-center gap-1.5">
        <span className={cn('h-2 w-2 rounded-full', dotClass)} />
        <span className="text-[10px] font-semibold uppercase tracking-wider text-slate-400">
          {title}
        </span>
        <span className="ml-auto text-[9px] text-slate-500">{items.length}</span>
      </div>
      <div className="space-y-0.5">
        {items.map((item, i) => (
          <button
            key={`${item.residue}-${i}`}
            type="button"
            onClick={() => onResidueClick(item.residue)}
            className="flex w-full items-center justify-between rounded px-2 py-1 text-left transition-colors hover:bg-slate-700/60"
          >
            <span className="font-mono text-[11px] font-medium text-slate-200">
              {item.residue}
            </span>
            {item.detail && (
              <span className="text-[10px] text-slate-500">{item.detail}</span>
            )}
          </button>
        ))}
      </div>
    </div>
  )
}

// ═══════════════════════════════════════════════════════════════════════════
// Hover Tooltip Sub-Component
// ═══════════════════════════════════════════════════════════════════════════

interface HoverInfo {
  text: string
  x: number
  y: number
  isLigand: boolean
}

function HoverTooltip({ info }: { info: HoverInfo | null }) {
  if (!info) return null
  return (
    <div
      className="pointer-events-none absolute z-30 rounded-md border px-2.5 py-1.5 shadow-xl backdrop-blur-md transition-opacity"
      style={{
        left: info.x + 14,
        top: info.y - 10,
        borderColor: info.isLigand ? '#22d3ee' : '#6366f1',
        backgroundColor: info.isLigand ? 'rgba(8, 51, 68, 0.92)' : 'rgba(30, 27, 75, 0.92)',
      }}
    >
      <span
        className="text-[11px] font-semibold"
        style={{ color: info.isLigand ? '#67e8f9' : '#a5b4fc' }}
      >
        {info.text}
      </span>
    </div>
  )
}

// ═══════════════════════════════════════════════════════════════════════════
// Main Viewer Component
// ═══════════════════════════════════════════════════════════════════════════

function DockingViewer3DInner({
  proteinPdb,
  ligandPdbqt,
  activePoseIndex,
  interactions,
  height = 600,
}: DockingViewer3DProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const viewerRef = useRef<any>(null)
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const proteinModelRef = useRef<any>(null)
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const ligandModelRef = useRef<any>(null)
  const [showSurface, setShowSurface] = useState(true)
  const [showInteractions, setShowInteractions] = useState(true)
  const [showLabels, setShowLabels] = useState(true)
  const [proteinStyle, setProteinStyle] = useState<'cartoon' | 'stick' | 'sphere'>('cartoon')
  const [panelVisible, setPanelVisible] = useState(true)
  const [hoverInfo, setHoverInfo] = useState<HoverInfo | null>(null)
  const prevPoseRef = useRef<number>(-1)
  const hoverLabelRef = useRef<any>(null)

  // ── Parse ligand poses once (memoised on ligandPdbqt) ───────────
  const poseModels = useMemo(
    () => (ligandPdbqt ? splitPdbqtModels(ligandPdbqt) : []),
    [ligandPdbqt],
  )

  // ── Zoom to a specific residue (clicked in the panel) ──────────
  const zoomToResidue = useCallback((residue: string) => {
    const viewer = viewerRef.current
    const proteinModel = proteinModelRef.current
    if (!viewer || !proteinModel) return

    const parsed = parseResidue(residue)
    if (!parsed) return

    const resAtoms = proteinModel.selectedAtoms({ resi: parsed.resi })
    if (!resAtoms || resAtoms.length === 0) return

    // Compute residue centroid
    let cx = 0, cy = 0, cz = 0
    for (const a of resAtoms) { cx += a.x; cy += a.y; cz += a.z }
    cx /= resAtoms.length; cy /= resAtoms.length; cz /= resAtoms.length

    viewer.center({ x: cx, y: cy, z: cz })
    viewer.zoom(1.8, 500)
    viewer.render()
  }, [])

  // ── Initialise viewer when protein data changes ────────────────────
  useEffect(() => {
    if (!proteinPdb || !containerRef.current) return

    const el = containerRef.current
    const lib = get3Dmol()
    const createFn = lib?.createViewer
    if (typeof createFn !== 'function') {
      console.error('[DockingViewer3D] window.$3Dmol.createViewer not available')
      return
    }

    // Tear down previous viewer
    if (viewerRef.current) {
      try {
        viewerRef.current.removeAllShapes()
        viewerRef.current.removeAllModels()
        viewerRef.current.removeAllLabels()
        viewerRef.current.clear()
      } catch { /* noop */ }
      viewerRef.current = null
      proteinModelRef.current = null
      ligandModelRef.current = null
    }
    el.innerHTML = ''
    prevPoseRef.current = -1

    const timer = setTimeout(() => {
      const rect = el.getBoundingClientRect()
      if (rect.width === 0 || rect.height === 0) {
        console.warn('[DockingViewer3D] Container has 0 dimensions — skipping init')
        return
      }

      try {
        const viewer = createFn(el, {
          backgroundColor: '#0a0f1e',
          antialias: true,
        })
        viewerRef.current = viewer

        // ── Model 1: Protein ──────────────────────────────────────
        const proteinModel = viewer.addModel(proteinPdb, 'pdb')
        proteinModelRef.current = proteinModel

        // Vibrant protein — rainbow spectrum with full opacity
        const proteinVis =
          proteinStyle === 'stick'
            ? { stick: { colorscheme: 'spectrum', radius: 0.12 } }
            : proteinStyle === 'sphere'
              ? { sphere: { colorscheme: 'spectrum', scale: 0.3 } }
              : { cartoon: { colorscheme: 'spectrum', style: 'oval', thickness: 0.4, arrows: true } }

        viewer.setStyle({ model: proteinModel }, proteinVis)

        // Ghost surface — faint binding pocket outline
        if (showSurface) {
          viewer.addSurface(
            lib.SurfaceType?.VDW ?? 1,
            { opacity: 0.08, color: '#4f6d8f', voldata: null },
            { model: proteinModel },
          )
        }

        // ── Model 2: Ligand (active pose from PDBQT) ──────────────
        const poseBlock = poseModels[activePoseIndex]
        if (poseBlock) {
          const ligModel = viewer.addModel(poseBlock, 'pdb')
          ligandModelRef.current = ligModel

          // Vibrant ligand — standard green sticks
          viewer.setStyle(
            { model: ligModel },
            {
              stick: {
                colorscheme: 'greenCarbon',
                radius: 0.2,
              },
              sphere: {
                colorscheme: 'greenCarbon',
                scale: 0.3,
              },
            },
          )

          // ── Binding-pocket residues (within 5Å) — show as sticks
          const ligAtoms = ligModel.selectedAtoms({})
          if (ligAtoms && ligAtoms.length > 0) {
            const cx = ligAtoms.reduce((s: number, a: any) => s + a.x, 0) / ligAtoms.length
            const cy = ligAtoms.reduce((s: number, a: any) => s + a.y, 0) / ligAtoms.length
            const cz = ligAtoms.reduce((s: number, a: any) => s + a.z, 0) / ligAtoms.length

            // 5Å Pocket — secondary structure coloring (ssPyMOL)
            viewer.setStyle(
              { model: proteinModel, byres: true, within: { distance: 5, sel: { x: cx, y: cy, z: cz } } },
              {
                stick: { colorscheme: 'ssPyMOL', radius: 0.15 },
              },
            )
          }

          // ── Hover callback for interactive tooltips ─────────────
          setupHoverCallbacks(viewer, proteinModel, ligModel, el, setHoverInfo, hoverLabelRef)

          // Focus camera on the ligand inside the pocket
          viewer.zoomTo({ model: ligModel })
        } else {
          ligandModelRef.current = null
          // Hover for protein-only mode
          setupHoverCallbacks(viewer, proteinModel, null, el, setHoverInfo, hoverLabelRef)
          viewer.zoomTo()
        }

        // ── Interaction dashed lines + labels ──────────────────────
        if (showInteractions && interactions && proteinModelRef.current && ligandModelRef.current) {
          drawInteractions(viewer, proteinModelRef.current, ligandModelRef.current, interactions, showLabels)
        }

        viewer.render()
        viewer.zoom(0.82, 400)

        prevPoseRef.current = activePoseIndex

        requestAnimationFrame(() => {
          viewer.resize()
          viewer.render()
        })
      } catch (err) {
        console.error('[DockingViewer3D] createViewer threw:', err)
      }
    }, 60)

    return () => {
      clearTimeout(timer)
      if (viewerRef.current) {
        try {
          viewerRef.current.removeAllShapes()
          viewerRef.current.removeAllModels()
          viewerRef.current.removeAllLabels()
          viewerRef.current.clear()
        } catch { /* noop */ }
        viewerRef.current = null
        proteinModelRef.current = null
        ligandModelRef.current = null
      }
      // Release WebGL context by destroying the canvas element
      if (el) el.innerHTML = ''
    }
    // Re-create viewer when protein data, surface, style, or label toggle changes
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [proteinPdb, showSurface, proteinStyle, showLabels])

  // ── Update ligand model when activePoseIndex changes ───────────────
  useEffect(() => {
    const viewer = viewerRef.current
    if (!viewer || !proteinPdb) return
    // Skip if this is the initial render (already handled above)
    if (prevPoseRef.current === activePoseIndex) return
    if (prevPoseRef.current === -1) return

    try {
      // Remove old ligand model
      if (ligandModelRef.current) {
        viewer.removeModel(ligandModelRef.current)
        ligandModelRef.current = null
      }

      // Remove all shapes + labels (interaction lines)
      viewer.removeAllShapes()
      viewer.removeAllLabels()

      // Add new ligand pose
      const poseBlock = poseModels[activePoseIndex]
      if (poseBlock) {
        const ligModel = viewer.addModel(poseBlock, 'pdb')
        ligandModelRef.current = ligModel

        viewer.setStyle(
          { model: ligModel },
          {
            stick: { colorscheme: 'greenCarbon', radius: 0.2 },
            sphere: { colorscheme: 'greenCarbon', scale: 0.3 },
          },
        )

        // Focus on new ligand position
        viewer.zoomTo({ model: ligModel })
      }

      // Redraw interaction lines for new pose
      if (showInteractions && interactions && proteinModelRef.current && ligandModelRef.current) {
        drawInteractions(viewer, proteinModelRef.current, ligandModelRef.current, interactions, showLabels)
      }

      viewer.render()
      viewer.zoom(0.82, 400)
      prevPoseRef.current = activePoseIndex
    } catch (err) {
      console.error('[DockingViewer3D] pose switch error:', err)
    }
  }, [activePoseIndex, proteinPdb, interactions, showInteractions, showLabels])

  // ── Redraw interaction lines when toggle changes ───────────────────
  useEffect(() => {
    const viewer = viewerRef.current
    if (!viewer || !proteinPdb) return

    viewer.removeAllShapes()
    viewer.removeAllLabels()

    if (showInteractions && interactions && proteinModelRef.current && ligandModelRef.current) {
      drawInteractions(viewer, proteinModelRef.current, ligandModelRef.current, interactions, showLabels)
    }

    viewer.render()
  }, [showInteractions, interactions, proteinPdb, showLabels])

  // ── Resize observer ────────────────────────────────────────────────
  useEffect(() => {
    if (!containerRef.current) return
    const observer = new ResizeObserver(() => {
      if (viewerRef.current) {
        viewerRef.current.resize()
        viewerRef.current.render()
      }
    })
    observer.observe(containerRef.current)
    return () => observer.disconnect()
  }, [])

  // ── Control callbacks ──────────────────────────────────────────────
  const resetView = useCallback(() => {
    const viewer = viewerRef.current
    if (!viewer) return
    if (ligandModelRef.current) {
      viewer.zoomTo({ model: ligandModelRef.current })
    } else {
      viewer.zoomTo()
    }
    viewer.render()
  }, [])

  const focusLigand = useCallback(() => {
    const viewer = viewerRef.current
    if (!viewer || !ligandModelRef.current) return
    viewer.zoomTo({ model: ligandModelRef.current })
    viewer.zoom(1.2, 400)
    viewer.render()
  }, [])

  // ── Render ─────────────────────────────────────────────────────────
  const hasLigand = poseModels.length > 0
  const hasInteractions = interactions && (
    (interactions.hydrogen_bonds?.length ?? 0) +
    (interactions.hydrophobic?.length ?? 0) +
    (interactions.pi_stacking?.length ?? 0) +
    (interactions.salt_bridges?.length ?? 0)
  ) > 0

  return (
    <div className="overflow-hidden rounded-2xl border border-surface-border bg-surface/40">
      {/* Toolbar */}
      <div className="flex items-center justify-between border-b border-surface-border/50 px-4 py-2">
        <div className="flex items-center gap-2">
          <Layers className="h-3.5 w-3.5 text-primary" />
          <span className="text-xs font-bold uppercase tracking-wider text-muted">
            3D Complex Viewer
          </span>
          {hasLigand && (
            <span className="rounded-full bg-emerald-500/10 px-2 py-0.5 text-[9px] font-bold text-emerald-400">
              Pose #{activePoseIndex + 1}
            </span>
          )}
        </div>

        <div className="flex items-center gap-1">
          {/* Protein style selector */}
          {(['cartoon', 'stick', 'sphere'] as const).map((style) => {
            const icons = { cartoon: Cylinder, stick: Atom, sphere: Circle }
            const Icon = icons[style]
            const isActive = proteinStyle === style
            return (
              <button
                key={style}
                type="button"
                onClick={() => setProteinStyle(style)}
                className={cn(
                  'rounded-md px-2 py-1 text-[10px] font-medium capitalize transition-colors',
                  isActive
                    ? 'bg-sky-500/20 text-sky-400'
                    : 'text-muted hover:bg-surface-highlight hover:text-white',
                )}
                title={`${style} representation`}
              >
                <span className="inline-flex items-center gap-1">
                  <Icon className="h-2.5 w-2.5" />
                  {style}
                </span>
              </button>
            )
          })}

          {/* Divider */}
          <div className="mx-0.5 h-4 w-px bg-surface-border/50" />

          {/* Surface toggle */}
          <button
            type="button"
            onClick={() => setShowSurface((s) => !s)}
            className={cn(
              'rounded-md px-2 py-1 text-[10px] font-medium transition-colors',
              showSurface
                ? 'bg-primary/20 text-primary'
                : 'text-muted hover:bg-surface-highlight hover:text-white',
            )}
          >
            Surface
          </button>

          {/* Interactions toggle */}
          {hasLigand && (
            <button
              type="button"
              onClick={() => setShowInteractions((s) => !s)}
              className={cn(
                'rounded-md px-2 py-1 text-[10px] font-medium transition-colors',
                showInteractions
                  ? 'bg-amber-500/20 text-amber-400'
                  : 'text-muted hover:bg-surface-highlight hover:text-white',
              )}
            >
              Bonds
            </button>
          )}

          {/* Labels toggle */}
          {hasLigand && (
            <button
              type="button"
              onClick={() => setShowLabels((s) => !s)}
              className={cn(
                'rounded-md px-2 py-1 text-[10px] font-medium transition-colors',
                showLabels
                  ? 'bg-violet-500/20 text-violet-400'
                  : 'text-muted hover:bg-surface-highlight hover:text-white',
              )}
              title="Toggle residue labels"
            >
              {showLabels ? <Eye className="inline h-3 w-3" /> : <EyeOff className="inline h-3 w-3" />}
            </button>
          )}

          {/* Focus ligand */}
          {hasLigand && (
            <button
              type="button"
              onClick={focusLigand}
              className="rounded-md p-1 text-muted transition-colors hover:bg-surface-highlight hover:text-white"
              title="Focus on ligand"
            >
              <Crosshair className="h-3.5 w-3.5" />
            </button>
          )}
          {/* Reset camera */}
          <button
            type="button"
            onClick={resetView}
            className="rounded-md p-1 text-muted transition-colors hover:bg-surface-highlight hover:text-white"
            title="Reset camera"
          >
            <RotateCcw className="h-3.5 w-3.5" />
          </button>
        </div>
      </div>

      {/* WebGL Canvas Container + Panels */}
      <div className="relative" style={{ height: `${height}px` }}>
        {!proteinPdb && (
          <div className="absolute inset-0 z-10 flex flex-col items-center justify-center bg-[#0a0f1e]">
            <p className="text-sm font-medium text-muted-foreground">No structure data</p>
            <p className="mt-1 text-xs text-muted">Protein PDB data is not available</p>
          </div>
        )}
        <div
          ref={containerRef}
          className="h-full w-full"
          style={{ position: 'relative' }}
        />

        {/* Hover tooltip (follows cursor) */}
        <HoverTooltip info={hoverInfo} />

        {/* Interaction detail panel (right sidebar overlay) */}
        {hasLigand && hasInteractions && showInteractions && (
          <InteractionPanel
            interactions={interactions}
            visible={panelVisible}
            onToggle={() => setPanelVisible((v) => !v)}
            onResidueClick={zoomToResidue}
          />
        )}

        {/* Legend overlay (bottom-left) */}
        {hasLigand && (
          <div className="absolute bottom-3 left-3 z-20 flex flex-col gap-1 rounded-lg bg-slate-900/85 px-3 py-2 backdrop-blur-sm">
            <div className="flex items-center gap-2">
              <span className="h-2.5 w-5 rounded-sm bg-gradient-to-r from-blue-500 via-green-400 to-red-500" />
              <span className="text-[10px] text-slate-400">Protein (N→C)</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="h-2.5 w-5 rounded-sm bg-green-400" />
              <span className="text-[10px] text-slate-400">Ligand</span>
            </div>
            {showInteractions && (
              <>
                <div className="my-0.5 h-px bg-slate-700/60" />
                <div className="flex items-center gap-2">
                  <span className="h-1 w-5 rounded-full bg-amber-400" />
                  <span className="text-[10px] text-slate-500">H-Bond</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="h-1 w-5 rounded-full bg-lime-400" />
                  <span className="text-[10px] text-slate-500">Hydrophobic</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="h-1 w-5 rounded-full bg-purple-400" />
                  <span className="text-[10px] text-slate-500">π-Stack</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="h-1 w-5 rounded-full bg-cyan-400" />
                  <span className="text-[10px] text-slate-500">Salt Bridge</span>
                </div>
              </>
            )}
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="flex items-center justify-between border-t border-surface-border/50 px-4 py-1.5">
        <span className="text-[10px] text-muted">
          Drag to rotate &middot; Scroll to zoom &middot; Right-click to pan &middot; Hover for details
        </span>
        {!hasLigand && proteinPdb && (
          <span className="text-[10px] text-amber-400/80">
            Protein-only view (no ligand coordinates in simulation mode)
          </span>
        )}
      </div>
    </div>
  )
}

// ═══════════════════════════════════════════════════════════════════════════
// Hover Callback Setup
// ═══════════════════════════════════════════════════════════════════════════

function setupHoverCallbacks(
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  viewer: any,
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  proteinModel: any,
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  ligandModel: any | null,
  containerEl: HTMLElement,
  setHoverInfo: (info: HoverInfo | null) => void,
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  hoverLabelRef: React.MutableRefObject<any>,
) {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const showLabel = (atom: any, _viewer: any, event: any) => {
    if (!atom || !atom.resn) return

    // Determine if this atom belongs to the ligand model
    const isLigand = ligandModel && atom.model === ligandModel.getID()

    let text: string
    if (isLigand) {
      text = `Ligand · ${atom.elem || '?'}${atom.serial ? ' #' + atom.serial : ''}`
    } else {
      // Handle resn that might be an object with a trim method
      const resName = (atom.resn && typeof atom.resn.trim === 'function') ? atom.resn.trim() : String(atom.resn || '???')
      const resSeq = atom.resi || '?'
      const chain = atom.chain ? ` (Chain ${atom.chain})` : ''
      const atomName = atom.atom || atom.elem || ''
      text = `${resName}-${resSeq}${chain} · ${atomName}`
    }

    // Get mouse position relative to container
    const rect = containerEl.getBoundingClientRect()
    const x = (event?.clientX ?? 0) - rect.left
    const y = (event?.clientY ?? 0) - rect.top

    setHoverInfo({ text, x, y, isLigand: !!isLigand })

    // 3D label on the atom
    if (hoverLabelRef.current) {
      viewer.removeLabel(hoverLabelRef.current)
      hoverLabelRef.current = null
    }

    hoverLabelRef.current = viewer.addLabel(
      isLigand ? (atom.elem || "?") : `${String(atom.resn || "???")}-${atom.resi || "?"}`,
      {
        position: { x: atom.x, y: atom.y, z: atom.z },
        fontSize: 10,
        fontColor: isLigand ? '#67e8f9' : '#c7d2fe',
        backgroundColor: isLigand ? '#083344' : '#1e1b4b',
        backgroundOpacity: 0.88,
        borderColor: isLigand ? '#22d3ee' : '#6366f1',
        borderThickness: 0.5,
        showBackground: true,
      },
    )
    viewer.render()
  }

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const removeLabel = (_atom: any) => {
    setHoverInfo(null)
    if (hoverLabelRef.current) {
      try { viewer.removeLabel(hoverLabelRef.current) } catch { /* noop */ }
      hoverLabelRef.current = null
    }
    viewer.render()
  }

  // Set hoverable on protein atoms
  viewer.setHoverable(
    { model: proteinModel },
    true,
    showLabel,
    removeLabel,
  )

  // Set hoverable on ligand atoms
  if (ligandModel) {
    viewer.setHoverable(
      { model: ligandModel },
      true,
      showLabel,
      removeLabel,
    )
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Interaction Rendering
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Draw dashed lines + labels for all non-covalent interactions between
 * protein residues and the ligand.
 */
function drawInteractions(
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  viewer: any,
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  proteinModel: any,
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  ligandModel: any,
  interactions: InteractionSet,
  showLabels: boolean,
) {
  // Compute ligand centroid for line endpoints
  const ligandAtoms = ligandModel.selectedAtoms({})
  if (!ligandAtoms || ligandAtoms.length === 0) return

  const ligandCentroid = { x: 0, y: 0, z: 0 }
  for (const atom of ligandAtoms) {
    ligandCentroid.x += atom.x
    ligandCentroid.y += atom.y
    ligandCentroid.z += atom.z
  }
  ligandCentroid.x /= ligandAtoms.length
  ligandCentroid.y /= ligandAtoms.length
  ligandCentroid.z /= ligandAtoms.length

  // ── Hydrogen bonds → gold dashed lines ──────────────────────────
  const hbColor = INTERACTION_COLORS.hydrogen_bond
  for (const hbond of interactions.hydrogen_bonds ?? []) {
    const parsed = parseResidue(hbond.residue)
    if (!parsed) continue

    const resAtoms = proteinModel.selectedAtoms({ resi: parsed.resi })
    if (!resAtoms || resAtoms.length === 0) continue

    const { proteinAtom, ligandAtom } = findClosestPair(resAtoms, ligandAtoms, ligandCentroid)

    viewer.addCylinder({
      start: { x: proteinAtom.x, y: proteinAtom.y, z: proteinAtom.z },
      end: { x: ligandAtom.x, y: ligandAtom.y, z: ligandAtom.z },
      radius: 0.045,
      color: hbColor.line,
      dashed: true,
      dashLength: 0.2,
      gapLength: 0.12,
      fromCap: 1,
      toCap: 1,
    })

    // Midpoint label with distance
    if (showLabels) {
      const mx = (proteinAtom.x + ligandAtom.x) / 2
      const my = (proteinAtom.y + ligandAtom.y) / 2
      const mz = (proteinAtom.z + ligandAtom.z) / 2
      viewer.addLabel(`${hbond.residue}  H-Bond: ${hbond.distance.toFixed(1)}Å`, {
        position: { x: mx, y: my, z: mz },
        fontSize: 10,
        fontColor: hbColor.label,
        backgroundColor: hbColor.bg,
        backgroundOpacity: 0.85,
        borderColor: hbColor.line,
        borderThickness: 0.5,
        showBackground: true,
        alignment: 'center',
      })
    }
  }

  // ── Hydrophobic contacts → lime dashed lines ────────────────────
  const hpColor = INTERACTION_COLORS.hydrophobic
  for (const hp of interactions.hydrophobic ?? []) {
    const parsed = parseResidue(hp.residue)
    if (!parsed) continue

    const resAtoms = proteinModel.selectedAtoms({ resi: parsed.resi })
    if (!resAtoms || resAtoms.length === 0) continue

    const { proteinAtom, ligandAtom } = findClosestPair(resAtoms, ligandAtoms, ligandCentroid)

    viewer.addCylinder({
      start: { x: proteinAtom.x, y: proteinAtom.y, z: proteinAtom.z },
      end: { x: ligandAtom.x, y: ligandAtom.y, z: ligandAtom.z },
      radius: 0.035,
      color: hpColor.line,
      dashed: true,
      dashLength: 0.18,
      gapLength: 0.18,
      opacity: 0.55,
    })

    if (showLabels) {
      viewer.addLabel(hp.residue, {
        position: { x: proteinAtom.x, y: proteinAtom.y, z: proteinAtom.z },
        fontSize: 9,
        fontColor: hpColor.label,
        backgroundColor: hpColor.bg,
        backgroundOpacity: 0.80,
        borderColor: hpColor.line,
        borderThickness: 0.4,
        showBackground: true,
        alignment: 'bottomCenter',
      })
    }
  }

  // ── Pi-stacking → purple dashed lines ───────────────────────────
  const piColor = INTERACTION_COLORS.pi_stacking
  for (const ps of interactions.pi_stacking ?? []) {
    const parsed = parseResidue(ps.residue)
    if (!parsed) continue

    const resAtoms = proteinModel.selectedAtoms({ resi: parsed.resi })
    if (!resAtoms || resAtoms.length === 0) continue

    const { proteinAtom } = findClosestPair(resAtoms, ligandAtoms, ligandCentroid)

    viewer.addCylinder({
      start: { x: proteinAtom.x, y: proteinAtom.y, z: proteinAtom.z },
      end: { x: ligandCentroid.x, y: ligandCentroid.y, z: ligandCentroid.z },
      radius: 0.04,
      color: piColor.line,
      dashed: true,
      dashLength: 0.22,
      gapLength: 0.14,
      opacity: 0.65,
    })

    if (showLabels) {
      viewer.addLabel(`${ps.residue}  π`, {
        position: { x: proteinAtom.x, y: proteinAtom.y, z: proteinAtom.z },
        fontSize: 9,
        fontColor: piColor.label,
        backgroundColor: piColor.bg,
        backgroundOpacity: 0.80,
        borderColor: piColor.line,
        borderThickness: 0.4,
        showBackground: true,
        alignment: 'bottomCenter',
      })
    }
  }

  // ── Salt bridges → cyan dashed lines ────────────────────────────
  const sbColor = INTERACTION_COLORS.salt_bridge
  for (const sb of interactions.salt_bridges ?? []) {
    const parsed = parseResidue(sb.residue)
    if (!parsed) continue

    const resAtoms = proteinModel.selectedAtoms({ resi: parsed.resi })
    if (!resAtoms || resAtoms.length === 0) continue

    const { proteinAtom, ligandAtom } = findClosestPair(resAtoms, ligandAtoms, ligandCentroid)

    viewer.addCylinder({
      start: { x: proteinAtom.x, y: proteinAtom.y, z: proteinAtom.z },
      end: { x: ligandAtom.x, y: ligandAtom.y, z: ligandAtom.z },
      radius: 0.04,
      color: sbColor.line,
      dashed: true,
      dashLength: 0.22,
      gapLength: 0.14,
      opacity: 0.65,
    })

    if (showLabels) {
      viewer.addLabel(`${sb.residue}  ⊕⊖`, {
        position: { x: proteinAtom.x, y: proteinAtom.y, z: proteinAtom.z },
        fontSize: 9,
        fontColor: sbColor.label,
        backgroundColor: sbColor.bg,
        backgroundOpacity: 0.80,
        borderColor: sbColor.line,
        borderThickness: 0.4,
        showBackground: true,
        alignment: 'bottomCenter',
      })
    }
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Memoised export — skip re-render if data+pose haven't changed
// ═══════════════════════════════════════════════════════════════════════════

export const DockingViewer3D = memo(DockingViewer3DInner, (prev, next) => {
  return (
    prev.proteinPdb === next.proteinPdb &&
    prev.ligandPdbqt === next.ligandPdbqt &&
    prev.activePoseIndex === next.activePoseIndex &&
    prev.interactions === next.interactions &&
    prev.height === next.height
  )
})

DockingViewer3D.displayName = 'DockingViewer3D'

export default DockingViewer3D
