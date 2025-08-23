import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { logAuth, logger } from '@/lib/logger'

export interface User {
  id: number
  email: string
  username: string
  role: 'patient' | 'doctor' | 'admin'
  is_active: boolean
  is_verified: boolean
  created_at: string
}

export interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (email: string, password: string, rememberMe?: boolean) => Promise<void>
  socialLogin: (provider: string, token: string) => Promise<void>
  register: (userData: RegisterData) => Promise<void>
  logout: () => void
  setUser: (user: User) => void
  setToken: (token: string) => void
  forgotPassword: (email: string) => Promise<void>
  resetPassword: (token: string, password: string) => Promise<void>
  fetchUserData: () => Promise<void>
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

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,

      login: async (email: string, password: string, rememberMe: boolean = false) => {
        set({ isLoading: true })
        try {
          logAuth('debug', 'Login process started', undefined, {
            apiUrl: API_BASE_URL,
            email: email,
            endpoint: '/api/auth/login'
          })

          const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password, remember_me: rememberMe }),
          })

          logAuth('debug', 'Login response received', undefined, {
            status: response.status,
            statusText: response.statusText
          })

          if (!response.ok) {
            const errorText = await response.text()
            logAuth('error', 'Login failed', undefined, {
              status: response.status,
              errorText,
              endpoint: '/api/auth/login'
            })
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
          logAuth('info', 'Login successful', undefined, {
            userId: data.user_id,
            role: data.role
          })

          // Create user object from login response
          const user: User = {
            id: data.user_id,
            email: email,
            username: '', // Will be filled if needed
            role: data.role || 'patient',
            is_active: true,
            is_verified: true,
            created_at: new Date().toISOString()
          }

          set({
            token: data.access_token,
            user: user,
            isAuthenticated: true,
            isLoading: false
          })

          // Optionally fetch additional user data
          try {
            await get().fetchUserData()
          } catch (error) {
            logAuth('warn', 'Failed to fetch additional user data, using login data', undefined, { error: error.message })
          }
        } catch (error) {
          logAuth('error', 'Login process failed', undefined, { error: error.message })
          set({ isLoading: false })
          throw error
        }
      },

      socialLogin: async (provider: string, token: string) => {
        set({ isLoading: true })
        try {
          // This would integrate with actual social auth
          // For now, it's a placeholder
          throw new Error('Social login not implemented yet')
        } catch (error) {
          set({ isLoading: false })
          throw error
        }
      },

      register: async (userData: RegisterData) => {
        set({ isLoading: true })
        try {
          logAuth('debug', 'Registration process started', undefined, { email: userData.email })
          const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify(userData),
          })

          logAuth('debug', 'Registration response received', undefined, { status: response.status })

          if (!response.ok) {
            const errorText = await response.text()
            logAuth('error', 'Registration failed', undefined, {
              status: response.status,
              errorText,
              endpoint: '/api/auth/register'
            })
            let errorMessage = 'Registration failed'
            try {
              const error = JSON.parse(errorText)
              errorMessage = error.detail || error.message || 'Registration failed'
            } catch {
              errorMessage = `HTTP ${response.status}: ${response.statusText}`
            }
            throw new Error(errorMessage)
          }

          const user = await response.json()
          logAuth('info', 'Registration successful', undefined, { userId: user.id })

          // After registration, automatically login
          await get().login(userData.email, userData.password)
        } catch (error) {
          logAuth('error', 'Registration process failed', undefined, { error: error.message })
          set({ isLoading: false })
          throw error
        }
      },

      logout: () => {
        set({
          user: null,
          token: null,
          isAuthenticated: false,
          isLoading: false,
        })

        // Clear token from API calls
        fetch(`${API_BASE_URL}/api/auth/logout`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${get().token}`,
          },
        }).catch(() => {
          // Ignore logout API errors
        })
      },

      setUser: (user: User) => {
        set({ user, isAuthenticated: true })
      },

      setToken: (token: string) => {
        set({ token })
      },

      forgotPassword: async (email: string) => {
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
          throw error
        }
      },

      resetPassword: async (token: string, password: string) => {
        try {
          const response = await fetch(`${API_BASE_URL}/api/auth/reset-password`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ token, new_password: password }),
          })

          if (!response.ok) {
            const error = await response.json()
            throw new Error(error.detail || 'Password reset failed')
          }
        } catch (error) {
          throw error
        }
      },

      // Helper method to fetch user data
      fetchUserData: async () => {
        try {
          const token = get().token
          if (!token) return

          const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
            headers: {
              'Authorization': `Bearer ${token}`,
            },
          })

          if (response.ok) {
            const user = await response.json()
            set({ user })
          }
        } catch (error) {
          logAuth('error', 'Failed to fetch user data', undefined, { error: error.message })
        }
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        token: state.token,
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
)
