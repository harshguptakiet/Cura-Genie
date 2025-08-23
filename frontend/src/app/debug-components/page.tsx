'use client';

import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ResultsTimeline } from '@/components/timeline/results-timeline';
import ModernGenomeBrowser from '@/components/genome/modern-genome-browser';
import GenomeBrowser from '@/components/genome/genome-browser';
import { Brain, BarChart3, Clock, Dna, Activity, Info, CheckCircle, XCircle } from 'lucide-react';
import { useAuthStore } from '@/store/auth-store';

export default function DebugComponentsPage() {
  const { user } = useAuthStore();
  const testUserId = user?.id?.toString() || '1';
  
  const [apiTests, setApiTests] = React.useState({
    backend: { status: 'pending', data: null },
    variants: { status: 'pending', data: null },
    timeline: { status: 'pending', data: null }
  });

  const testAPI = async (endpoint: string, label: string) => {
    try {
      console.log(`🧪 Testing ${label} API:`, endpoint);
      const response = await fetch(endpoint);
      const data = await response.json();
      
      setApiTests(prev => ({
        ...prev,
        [label]: { 
          status: response.ok ? 'success' : 'error', 
          data: response.ok ? data : { error: response.statusText, status: response.status }
        }
      }));
      
      console.log(`✅ ${label} API Response:`, { status: response.status, data });
    } catch (error) {
      console.error(`❌ ${label} API Error:`, error);
      setApiTests(prev => ({
        ...prev,
        [label]: { status: 'error', data: { error: error.message } }
      }));
    }
  };

  React.useEffect(() => {
    const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';
    
    // Test APIs
    testAPI(`${API_BASE}/health`, 'backend');
    testAPI(`${API_BASE}/api/genomic/variants/${testUserId}`, 'variants');
    testAPI(`${API_BASE}/api/timeline/${testUserId}`, 'timeline');
  }, [testUserId]);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success': return <CheckCircle className="h-4 w-4 text-green-600" />;
      case 'error': return <XCircle className="h-4 w-4 text-red-600" />;
      default: return <Activity className="h-4 w-4 text-yellow-600 animate-spin" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'success': return 'border-green-200 bg-green-50';
      case 'error': return 'border-red-200 bg-red-50';
      default: return 'border-yellow-200 bg-yellow-50';
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <div className="text-center space-y-4">
          <h1 className="text-4xl font-bold text-gray-900">🧬 Component Debug Dashboard</h1>
          <p className="text-xl text-gray-600">Testing Genome Browser and Timeline Components</p>
          <Badge variant="outline" className="text-lg px-4 py-2">
            User ID: {testUserId}
          </Badge>
        </div>

        {/* API Status Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {Object.entries(apiTests).map(([key, test]) => (
            <Card key={key} className={`${getStatusColor(test.status)} border-2`}>
              <CardHeader className="pb-2">
                <CardTitle className="flex items-center gap-2 capitalize">
                  {getStatusIcon(test.status)}
                  {key} API
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="text-sm font-medium">
                    Status: <span className={test.status === 'success' ? 'text-green-600' : 'text-red-600'}>{test.status}</span>
                  </div>
                  {test.data && (
                    <div className="text-xs">
                      <pre className="bg-gray-100 p-2 rounded overflow-auto max-h-20">
                        {JSON.stringify(test.data, null, 2).substring(0, 200)}...
                      </pre>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Component Testing Tabs */}
        <Card className="shadow-xl">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="h-6 w-6 text-blue-600" />
              Component Testing Dashboard
            </CardTitle>
            <CardDescription>
              Test individual components with real data from the backend API
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Tabs defaultValue="modern-browser" className="w-full">
              <TabsList className="grid grid-cols-3 w-full mb-6">
                <TabsTrigger value="modern-browser" className="flex items-center gap-2">
                  <Dna className="h-4 w-4" />
                  Modern Genome Browser
                </TabsTrigger>
                <TabsTrigger value="classic-browser" className="flex items-center gap-2">
                  <BarChart3 className="h-4 w-4" />
                  Classic Genome Browser
                </TabsTrigger>
                <TabsTrigger value="timeline" className="flex items-center gap-2">
                  <Clock className="h-4 w-4" />
                  Results Timeline
                </TabsTrigger>
              </TabsList>

              {/* Modern Genome Browser */}
              <TabsContent value="modern-browser" className="space-y-6">
                <Alert>
                  <Info className="h-4 w-4" />
                  <AlertDescription>
                    Testing the modern genome browser component with real VCF data from the backend.
                    This should show genomic variants, charts, and statistics.
                  </AlertDescription>
                </Alert>
                
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-4">
                  <ModernGenomeBrowser userId={testUserId} />
                </div>
              </TabsContent>

              {/* Classic Genome Browser */}
              <TabsContent value="classic-browser" className="space-y-6">
                <Alert>
                  <Info className="h-4 w-4" />
                  <AlertDescription>
                    Testing the classic genome browser with D3.js visualization.
                    This should render an interactive scatter plot of genomic variants.
                  </AlertDescription>
                </Alert>
                
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-4">
                  <GenomeBrowser userId={testUserId} />
                </div>
              </TabsContent>

              {/* Timeline */}
              <TabsContent value="timeline" className="space-y-6">
                <Alert>
                  <Info className="h-4 w-4" />
                  <AlertDescription>
                    Testing the results timeline component with real timeline events.
                    This should show upload events, analysis completions, and other milestones.
                  </AlertDescription>
                </Alert>
                
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-4">
                  <ResultsTimeline userId={testUserId} />
                </div>
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>

        {/* Debug Information */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Info className="h-5 w-5 text-blue-600" />
              Debug Information
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
              <div>
                <h4 className="font-semibold mb-2">Environment Variables</h4>
                <div className="space-y-1">
                  <div>API URL: <code className="bg-gray-100 px-2 py-1 rounded">{process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'}</code></div>
                  <div>Test User ID: <code className="bg-gray-100 px-2 py-1 rounded">{testUserId}</code></div>
                </div>
              </div>
              <div>
                <h4 className="font-semibold mb-2">Expected API Endpoints</h4>
                <div className="space-y-1 text-xs">
                  <div>• GET /health - Backend health check</div>
                  <div>• GET /api/genomic/variants/1 - Genomic variants data</div>
                  <div>• GET /api/timeline/1 - Timeline events</div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Instructions */}
        <Card className="bg-blue-50 border-blue-200">
          <CardHeader>
            <CardTitle className="text-blue-900">🔍 Debugging Instructions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3 text-sm">
              <p><strong>1. Check API Status:</strong> Ensure all three API endpoints show "success" status above.</p>
              <p><strong>2. Open Browser Console:</strong> Press F12 and check the Console tab for detailed API logs and errors.</p>
              <p><strong>3. Test Components:</strong> Switch between the tabs above to test each component individually.</p>
              <p><strong>4. Expected Results:</strong></p>
              <ul className="ml-6 space-y-1">
                <li>• Modern Browser: Should show variant distribution charts and statistics</li>
                <li>• Classic Browser: Should render D3.js scatter plot with genomic data</li>
                <li>• Timeline: Should display chronological events with upload and analysis history</li>
              </ul>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
