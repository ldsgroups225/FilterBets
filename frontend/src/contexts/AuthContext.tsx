/* eslint-disable react-refresh/only-export-components */
import { createContext, useEffect, useState, useCallback, type ReactNode } from 'react'
import { useNavigate } from 'react-router-dom'
import * as authService from '@/services/auth'
import type { AuthContextType, User } from '@/types/auth'

export const AuthContext = createContext<AuthContextType | undefined>(undefined)

interface AuthProviderProps {
  children: ReactNode
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const navigate = useNavigate()

  const logout = useCallback(() => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    setUser(null)
    navigate('/login')
  }, [navigate])

  const refreshToken = useCallback(async () => {
    const token = localStorage.getItem('refresh_token')
    if (!token) throw new Error('No refresh token')

    const response = await authService.refreshAccessToken(token)
    localStorage.setItem('access_token', response.access_token)
    localStorage.setItem('refresh_token', response.refresh_token)
    setUser(response.user)
  }, [])

  // Check for existing token on mount
  useEffect(() => {
    const initAuth = async () => {
      const token = localStorage.getItem('access_token')
      if (token) {
        try {
          const currentUser = await authService.getCurrentUser()
          setUser(currentUser)
        } catch {
          // Token invalid, clear storage
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
        }
      }
      setIsLoading(false)
    }

    initAuth()
  }, [])

  // Auto-refresh token before expiry
  useEffect(() => {
    if (!user) return

    // Refresh token every 25 minutes (tokens expire in 30 minutes)
    const interval = setInterval(
      async () => {
        try {
          await refreshToken()
        } catch (error) {
          console.error('Token refresh failed:', error)
          logout()
        }
      },
      25 * 60 * 1000
    )

    return () => clearInterval(interval)
  }, [user, refreshToken, logout])

  const login = async (email: string, password: string) => {
    const response = await authService.login({ email, password })
    localStorage.setItem('access_token', response.access_token)
    localStorage.setItem('refresh_token', response.refresh_token)
    setUser(response.user)
    navigate('/')
  }

  const register = async (email: string, password: string) => {
    const response = await authService.register({ email, password })
    localStorage.setItem('access_token', response.access_token)
    localStorage.setItem('refresh_token', response.refresh_token)
    setUser(response.user)
    navigate('/')
  }

  const value: AuthContextType = {
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
    register,
    logout,
    refreshToken,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
