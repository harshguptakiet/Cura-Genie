'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { CheckCircle, XCircle, Clock, RefreshCw, AlertTriangle } from 'lucide-react'

interface HealthCheckResult {
  status: 'checking' | 'success' | 'error'
  message: string
  details?: {
    status?: number;
    headers?: Record<string, string>;
    data?: string;
    error?: string;
  }
  timestamp: string
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000'

export function BackendHealthCheck() {
  const [results, setResults] = useState<Record<string, HealthCheckResult>>({})
  const [isChecking, setIsChecking] = useState(false)

  const updateResult = (endpoint: string, status: HealthCheckResult['status'], message: string, details?: HealthCheckResult['details']) => {
    setResults(prev => ({
      ...prev,
      [endpoint]: {
        status,
        message,
        details,
        timestamp: new Date().toISOString()
      }
    }))
  }

  const checkEndpoint = async (endpoint: string, method: string = 'GET', body?: Record<string, unknown>) => {
    updateResult(endpoint, 'checking', 'Testing...')
    
    try {
      const options: RequestInit = {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
      }

      if (body) {
        options.body = JSON.stringify(body)
      }

      console.log(`Testing ${method} ${API_BASE_URL}${endpoint}`)
      
      const response = await fetch(`${API_BASE_URL}${endpoint}`, options)
      const responseData = await response.text()
      
      if (response.ok) {
        updateResult(endpoint, 'success', `${response.status} ${response.statusText}`, {
          status: response.status,
          headers: Object.fromEntries(response.headers.entries()),
          data: responseData
        })
      } else {
        updateResult(endpoint, 'error', `${response.status} ${response.statusText}`, {
          status: response.status,
          headers: Object.fromEntries(response.headers.entries()),
          error: responseData
        })
      }
    } catch (error) {
      updateResult(endpoint, 'error', `Network Error: ${error instanceof Error ? error.message : 'Unknown error'}`, {
        error: error instanceof Error ? error.message : 'Unknown error'
      })
    }
  }

  const runAllChecks = async () => {
    setIsChecking(true)
    setResults({})

    // Test different endpoints
    await Promise.allSettled([
      checkEndpoint('/'),
      checkEndpoint('/docs'),
      checkEndpoint('/health'),
      checkEndpoint('/api/auth/login', 'POST', { email: 'test@example.com', password: 'test123' }),
      checkEndpoint('/api/auth/register', 'POST', { 
        email: 'test@example.com', 
        username: 'testuser', 
        password: 'test123456' 
      }),
    ])

    setIsChecking(false)
  }

  useEffect(() => {
    runAllChecks()
  }, [])

  const getStatusIcon = (status: HealthCheckResult['status']) => {
    switch (status) {
      case 'checking':
        return <Clock className="h-4 w-4 animate-spin text-blue-500" />
      case 'success':
        return <CheckCircle className="h-4 w-4 text-green-500" />
      case 'error':
        return <XCircle className="h-4 w-4 text-red-500" />
    }
  }

  const getStatusBadge = (status: HealthCheckResult['status']) => {
    switch (status) {
      case 'checking':
        return <Badge variant="outline" className="text-blue-600">Checking</Badge>
      case 'success':
        return <Badge className="bg-green-600">Success</Badge>
      case 'error':
        return <Badge variant="destructive">Error</Badge>
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <AlertTriangle className="h-5 w-5 text-orange-500" />
                Backend Health Check
              </CardTitle>
              <p className="text-sm text-gray-600 mt-1">
                Debugging connectivity to: <code className="bg-gray-100 px-2 py-1 rounded text-xs">{API_BASE_URL}</code>
              </p>
            </div>
            <Button onClick={runAllChecks} disabled={isChecking} variant="outline">
              <RefreshCw className={`h-4 w-4 mr-2 ${isChecking ? 'animate-spin' : ''}`} />
              Recheck
            </Button>
          </div>
        </CardHeader>
      </Card>

      {/* Environment Info */}
      <Alert>
        <AlertDescription>
          <div className="space-y-2">
            <div><strong>API Base URL:</strong> {API_BASE_URL}</div>
            <div><strong>Environment:</strong> {process.env.NODE_ENV}</div>
            <div><strong>Current URL:</strong> {typeof window !== 'undefined' ? window.location.origin : 'N/A'}</div>
          </div>
        </AlertDescription>
      </Alert>

      {/* Results */}
      <div className="space-y-4">
        {Object.entries(results).map(([endpoint, result]) => (
          <Card key={endpoint}>
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  {getStatusIcon(result.status)}
                  <span className="font-mono text-sm">{endpoint}</span>
                </div>
                {getStatusBadge(result.status)}
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <p className="text-sm">{result.message}</p>
                <p className="text-xs text-gray-500">
                  Last checked: {new Date(result.timestamp).toLocaleString()}
                </p>
                
                {result.details && (
                  <details className="mt-2">
                    <summary className="text-xs cursor-pointer text-blue-600 hover:text-blue-800">
                      Show Details
                    </summary>
                    <pre className="text-xs bg-gray-100 p-2 rounded mt-2 overflow-auto max-h-40">
                      {JSON.stringify(result.details, null, 2)}
                    </pre>
                  </details>
                )}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Quick Fixes */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Quick Fixes</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="text-sm space-y-2">
            <p><strong>If you see 405 Method Not Allowed:</strong></p>
            <ul className="list-disc list-inside space-y-1 text-gray-700">
              <li>Your backend server might not be running</li>
              <li>The API endpoint doesn't exist or doesn't support POST</li>
              <li>CORS issues in production deployment</li>
            </ul>
          </div>
          
          <div className="text-sm space-y-2">
            <p><strong>If you see Network/Connection errors:</strong></p>
            <ul className="list-disc list-inside space-y-1 text-gray-700">
              <li>Backend server is not accessible at {API_BASE_URL}</li>
              <li>Check if your backend is deployed and running</li>
              <li>Update NEXT_PUBLIC_API_URL to point to your deployed backend</li>
            </ul>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
