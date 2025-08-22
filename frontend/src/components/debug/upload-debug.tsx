'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { useAuthStore } from '@/store/auth-store';
import { Info, CheckCircle, XCircle, RefreshCw } from 'lucide-react';

// Define proper interfaces for type safety
interface HealthCheckResult {
  status: 'success' | 'error' | 'unknown' | 'no-data';
  data: unknown;
}

interface DebugResults {
  auth: HealthCheckResult;
  uploadEndpoint: HealthCheckResult;
  prsEndpoint: HealthCheckResult;
}

export function UploadDebug() {
  const { user, token, isAuthenticated } = useAuthStore();
  const [isChecking, setIsChecking] = useState(false);
  const [results, setResults] = useState<DebugResults | null>(null);

  const checkAPIs = async () => {
    setIsChecking(true);
    const results: DebugResults = {
      auth: { status: 'unknown', data: null },
      uploadEndpoint: { status: 'unknown', data: null },
      prsEndpoint: { status: 'unknown', data: null }
    };

    // Check authentication
    try {
      results.auth = {
        status: isAuthenticated ? 'success' : 'error',
        data: {
          isAuthenticated,
          hasUser: !!user,
          hasToken: !!token,
          userId: user?.id,
          username: user?.username
        }
      };
    } catch (error) {
      results.auth = { status: 'error', data: error };
    }

    // Check upload endpoint
    try {
      // Test the local upload endpoint with GET to /api/local-upload/test
      const response = await fetch('http://localhost:8000/api/local-upload/test', {
        method: 'GET'
      });
      const data = response.ok ? await response.json() : null;
      results.uploadEndpoint = {
        status: response.ok ? 'success' : 'error',
        data: {
          status: response.status,
          statusText: response.statusText,
          responseData: data,
          headers: Object.fromEntries(response.headers.entries())
        }
      };
    } catch (error) {
      results.uploadEndpoint = { status: 'error', data: error };
    }

    // Check PRS endpoint
    try {
      const userId = user?.id?.toString() || "1";
      const response = await fetch(`http://localhost:8000/api/prs/scores/user/${userId}`);
      const data = response.ok ? await response.json() : null;
      results.prsEndpoint = {
        status: response.ok ? 'success' : (response.status === 404 ? 'no-data' : 'error'),
        data: {
          status: response.status,
          statusText: response.statusText,
          responseData: data
        }
      };
    } catch (error) {
      results.prsEndpoint = { status: 'error', data: error };
    }

    setResults(results);
    setIsChecking(false);
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success':
        return <CheckCircle className="h-4 w-4 text-green-600" />;
      case 'no-data':
        return <Info className="h-4 w-4 text-blue-600" />;
      case 'error':
        return <XCircle className="h-4 w-4 text-red-600" />;
      default:
        return <RefreshCw className="h-4 w-4 text-gray-400" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'success':
        return 'border-green-200 bg-green-50';
      case 'no-data':
        return 'border-blue-200 bg-blue-50';
      case 'error':
        return 'border-red-200 bg-red-50';
      default:
        return 'border-gray-200 bg-gray-50';
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <RefreshCw className="h-5 w-5 text-blue-600" />
          API & Upload Debug
        </CardTitle>
        <CardDescription>
          Check API connectivity and troubleshoot upload issues
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <Button onClick={checkAPIs} disabled={isChecking} className="w-full">
          {isChecking ? 'Checking...' : 'Check API Status'}
        </Button>

        {/* Test Upload Button */}
        <Button 
          onClick={async () => {
            try {
              const formData = new FormData();
              const testFile = new Blob(['##fileformat=VCFv4.2\n#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\nchr1\t1000\trs123\tA\tT\t100\tPASS\t.'], { type: 'text/plain' });
              formData.append('file', testFile, 'test.vcf');
              formData.append('user_id', user?.id?.toString() || '1');
              
              const response = await fetch('http://localhost:8000/api/local-upload/genomic-data', {
                method: 'POST',
                headers: token ? { 'Authorization': `Bearer ${token}` } : {},
                body: formData
              });
              
              const result = response.ok ? await response.json() : await response.text();
              
              // Check for database schema error
              if (!response.ok && typeof result === 'string' && result.includes('no such column: uploaded_at')) {
                alert(`Database schema error: The backend database is missing the 'uploaded_at' column. Please run database migrations to update the schema.\n\nError: ${result}`);
              } else {
                alert(`Upload test result: ${response.status} - ${JSON.stringify(result)}`);
              }
            } catch (error) {
              alert(`Upload test error: ${error}`);
            }
          }}
          variant="outline"
          className="w-full"
        >
          Test Upload
        </Button>

        {results && (
          <div className="space-y-4">
            {/* Authentication Status */}
            <Alert className={getStatusColor(results.auth.status)}>
              <div className="flex items-center gap-2">
                {getStatusIcon(results.auth.status)}
                <AlertDescription>
                  <strong>Authentication:</strong> {results.auth.status}
                  <pre className="mt-2 text-xs bg-white p-2 rounded border overflow-auto">
                    {JSON.stringify(results.auth.data, null, 2)}
                  </pre>
                </AlertDescription>
              </div>
            </Alert>

            {/* Upload Endpoint Status */}
            <Alert className={getStatusColor(results.uploadEndpoint.status)}>
              <div className="flex items-center gap-2">
                {getStatusIcon(results.uploadEndpoint.status)}
                <AlertDescription>
                  <strong>Upload Endpoint:</strong> {results.uploadEndpoint.status}
                  <pre className="mt-2 text-xs bg-white p-2 rounded border overflow-auto">
                    {JSON.stringify(results.uploadEndpoint.data, null, 2)}
                  </pre>
                </AlertDescription>
              </div>
            </Alert>

            {/* PRS Endpoint Status */}
            <Alert className={getStatusColor(results.prsEndpoint.status)}>
              <div className="flex items-center gap-2">
                {getStatusIcon(results.prsEndpoint.status)}
                <AlertDescription>
                  <strong>PRS Endpoint:</strong> {results.prsEndpoint.status}
                  <pre className="mt-2 text-xs bg-white p-2 rounded border overflow-auto max-h-40">
                    {JSON.stringify(results.prsEndpoint.data, null, 2)}
                  </pre>
                </AlertDescription>
              </div>
            </Alert>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
