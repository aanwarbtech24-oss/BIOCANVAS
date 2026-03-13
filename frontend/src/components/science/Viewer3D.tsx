import { useEffect, useRef, useState, memo } from 'react'
import type { ReactNode } from 'react'
import { Card, CardContent } from '@/components/ui/Card'
import { LoadingSpinner } from '@/components/ui/LoadingSpinner'
import { cn } from '@/lib/cn'
import { Maximize2, Palette } from 'lucide-react'

/* ═══════════════════════════════════════════════════════════════════════
 * 3Dmol – loaded via CDN <script> tag in index.html.
 * Accessing it from window.$3Dmol avoids all Vite CJS interop issues.
 * ═══════════════════════════════════════════════════════════════════════ */
// eslint-disable-next-line @typescript-eslint/no-explicit-any
function get3Dmol(): any {
  return (window as any).$3Dmol
}

/* ═══════════════════════════════════════════════════════════════════════
 * Types
 * ═══════════════════════════════════════════════════════════════════════ */

interface Viewer3DProps {
  data: string | null
  format: 'pdb' | 'sdf'
  title?: string
  height?: number
  square?: boolean
  embedded?: boolean
  isLoading?: boolean
  error?: string | null
}

/* ═══════════════════════════════════════════════════════════════════════
 * Component
 * ═══════════════════════════════════════════════════════════════════════ */

function Viewer3DInner({
  data,
  format,
  title = 'Molecular Structure',
  height = 500,
  square = false,
  embedded = false,
  isLoading = false,
  error = null,
}: Viewer3DProps): ReactNode {
  const containerRef = useRef<HTMLDivElement>(null)
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const viewerRef = useRef<any>(null)
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const surfaceRef = useRef<any>(null)
  
  // Default representation based on format: PDB = cartoon, SDF = stick
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [representation, setRepresentation] = useState<'cartoon' | 'surface' | 'sphere' | 'stick'>(
    format === 'sdf' ? 'stick' : 'cartoon'
  )

  // Minimum valid PDB should have at least several lines with ATOM/HETATM
  const hasValidData = data && typeof data === 'string' && data.trim().length >= 200

  // Initialize 3Dmol viewer when data changes
  // IMPORTANT: All hooks must be called unconditionally (React Rules of Hooks)
  useEffect(() => {
    // Guard inside the effect, not before it
    if (!hasValidData || !containerRef.current) {
      return
    }
    
    const $3Dmol = get3Dmol()
    if (!$3Dmol) {
      console.warn('3Dmol not loaded yet')
      return
    }

    // Clean up previous viewer and surface
    if (viewerRef.current) {
      try {
        if (surfaceRef.current) {
          viewerRef.current.removeSurface(surfaceRef.current)
          surfaceRef.current = null
        }
        viewerRef.current.clear()
      } catch (e) {
        console.warn('Error cleaning up previous viewer:', e)
      }
    }

    // Create viewer with try/catch to prevent crashes
    let viewer
    try {
      viewer = $3Dmol.createViewer(containerRef.current, {
        backgroundColor: 'black',
      })
      viewerRef.current = viewer
    } catch (err) {
      console.error('[Viewer3D] Failed to create viewer:', err)
      return
    }

    try {
      // Add molecule - wrap in try/catch
      viewer.addModel(data, format)
      
      // Set default style based on format (cartoon for PDB, stick for SDF/ligands)
      // SDF files don't have secondary structure, so cartoon would crash
      const defaultStyle = format === 'sdf' 
        ? { stick: { colorscheme: 'greenCarbon', radius: 0.2 } }
        : { cartoon: { colorscheme: 'spectrum', style: 'oval', thickness: 0.4, arrows: true } }
      
      viewer.setStyle({}, defaultStyle)
      viewer.zoomTo()
      viewer.render()

      // Set click handler
      viewer.setClickable({}, true, function(atom: any) {
        console.log('Clicked atom:', atom)
      })
    } catch (err) {
      console.error('[Viewer3D] Failed to add model or set style:', err)
    }
  }, [data, format, hasValidData])

  // Update style when representation changes
  // IMPORTANT: Do NOT use viewer.clear() here — it removes all models and
  // destroys the molecule that the initialization effect just added.
  // Only update styles and surfaces; models stay intact.
  const representationRef = useRef(representation)
  useEffect(() => {
    representationRef.current = representation

    if (!viewerRef.current || !hasValidData) return
    
    const viewer = viewerRef.current

    // Skip the very first run — the init effect already set the default style
    // We detect this by checking if the model count is zero (clear was called)
    // or if the viewer was just created. Only act on actual representation changes.
    
    try {
      const $3Dmol = get3Dmol()
      
      // Remove existing surface when switching away from surface mode
      // addSurface() returns a Promise in 3Dmol v2+, so we must resolve before removing
      if (surfaceRef.current && representation !== 'surface') {
        const pending = surfaceRef.current
        surfaceRef.current = null
        Promise.resolve(pending).then((surf: any) => {
          try {
            viewer.removeSurface(surf)
            viewer.render()
          } catch { /* surface may already be gone */ }
        })
      }
      
      // For SDF format, always use stick representation (no secondary structure)
      const isSDF = format === 'sdf'
      
      if (representation === 'surface') {
        const baseStyle = isSDF
          ? { stick: { colorscheme: 'greenCarbon', radius: 0.15 } }
          : { cartoon: { colorscheme: 'spectrum', style: 'oval', thickness: 0.3 } }
        viewer.setStyle({}, baseStyle)
        
        if (!surfaceRef.current && $3Dmol) {
          // Store the Promise — removeSurface will resolve it before removing
          const surfPromise = viewer.addSurface($3Dmol.SurfaceType.VDW, {
            opacity: 0.85,
            colorscheme: 'Jmol',
          })
          surfaceRef.current = surfPromise
          // If user switches away before surface finishes loading, handle cleanup
          Promise.resolve(surfPromise).then((surf: any) => {
            if (representationRef.current !== 'surface') {
              // User already navigated away — remove immediately
              try { viewer.removeSurface(surf); viewer.render() } catch {}
              surfaceRef.current = null
            }
          })
        }
      } else if (representation === 'cartoon') {
        if (isSDF) {
          viewer.setStyle({}, { stick: { colorscheme: 'greenCarbon', radius: 0.2 } })
        } else {
          viewer.setStyle({}, { cartoon: { colorscheme: 'spectrum', style: 'oval', thickness: 0.4, arrows: true } })
        }
      } else if (representation === 'sphere') {
        viewer.setStyle({}, { sphere: { colorscheme: 'spectrum', scale: 0.3 } })
      } else if (representation === 'stick') {
        viewer.setStyle({}, { stick: { colorscheme: 'spectrum', radius: 0.15 } })
      }
      
      viewer.render()
    } catch (err) {
      console.error('[Viewer3D] Error updating style:', err)
    }
  }, [representation, data, format, hasValidData])

  // ── Early return AFTER all hooks ──────────────────────────────────────
  if (!hasValidData) {
    return (
      <div className={cn(
        'relative rounded-lg overflow-hidden',
        !embedded && 'border border-purple-900/30',
        square && 'aspect-square',
      )}
      style={square ? undefined : { height: `${height}px` }}>
        <div className="absolute inset-0 bg-zinc-950 flex items-center justify-center z-10">
          <div className="text-center space-y-2">
            <Maximize2 className="w-10 h-10 text-zinc-700 mx-auto" />
            <p className="text-sm text-zinc-500">Waiting for structure data...</p>
          </div>
        </div>
      </div>
    )
  }

  const headerRow = (
    <div className="flex items-center gap-2 mb-2">
      <span className="text-lg font-bold text-zinc-200">{title}</span>
    </div>
  )

  const canvasArea = (
    <div
      className={cn(
        'relative rounded-lg overflow-hidden',
        !embedded && 'border border-purple-900/30',
        square && 'aspect-square',
      )}
      style={square ? undefined : { height: `${height}px` }}
    >
      {isLoading && (
        <div className="absolute inset-0 bg-zinc-950/80 flex items-center justify-center z-10">
          <div className="flex flex-col items-center gap-3">
            <LoadingSpinner />
            <p className="text-xs text-zinc-400">Loading structure…</p>
          </div>
        </div>
      )}
      {error && !isLoading && (
        <div className="absolute inset-0 bg-zinc-950 flex items-center justify-center z-10">
          <div className="text-center space-y-2 px-6">
            <p className="text-sm text-red-400 font-medium">Failed to load structure</p>
            <p className="text-xs text-zinc-500">{error}</p>
          </div>
        </div>
      )}
      {/* This div is where 3Dmol places its WebGL canvas */}
      <div
        ref={containerRef}
        className="w-full h-full"
        style={{ position: 'relative' }}
      />
      {/* Classic representation controls - Cartoon, Surface, Sphere, Stick */}
      {/* Hide Cartoon option for SDF format since it crashes */}
      <div className="absolute bottom-4 left-1/2 z-30 -translate-x-1/2 flex gap-1 rounded-full bg-black/60 backdrop-blur-lg px-4 py-1.5 shadow-lg border border-slate-700">
        {(format === 'sdf' 
          ? (['surface', 'sphere', 'stick'] as const)
          : (['cartoon', 'surface', 'sphere', 'stick'] as const)
        ).map((rep) => (
          <button
            key={rep}
            className={cn(
              'px-3 py-1 rounded-full text-[10px] font-semibold capitalize transition',
              representation === rep 
                ? 'bg-sky-500/80 text-white' 
                : 'bg-slate-800/80 text-slate-300 hover:bg-slate-700'
            )}
            onClick={() => setRepresentation(rep)}
          >
            {rep}
          </button>
        ))}
      </div>
    </div>
  )

  const footerRow = hasValidData ? (
    <div className="flex items-center gap-2 text-xs text-zinc-500 flex-shrink-0">
      <Palette className="w-3 h-3" />
      <span>Drag to rotate, scroll to zoom, right-click to translate</span>
    </div>
  ) : null

  if (embedded) {
    return (
      <div className="flex flex-col gap-3 p-4">
        {headerRow}
        {canvasArea}
        {footerRow}
      </div>
    )
  }
  return (
    <Card>
      <CardContent className="p-4 space-y-3">
        {headerRow}
        {canvasArea}
        {footerRow}
      </CardContent>
    </Card>
  )
}

// Named export
export { Viewer3DInner as Viewer3D }

// Default export (memoized)
export default memo(Viewer3DInner)
