import { useCallback } from 'react'
import { useProteinStructure } from '@/hooks/useMoleculeLibrary'
import { useDockingJob } from '@/hooks/useDockingJob'
import { useDockingStore } from '@/stores/useDockingStore'

import { ProgressBar, BottomNav, STEPS } from './pipeline/StepNav'
import { ProteinTargetStep } from './docking-steps/ProteinTargetStep'
import { LigandSelectionStep } from './docking-steps/LigandSelectionStep'
import { DockingRunStep } from './docking-steps/DockingRunStep'
import { ResultsStep } from './docking-steps/ResultsStep'

// ---------------------------------------------------------------------------
// Main Pipeline Component — Zustand-based State Management
// ---------------------------------------------------------------------------

export function DockingPipeline() {
  // ── Zustand Store State ───────────────────────────────────────────────
  const {
    activeStep,
    setActiveStep,
    selectedProtein,
    customPdbData,
    
    ligandSmiles,
    dockingJobId,
  } = useDockingStore()

  // ── Protein structure hook (viewerData feeds Step 1 viewer + Step 3 submission) ──
  const selectedUniprotId = selectedProtein?.uniprot_id ?? null
  // pdbData is fetched in child components
  const { isLoading: pdbLoading } = useProteinStructure(
    customPdbData ? null : selectedUniprotId,
  )
  

  // ── Job polling (needed here for step derivation) ────────────────────
  const jobQuery = useDockingJob(dockingJobId)
  const jobStatus = jobQuery.data?.status ?? null

  // ── Step completion derivation ───────────────────────────────────────
  const step1Complete = !!(selectedProtein || customPdbData) && !pdbLoading
  const step2Complete = !!ligandSmiles
  const step3Complete = jobStatus === 'completed'
  const maxUnlocked = step3Complete ? 4 : step2Complete ? 3 : step1Complete ? 2 : 1

  // ── Navigation ───────────────────────────────────────────────────────
  const goBack = useCallback(() => setActiveStep(Math.max(1, activeStep - 1)), [activeStep, setActiveStep])
  const goNext = useCallback(() => setActiveStep(Math.min(STEPS.length, activeStep + 1)), [activeStep, setActiveStep])
  const goToStep = useCallback((n: number) => setActiveStep(n), [setActiveStep])

  const canProceed =
    activeStep < maxUnlocked ||
    (activeStep === 1 && step1Complete) ||
    (activeStep === 2 && step2Complete) ||
    (activeStep === 3 && step3Complete)

  // ── Render ───────────────────────────────────────────────────────────
  return (
    <div className="mx-auto max-w-4xl pb-20">
      {/* Page header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold tracking-tight text-white sm:text-3xl">
          Molecular Docking Pipeline
        </h1>
        <p className="mt-2 max-w-xl text-sm leading-relaxed text-muted-foreground">
          Follow the guided workflow to set up, execute, and analyze a
          molecular docking simulation.
        </p>
      </div>

      {/* Horizontal progress bar */}
      <ProgressBar activeStep={activeStep} maxUnlocked={maxUnlocked} onStepClick={goToStep} />

      {/* Step panels - using Zustand-wired components */}
      {activeStep === 1 && <ProteinTargetStep />}

      {activeStep === 2 && <LigandSelectionStep />}

      {activeStep === 3 && <DockingRunStep />}

      {activeStep === 4 && <ResultsStep />}

      <BottomNav
        activeStep={activeStep}
        maxUnlocked={maxUnlocked}
        canProceed={canProceed}
        onBack={goBack}
        onNext={goNext}
      />
    </div>
  )
}
