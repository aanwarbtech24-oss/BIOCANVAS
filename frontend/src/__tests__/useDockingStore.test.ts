/**
 * BioCanvas Pro — Zustand Store unit tests.
 * Tests useDockingStore state transitions: activePoseIndex, jobs, resets.
 */

import { describe, it, expect, beforeEach } from 'vitest'
import { useDockingStore } from '@/stores/useDockingStore'
import type { DockingResult } from '@/types/api'

// Reset store between tests
beforeEach(() => {
  useDockingStore.setState({
    jobs: new Map(),
    activeJobId: null,
    activePoseIndex: 0,
  })
})

describe('useDockingStore', () => {
  // ── activePoseIndex ────────────────────────────────────────────────

  describe('activePoseIndex', () => {
    it('defaults to 0', () => {
      expect(useDockingStore.getState().activePoseIndex).toBe(0)
    })

    it('updates via setActivePose', () => {
      useDockingStore.getState().setActivePose(3)
      expect(useDockingStore.getState().activePoseIndex).toBe(3)
    })

    it('can be set to any valid number', () => {
      useDockingStore.getState().setActivePose(7)
      expect(useDockingStore.getState().activePoseIndex).toBe(7)
      useDockingStore.getState().setActivePose(0)
      expect(useDockingStore.getState().activePoseIndex).toBe(0)
    })
  })

  // ── Job management ─────────────────────────────────────────────────

  describe('job CRUD', () => {
    const mockJob = {
      id: 'job-001',
      smiles: 'CCO',
      protein_file: 'test.pdb',
      status: 'queued' as const,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    }

    it('creates a job and sets it as active', () => {
      useDockingStore.getState().createJob('job-001', mockJob)
      const state = useDockingStore.getState()
      expect(state.jobs.size).toBe(1)
      expect(state.activeJobId).toBe('job-001')
    })

    it('getJob returns the correct job', () => {
      useDockingStore.getState().createJob('job-001', mockJob)
      const job = useDockingStore.getState().getJob('job-001')
      expect(job).toBeDefined()
      expect(job?.smiles).toBe('CCO')
    })

    it('getJob returns undefined for missing job', () => {
      const job = useDockingStore.getState().getJob('nonexistent')
      expect(job).toBeUndefined()
    })

    it('updateJobStatus changes status', () => {
      useDockingStore.getState().createJob('job-001', mockJob)
      useDockingStore.getState().updateJobStatus('job-001', 'running')
      expect(useDockingStore.getState().getJob('job-001')?.status).toBe('running')
    })

    it('updateJobResult sets result and resets activePoseIndex to 0', () => {
      useDockingStore.getState().createJob('job-001', mockJob)
      useDockingStore.getState().setActivePose(5)
      expect(useDockingStore.getState().activePoseIndex).toBe(5)

      const mockResult: DockingResult = {
        success: true,
        job_id: 'job-001',
        affinity: -7.3,
        simulated: true,
        lipinski: { mw: 180, logp: 1.2, hbd: 1, hba: 4, pass_rule_of_five: true },
        poses: [
          {
            pose_rank: 1,
            affinity: -7.3,
            ligand_efficiency: -0.56,
            rmsd_lb: 0.0,
            rmsd_ub: 0.0,
            interactions: {
              hydrogen_bonds: [],
              hydrophobic: [],
              pi_stacking: [],
              salt_bridges: [],
            },
          },
        ],
      }

      useDockingStore.getState().updateJobResult('job-001', mockResult)
      const state = useDockingStore.getState()
      expect(state.activePoseIndex).toBe(0) // Reset on new result!
      expect(state.getJob('job-001')?.result).toBeDefined()
    })

    it('removeJob deletes job and clears activeJobId if needed', () => {
      useDockingStore.getState().createJob('job-001', mockJob)
      expect(useDockingStore.getState().activeJobId).toBe('job-001')
      useDockingStore.getState().removeJob('job-001')
      expect(useDockingStore.getState().jobs.size).toBe(0)
      expect(useDockingStore.getState().activeJobId).toBeNull()
    })

    it('removeJob preserves activeJobId if different job removed', () => {
      const mockJob2 = { ...mockJob, id: 'job-002' }
      useDockingStore.getState().createJob('job-001', mockJob)
      useDockingStore.getState().createJob('job-002', mockJob2)
      useDockingStore.getState().removeJob('job-001')
      expect(useDockingStore.getState().activeJobId).toBe('job-002')
    })

    it('clearJobs empties all state', () => {
      useDockingStore.getState().createJob('job-001', mockJob)
      useDockingStore.getState().clearJobs()
      const state = useDockingStore.getState()
      expect(state.jobs.size).toBe(0)
      expect(state.activeJobId).toBeNull()
    })
  })

  // ── setActiveJob ───────────────────────────────────────────────────

  describe('setActiveJob', () => {
    it('sets active job and resets activePoseIndex', () => {
      useDockingStore.getState().setActivePose(4)
      useDockingStore.getState().setActiveJob('job-xyz')
      const state = useDockingStore.getState()
      expect(state.activeJobId).toBe('job-xyz')
      expect(state.activePoseIndex).toBe(0) // Reset!
    })

    it('can clear active job to null', () => {
      useDockingStore.getState().setActiveJob('job-xyz')
      useDockingStore.getState().setActiveJob(null)
      expect(useDockingStore.getState().activeJobId).toBeNull()
    })
  })
})
