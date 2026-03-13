/**
 * BioCanvas Pro — Step4_Results component render tests.
 * Ensures the Bento dashboard renders without crashing with various data states.
 */

import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { Step4_Results } from '@/components/features/docking-steps/Step4_Results'
import type { SelectedJobData } from '@/hooks/useDockingJob'
import type { Protein, Ligand } from '@/types/api'

// ── Mock 3Dmol (not available in jsdom) ─────────────────────────────────

vi.mock('@/components/science/DockingViewer3D', () => ({
  DockingViewer3D: (props: any) => (
    <div data-testid="docking-viewer-3d">
      Mock DockingViewer3D — pose {props.activePoseIndex}
    </div>
  ),
}))

// ── Mock Zustand store ──────────────────────────────────────────────────

vi.mock('@/stores/useDockingStore', () => ({
  useDockingStore: (selector: any) => {
    const state = { activePoseIndex: 0, setActivePose: vi.fn() }
    return selector(state)
  },
}))

// ── Test data ───────────────────────────────────────────────────────────

const mockProtein: Protein = {
  id: 1,
  name: 'Hemoglobin',
  uniprot_id: 'P69905',
  function: 'Oxygen transport',
  category: 'Transport',
}

const mockLigand: Ligand = {
  id: 1,
  name: 'Aspirin',
  type: 'drug',
  description: 'Anti-inflammatory',
  pubchem_cid: 2244,
  smiles: 'CC(=O)OC1=CC=CC=C1C(=O)O',
}

const mockJobData: SelectedJobData = {
  job_id: 'test-job-001',
  status: 'completed',
  submitted_at: Date.now() / 1000,
  completed_at: Date.now() / 1000 + 5,
  affinity: -7.3,
  rmsd: 0.0,
  poses: 3,
  output_pdbqt: 'MODEL 1\nATOM...\nENDMDL',
  error: null,
  result: {
    success: true,
    job_id: 'test-job-001',
    affinity: -7.3,
    simulated: true,
  },
  lipinski: {
    mw: 180.16,
    logp: 1.24,
    hbd: 1,
    hba: 4,
    pass_rule_of_five: true,
  },
  dockingPoses: [
    {
      pose_rank: 1,
      affinity: -7.3,
      ligand_efficiency: -0.56,
      rmsd_lb: 0.0,
      rmsd_ub: 0.0,
      interactions: {
        hydrogen_bonds: [{ residue: 'TYR-102', distance: 2.8 }],
        hydrophobic: [],
        pi_stacking: [],
        salt_bridges: [],
      },
    },
    {
      pose_rank: 2,
      affinity: -6.5,
      ligand_efficiency: -0.5,
      rmsd_lb: 1.2,
      rmsd_ub: 2.3,
      interactions: {
        hydrogen_bonds: [],
        hydrophobic: [{ residue: 'LEU-45', distance: 3.5 }],
        pi_stacking: [],
        salt_bridges: [],
      },
    },
    {
      pose_rank: 3,
      affinity: -5.8,
      ligand_efficiency: -0.45,
      rmsd_lb: 2.0,
      rmsd_ub: 3.4,
      interactions: {
        hydrogen_bonds: [],
        hydrophobic: [],
        pi_stacking: [],
        salt_bridges: [],
      },
    },
  ],
}

// ═══════════════════════════════════════════════════════════════════════════
//  Tests
// ═══════════════════════════════════════════════════════════════════════════

describe('Step4_Results', () => {
  it('renders without crashing with full mock data', () => {
    const { container } = render(
      <Step4_Results
        jobData={mockJobData}
        selectedProtein={mockProtein}
        customPdbName={null}
        selectedLigand={mockLigand}
        viewerData="ATOM...PDB DATA..."
      />,
    )
    expect(container).toBeTruthy()
  })

  it('renders the results header with protein and ligand names', () => {
    render(
      <Step4_Results
        jobData={mockJobData}
        selectedProtein={mockProtein}
        customPdbName={null}
        selectedLigand={mockLigand}
        viewerData={null}
      />,
    )
    expect(screen.getByText('Docking Results')).toBeInTheDocument()
    expect(screen.getByText('Hemoglobin')).toBeInTheDocument()
    expect(screen.getByText('Aspirin')).toBeInTheDocument()
  })

  it('renders the DockingViewer3D mock', () => {
    render(
      <Step4_Results
        jobData={mockJobData}
        selectedProtein={mockProtein}
        customPdbName={null}
        selectedLigand={mockLigand}
        viewerData="PDB DATA"
      />,
    )
    expect(screen.getByTestId('docking-viewer-3d')).toBeInTheDocument()
  })

  it('renders the pose table with correct number of rows', () => {
    render(
      <Step4_Results
        jobData={mockJobData}
        selectedProtein={mockProtein}
        customPdbName={null}
        selectedLigand={mockLigand}
        viewerData={null}
      />,
    )
    // Each pose becomes a table row; look for affinity values
    // -7.3 appears in both LeadCard and PoseTable, so use getAllByText
    expect(screen.getAllByText('-7.3').length).toBeGreaterThanOrEqual(1)
    expect(screen.getAllByText('-6.5').length).toBeGreaterThanOrEqual(1)
    expect(screen.getAllByText('-5.8').length).toBeGreaterThanOrEqual(1)
  })

  it('renders Lipinski PASS badge for passing profile', () => {
    render(
      <Step4_Results
        jobData={mockJobData}
        selectedProtein={mockProtein}
        customPdbName={null}
        selectedLigand={mockLigand}
        viewerData={null}
      />,
    )
    expect(screen.getByText('PASS')).toBeInTheDocument()
  })

  it('renders without crashing with null jobData', () => {
    const { container } = render(
      <Step4_Results
        jobData={null}
        selectedProtein={null}
        customPdbName={null}
        selectedLigand={null}
        viewerData={null}
      />,
    )
    expect(container).toBeTruthy()
  })

  it('shows "No pose data" when jobData has no poses', () => {
    const emptyJobData: SelectedJobData = {
      ...mockJobData,
      dockingPoses: [],
    }
    render(
      <Step4_Results
        jobData={emptyJobData}
        selectedProtein={mockProtein}
        customPdbName={null}
        selectedLigand={mockLigand}
        viewerData={null}
      />,
    )
    const noPoseTexts = screen.getAllByText('No pose data available')
    expect(noPoseTexts.length).toBeGreaterThanOrEqual(1)
  })

  it('uses customPdbName when protein is null', () => {
    render(
      <Step4_Results
        jobData={mockJobData}
        selectedProtein={null}
        customPdbName="my_custom_protein.pdb"
        selectedLigand={mockLigand}
        viewerData={null}
      />,
    )
    expect(screen.getByText('my_custom_protein.pdb')).toBeInTheDocument()
  })

  it('shows simulated badge when result is simulated', () => {
    render(
      <Step4_Results
        jobData={mockJobData}
        selectedProtein={mockProtein}
        customPdbName={null}
        selectedLigand={mockLigand}
        viewerData={null}
      />,
    )
    expect(screen.getByText('Simulated')).toBeInTheDocument()
  })
})
