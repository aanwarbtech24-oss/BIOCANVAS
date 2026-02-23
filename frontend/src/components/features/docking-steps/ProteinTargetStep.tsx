import { useState, useRef, useCallback, useMemo } from 'react'
import { Viewer3D } from '@/components/science/Viewer3D'
import { useProteins, useProteinStructure } from '@/hooks/useMoleculeLibrary'
import { useDockingStore } from '@/stores/useDockingStore'
import { cn } from '@/lib/cn'
import { toast } from 'sonner'
import type { Protein } from '@/types/api'
import { categoryColor } from '../pipeline/helpers'

import {
  Check,
  Upload,
  Search,
  
  X,
  
  ExternalLink,
  Info,
  Loader2,
} from 'lucide-react'

// ---------------------------------------------------------------------------
// Step 1 — Protein Target Selection (Wired to Zustand Store)
// ---------------------------------------------------------------------------

export function ProteinTargetStep() {
  // ── Zustand Store State ───────────────────────────────────────────────
  const {
    selectedProtein,
    setSelectedProtein,
    customPdbData,
    setCustomPdbData,
    customPdbName,
    setCustomPdbName,
    proteinPdbData,
    setProteinPdbData,
    resetLigandAndDocking,
  } = useDockingStore()

  // ── Local UI state ───────────────────────────────────────────────────
  const [searchQuery, setSearchQuery] = useState('')
  const [dropdownOpen, setDropdownOpen] = useState(true)  // Show dropdown by default
  const [showCustomUpload, setShowCustomUpload] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  // ── Data hooks ───────────────────────────────────────────────────────
  const { data: proteins, isLoading: proteinsLoading, isError: proteinsError } = useProteins()

  const selectedUniprotId = selectedProtein?.uniprot_id ?? null
  const {
    data: pdbData,
    isLoading: pdbLoading,
    error: pdbError,
  } = useProteinStructure(customPdbData ? null : selectedUniprotId)

  const viewerData = customPdbData ?? pdbData ?? null

  // Store fetched PDB data when it changes (for library proteins)
  useMemo(() => {
    if (pdbData && selectedProtein) {
      setProteinPdbData(pdbData)
    }
  }, [pdbData, selectedProtein, setProteinPdbData])

  // ── Filtered protein list ───────────────────────────────────────────
  const filtered = useMemo(() => {
    const list = proteins ?? []
    if (!searchQuery.trim()) return list
    const q = searchQuery.toLowerCase()
    return list.filter(
      (p) =>
        p.name.toLowerCase().includes(q) ||
        p.uniprot_id.toLowerCase().includes(q) ||
        p.function.toLowerCase().includes(q),
    )
  }, [proteins, searchQuery])

  // ── Handlers ────────────────────────────────────────────────────────
  const handleSelectProtein = useCallback((protein: Protein) => {
    setSelectedProtein(protein)
    setCustomPdbData(null)
    setCustomPdbName(null)
    setDropdownOpen(false)
    setSearchQuery('')
    toast.success(`Selected ${protein.name}`)
  }, [setSelectedProtein, setCustomPdbData, setCustomPdbName])

  const handleCustomUpload = useCallback(() => {
    fileInputRef.current?.click()
  }, [])

  const handleFileChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    if (!file.name.endsWith('.pdb')) {
      toast.error('Only .pdb files are supported')
      return
    }

    const reader = new FileReader()
    reader.onload = (event) => {
      const content = event.target?.result as string
      if (content) {
        setCustomPdbData(content)
        setCustomPdbName(file.name.replace('.pdb', ''))
        setSelectedProtein(null)
        toast.success(`Loaded custom PDB: ${file.name}`)
      }
    }
    reader.readAsText(file)
    e.target.value = ''
  }, [setCustomPdbData, setCustomPdbName, setSelectedProtein])

  const handleClear = useCallback(() => {
    setSelectedProtein(null)
    setCustomPdbData(null)
    setCustomPdbName(null)
    resetLigandAndDocking()
  }, [setSelectedProtein, setCustomPdbData, setCustomPdbName, resetLigandAndDocking])

  const viewerTitle = selectedProtein?.name ?? 'Protein Structure'

  // ── JSX ─────────────────────────────────────────────────────────────
  return (
    <div className="min-h-[400px] animate-in fade-in slide-in-from-right-4 duration-300">
      <div className="mb-5">
        <h2 className="text-xl font-semibold text-white">Protein Target</h2>
        <p className="mt-1 text-sm text-muted-foreground">
          Choose a protein from the library or upload your own PDB file
        </p>
      </div>

      <div className="space-y-4">
        {/* Mode toggle: Library / Custom PDB */}
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => setShowCustomUpload(false)}
            className={cn(
              'inline-flex items-center gap-1.5 rounded-lg px-4 py-2 text-sm font-medium transition-all',
              !showCustomUpload
                ? 'bg-primary/15 text-primary border border-primary/30'
                : 'text-muted-foreground hover:text-white hover:bg-surface-highlight border border-transparent',
            )}
          >
            <Search className="h-3.5 w-3.5" />
            Protein Library
          </button>
          <button
            type="button"
            onClick={() => { setShowCustomUpload(true); setSelectedProtein(null) }}
            className={cn(
              'inline-flex items-center gap-1.5 rounded-lg px-4 py-2 text-sm font-medium transition-all',
              showCustomUpload
                ? 'bg-primary/15 text-primary border border-primary/30'
                : 'text-muted-foreground hover:text-white hover:bg-surface-highlight border border-transparent',
            )}
          >
            <Upload className="h-3.5 w-3.5" />
            Upload Custom PDB
          </button>
        </div>

        {/* Custom PDB upload */}
        {showCustomUpload && (
          <div className="space-y-3 rounded-xl border border-surface-border bg-surface/40 p-5">
            <div className="flex items-center justify-between">
              <label className="text-xs font-bold uppercase tracking-widest text-muted">
                PDB File
              </label>
              {customPdbName && (
                <button
                  type="button"
                  onClick={handleClear}
                  className="text-xs text-destructive hover:underline"
                >
                  Clear
                </button>
              )}
            </div>
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdb"
              onChange={handleFileChange}
              className="hidden"
            />
            <button
              type="button"
              onClick={handleCustomUpload}
              className={cn(
                'flex w-full items-center justify-center gap-2 rounded-lg border-2 border-dashed p-4 transition-colors',
                customPdbData
                  ? 'border-emerald-500/30 bg-emerald-500/5'
                  : 'border-surface-border hover:border-muted',
              )}
            >
              {customPdbData ? (
                <>
                  <Check className="h-4 w-4 text-emerald-400" />
                  <span className="text-sm text-emerald-300">{customPdbName}.pdb</span>
                </>
              ) : (
                <>
                  <Upload className="h-4 w-4 text-muted" />
                  <span className="text-sm text-muted-foreground">
                    Click to upload a .pdb file
                  </span>
                </>
              )}
            </button>
            <p className="text-xs text-muted">
              Upload a protein structure in PDB format. The file will be used for molecular docking.
            </p>
          </div>
        )}

        {/* Protein library */}
        {!showCustomUpload && (
          <>
            {proteinsLoading && (
              <div className="flex items-center gap-2 py-8 justify-center">
                <Loader2 className="h-5 w-5 animate-spin text-primary" />
                <span className="text-sm text-muted-foreground">Loading protein library…</span>
              </div>
            )}

            {proteinsError && (
              <div className="rounded-xl border border-destructive/30 bg-destructive/5 px-5 py-4 text-center">
                <p className="text-sm text-destructive">
                  Could not reach the backend — is it running on <code className="text-destructive/80">:8000</code>?
                </p>
              </div>
            )}

            {!proteinsLoading && !proteinsError && (
              <div className="space-y-3">
                {/* Search bar */}
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-muted" />
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => { setSearchQuery(e.target.value); setDropdownOpen(true) }}
                    placeholder="Search by name, UniProt ID, or function…"
                    className="w-full rounded-lg border border-surface-border bg-surface-highlight py-2.5 pl-9 pr-3 text-sm text-white placeholder-muted outline-none transition-colors focus:border-primary focus:ring-1 focus:ring-primary/30"
                  />
                </div>

                {/* Protein dropdown */}
                {dropdownOpen && (
                  <div className="max-h-64 overflow-y-auto rounded-xl border border-surface-border bg-surface/80">
                    {filtered.length === 0 ? (
                      <p className="p-4 text-center text-xs text-muted-foreground">
                        No proteins match &ldquo;{searchQuery}&rdquo;
                      </p>
                    ) : (
                      filtered.slice(0, 10).map((p) => (
                        <button
                          key={p.id}
                          type="button"
                          onClick={() => handleSelectProtein(p)}
                          className="flex w-full items-start gap-3 px-4 py-3 text-left hover:bg-surface-highlight/50"
                        >
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2">
                              <span className="text-sm font-medium text-white truncate">
                                {p.name}
                              </span>
                              <span className={cn('rounded-full px-1.5 py-0.5 text-[9px] font-bold uppercase', categoryColor(p.category))}>
                                {p.category}
                              </span>
                            </div>
                            <p className="mt-0.5 font-mono text-[10px] text-muted-foreground">
                              {p.uniprot_id}
                            </p>
                          </div>
                        </button>
                      ))
                    )}
                  </div>
                )}
              </div>
            )}
          </>
        )}

        {/* 3D Viewer */}
        <div className="space-y-3">
          {(viewerData || pdbLoading) && (
            <div className="overflow-hidden rounded-xl border border-surface-border bg-surface/60">
              {/* Header bar */}
              <div className="flex items-center justify-between border-b border-surface-border px-4 py-3">
                <div className="flex items-center gap-2">
                  <span className="h-2 w-2 rounded-full bg-emerald-400" />
                  <span className="text-sm font-medium text-white">
                    {selectedProtein
                      ? viewerTitle
                      : customPdbName
                        ? `Custom: ${customPdbName}`
                        : 'Loading…'}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  {selectedProtein && (
                    <a
                      href={`https://www.uniprot.org/uniprot/${selectedProtein.uniprot_id}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1 text-[11px] text-muted-foreground transition-colors hover:text-primary"
                    >
                      UniProt <ExternalLink className="h-3 w-3" />
                    </a>
                  )}
                  <button
                    type="button"
                    onClick={handleClear}
                    className="inline-flex items-center gap-1 rounded-md px-2 py-1 text-[11px]
                               text-destructive transition-colors hover:bg-destructive/10"
                  >
                    <X className="h-3 w-3" /> Clear
                  </button>
                </div>
              </div>

              {/* 3Dmol Viewer */}
              <Viewer3D
                data={viewerData}
                format="pdb"
                title={viewerTitle}
                height={420}
                isLoading={pdbLoading}
                error={pdbError ? String(pdbError) : null}
              />
            </div>
          )}

          {/* Inline helper when nothing selected */}
          {!viewerData && !pdbLoading && !proteinsLoading && (
            <div className="flex items-start gap-2 rounded-lg bg-surface-highlight/30 px-4 py-3">
              <Info className="mt-0.5 h-4 w-4 shrink-0 text-muted" />
              <p className="text-xs leading-relaxed text-muted-foreground">
                Select a protein above to fetch its AlphaFold-predicted structure and render it in 3D.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
