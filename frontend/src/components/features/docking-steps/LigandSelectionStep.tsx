import { useState, useCallback, useMemo } from 'react'
import MemoizedViewer3D from '@/components/science/Viewer3D'
import { useLigands, useLigandStructure } from '@/hooks/useMoleculeLibrary'
import { useDockingStore } from '@/stores/useDockingStore'
import { cn } from '@/lib/cn'
import { toast } from 'sonner'
import type { Ligand } from '@/types/api'
import { ligandTypeColor } from '../pipeline/helpers'

import {
  Check,
  Search,
  Atom,
  ChevronDown,
  X,
  FileText,
  ExternalLink,
  Info,
  Loader2,
} from 'lucide-react'

// ---------------------------------------------------------------------------
// Step 2 — Ligand Selection (Wired to Zustand Store)
// ---------------------------------------------------------------------------

export function LigandSelectionStep() {
  // ── Zustand Store State ───────────────────────────────────────────────
  const {
    customPdbData,
    selectedProtein,
    customPdbName,
    selectedLigand,
    setSelectedLigand,
    ligandSmiles,
    setLigandSmiles,
    resetDocking,
  } = useDockingStore()

  // Step 1 is complete if we have protein data
  const step1Complete = !!(selectedProtein || customPdbData)

  // ── Local UI state ──────────────────────────────────────────────────
  const [useCustomSmilesMode, setUseCustomSmilesMode] = useState(false)
  const [customSmilesInput, setCustomSmilesInput] = useState('')
  const [ligandSearchQuery, setLigandSearchQuery] = useState('')
  const [ligandDropdownOpen, setLigandDropdownOpen] = useState(false)

  // ── Data hooks ───────────────────────────────────────────────────────
  const { data: ligands, isLoading: ligandsLoading, isError: ligandsError } = useLigands()

  const selectedCid = selectedLigand?.pubchem_cid ?? null
  const {
    data: ligandSdfData,
    isLoading: isLoadingPubChem,
    error: ligandSdfError,
  } = useLigandStructure(selectedCid)

  // ── Filtered ligand list ────────────────────────────────────────────
  const filteredLigands = useMemo(() => {
    const list = ligands ?? []
    if (!ligandSearchQuery.trim()) return list
    const q = ligandSearchQuery.toLowerCase()
    return list.filter(
      (l) =>
        l.name.toLowerCase().includes(q) ||
        l.type.toLowerCase().includes(q) ||
        l.description.toLowerCase().includes(q),
    )
  }, [ligands, ligandSearchQuery])

  // ── Handlers ────────────────────────────────────────────────────────
  const handleLigandSelect = useCallback(
    (ligand: Ligand) => {
      setSelectedLigand(ligand)
      setLigandSmiles(ligand.smiles)
      setUseCustomSmilesMode(false)
      setCustomSmilesInput('')
      setLigandDropdownOpen(false)
      setLigandSearchQuery('')
    },
    [setSelectedLigand, setLigandSmiles],
  )

  const handleCustomSmilesCommit = useCallback(() => {
    const trimmed = customSmilesInput.trim()
    if (!trimmed) {
      toast.warning('Please enter a valid SMILES string')
      return
    }
    setSelectedLigand(null)
    setLigandSmiles(trimmed)
    toast.success('Custom SMILES accepted', {
      description: trimmed.length > 50 ? trimmed.slice(0, 50) + '…' : trimmed,
    })
  }, [customSmilesInput, setSelectedLigand, setLigandSmiles])

  const handleClearLigand = useCallback(() => {
    setSelectedLigand(null)
    setLigandSmiles(null)
    setUseCustomSmilesMode(false)
    setCustomSmilesInput('')
    setLigandSearchQuery('')
    resetDocking()
  }, [setSelectedLigand, setLigandSmiles, resetDocking])

  // ── JSX ─────────────────────────────────────────────────────────────
  return (
    <div className="min-h-[400px] animate-in fade-in slide-in-from-right-4 duration-300">
      <div className="mb-5">
        <h2 className="text-xl font-semibold text-white">Ligand Selection</h2>
        <p className="mt-1 text-sm text-muted-foreground">
          Choose a drug or ligand from the curated library, or paste a custom SMILES string
        </p>
      </div>

      {/* Summary of Step 1 selection */}
      {step1Complete && (
        <div className="mb-6 flex items-center gap-3 rounded-xl border border-emerald-500/30 bg-emerald-500/5 px-4 py-3">
          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-emerald-500/20">
            <Check className="h-4 w-4 text-emerald-400" />
          </div>
          <div className="text-sm">
            <span className="font-medium text-emerald-300">Protein selected: </span>
            <span className="text-muted-foreground">
              {selectedProtein
                ? `${selectedProtein.name} (${selectedProtein.uniprot_id})`
                : customPdbName ?? 'Custom PDB'}
            </span>
          </div>
        </div>
      )}

      <div className="space-y-4">
        {/* Mode toggle: Library / Custom SMILES */}
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => setUseCustomSmilesMode(false)}
            className={cn(
              'inline-flex items-center gap-1.5 rounded-lg px-4 py-2 text-sm font-medium transition-all',
              !useCustomSmilesMode
                ? 'bg-primary/15 text-primary border border-primary/30'
                : 'text-muted-foreground hover:text-white hover:bg-surface-highlight border border-transparent',
            )}
          >
            <Atom className="h-3.5 w-3.5" />
            Curated Library
          </button>
          <button
            type="button"
            onClick={() => { setUseCustomSmilesMode(true); setSelectedLigand(null) }}
            className={cn(
              'inline-flex items-center gap-1.5 rounded-lg px-4 py-2 text-sm font-medium transition-all',
              useCustomSmilesMode
                ? 'bg-primary/15 text-primary border border-primary/30'
                : 'text-muted-foreground hover:text-white hover:bg-surface-highlight border border-transparent',
            )}
          >
            <FileText className="h-3.5 w-3.5" />
            Paste Custom SMILES
          </button>
        </div>

        {/* Custom SMILES input */}
        {useCustomSmilesMode && (
          <div className="space-y-3 rounded-xl border border-surface-border bg-surface/40 p-5">
            <label htmlFor="custom-smiles" className="block text-xs font-bold uppercase tracking-widest text-muted">
              SMILES String
            </label>
            <div className="flex gap-3">
              <input
                id="custom-smiles"
                type="text"
                placeholder="e.g. CC(=O)Oc1ccccc1C(O)=O"
                value={customSmilesInput}
                onChange={(e) => setCustomSmilesInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleCustomSmilesCommit()}
                className="flex-1 rounded-lg border border-surface-border bg-surface-highlight px-4 py-2.5 text-sm
                           text-white placeholder-muted outline-none transition-colors
                           focus:border-primary focus:ring-1 focus:ring-primary/30"
              />
              <button
                type="button"
                onClick={handleCustomSmilesCommit}
                disabled={!customSmilesInput.trim()}
                className={cn(
                  'rounded-lg px-5 py-2.5 text-sm font-semibold transition-all',
                  customSmilesInput.trim()
                    ? 'bg-primary text-white hover:bg-primary/90 shadow-lg shadow-primary/20'
                    : 'bg-surface-highlight text-muted cursor-not-allowed',
                )}
              >
                Use SMILES
              </button>
            </div>
            <p className="text-xs text-muted">
              3D preview is only available for curated ligands. Custom SMILES will proceed directly to docking.
            </p>
          </div>
        )}

        {/* Curated ligand library */}
        {!useCustomSmilesMode && (
          <>
            {ligandsLoading && (
              <div className="flex items-center gap-2 py-8 justify-center">
                <Loader2 className="h-5 w-5 animate-spin text-primary" />
                <span className="text-sm text-muted-foreground">Loading ligand library…</span>
              </div>
            )}

            {ligandsError && (
              <div className="rounded-xl border border-destructive/30 bg-destructive/5 px-5 py-4 text-center">
                <p className="text-sm text-destructive">
                  Could not reach the backend — is it running on <code className="text-destructive/80">:8000</code>?
                </p>
              </div>
            )}

            {!ligandsLoading && !ligandsError && (
              <div className="relative">
                {/* Dropdown trigger */}
                <button
                  type="button"
                  onClick={() => setLigandDropdownOpen((o) => !o)}
                  className={cn(
                    'flex w-full items-center justify-between rounded-xl border px-4 py-3 text-left text-sm transition-colors',
                    ligandDropdownOpen
                      ? 'border-primary bg-surface-highlight ring-1 ring-primary/30'
                      : 'border-surface-border bg-surface-highlight/60 hover:border-muted',
                  )}
                >
                  {selectedLigand ? (
                    <span className="flex items-center gap-2">
                      <span className="h-2 w-2 rounded-full bg-secondary" />
                      <span className="font-medium text-white">{selectedLigand.name}</span>
                      <span className="text-xs text-muted-foreground">CID {selectedLigand.pubchem_cid}</span>
                    </span>
                  ) : (
                    <span className="text-muted-foreground">Select a ligand…</span>
                  )}
                  <ChevronDown className={cn('h-4 w-4 text-muted-foreground transition-transform', ligandDropdownOpen && 'rotate-180')} />
                </button>

                {/* Dropdown panel */}
                {ligandDropdownOpen && (
                  <div className="absolute z-30 mt-2 w-full rounded-xl border border-surface-border bg-surface shadow-2xl shadow-black/50">
                    {/* Search inside dropdown */}
                    <div className="border-b border-surface-border px-3 py-2">
                      <div className="relative">
                        <Search className="absolute left-2.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-muted" />
                        <input
                          type="text"
                          value={ligandSearchQuery}
                          onChange={(e) => setLigandSearchQuery(e.target.value)}
                          placeholder="Search name, type, description…"
                          autoFocus
                          className="w-full rounded-lg bg-surface-highlight py-2 pl-8 pr-3 text-xs text-white placeholder-muted focus:outline-none"
                        />
                      </div>
                    </div>

                    <div className="max-h-60 overflow-y-auto overscroll-contain py-1">
                      {filteredLigands.length === 0 ? (
                        <p className="px-4 py-6 text-center text-xs text-muted-foreground">
                          No results for &ldquo;{ligandSearchQuery}&rdquo;
                        </p>
                      ) : (
                        filteredLigands.map((l) => {
                          const isSelected = selectedLigand?.id === l.id
                          return (
                            <button
                              key={l.id}
                              type="button"
                              onClick={() => handleLigandSelect(l)}
                              className={cn(
                                'flex w-full items-start gap-3 px-4 py-3 text-left transition-colors',
                                isSelected ? 'bg-primary/5' : 'hover:bg-surface-highlight',
                              )}
                            >
                              <div className="min-w-0 flex-1">
                                <div className="flex items-center gap-2">
                                  <span className="text-sm font-medium text-white">
                                    {l.name}
                                  </span>
                                  <span className={cn(
                                    'rounded-full px-1.5 py-0.5 text-[10px] font-bold uppercase',
                                    ligandTypeColor(l.type),
                                  )}>
                                    {l.type}
                                  </span>
                                </div>
                                <p className="mt-0.5 text-[11px] text-muted-foreground truncate">
                                  CID {l.pubchem_cid} · {l.description}
                                </p>
                              </div>
                            </button>
                          )
                        })
                      )}
                    </div>
                  </div>
                )}
              </div>
            )}
          </>
        )}

        {/* PubChem loading indicator */}
        {isLoadingPubChem && selectedLigand && (
          <div className="flex items-center gap-3 rounded-xl border border-primary/20 bg-primary/5 px-4 py-3">
            <Loader2 className="h-4 w-4 animate-spin text-primary" />
            <span className="text-sm text-muted-foreground">
              Fetching 3D structure for <span className="font-medium text-white">{selectedLigand.name}</span> from PubChem…
            </span>
          </div>
        )}

        {/* PubChem error */}
        {ligandSdfError && selectedLigand && !isLoadingPubChem && (
          <div className="flex items-start gap-2 rounded-xl border border-destructive/20 bg-destructive/5 px-4 py-3">
            <Info className="mt-0.5 h-4 w-4 shrink-0 text-destructive" />
            <div className="text-sm">
              <p className="font-medium text-destructive">3D structure unavailable</p>
              <p className="mt-0.5 text-xs text-muted-foreground">
                Could not fetch from PubChem. The SMILES is still valid for docking.
              </p>
            </div>
          </div>
        )}

        {/* 3D Ligand Viewer */}
        {ligandSdfData && selectedLigand && !isLoadingPubChem && (
          <div className="overflow-hidden rounded-xl border border-surface-border bg-surface/60">
            {/* Header bar */}
            <div className="flex items-center justify-between border-b border-surface-border px-4 py-3">
              <div className="flex items-center gap-2">
                <span className="h-2 w-2 rounded-full bg-primary" />
                <span className="text-sm font-medium text-white">{selectedLigand.name}</span>
                <span className={cn(
                  'rounded-full px-1.5 py-0.5 text-[10px] font-bold uppercase',
                  ligandTypeColor(selectedLigand.type),
                )}>
                  {selectedLigand.type}
                </span>
              </div>
              <div className="flex items-center gap-2">
                <a
                  href={`https://pubchem.ncbi.nlm.nih.gov/compound/${selectedLigand.pubchem_cid}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1 text-[11px] text-muted-foreground transition-colors hover:text-primary"
                >
                  PubChem <ExternalLink className="h-3 w-3" />
                </a>
                <button
                  type="button"
                  onClick={handleClearLigand}
                  className="inline-flex items-center gap-1 rounded-md px-2 py-1 text-[11px]
                             text-destructive transition-colors hover:bg-destructive/10"
                >
                  <X className="h-3 w-3" /> Clear
                </button>
              </div>
            </div>

            {/* 3Dmol viewer */}
            <MemoizedViewer3D
              data={ligandSdfData}
              format="sdf"
              title={selectedLigand.name}
              height={340}
              isLoading={false}
              error={null}
            />
          </div>
        )}

        {/* SMILES confirmation */}
        {ligandSmiles && (
          <div className="flex items-center gap-3 rounded-xl border border-emerald-500/30 bg-emerald-500/5 px-4 py-3">
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-emerald-500/20">
              <Check className="h-4 w-4 text-emerald-400" />
            </div>
            <div className="min-w-0 flex-1 text-sm">
              <span className="font-medium text-emerald-300">SMILES ready for docking</span>
              <p className="mt-0.5 truncate font-mono text-[11px] text-muted-foreground">
                {ligandSmiles}
              </p>
            </div>
            <button
              type="button"
              onClick={handleClearLigand}
              className="shrink-0 text-muted-foreground transition-colors hover:text-destructive"
            >
              <X className="h-3.5 w-3.5" />
            </button>
          </div>
        )}

        {/* Inline helper when nothing selected */}
        {!ligandSmiles && !ligandsLoading && !useCustomSmilesMode && (
          <div className="flex items-start gap-2 rounded-lg bg-surface-highlight/30 px-4 py-3">
            <Info className="mt-0.5 h-4 w-4 shrink-0 text-muted" />
            <p className="text-xs leading-relaxed text-muted-foreground">
              Select a ligand above to fetch its 3D structure from PubChem and prepare it for docking.
            </p>
          </div>
        )}
      </div>
    </div>
  )
}
