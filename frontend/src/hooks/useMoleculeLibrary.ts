import { useQuery } from '@tanstack/react-query'
import { axiosInstance } from '@/lib/axios'
import type { Protein, Ligand } from '@/types/api'

/**
 * ============================================================================
 * Molecule Library Hooks
 * ============================================================================
 */

/**
 * Fetch the curated protein library (10 proteins)
 */
export function useProteins() {
  return useQuery<Protein[]>({
    queryKey: ['proteins'],
    queryFn: async () => {
      const { data } = await axiosInstance.get<Protein[]>('/proteins')
      return data
    },
    staleTime: 1000 * 60 * 30, // 30 min – data is static
  })
}

/**
 * Fetch the curated ligand library (10 ligands)
 */
export function useLigands() {
  return useQuery<Ligand[]>({
    queryKey: ['ligands'],
    queryFn: async () => {
      const { data } = await axiosInstance.get<Ligand[]>('/ligands')
      return data
    },
    staleTime: 1000 * 60 * 30,
  })
}

/**
 * Fetch a protein 3D structure from AlphaFold DB via UniProt ID.
 * Queries the prediction API to resolve the latest PDB URL (version-safe),
 * then downloads the raw PDB text.
 *
 * RACE-SAFE: Uses React Query's built-in AbortController signal. When the
 * user selects a different protein before the previous fetch completes,
 * React Query automatically aborts the stale request so the viewer never
 * receives the wrong molecule.
 */
export function useProteinStructure(uniprotId: string | null) {
  return useQuery<string>({
    queryKey: ['protein-structure', uniprotId],
    queryFn: async ({ signal }) => {
      if (!uniprotId) throw new Error('No UniProt ID')

      // Step 1 — resolve the latest PDB URL via AlphaFold prediction API
      const metaRes = await fetch(
        `https://alphafold.ebi.ac.uk/api/prediction/${uniprotId}`,
        { signal },
      )
      if (!metaRes.ok) {
        if (metaRes.status === 404)
          throw new Error(`AlphaFold has no prediction for ${uniprotId}`)
        throw new Error(`AlphaFold API error: ${metaRes.status}`)
      }

      const meta = await metaRes.json()
      const entry = Array.isArray(meta) ? meta[0] : meta
      const pdbUrl: string | undefined = entry?.pdbUrl

      if (!pdbUrl)
        throw new Error('No PDB URL in AlphaFold response')

      // Step 2 — download the PDB file
      const pdbRes = await fetch(pdbUrl, { signal })
      if (!pdbRes.ok)
        throw new Error(`PDB download failed: ${pdbRes.status}`)

      const text = await pdbRes.text()

      // Sanity check — must look like PDB data
      if (!text || text.length < 200 || !text.includes('ATOM'))
        throw new Error('AlphaFold returned invalid or empty PDB data')

      return text
    },
    enabled: !!uniprotId,
    staleTime: 1000 * 60 * 60, // 1 hour – structures rarely change
    retry: 1,
  })
}

/**
 * Fetch a ligand 3D structure from PubChem via CID.
 * Tries 3D conformer first, falls back to 2D SDF if unavailable.
 * Returns raw SDF text.
 *
 * RACE-SAFE: Uses React Query's built-in AbortController signal.
 * Switching ligands mid-fetch automatically aborts the stale request.
 */
export function useLigandStructure(pubchemCid: number | null) {
  return useQuery<string>({
    queryKey: ['ligand-structure', pubchemCid],
    queryFn: async ({ signal }) => {
      if (!pubchemCid) throw new Error('No PubChem CID')

      // Try 3D conformer first
      const url3d = `https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/${pubchemCid}/SDF?record_type=3d`
      const res3d = await fetch(url3d, { signal })
      if (res3d.ok) return res3d.text()

      // Fallback to 2D structure (some molecules like Heme B have no 3D conformer)
      const url2d = `https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/${pubchemCid}/SDF`
      const res2d = await fetch(url2d, { signal })
      if (!res2d.ok)
        throw new Error(`PubChem fetch failed for CID ${pubchemCid}: ${res2d.status}`)

      return res2d.text()
    },
    enabled: !!pubchemCid,
    staleTime: 1000 * 60 * 60,
    retry: 1,
  })
}
