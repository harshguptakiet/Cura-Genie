'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuthStore } from '@/store/auth-store'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Switch } from '@/components/ui/switch'
import { Alert } from '@/components/ui/alert'
import { Loader2, Eye, EyeOff, Mail, Lock, User, Phone, Github, Chrome } from 'lucide-react'
import { toast } from 'sonner'

type AuthMode = 'login' | 'register' | 'forgot-password' | 'reset-password'

interface AuthFormProps {
  initialMode?: AuthMode
  resetToken?: string
}

export function AuthForm({ initialMode = 'login', resetToken }: AuthFormProps) {
  const [mode, setMode] = useState<AuthMode>(initialMode)
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    username: '',
    firstName: '',
    lastName: '',
    phone: '',
    rememberMe: false,
    role: 'patient' as 'patient' | 'doctor' | 'admin'
  })
  const [errors, setErrors] = useState<Record<string, string>>({})

  const { login, register, forgotPassword, resetPassword, isLoading } = useAuthStore()
  const router = useRouter()

  const validateForm = () => {
    const newErrors: Record<string, string> = {}

    // Email validation
    if (!formData.email) {
      newErrors.email = 'Email is required'
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Please enter a valid email'
    }

    // Password validation for login, register, and reset
    if ((mode === 'login' || mode === 'register' || mode === 'reset-password') && !formData.password) {
      newErrors.password = 'Password is required'
    }

    if (mode === 'register') {
      // Username validation
      if (!formData.username) {
        newErrors.username = 'Username is required'
      } else if (formData.username.length < 3) {
        newErrors.username = 'Username must be at least 3 characters'
      }

      // Password strength validation
      if (formData.password.length < 8) {
        newErrors.password = 'Password must be at least 8 characters'
      }

      // Confirm password validation
      if (formData.password !== formData.confirmPassword) {
        newErrors.confirmPassword = 'Passwords do not match'
      }
    }

    if (mode === 'reset-password') {
      if (formData.password.length < 8) {
        newErrors.password = 'Password must be at least 8 characters'
      }
      if (formData.password !== formData.confirmPassword) {
        newErrors.confirmPassword = 'Passwords do not match'
      }
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!validateForm()) return

    try {
      switch (mode) {
        case 'login':
          await login(formData.email, formData.password, formData.rememberMe)
          toast.success('Login successful!')
          router.push('/dashboard')
          break

        case 'register':
          await register({
            email: formData.email,
            username: formData.username,
            password: formData.password,
            first_name: formData.firstName,
            last_name: formData.lastName,
            phone: formData.phone,
            role: formData.role
          })
          toast.success('Registration successful! Welcome to CuraGenie!')
          router.push('/dashboard')
          break

        case 'forgot-password':
          await forgotPassword(formData.email)
          toast.success('Password reset instructions sent to your email')
          setMode('login')
          break

        case 'reset-password':
          if (!resetToken) {
            toast.error('Invalid reset token')
            return
          }
          await resetPassword(resetToken, formData.password)
          toast.success('Password reset successfully!')
          setMode('login')
          break
      }
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'An error occurred')
    }
  }

  const handleSocialLogin = async (provider: 'google' | 'github') => {
    toast.info(`${provider} login coming soon!`)
    // In a real implementation, this would trigger OAuth flow
  }

  const updateFormData = (field: string, value: string | boolean) => {
    setFormData(prev => ({ ...prev, [field]: value }))
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }))
    }
  }

  const getTitle = () => {
    switch (mode) {
      case 'login': return 'Welcome Back'
      case 'register': return 'Create Account'
      case 'forgot-password': return 'Forgot Password'
      case 'reset-password': return 'Reset Password'
    }
  }

  const getDescription = () => {
    switch (mode) {
      case 'login': return 'Sign in to your CuraGenie account'
      case 'register': return 'Join CuraGenie for personalized healthcare insights'
      case 'forgot-password': return 'Enter your email to receive reset instructions'
      case 'reset-password': return 'Enter your new password'
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <Card className="w-full max-w-md shadow-lg">
        <CardHeader className="space-y-1 text-center">
          <div className="mx-auto mb-4 h-12 w-12 rounded-full bg-gradient-to-r from-blue-600 to-indigo-600 flex items-center justify-center text-white font-bold text-xl">
            C
          </div>
          <CardTitle className="text-2xl font-bold">{getTitle()}</CardTitle>
          <CardDescription>{getDescription()}</CardDescription>
        </CardHeader>

        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Email Field */}
            <div className="space-y-2">
              <div className="relative">
                <Mail className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                <Input
                  type="email"
                  placeholder="Email address"
                  value={formData.email}
                  onChange={(e) => updateFormData('email', e.target.value)}
                  className={`pl-10 ${errors.email ? 'border-red-500' : ''}`}
                />
              </div>
              {errors.email && <p className="text-sm text-red-500">{errors.email}</p>}
            </div>

            {/* Username Field (Register only) */}
            {mode === 'register' && (
              <div className="space-y-2">
                <div className="relative">
                  <User className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                  <Input
                    type="text"
                    placeholder="Username"
                    value={formData.username}
                    onChange={(e) => updateFormData('username', e.target.value)}
                    className={`pl-10 ${errors.username ? 'border-red-500' : ''}`}
                  />
                </div>
                {errors.username && <p className="text-sm text-red-500">{errors.username}</p>}
              </div>
            )}

            {/* Name Fields (Register only) */}
            {mode === 'register' && (
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Input
                    type="text"
                    placeholder="First Name (Optional)"
                    value={formData.firstName}
                    onChange={(e) => updateFormData('firstName', e.target.value)}
                  />
                </div>
                <div>
                  <Input
                    type="text"
                    placeholder="Last Name (Optional)"
                    value={formData.lastName}
                    onChange={(e) => updateFormData('lastName', e.target.value)}
                  />
                </div>
              </div>
            )}

            {/* Phone Field (Register only) */}
            {mode === 'register' && (
              <div className="relative">
                <Phone className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                <Input
                  type="tel"
                  placeholder="Phone Number (Optional)"
                  value={formData.phone}
                  onChange={(e) => updateFormData('phone', e.target.value)}
                  className="pl-10"
                />
              </div>
            )}

            {/* Role Selection (Register only) */}
            {mode === 'register' && (
              <div className="space-y-2">
                <div className="relative">
                  <User className="absolute left-3 top-3 h-4 w-4 text-gray-500" />
                  <select
                    name="role"
                    value={formData.role}
                    onChange={(e) => updateFormData('role', e.target.value)}
                    className={`w-full rounded-md border border-gray-300 pl-10 pr-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                      !formData.role ? 'text-gray-500' : 'text-gray-500'
                    }`}
                  >
                    <option value="" disabled>
                      Select Role
                    </option>
                    <option value="patient">Patient</option>
                    <option value="doctor">Doctor</option>
                  </select>
                </div>
                {errors.role && <p className="text-sm text-red-500">{errors.role}</p>}
              </div>
            )}

            {/* Password Field */}
            {(mode === 'login' || mode === 'register' || mode === 'reset-password') && (
              <div className="space-y-2">
                <div className="relative">
                  <Lock className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                  <Input
                    type={showPassword ? 'text' : 'password'}
                    placeholder="Password"
                    value={formData.password}
                    onChange={(e) => updateFormData('password', e.target.value)}
                    className={`pl-10 pr-10 ${errors.password ? 'border-red-500' : ''}`}
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-3 h-4 w-4 text-gray-400 hover:text-gray-600"
                  >
                    {showPassword ? <EyeOff /> : <Eye />}
                  </button>
                </div>
                {errors.password && <p className="text-sm text-red-500">{errors.password}</p>}
              </div>
            )}

            {/* Confirm Password Field */}
            {(mode === 'register' || mode === 'reset-password') && (
              <div className="space-y-2">
                <div className="relative">
                  <Lock className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                  <Input
                    type={showConfirmPassword ? 'text' : 'password'}
                    placeholder="Confirm Password"
                    value={formData.confirmPassword}
                    onChange={(e) => updateFormData('confirmPassword', e.target.value)}
                    className={`pl-10 pr-10 ${errors.confirmPassword ? 'border-red-500' : ''}`}
                  />
                  <button
                    type="button"
                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                    className="absolute right-3 top-3 h-4 w-4 text-gray-400 hover:text-gray-600"
                  >
                    {showConfirmPassword ? <EyeOff /> : <Eye />}
                  </button>
                </div>
                {errors.confirmPassword && <p className="text-sm text-red-500">{errors.confirmPassword}</p>}
              </div>
            )}

            {/* Remember Me (Login only) */}
            {mode === 'login' && (
              <div className="flex items-center justify-between">
                <label className="flex items-center space-x-2 cursor-pointer">
                  <Switch
                    checked={formData.rememberMe}
                    onCheckedChange={(checked) => updateFormData('rememberMe', checked)}
                  />
                  <span className="text-sm">Remember me</span>
                </label>
                <button
                  type="button"
                  onClick={() => setMode('forgot-password')}
                  className="text-sm text-blue-600 hover:text-blue-800"
                >
                  Forgot password?
                </button>
              </div>
            )}

            {/* Submit Button */}
            <Button
              type="submit"
              className="w-full"
              disabled={isLoading}
            >
              {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              {mode === 'login' && 'Sign In'}
              {mode === 'register' && 'Create Account'}
              {mode === 'forgot-password' && 'Send Reset Link'}
              {mode === 'reset-password' && 'Reset Password'}
            </Button>

            {/* Social Login (Login and Register only) */}
            {(mode === 'login' || mode === 'register') && (
              <>
                <div className="relative">
                  <div className="absolute inset-0 flex items-center">
                    <span className="w-full border-t" />
                  </div>
                  <div className="relative flex justify-center text-xs uppercase">
                    <span className="bg-background px-2 text-muted-foreground">Or continue with</span>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => handleSocialLogin('google')}
                    disabled={isLoading}
                  >
                    <Chrome className="mr-2 h-4 w-4" />
                    Google
                  </Button>
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => handleSocialLogin('github')}
                    disabled={isLoading}
                  >
                    <Github className="mr-2 h-4 w-4" />
                    GitHub
                  </Button>
                </div>
              </>
            )}

            {/* Mode Switch */}
            <div className="text-center text-sm">
              {mode === 'login' && (
                <span>
                  Don't have an account?{' '}
                  <button
                    type="button"
                    onClick={() => setMode('register')}
                    className="text-blue-600 hover:text-blue-800 font-medium"
                  >
                    Sign up
                  </button>
                </span>
              )}
              {mode === 'register' && (
                <span>
                  Already have an account?{' '}
                  <button
                    type="button"
                    onClick={() => setMode('login')}
                    className="text-blue-600 hover:text-blue-800 font-medium"
                  >
                    Sign in
                  </button>
                </span>
              )}
              {mode === 'forgot-password' && (
                <span>
                  Remember your password?{' '}
                  <button
                    type="button"
                    onClick={() => setMode('login')}
                    className="text-blue-600 hover:text-blue-800 font-medium"
                  >
                    Sign in
                  </button>
                </span>
              )}
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
