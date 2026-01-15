import type { AuthResponse, LoginRequest, RegisterRequest, User } from '@/types/auth'
import { apiClient } from '@/api/client'

// Login user
export async function login(credentials: LoginRequest): Promise<AuthResponse> {
  const response = await apiClient.post<AuthResponse>('/api/v1/auth/login', {
    email: credentials.email,
    password: credentials.password,
  })
  return response.data
}

// Register new user
export async function register(data: RegisterRequest): Promise<AuthResponse> {
  const response = await apiClient.post<AuthResponse>('/api/v1/auth/register', data)
  return response.data
}

// Refresh access token
export async function refreshAccessToken(refreshToken: string): Promise<AuthResponse> {
  const response = await apiClient.post<AuthResponse>('/api/v1/auth/refresh', {
    refresh_token: refreshToken,
  })
  return response.data
}

// Get current user
export async function getCurrentUser(): Promise<User> {
  const response = await apiClient.get<User>('/api/v1/auth/me')
  return response.data
}
