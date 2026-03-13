import { useState, useRef, useCallback, useMemo } from 'react'
import { Viewer3D } from '@/components/science/Viewer3D'
import { useProteins, useProteinStructure } from '@/hooks/useMoleculeLibrary'
import { cn } from '@/lib/cn'
import { toast } from 'sonner'
import type { Protein } from '@/types/api'
import { categoryColor } from '../pipeline/helpers'

import {
  Check,
  Upload,
  Search,
  ChevronDown,
  X,
  FileText,
  ExternalLink,
  Info,
  Loader2,
} from 'lucide-react'

// ---------------------------------------------------------------------------
// Props — everything the parent passes down
// ---------------------------------------------------------------------------

export interface Step1Props {
  selectedProtein: Protein | null
  setSelectedProtein: (p: Protein | null) => void
  customPdbData: string | null
  setCustomPdbData: (d: string | null) => void
  customPdbName: string | null
  setCustomPdbName: (n: string | null) => void
  /** Called when the entire protein selection is cleared or replaced */
  onClear: () => void
}

// ---------------------------------------------------------------------------
// Step 1 — Protein Target Selection
// ---------------------------------------------------------------------------

export function Step1_ProteinTarget({
  selectedProtein,
  setSelectedProtein,
  customPdbData,
  setCustomPdbData,
  customPdbName,
  setCustomPdbName,
  onClear,
}: Step1Props) {
  // ── Local UI state (no need to lift — only relevant within this step) ──
  const [searchQuery, setSearchQuery] = useState('')
  const [dropdownOpen, setDropdownOpen] = useState(false)
  const [showCustomUpload, setShowCustomUpload] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  // ── Data hooks ──────────────────────────────────────────────────────
  const { data: proteins, isLoading: proteinsLoading, isError: proteinsError } = useProteins()

  const selectedUniprotId = selectedProtein?.uniprot_id ?? null
  const {
    data: pdbData,
    isLoading: pdbLoading,
    error: pdbError,
  } = useProteinStructure(customPdbData ? null : selectedUniprotId)

  const viewerData = customPdbData ?? pdbData ?? null

  // ── Filtered protein list ───────────────────────────────────────────
  const filtered = useMemo(() => {
    const list = proteins ?? []
    if (!searchQuery.trim()) return list
    const q = searchQuery.toLowerCase()
    return list.filter(
      (p) =>
        p.name.toLowerCase().includes(q) ||
        p.uniprot_id.toLowerCase().includes(q) ||
        p.category.toLowerCase().includes(q),
    )
  }, [proteins, searchQuery])

  // ── Viewer title ────────────────────────────────────────────────────
  const viewerTitle = useMemo(
    () =>
      selectedProtein
        ? `${selectedProtein.name} (${selectedProtein.uniprot_id})`
        : customPdbName ?? 'Protein Structure',
    [selectedProtein, customPdbName],
  )

  // ── Handlers ────────────────────────────────────────────────────────
  const handleSelectProtein = useCallback(
    (protein: Protein) => {
      setSelectedProtein(protein)
      setCustomPdbData(null)
      setCustomPdbName(null)
      setDropdownOpen(false)
      setSearchQuery('')
      // Parent resets downstream steps via onClear's sibling logic
    },
    [setSelectedProtein, setCustomPdbData, setCustomPdbName],
  )

  const handleFileUpload = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0]
      if (!file) return
      if (!file.name.endsWith('.pdb') && !file.name.endsWith('.pdbqt')) {
        toast.warning('Please upload a .pdb or .pdbqt file')
        if (e.target) e.target.value = ''
        return
      }
      const reader = new FileReader()
      reader.onload = () => {
        const text = reader.result as string
        if (text.length < 50) {
          toast.error('PDB file appears empty')
          return
        }
        setSelectedProtein(null)
        setCustomPdbData(text)
        setCustomPdbName(file.name)
        toast.success(`Loaded ${file.name}`, {
          description: `Custom PDB · ${(file.size / 1024).toFixed(1)} KB`,
        })
      }
      reader.onerror = () => toast.error('Failed to read file')
      reader.readAsText(file)
    },
    [setSelectedProtein, setCustomPdbData, setCustomPdbName],
  )

  const handleClear = useCallback(() => {
    setSelectedProtein(null)
    setCustomPdbData(null)
    setCustomPdbName(null)
    setShowCustomUpload(false)
    if (fileInputRef.current) fileInputRef.current.value = ''
    onClear()
  }, [setSelectedProtein, setCustomPdbData, setCustomPdbName, onClear])

  // ── JSX ─────────────────────────────────────────────────────────────
  return (
    <div className="min-h-[400px] animate-in fade-in slide-in-from-right-4 duration-300">
      <div className="mb-5">
        <h2 className="text-xl font-semibold text-white">Protein Target Selection</h2>
        <p className="mt-1 text-sm text-muted-foreground">
          Choose a curated receptor or upload your own PDB file
        </p>
      </div>

      <div className="space-y-4">
        {/* Protein dropdown */}
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
          <div className="relative">
            {/* Trigger button */}
            <button
              type="button"
              onClick={() => setDropdownOpen((o) => !o)}
              className={cn(
                'flex w-full items-center justify-between rounded-xl border px-4 py-3 text-left text-sm transition-colors',
                dropdownOpen
                  ? 'border-primary bg-surface-highlight ring-1 ring-primary/30'
                  : 'border-surface-border bg-surface-highlight/60 hover:border-muted',
              )}
            >
              {selectedProtein ? (
                <span className="flex items-center gap-2">
                  <span className="h-2 w-2 rounded-full bg-emerald-400" />
                  <span className="font-medium text-white">{selectedProtein.name}</span>
                  <span className="text-muted-foreground">({selectedProtein.uniprot_id})</span>
                </span>
              ) : (
                <span className="text-muted-foreground">Select a protein target…</span>
              )}
              <ChevronDown
                className={cn('h-4 w-4 text-muted-foreground transition-transform', dropdownOpen && 'rotate-180')}
              />
            </button>

            {/* Dropdown panel */}
            {dropdownOpen && (
              <div className="absolute z-30 mt-2 w-full rounded-xl border border-surface-border bg-surface shadow-2xl shadow-black/50">
                {/* Search */}
                <div className="border-b border-surface-border px-3 py-2">
                  <div className="relative">
                    <Search className="absolute left-2.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-muted" />
                    <input
                      type="text"
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      placeholder="Search by name, UniProt ID, category…"
                      autoFocus
                      className="w-full rounded-lg bg-surface-highlight py-2 pl-8 pr-3 text-xs text-white placeholder-muted focus:outline-none"
                    />
                  </div>
                </div>

                {/* List */}
                <div className="max-h-72 overflow-y-auto overscroll-contain py-1">
                  {filtered.length === 0 && (
                    <p className="px-4 py-6 text-center text-xs text-muted-foreground">
                      No proteins match &ldquo;{searchQuery}&rdquo;
                    </p>
                  )}
                  {filtered.map((p) => (
                    <button
                      key={p.id}
                      type="button"
                      onClick={() => handleSelectProtein(p)}
                      className={cn(
                        'flex w-full items-start gap-3 px-4 py-3 text-left transition-colors',
                        selectedProtein?.id === p.id ? 'bg-primary/5' : 'hover:bg-surface-highlight',
                      )}
                    >
                      <div className="min-w-0 flex-1">
                        <div className="flex items-center gap-2">
                          <span className="text-sm font-medium text-white">{p.name}</span>
                          <span
                            className={cn(
                              'rounded-full px-1.5 py-0.5 text-[10px] font-bold uppercase',
                              categoryColor(p.category),
                            )}
                          >
                            {p.category}
                          </span>
                        </div>
                        <p className="mt-0.5 text-[11px] text-muted-foreground">
                          {p.uniprot_id} · {p.function.length > 80 ? p.function.slice(0, 80) + '…' : p.function}
                        </p>
                      </div>
                      {selectedProtein?.id === p.id && (
                        <Check className="mt-0.5 h-4 w-4 shrink-0 text-primary" />
                      )}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Custom upload toggle */}
        <div className="flex items-center gap-3 border-t border-surface-border/50 pt-3">
          <button
            type="button"
            onClick={() => setShowCustomUpload((v) => !v)}
            className="inline-flex items-center gap-1.5 text-xs font-medium text-muted-foreground transition-colors hover:text-primary"
          >
            <Upload className="h-3.5 w-3.5" />
            Or upload custom PDB
            <ChevronDown className={cn('h-3 w-3 transition-transform', showCustomUpload && 'rotate-180')} />
          </button>
        </div>

        {showCustomUpload && (
          <div
            onClick={() => fileInputRef.current?.click()}
            className="group cursor-pointer rounded-xl border-2 border-dashed border-surface-border bg-surface/20
                       px-6 py-6 text-center transition-colors hover:border-muted hover:bg-surface-highlight/40"
          >
            <Upload className="mx-auto mb-2 h-6 w-6 text-muted group-hover:text-muted-foreground" />
            <p className="text-sm text-muted-foreground">
              Click to upload a <code className="text-primary">.pdb</code> file
            </p>
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdb,.pdbqt"
              onChange={handleFileUpload}
              className="hidden"
            />
          </div>
        )}

        {/* Uploaded file indicator */}
        {customPdbName && (
          <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-primary/10 border border-primary/30 text-xs text-primary">
            <FileText className="w-3.5 h-3.5 flex-shrink-0" />
            <span className="truncate flex-1">{customPdbName}</span>
            <button type="button" onClick={handleClear} className="hover:text-white transition-colors">
              <X className="w-3.5 h-3.5" />
            </button>
          </div>
        )}

        {/* 3D Viewer */}
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
  )
}
