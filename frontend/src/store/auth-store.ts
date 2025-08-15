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
            console.warn('Failed to fetch additional user data, using login data:', error)
          }
        } catch (error) {
          console.error('Login error:', error)
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

          const user = await response.json()
          console.log('Registration successful:', user)
          
          // After registration, automatically login
          await get().login(userData.email, userData.password)
        } catch (error) {
          console.error('Registration error:', error)
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
          console.error('Failed to fetch user data:', error)
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
