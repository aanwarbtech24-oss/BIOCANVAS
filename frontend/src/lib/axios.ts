import axios, { AxiosInstance, AxiosError } from 'axios'
import { toast } from 'sonner'

const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'

export const axiosInstance: AxiosInstance = axios.create({
  baseURL: API_URL,
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
})

/** Global error interceptor — surfaces user-friendly toast for failures. */
axiosInstance.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    const status = error.response?.status
    const data = error.response?.data as any

    const messages: Record<number, string> = {
      400: data?.detail || 'Bad request. Please check your inputs.',
      401: 'Unauthorized. Please log in again.',
      403: 'Forbidden. You do not have access to this resource.',
      404: 'Not found. The resource does not exist.',
      422: 'Validation error. Please check your inputs.',
      500: 'Server error. Please try again later.',
      503: 'Backend server is offline. Start with: python3 run.py',
    }

    const message = status
      ? messages[status] ?? 'An unexpected error occurred.'
      : 'Network error or backend unreachable.'

    if (error.config?.method !== 'get' || status === 503) {
      toast.error(message)
    }

    return Promise.reject(error)
  }
)

export default axiosInstance
