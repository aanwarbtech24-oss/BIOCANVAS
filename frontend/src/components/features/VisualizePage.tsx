import { useState, useCallback } from 'react'
import MemoizedViewer3D from '@/components/science/Viewer3D'
import {
  useProteins,
  useLigands,
  useProteinStructure,
  useLigandStructure,
} from '@/hooks/useMoleculeLibrary'
import { cn } from '@/lib/cn'
import type { Protein, Ligand } from '@/types/api'
import { categoryColor, ligandTypeColor } from './pipeline/helpers'
import {
  Search,
  FlaskConical,
  Atom,
  ChevronDown,
  ExternalLink,
  Loader2,
  RotateCcw,
} from 'lucide-react'

// ---------------------------------------------------------------------------
// Shared molecule dropdown
// ---------------------------------------------------------------------------

type MoleculeKind = 'protein' | 'ligand'

function MoleculeSelector<T extends Protein | Ligand>({
  kind,
  items,
  isLoading,
  isError,
  selected,
  onSelect,
}: {
  kind: MoleculeKind
  items: T[] | undefined
  isLoading: boolean
  isError: boolean
  selected: T | null
  onSelect: (item: T) => void
}) {
  const [open, setOpen] = useState(false)
  const [query, setQuery] = useState('')

  const filtered = (items ?? []).filter((item) => {
    if (!query.trim()) return true
    const q = query.toLowerCase()
    if (kind === 'protein') {
      const p = item as Protein
      return (
        p.name.toLowerCase().includes(q) ||
        p.uniprot_id.toLowerCase().includes(q) ||
        p.category.toLowerCase().includes(q)
      )
    }
    const l = item as Ligand
    return (
      l.name.toLowerCase().includes(q) ||
      l.type.toLowerCase().includes(q) ||
      l.description.toLowerCase().includes(q)
    )
  })

  const icon = kind === 'protein'
    ? <FlaskConical className="h-4 w-4 text-primary" />
    : <Atom className="h-4 w-4 text-secondary" />

  const label = kind === 'protein' ? 'Protein Target' : 'Ligand'

  return (
    <div className="space-y-2">
      <label className="flex items-center gap-1.5 text-xs font-bold uppercase tracking-widest text-muted">
        {icon} {label}
      </label>

      {isLoading && (
        <div className="flex items-center gap-2 py-4 justify-center">
          <Loader2 className="h-4 w-4 animate-spin text-primary" />
          <span className="text-xs text-muted-foreground">Loading…</span>
        </div>
      )}

      {isError && (
        <p className="text-xs text-destructive text-center py-4">
          Backend unreachable — is it running on <code className="text-destructive/80">:8000</code>?
        </p>
      )}

      {!isLoading && !isError && (
        <div className="relative">
          {/* Trigger */}
          <button
            type="button"
            onClick={() => setOpen((o) => !o)}
            className={cn(
              'flex w-full items-center justify-between rounded-xl border px-4 py-3 text-left text-sm transition-colors',
              open
                ? 'border-primary bg-surface-highlight ring-1 ring-primary/30'
                : 'border-surface-border bg-surface-highlight/60 hover:border-muted',
            )}
          >
            {selected ? (
              <span className="flex items-center gap-2">
                <span className={cn('h-2 w-2 rounded-full', kind === 'protein' ? 'bg-emerald-400' : 'bg-secondary')} />
                <span className="font-medium text-white">
                  {'uniprot_id' in selected ? (selected as Protein).name : (selected as Ligand).name}
                </span>
                <span className="text-muted-foreground text-xs">
                  {'uniprot_id' in selected
                    ? `(${(selected as Protein).uniprot_id})`
                    : `CID ${(selected as Ligand).pubchem_cid}`}
                </span>
              </span>
            ) : (
              <span className="text-muted-foreground">Select a {kind}…</span>
            )}
            <ChevronDown className={cn('h-4 w-4 text-muted-foreground transition-transform', open && 'rotate-180')} />
          </button>

          {/* Dropdown */}
          {open && (
            <div className="absolute z-30 mt-2 w-full rounded-xl border border-surface-border bg-surface shadow-2xl shadow-black/50">
              <div className="border-b border-surface-border px-3 py-2">
                <div className="relative">
                  <Search className="absolute left-2.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-muted" />
                  <input
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder={kind === 'protein' ? 'Search name, UniProt ID, category…' : 'Search name, type…'}
                    autoFocus
                    className="w-full rounded-lg bg-surface-highlight py-2 pl-8 pr-3 text-xs text-white placeholder-muted focus:outline-none"
                  />
                </div>
              </div>

              <div className="max-h-60 overflow-y-auto overscroll-contain py-1">
                {filtered.length === 0 && (
                  <p className="px-4 py-6 text-center text-xs text-muted-foreground">
                    No results for "{query}"
                  </p>
                )}
                {filtered.map((item) => {
                  const isProtein = 'uniprot_id' in item
                  const p = item as Protein
                  const l = item as Ligand
                  const isSelected = selected && ('id' in selected) && selected.id === item.id
                  return (
                    <button
                      key={item.id}
                      type="button"
                      onClick={() => {
                        onSelect(item)
                        setOpen(false)
                        setQuery('')
                      }}
                      className={cn(
                        'flex w-full items-start gap-3 px-4 py-3 text-left transition-colors',
                        isSelected ? 'bg-primary/5' : 'hover:bg-surface-highlight',
                      )}
                    >
                      <div className="min-w-0 flex-1">
                        <div className="flex items-center gap-2">
                          <span className="text-sm font-medium text-white">
                            {isProtein ? p.name : l.name}
                          </span>
                          <span
                            className={cn(
                              'rounded-full px-1.5 py-0.5 text-[10px] font-bold uppercase',
                              isProtein ? categoryColor(p.category) : ligandTypeColor(l.type),
                            )}
                          >
                            {isProtein ? p.category : l.type}
                          </span>
                        </div>
                        <p className="mt-0.5 text-[11px] text-muted-foreground truncate">
                          {isProtein
                            ? `${p.uniprot_id} · ${p.function}`
                            : `CID ${l.pubchem_cid} · ${l.description}`}
                        </p>
                      </div>
                    </button>
                  )
                })}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

// ---------------------------------------------------------------------------
// Visualize Page
// ---------------------------------------------------------------------------

export function VisualizePage() {
  const [selectedProtein, setSelectedProtein] = useState<Protein | null>(null)
  const [selectedLigand, setSelectedLigand] = useState<Ligand | null>(null)

  const { data: proteins, isLoading: proteinsLoading, isError: proteinsError } = useProteins()
  const { data: ligands, isLoading: ligandsLoading, isError: ligandsError } = useLigands()

  const {
    data: pdbData,
    isLoading: pdbLoading,
    error: pdbError,
  } = useProteinStructure(selectedProtein?.uniprot_id ?? null)

  const {
    data: sdfData,
    isLoading: sdfLoading,
    error: sdfError,
  } = useLigandStructure(selectedLigand?.pubchem_cid ?? null)

  const handleClearProtein = useCallback(() => setSelectedProtein(null), [])
  const handleClearLigand = useCallback(() => setSelectedLigand(null), [])

  return (
    <div>
      {/* Page header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold tracking-tight text-white sm:text-3xl">
          Molecule Viewer
        </h1>
        <p className="mt-2 max-w-xl text-sm leading-relaxed text-muted-foreground">
          Browse our curated protein and ligand libraries, then view their 3D
          structures in real time.
        </p>
      </div>

      {/* Selectors row */}
      <div className="grid gap-4 sm:grid-cols-2 mb-6">
        <MoleculeSelector
          kind="protein"
          items={proteins}
          isLoading={proteinsLoading}
          isError={proteinsError}
          selected={selectedProtein}
          onSelect={setSelectedProtein}
        />
        <MoleculeSelector
          kind="ligand"
          items={ligands}
          isLoading={ligandsLoading}
          isError={ligandsError}
          selected={selectedLigand}
          onSelect={setSelectedLigand}
        />
      </div>

      {/* 3D Viewers */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Protein Viewer */}
        <ViewerCard
          title={selectedProtein ? `${selectedProtein.name} (${selectedProtein.uniprot_id})` : 'Protein Structure'}
          subtitle={selectedProtein?.function}
          kind="protein"
          data={pdbData ?? null}
          format="pdb"
          isLoading={pdbLoading}
          error={pdbError ? String(pdbError) : null}
          externalUrl={
            selectedProtein
              ? `https://www.uniprot.org/uniprot/${selectedProtein.uniprot_id}`
              : undefined
          }
          externalLabel="UniProt"
          onClear={handleClearProtein}
          isEmpty={!selectedProtein}
          emptyIcon={<FlaskConical className="h-10 w-10 text-muted" />}
          emptyText="Select a protein above to view its AlphaFold-predicted 3D structure."
        />

        {/* Ligand Viewer */}
        <ViewerCard
          title={selectedLigand ? `${selectedLigand.name} (CID ${selectedLigand.pubchem_cid})` : 'Ligand Structure'}
          subtitle={selectedLigand?.description}
          kind="ligand"
          data={sdfData ?? null}
          format="sdf"
          isLoading={sdfLoading}
          error={sdfError ? String(sdfError) : null}
          externalUrl={
            selectedLigand
              ? `https://pubchem.ncbi.nlm.nih.gov/compound/${selectedLigand.pubchem_cid}`
              : undefined
          }
          externalLabel="PubChem"
          onClear={handleClearLigand}
          isEmpty={!selectedLigand}
          emptyIcon={<Atom className="h-10 w-10 text-muted" />}
          emptyText="Select a ligand above to view its 3D molecular structure."
        />
      </div>
    </div>
  )
}

// ---------------------------------------------------------------------------
// ViewerCard — wraps Viewer3D with a header bar & empty state
// ---------------------------------------------------------------------------

function ViewerCard({
  title,
  subtitle,
  kind,
  data,
  format,
  isLoading,
  error,
  externalUrl,
  externalLabel,
  onClear,
  isEmpty,
  emptyIcon,
  emptyText,
}: {
  title: string
  subtitle?: string
  kind: MoleculeKind
  data: string | null
  format: 'pdb' | 'sdf'
  isLoading: boolean
  error: string | null
  externalUrl?: string
  externalLabel?: string
  onClear: () => void
  isEmpty: boolean
  emptyIcon: React.ReactNode
  emptyText: string
}) {
  // Guard 1: Show empty state when nothing is selected AND not loading
  if (isEmpty && !isLoading) {
    return (
      <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-surface-border bg-surface/20 px-6 py-16 text-center">
        {emptyIcon}
        <p className="mt-3 max-w-xs text-sm text-muted-foreground">{emptyText}</p>
      </div>
    )
  }

  // Guard 2: Show loading state while fetching from AlphaFold/PubChem
  // This prevents mounting Viewer3D with null/undefined data
  if (isLoading) {
    return (
      <div className="overflow-hidden rounded-xl border border-surface-border bg-surface/60">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-surface-border px-4 py-3">
          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-2">
              <span className={cn('h-2 w-2 rounded-full', kind === 'protein' ? 'bg-emerald-400' : 'bg-secondary')} />
              <span className="truncate text-sm font-medium text-white">{title}</span>
            </div>
            {subtitle && (
              <p className="mt-0.5 truncate pl-4 text-[11px] text-muted-foreground">{subtitle}</p>
            )}
          </div>
        </div>

        {/* Loading State - No Viewer3D mounted yet */}
        <div className="flex flex-col items-center justify-center px-6 py-16" style={{ height: '380px' }}>
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <p className="mt-4 text-sm text-muted-foreground">
            Fetching structure from {kind === 'protein' ? 'AlphaFold...' : 'PubChem...'}
          </p>
          <p className="mt-2 text-xs text-muted-foreground/60">
            This may take a few seconds
          </p>
        </div>
      </div>
    )
  }

  // Guard 3: Show error state if API fetch failed
  if (error) {
    return (
      <div className="overflow-hidden rounded-xl border border-surface-border bg-surface/60">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-surface-border px-4 py-3">
          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-2">
              <span className={cn('h-2 w-2 rounded-full', kind === 'protein' ? 'bg-emerald-400' : 'bg-secondary')} />
              <span className="truncate text-sm font-medium text-white">{title}</span>
            </div>
          </div>
          <div className="flex items-center gap-2 ml-2 flex-shrink-0">
            <button
              type="button"
              onClick={onClear}
              className="inline-flex items-center gap-1 rounded-md px-2 py-1 text-[11px] text-muted-foreground hover:text-destructive transition-colors"
            >
              <RotateCcw className="h-3 w-3" /> Clear
            </button>
          </div>
        </div>

        {/* Error State */}
        <div className="flex flex-col items-center justify-center px-6 py-16" style={{ height: '380px' }}>
          <div className="rounded-full bg-destructive/10 p-3">
            <Atom className="h-6 w-6 text-destructive" />
          </div>
          <p className="mt-4 text-sm font-medium text-destructive">
            Failed to load structure
          </p>
          <p className="mt-2 text-xs text-muted-foreground text-center max-w-xs">
            {kind === 'protein' 
              ? 'AlphaFold may not have a prediction for this protein, or the service is temporarily unavailable.'
              : 'PubChem may not have a 3D structure for this compound.'
            }
          </p>
        </div>
      </div>
    )
  }

  // Guard 4: Only render Viewer3D when we have valid data
  if (!data) {
    return (
      <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-surface-border bg-surface/20 px-6 py-16 text-center">
        {emptyIcon}
        <p className="mt-3 max-w-xs text-sm text-muted-foreground">{emptyText}</p>
      </div>
    )
  }

  // Finally: Render the 3D Viewer with valid data
  return (
    <div className="overflow-hidden rounded-xl border border-surface-border bg-surface/60">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-surface-border px-4 py-3">
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2">
            <span className={cn('h-2 w-2 rounded-full', kind === 'protein' ? 'bg-emerald-400' : 'bg-secondary')} />
            <span className="truncate text-sm font-medium text-white">{title}</span>
          </div>
          {subtitle && (
            <p className="mt-0.5 truncate pl-4 text-[11px] text-muted-foreground">{subtitle}</p>
          )}
        </div>
        <div className="flex items-center gap-2 ml-2 flex-shrink-0">
          {externalUrl && (
            <a
              href={externalUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1 rounded-md px-2 py-1 text-[11px] text-muted-foreground hover:text-primary transition-colors"
            >
              {externalLabel} <ExternalLink className="h-3 w-3" />
            </a>
          )}
          <button
            type="button"
            onClick={onClear}
            className="inline-flex items-center gap-1 rounded-md px-2 py-1 text-[11px] text-muted-foreground hover:text-destructive transition-colors"
          >
            <RotateCcw className="h-3 w-3" /> Clear
          </button>
        </div>
      </div>

      {/* 3D Viewer - Only mounted when data is valid */}
      <MemoizedViewer3D
        data={data}
        format={format}
        title={title}
        height={380}
        isLoading={false}
        error={null}
      />
    </div>
  )
}
