'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { CheckCircle, XCircle, Loader2 } from 'lucide-react';

// Use environment variable for API base URL
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

export function ApiTester() {
  const [testResults, setTestResults] = useState<{ [key: string]: 'loading' | 'success' | 'error' | 'idle' }>({});
  const [responses, setResponses] = useState<Record<string, APIResponse>>({});
  const [userId, setUserId] = useState('1');

  const testEndpoint = async (name: string, url: string, options?: RequestInit) => {
    setTestResults(prev => ({ ...prev, [name]: 'loading' }));

    try {
      const response = await fetch(url, options);
      const data = await response.text();

      try {
        const jsonData = JSON.parse(data);
        setResponses(prev => ({ ...prev, [name]: { status: response.status, data: jsonData } }));
      } catch {
        setResponses(prev => ({ ...prev, [name]: { status: response.status, data: data } }));
      }

      if (response.ok) {
        setTestResults(prev => ({ ...prev, [name]: 'success' }));
      } else {
        setTestResults(prev => ({ ...prev, [name]: 'error' }));
      }
    } catch (error) {
      setTestResults(prev => ({ ...prev, [name]: 'error' }));
      setResponses(prev => ({ ...prev, [name]: { error: error.message } }));
    }
  };

  const testEndpoints = [
    {
      name: 'API Root',
      url: `${API_BASE_URL}/`,
      method: 'GET'
    },
    {
      name: 'API Docs',
      url: `${API_BASE_URL}/docs`,
      method: 'GET'
    },
    {
      name: 'Local Upload Test',
      url: `${API_BASE_URL}/api/local-upload/test`,
      method: 'GET'
    },
    {
      name: 'PRS Scores',
      url: `${API_BASE_URL}/api/prs/scores/user/${userId}`,
      method: 'GET'
    },
    {
      name: 'Genomic Data (Original)',
      url: `${API_BASE_URL}/api/genomic-data/user/${userId}`,
      method: 'GET'
    },
    {
      name: 'Chatbot Test',
      url: `${API_BASE_URL}/api/chatbot/chat`,
      method: 'POST'
    }
  ];

  const createMockData = async () => {
    // Create PRS data
    await testEndpoint('Create PRS', `${API_BASE_URL}/api/prs/scores`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_id: parseInt(userId),
        disease_type: "cardiovascular_disease",
        score: 0.75,
        confidence: 0.89
      })
    });

    // Create recommendations
    await testEndpoint('Create Recommendations', `${API_BASE_URL}/api/recommendations`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_id: parseInt(userId),
        title: "Cardiovascular Health Focus",
        description: "Based on your genetic profile, you have an elevated risk for cardiovascular disease.",
        category: "medical",
        priority: "high"
      })
    });
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'loading':
        return <Badge variant="secondary"><Loader2 className="h-3 w-3 animate-spin mr-1" />Loading</Badge>;
      case 'success':
        return <Badge variant="default" className="bg-green-500"><CheckCircle className="h-3 w-3 mr-1" />Success</Badge>;
      case 'error':
        return <Badge variant="destructive"><XCircle className="h-3 w-3 mr-1" />Error</Badge>;
      default:
        return <Badge variant="outline">Not tested</Badge>;
    }
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle>API Endpoint Tester</CardTitle>
        <CardDescription>Test API endpoints and create mock data for development</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-center gap-2">
          <label className="text-sm font-medium">User ID:</label>
          <Input
            value={userId}
            onChange={(e) => setUserId(e.target.value)}
            className="w-20"
          />
          <Button onClick={createMockData} variant="outline">
            Create Mock Data
          </Button>
        </div>

        <div className="grid grid-cols-1 gap-4">
          {testEndpoints.map((endpoint) => (
            <div key={endpoint.name} className="border rounded p-3">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <span className="font-medium">{endpoint.name}</span>
                  {getStatusBadge(testResults[endpoint.name] || 'idle')}
                </div>
                <Button
                  onClick={() => testEndpoint(endpoint.name, endpoint.url)}
                  size="sm"
                  variant="outline"
                >
                  Test
                </Button>
              </div>
              <div className="text-sm text-gray-600 mb-2">
                {endpoint.method} {endpoint.url}
              </div>
              {responses[endpoint.name] && (
                <Alert className="mt-2">
                  <AlertDescription>
                    <pre className="text-xs overflow-auto max-h-32">
                      {JSON.stringify(responses[endpoint.name], null, 2)}
                    </pre>
                  </AlertDescription>
                </Alert>
              )}
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
