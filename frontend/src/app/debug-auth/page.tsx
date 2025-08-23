'use client'

import { useState } from 'react'
import { useAuthStore } from '@/store/auth-store'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { useRouter } from 'next/navigation'

export default function DebugAuthPage() {
  const [email, setEmail] = useState('demo@test.com')
  const [password, setPassword] = useState('password')
  const [status, setStatus] = useState('')
  const [error, setError] = useState('')
  
  const { login, register, isLoading, user, token, isAuthenticated } = useAuthStore()
  const router = useRouter()

  const testBackendHealth = async () => {
    setStatus('Testing backend health...')
    setError('')
    
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/health`)
      if (response.ok) {
        const data = await response.json()
        setStatus(`✅ Backend healthy: ${JSON.stringify(data)}`)
      } else {
        setStatus(`❌ Backend unhealthy: ${response.status}`)
      }
    } catch (err) {
      setStatus(`❌ Backend unreachable: ${err}`)
    }
  }

  const testLogin = async () => {
    setStatus('Testing login...')
    setError('')
    
    try {
      await login(email, password)
      setStatus('✅ Login successful!')
      setTimeout(() => router.push('/dashboard'), 1000)
    } catch (err: any) {
      setError(`❌ Login failed: ${err.message}`)
      setStatus('')
    }
  }

  const testRegister = async () => {
    setStatus('Testing registration...')
    setError('')
    
    try {
      await register({
        email: email,
        username: email.split('@')[0],
        password: password,
        role: 'patient'
      })
      setStatus('✅ Registration successful!')
      setTimeout(() => router.push('/dashboard'), 1000)
    } catch (err: any) {
      setError(`❌ Registration failed: ${err.message}`)
      setStatus('')
    }
  }

  const manualLogin = () => {
    setStatus('Creating manual demo user...')
    
    // Manually set authentication state
    useAuthStore.setState({
      user: {
        id: 1,
        email: email,
        username: email.split('@')[0],
        role: 'patient',
        is_active: true,
        is_verified: true,
        created_at: new Date().toISOString()
      },
      token: 'manual-demo-token',
      isAuthenticated: true,
      isLoading: false
    })
    
    setStatus('✅ Manual login successful!')
    setTimeout(() => router.push('/dashboard'), 1000)
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <Card className="w-full max-w-lg">
        <CardHeader>
          <CardTitle>🔧 CuraGenie Auth Debug</CardTitle>
          <CardDescription>
            Debug authentication issues and test different scenarios
          </CardDescription>
        </CardHeader>
        
        <CardContent className="space-y-4">
          {/* Current Status */}
          <div className="bg-gray-50 p-4 rounded-lg">
            <h3 className="font-medium mb-2">Current State:</h3>
            <p><strong>Authenticated:</strong> {isAuthenticated ? '✅ Yes' : '❌ No'}</p>
            <p><strong>User:</strong> {user?.email || 'None'}</p>
            <p><strong>Token:</strong> {token ? '✅ Present' : '❌ None'}</p>
            <p><strong>Loading:</strong> {isLoading ? '🔄 Yes' : '❌ No'}</p>
          </div>

          {/* Test Inputs */}
          <div className="space-y-2">
            <Input
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
            <Input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>

          {/* Test Buttons */}
          <div className="grid grid-cols-2 gap-2">
            <Button onClick={testBackendHealth} variant="outline">
              Test Backend
            </Button>
            <Button onClick={testLogin}>
              Test Login
            </Button>
            <Button onClick={testRegister} variant="outline">
              Test Register
            </Button>
            <Button onClick={manualLogin} variant="secondary">
              Manual Login
            </Button>
          </div>

          {/* Status Display */}
          {status && (
            <Alert>
              <AlertDescription>{status}</AlertDescription>
            </Alert>
          )}

          {error && (
            <Alert variant="destructive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {/* Quick Access */}
          <div className="pt-4 border-t">
            <Button 
              onClick={() => router.push('/dashboard')} 
              className="w-full"
              variant="outline"
            >
              Go to Dashboard (Skip Auth)
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
