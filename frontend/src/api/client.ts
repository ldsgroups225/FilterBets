import type { AxiosError, InternalAxiosRequestConfig } from 'axios'
import axios from 'axios'

// API base URL from environment variable
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Create axios instance
export const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 60000,
})

// Request interceptor - add auth token
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('access_token')
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error: AxiosError) => {
    return Promise.reject(error)
  },
)

// Response interceptor - handle errors
apiClient.interceptors.response.use(
  response => response,
  async (error: AxiosError) => {
    const originalRequest = error.config

    // Handle 401 Unauthorized - token expired
    if (error.response?.status === 401 && originalRequest) {
      // Clear tokens and redirect to login
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      window.location.href = '/login'
    }

    // Handle network errors
    if (!error.response) {
      console.error('Network error:', error.message)
    }

    return Promise.reject(error)
  },
)

// Type-safe API response
export interface ApiResponse<T> {
  data: T
  status: number
}

// Health check
export async function checkHealth() {
  const response = await apiClient.get<{ status: string, database: string }>('/health')
  return response.data
}

export default apiClient
