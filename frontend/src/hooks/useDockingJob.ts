import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { AxiosError } from 'axios'
import { axiosInstance } from '@/lib/axios'
import {
  JobResponse, JobStatus, HealthResponse,
  DockingResult, LipinskiProfile, DockingPose,
} from '@/types/api'
import { toast } from 'sonner'

/** Flattened / derived shape returned by the select transform. */
export interface SelectedJobData {
  job_id: string
  status: JobStatus
  submitted_at: number
  completed_at?: number | null
  affinity?: number
  rmsd?: number
  /** Pose count (number) — for "Quick Results" display. */
  poses?: number
  output_pdbqt?: string
  receptor_pdbqt?: string
  ligand_pdbqt?: string
  error?: string | null
  result?: DockingResult | null
  // Phase 1 — Unified Discovery Report
  lipinski?: LipinskiProfile | null
  dockingPoses?: DockingPose[] | null
}

/** Fetch job status with smart polling — stops on terminal states or 404. */
export function useDockingJob(jobId: string | null, enabled = true) {
  const query = useQuery<JobResponse | null, AxiosError, SelectedJobData | null>({
    queryKey: ['docking-job', jobId],
    queryFn: async (): Promise<JobResponse | null> => {
      if (!jobId) return null
      const response = await axiosInstance.get<JobResponse>(`/jobs/${jobId}`)
      return response.data
    },
    enabled: !!jobId && enabled,

    refetchInterval: (query) => {
      const error = query.state.error as AxiosError | null
      if (error?.response?.status === 404) return false

      const status = query.state.data?.status
      if (status === 'completed' || status === 'failed') return false

      return 2000
    },

    retry: (failureCount, error) => {
      if ((error as AxiosError)?.response?.status === 404) return false
      if ((error as AxiosError)?.response?.status === 408 || (error as AxiosError)?.response?.status === 429) {
        return failureCount < 2
      }
      return failureCount < 3
    },

    select: (data: JobResponse | null) => {
      if (!data) return null
      return {
        job_id: data.job_id,
        status: data.status,
        submitted_at: data.submitted_at,
        completed_at: data.completed_at,
        affinity: data.result?.affinity,
        rmsd: data.result?.rmsd,
        // Backward compat: Quick Results uses .poses as a number
        poses: data.result?.poses_count ?? data.result?.poses?.length,
        output_pdbqt: data.result?.output_pdbqt,
        receptor_pdbqt: data.result?.receptor_pdbqt,
        ligand_pdbqt: data.result?.ligand_pdbqt,
        error: data.error || data.result?.error,
        result: data.result,
        // Phase 1 — Unified Discovery Report
        lipinski: data.lipinski ?? data.result?.lipinski,
        dockingPoses: data.poses ?? data.result?.poses,
      }
    },

    staleTime: 500,
    placeholderData: (prev) => prev,
  })


  const is404 = (query.error as AxiosError)?.response?.status === 404
  if (is404 && query.errorUpdateCount === 1) {
    toast.error('Job lost due to server restart', {
      description:
        'The backend was restarted and this job no longer exists. Please re-submit.',
      duration: 8000,
    })
  }

  return {
    ...query,
    isLost: is404,
  }
}

/** Submit a new docking job. */
export function useSubmitDocking() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async ({
      file,
      smiles,
    }: {
      file: File
      smiles: string
    }) => {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('smiles', smiles)

      const response = await axiosInstance.post<JobResponse>('/dock', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })
      return response.data
    },

    onSuccess: (data: JobResponse) => {
      toast.success(`✓ Job submitted: ${data.job_id.slice(0, 8)}...`)
      
      queryClient.prefetchQuery({
        queryKey: ['docking-job', data.job_id],
        queryFn: async () => {
          const response = await axiosInstance.get<JobResponse>(`/jobs/${data.job_id}`)
          return response.data
        },
      })
    },

    onError: (error: any) => {
      const message = error.response?.data?.detail || 'Failed to submit docking job'
      toast.error(`✗ ${message}`)
    },
  })
}

/** Check backend health status. */
export function useHealthCheck() {
  return useQuery({
    queryKey: ['health-check'],
    queryFn: async () => {
      const response = await axiosInstance.get<HealthResponse>('/health')
      return response.data
    },
    refetchInterval: 10000,
    retry: 1,
  })
}
