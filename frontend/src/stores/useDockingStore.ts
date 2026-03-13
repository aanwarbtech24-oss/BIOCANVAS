import { create } from 'zustand'
import type {
  JobStatus,
  DockingResult,
  LipinskiProfile,
  DockingPose,
  Protein,
  Ligand,
} from '@/types/api'

// ---------------------------------------------------------------------------
// Pipeline State Types
// ---------------------------------------------------------------------------

interface DockingJob {
  id: string
  smiles: string
  protein_file: string
  status: JobStatus
  result?: DockingResult
  lipinski?: LipinskiProfile
  poses?: DockingPose[]
  created_at: string
  updated_at: string
}

// Extended store interface including pipeline state
interface DockingStore {
  // ── Pipeline Wizard State ───────────────────────────────────────────
  activeStep: number
  selectedProtein: Protein | null
  customPdbData: string | null
  customPdbName: string | null
  // Fetched PDB data from AlphaFold (for library proteins)
  proteinPdbData: string | null
  selectedLigand: Ligand | null
  ligandSmiles: string | null
  dockingJobId: string | null
  
  // ── Job Management State ───────────────────────────────────────────
  jobs: Map<string, DockingJob>
  activeJobId: string | null
  activePoseIndex: number

  // ── Pipeline Actions ───────────────────────────────────────────────
  setActiveStep: (step: number) => void
  setSelectedProtein: (protein: Protein | null) => void
  setCustomPdbData: (data: string | null) => void
  setCustomPdbName: (name: string | null) => void
  setProteinPdbData: (data: string | null) => void
  setSelectedLigand: (ligand: Ligand | null) => void
  setLigandSmiles: (smiles: string | null) => void
  setDockingJobId: (jobId: string | null) => void
  
  // ── Reset Actions ──────────────────────────────────────────────────
  resetLigandAndDocking: () => void
  resetDocking: () => void
  resetAll: () => void

  // ── Job Actions ─────────────────────────────────────────────────────
  createJob: (id: string, job: DockingJob) => void
  updateJobStatus: (id: string, status: JobStatus) => void
  updateJobResult: (id: string, result: DockingResult) => void
  setActiveJob: (id: string | null) => void
  setActivePose: (index: number) => void
  removeJob: (id: string) => void
  getJob: (id: string) => DockingJob | undefined
  getActiveJob: () => DockingJob | undefined
  clearJobs: () => void
  
  // ── Computed Getters ────────────────────────────────────────────────
  getViewerData: (pdbData: string | null) => string | null
  getStepCompletion: (jobStatus: JobStatus | null) => {
    step1Complete: boolean
    step2Complete: boolean
    step3Complete: boolean
    maxUnlocked: number
  }
}

const initialState = {
  activeStep: 1,
  selectedProtein: null,
  customPdbData: null,
  customPdbName: null,
  proteinPdbData: null,
  selectedLigand: null,
  ligandSmiles: null,
  dockingJobId: null,
  jobs: new Map(),
  activeJobId: null,
  activePoseIndex: 0,
}

export const useDockingStore = create<DockingStore>((set: any, get: any) => ({
  ...initialState,

  // ── Pipeline Actions ───────────────────────────────────────────────
  setActiveStep: (step) => set({ activeStep: step }),
  setSelectedProtein: (protein) => set({ selectedProtein: protein }),
  setCustomPdbData: (data) => set({ customPdbData: data }),
  setCustomPdbName: (name) => set({ customPdbName: name }),
  setProteinPdbData: (data) => set({ proteinPdbData: data }),
  setSelectedLigand: (ligand) => set({ selectedLigand: ligand }),
  setLigandSmiles: (smiles) => set({ ligandSmiles: smiles }),
  setDockingJobId: (jobId) => set({ dockingJobId: jobId }),

  // ── Reset Actions ──────────────────────────────────────────────────
  resetLigandAndDocking: () => set({
    selectedLigand: null,
    ligandSmiles: null,
    dockingJobId: null,
  }),

  resetDocking: () => set({
    dockingJobId: null,
  }),

  resetAll: () => set(initialState),

  // ── Job Actions ─────────────────────────────────────────────────────
  createJob: (id, job) =>
    set((state: DockingStore) => {
      const newJobs = new Map(state.jobs)
      newJobs.set(id, job)
      return { jobs: newJobs, activeJobId: id }
    }),

  updateJobStatus: (id, status) =>
    set((state: DockingStore) => {
      const newJobs = new Map(state.jobs)
      const job = newJobs.get(id)
      if (job) {
        newJobs.set(id, { ...job, status })
      }
      return { jobs: newJobs }
    }),

  updateJobResult: (id, result) =>
    set((state: DockingStore) => {
      const newJobs = new Map(state.jobs)
      const job = newJobs.get(id)
      if (job) {
        newJobs.set(id, {
          ...job,
          result,
          lipinski: result.lipinski ?? job.lipinski,
          poses: result.poses ?? job.poses,
        })
      }
      return { jobs: newJobs, activePoseIndex: 0 }
    }),

  setActiveJob: (id) => set({ activeJobId: id, activePoseIndex: 0 }),
  setActivePose: (index) => set({ activePoseIndex: index }),

  removeJob: (id) =>
    set((state: DockingStore) => {
      const newJobs = new Map(state.jobs)
      newJobs.delete(id)
      return {
        jobs: newJobs,
        activeJobId: state.activeJobId === id ? null : state.activeJobId,
      }
    }),

  getJob: (id) => get().jobs.get(id),

  getActiveJob: () => {
    const { activeJobId, jobs } = get()
    return activeJobId ? jobs.get(activeJobId) : undefined
  },

  clearJobs: () => set({ jobs: new Map(), activeJobId: null }),

  // ── Computed Getters ────────────────────────────────────────────────
  getViewerData: (_pdbData) => {
    const { customPdbData } = get()
    return customPdbData ?? _pdbData ?? null
  },

  getStepCompletion: (jobStatus) => {
    const { selectedProtein, customPdbData, ligandSmiles } = get()
    // Step 1 is complete if we have either a selected protein OR custom PDB data
    const step1Complete = !!(selectedProtein || customPdbData)
    const step2Complete = !!ligandSmiles
    const step3Complete = jobStatus === 'completed'
    const maxUnlocked = step3Complete ? 4 : step2Complete ? 3 : step1Complete ? 2 : 1
    return { step1Complete, step2Complete, step3Complete, maxUnlocked }
  },
}))
