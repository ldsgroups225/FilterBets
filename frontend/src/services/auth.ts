import { apiClient } from '@/api/client'
import type { AuthResponse, LoginRequest, RegisterRequest, User } from '@/types/auth'

// Login user
export const login = async (credentials: LoginRequest): Promise<AuthResponse> => {
  const response = await apiClient.post<AuthResponse>('/api/v1/auth/login', {
    email: credentials.email,
    password: credentials.password,
  })
  return response.data
}

// Register new user
export const register = async (data: RegisterRequest): Promise<AuthResponse> => {
  const response = await apiClient.post<AuthResponse>('/api/v1/auth/register', data)
  return response.data
}

// Refresh access token
export const refreshAccessToken = async (refreshToken: string): Promise<AuthResponse> => {
  const response = await apiClient.post<AuthResponse>('/api/v1/auth/refresh', {
    refresh_token: refreshToken,
  })
  return response.data
}

// Get current user
export const getCurrentUser = async (): Promise<User> => {
  const response = await apiClient.get<User>('/api/v1/auth/me')
  return response.data
}
