// ---------------------------------------------------------------------------
// API Response Types
// ---------------------------------------------------------------------------

export type JobStatus = 'queued' | 'running' | 'completed' | 'failed'

// ---------------------------------------------------------------------------
// Phase 1 — Unified Discovery Report Types
// ---------------------------------------------------------------------------

/** Lipinski Rule-of-Five drug-likeness profile */
export interface LipinskiProfile {
  mw: number        // Molecular weight (Da)
  logp: number      // Partition coefficient
  hbd: number       // Hydrogen bond donors
  hba: number       // Hydrogen bond acceptors
  pass_rule_of_five: boolean
}

/** Detail record for a hydrogen bond interaction */
export interface HydrogenBondDetail {
  residue: string           // e.g. "TYR-102"
  distance: number          // Angstroms
  protein_atom_idx?: number | null
  ligand_atom_idx?: number | null
}

/** Detail record for hydrophobic / pi-stacking / salt-bridge interactions */
export interface InteractionDetail {
  residue: string
  distance: number
  type?: string   // For pi-stacking: "P" (parallel) or "T" (T-shaped)
}

/** Full set of non-covalent interactions for a single docked pose */
export interface InteractionSet {
  hydrogen_bonds: HydrogenBondDetail[]
  hydrophobic: InteractionDetail[]
  pi_stacking: InteractionDetail[]
  salt_bridges: InteractionDetail[]
}

/** A single docked pose with affinity, LE, RMSD, and interaction fingerprint */
export interface DockingPose {
  pose_rank: number
  affinity: number            // kcal/mol
  ligand_efficiency: number   // ΔG / N_heavy_atoms
  rmsd_lb: number
  rmsd_ub: number
  interactions: InteractionSet
}

// ---------------------------------------------------------------------------
// Legacy + Unified result envelope
// ---------------------------------------------------------------------------

export interface DockingResult {
  success: boolean
  job_id: string
  // Backward-compat flat fields
  affinity?: number
  rmsd?: number
  /** @deprecated Use poses[] array instead. Kept for Quick Results panel compat. */
  poses_count?: number
  receptor_pdbqt?: string
  ligand_pdbqt?: string
  output_pdbqt?: string
  duration?: number
  box_center?: [number, number, number]
  box_size?: [number, number, number]
  error?: string
  simulated?: boolean
  // Phase 1 — Unified Discovery Report
  lipinski?: LipinskiProfile
  poses?: DockingPose[]
}

export interface JobResponse {
  job_id: string
  status: JobStatus
  submitted_at: number
  completed_at?: number | null
  result?: DockingResult | null
  error?: string | null
  // Phase 1 — top-level mirrors (also inside result for convenience)
  lipinski?: LipinskiProfile | null
  poses?: DockingPose[] | null
}

export interface HealthResponse {
  status: string
  engine: string
  timestamp: number
  jobs_running: number
}

// ---------------------------------------------------------------------------
// Molecule Library Types
// ---------------------------------------------------------------------------

export interface Protein {
  id: number
  name: string
  uniprot_id: string
  function: string
  category: string
}

export interface Ligand {
  id: number
  name: string
  type: string
  description: string
  pubchem_cid: number
  smiles: string
}
