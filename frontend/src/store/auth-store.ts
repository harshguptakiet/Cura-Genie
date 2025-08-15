import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export interface User {
  id: number
  email: string
  username: string
  role: 'patient' | 'doctor' | 'admin'
  is_active: boolean
  is_verified: boolean
  created_at: string
}

export interface AuthTokens {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
}

export interface AuthState {
  user: User | null
  tokens: AuthTokens | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null

  // Authentication methods
  login: (email: string, password: string, rememberMe?: boolean) => Promise<void>
  register: (userData: RegisterData) => Promise<void>
  logout: () => Promise<void>

  // Token management
  refreshAccessToken: () => Promise<boolean>
  setTokens: (tokens: AuthTokens) => void
  clearTokens: () => void

  // User management
  setUser: (user: User) => void
  fetchUserData: () => Promise<void>

  // Password management
  changePassword: (currentPassword: string, newPassword: string) => Promise<void>
  forgotPassword: (email: string) => Promise<void>
  resetPassword: (token: string, password: string) => Promise<void>

  // Error handling
  clearError: () => void
  setError: (error: string) => void
}

export interface RegisterData {
  email: string
  username: string
  password: string
  first_name?: string
  last_name?: string
  phone?: string
  role?: 'patient' | 'doctor' | 'admin'
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000'

// Token refresh timer
let refreshTimer: NodeJS.Timeout | null = null

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      tokens: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      login: async (email: string, password: string, rememberMe: boolean = false) => {
        set({ isLoading: true, error: null })
        try {
          console.log('=== LOGIN DEBUGGING START ===')
          console.log('API_BASE_URL:', API_BASE_URL)
          console.log('Attempting login with email:', email)
          console.log('Full URL:', `${API_BASE_URL}/api/auth/login`)

          const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password, remember_me: rememberMe }),
          })

          console.log('Login response status:', response.status)
          console.log('Login response headers:', Object.fromEntries(response.headers.entries()))

          if (!response.ok) {
            const errorText = await response.text()
            console.error('Login error response:', errorText)
            let errorMessage = 'Login failed'
            try {
              const error = JSON.parse(errorText)
              errorMessage = error.detail || error.message || 'Login failed'
            } catch {
              errorMessage = `HTTP ${response.status}: ${response.statusText}`
            }
            throw new Error(errorMessage)
          }

          const data = await response.json()
          console.log('Login successful:', data)

          // Extract tokens and user data
          const tokens: AuthTokens = {
            access_token: data.tokens.access_token,
            refresh_token: data.tokens.refresh_token,
            token_type: data.tokens.token_type,
            expires_in: data.tokens.expires_in
          }

          const user: User = {
            id: data.user.id,
            email: data.user.email,
            username: data.user.username,
            role: data.user.role,
            is_active: data.user.is_active,
            is_verified: data.user.is_verified,
            created_at: data.user.created_at
          }

          set({
            tokens,
            user,
            isAuthenticated: true,
            isLoading: false,
            error: null
          })

          // Set up automatic token refresh
          setupTokenRefresh(tokens.expires_in)

          // Optionally fetch additional user data
          try {
            await get().fetchUserData()
          } catch (error) {
            console.warn('Failed to fetch additional user data, using login data:', error)
          }
        } catch (error) {
          console.error('Login error:', error)
          const errorMessage = error instanceof Error ? error.message : 'Login failed'
          set({
            isLoading: false,
            error: errorMessage,
            isAuthenticated: false
          })
          throw error
        }
      },

      register: async (userData: RegisterData) => {
        set({ isLoading: true, error: null })
        try {
          console.log('Attempting registration with:', userData.email)
          const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify(userData),
          })

          console.log('Registration response status:', response.status)

          if (!response.ok) {
            const errorText = await response.text()
            console.error('Registration error response:', errorText)
            let errorMessage = 'Registration failed'
            try {
              const error = JSON.parse(errorText)
              errorMessage = error.detail || error.message || 'Registration failed'
            } catch {
              errorMessage = `HTTP ${response.status}: ${response.statusText}`
            }
            throw new Error(errorMessage)
          }

          const data = await response.json()
          console.log('Registration successful:', data)

          // After registration, automatically login
          await get().login(userData.email, userData.password)
        } catch (error) {
          console.error('Registration error:', error)
          const errorMessage = error instanceof Error ? error.message : 'Registration failed'
          set({
            isLoading: false,
            error: errorMessage
          })
          throw error
        }
      },

      logout: async () => {
        try {
          const tokens = get().tokens
          if (tokens?.access_token) {
            // Call logout endpoint
            await fetch(`${API_BASE_URL}/api/auth/logout`, {
              method: 'POST',
              headers: {
                'Authorization': `Bearer ${tokens.access_token}`,
              },
            }).catch(() => {
              // Ignore logout API errors
            })
          }
        } catch (error) {
          console.warn('Logout API call failed:', error)
        } finally {
          // Clear local state
          set({
            user: null,
            tokens: null,
            isAuthenticated: false,
            isLoading: false,
            error: null,
          })

          // Clear refresh timer
          if (refreshTimer) {
            clearTimeout(refreshTimer)
            refreshTimer = null
          }
        }
      },

      refreshAccessToken: async (): Promise<boolean> => {
        try {
          const tokens = get().tokens
          if (!tokens?.refresh_token) {
            return false
          }

          const response = await fetch(`${API_BASE_URL}/api/auth/refresh`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ refresh_token: tokens.refresh_token }),
          })

          if (!response.ok) {
            throw new Error('Token refresh failed')
          }

          const data = await response.json()
          const newTokens: AuthTokens = {
            access_token: data.access_token,
            refresh_token: tokens.refresh_token, // Keep existing refresh token
            token_type: data.token_type,
            expires_in: data.expires_in
          }

          set({ tokens: newTokens })

          // Set up new refresh timer
          setupTokenRefresh(newTokens.expires_in)

          return true
        } catch (error) {
          console.error('Token refresh failed:', error)
          // If refresh fails, logout user
          await get().logout()
          return false
        }
      },

      setTokens: (tokens: AuthTokens) => {
        set({ tokens })
        setupTokenRefresh(tokens.expires_in)
      },

      clearTokens: () => {
        set({ tokens: null })
        if (refreshTimer) {
          clearTimeout(refreshTimer)
          refreshTimer = null
        }
      },

      setUser: (user: User) => {
        set({ user, isAuthenticated: true })
      },

      fetchUserData: async () => {
        try {
          const tokens = get().tokens
          if (!tokens?.access_token) return

          const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
            headers: {
              'Authorization': `Bearer ${tokens.access_token}`,
            },
          })

          if (response.ok) {
            const user = await response.json()
            set({ user })
          } else if (response.status === 401) {
            // Token expired, try to refresh
            const refreshed = await get().refreshAccessToken()
            if (refreshed) {
              // Retry fetch
              await get().fetchUserData()
            }
          }
        } catch (error) {
          console.error('Failed to fetch user data:', error)
        }
      },

      changePassword: async (currentPassword: string, newPassword: string) => {
        set({ isLoading: true, error: null })
        try {
          const tokens = get().tokens
          if (!tokens?.access_token) {
            throw new Error('Not authenticated')
          }

          const response = await fetch(`${API_BASE_URL}/api/auth/change-password`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${tokens.access_token}`,
            },
            body: JSON.stringify({
              current_password: currentPassword,
              new_password: newPassword
            }),
          })

          if (!response.ok) {
            const error = await response.json()
            throw new Error(error.detail || 'Password change failed')
          }

          set({ isLoading: false })
        } catch (error) {
          const errorMessage = error instanceof Error ? error.message : 'Password change failed'
          set({
            isLoading: false,
            error: errorMessage
          })
          throw error
        }
      },

      forgotPassword: async (email: string) => {
        set({ error: null })
        try {
          const response = await fetch(`${API_BASE_URL}/api/auth/forgot-password`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email }),
          })

          if (!response.ok) {
            const error = await response.json()
            throw new Error(error.detail || 'Failed to send reset email')
          }
        } catch (error) {
          const errorMessage = error instanceof Error ? error.message : 'Failed to send reset email'
          set({ error: errorMessage })
          throw error
        }
      },

      resetPassword: async (token: string, password: string) => {
        set({ isLoading: true, error: null })
        try {
          const response = await fetch(`${API_BASE_URL}/api/auth/reset-password`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              token,
              new_password: password
            }),
          })

          if (!response.ok) {
            const error = await response.json()
            throw new Error(error.detail || 'Password reset failed')
          }

          set({ isLoading: false })
        } catch (error) {
          const errorMessage = error instanceof Error ? error.message : 'Password reset failed'
          set({
            isLoading: false,
            error: errorMessage
          })
          throw error
        }
      },

      clearError: () => set({ error: null }),
      setError: (error: string) => set({ error }),

    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        tokens: state.tokens,
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
)

// Helper function to set up automatic token refresh
function setupTokenRefresh(expiresIn: number) {
  if (refreshTimer) {
    clearTimeout(refreshTimer)
  }

  // Refresh token 1 minute before it expires
  const refreshTime = (expiresIn - 60) * 1000
  refreshTimer = setTimeout(async () => {
    const refreshed = await useAuthStore.getState().refreshAccessToken()
    if (!refreshed) {
      console.warn('Token refresh failed, user will need to login again')
    }
  }, refreshTime)
}

// Export helper functions for external use
export const getAuthHeaders = () => {
  const tokens = useAuthStore.getState().tokens
  if (!tokens?.access_token) {
    return {}
  }
  return {
    'Authorization': `Bearer ${tokens.access_token}`,
    'Content-Type': 'application/json',
  }
}

export const isTokenExpired = () => {
  const tokens = useAuthStore.getState().tokens
  if (!tokens) return true

  // Check if token is expired (with 1 minute buffer)
  const now = Date.now() / 1000
  const expiresAt = now + tokens.expires_in - 60
  return now >= expiresAt
}
