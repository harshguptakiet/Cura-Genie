'use client';

import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { useAuthStore } from '@/store/auth-store';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  FileText, 
  Download, 
  Calendar, 
  Clock,
  TrendingUp,
  Heart,
  Shield,
  Activity,
  AlertCircle
} from 'lucide-react';

// Fetch user data to determine report availability
const fetchUserData = async (userId: string) => {
  try {
    const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';
    const response = await fetch(`${baseUrl}/api/prs/scores/user/${userId}`);
    if (response.ok) {
      const data = await response.json();
      return Array.isArray(data) ? data : [data];
    }
  } catch (error) {
    console.log('No PRS data available yet');
  }
  return [];
};

export default function ReportsPage() {
  const { user } = useAuthStore();
  const userId = user?.id?.toString() || "1";
  
  // Fetch user data to determine report availability
  const { data: userData = [] } = useQuery({
    queryKey: ['user-data', userId],
    queryFn: () => fetchUserData(userId),
    enabled: !!userId,
  });
  
  const hasData = userData.length > 0;
  const reports = [
    {
      id: 1,
      title: "Comprehensive Genomic Analysis",
      description: `Complete genetic risk assessment and polygenic scores${hasData ? ` (${userData.length} conditions analyzed)` : ''}`,
      date: "2024-08-07",
      status: hasData ? "Ready" : "Pending Data",
      type: "genomic",
      icon: TrendingUp,
      color: "text-blue-600",
      bgColor: "bg-blue-50"
    },
    {
      id: 2,
      title: "Personalized Health Recommendations",
      description: "AI-generated health insights and action items",
      date: "2024-08-07",
      status: hasData ? "Ready" : "Pending Data",
      type: "recommendations",
      icon: Heart,
      color: "text-red-500",
      bgColor: "bg-red-50"
    },
    {
      id: 3,
      title: "Risk Assessment Summary",
      description: "Overview of genetic risk factors and prevention strategies",
      date: "2024-08-07",
      status: hasData ? "Ready" : "Pending Data",
      type: "risk",
      icon: Shield,
      color: "text-green-600",
      bgColor: "bg-green-50"
    },
    {
      id: 4,
      title: "Lifestyle Optimization Guide",
      description: "Personalized lifestyle recommendations based on genetic profile",
      date: "2024-08-07",
      status: hasData ? "Ready" : "Pending Data",
      type: "lifestyle",
      icon: Activity,
      color: "text-purple-600",
      bgColor: "bg-purple-50"
    }
  ];

  const handleDownload = (reportId: number, title: string) => {
    // In a real app, this would trigger a PDF download
    console.log(`Downloading report ${reportId}: ${title}`);
    alert(`Downloading ${title}...`);
  };

  return (
    <div className="space-y-8">
      {/* Header Section */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-xl p-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold mb-2 flex items-center gap-3">
              <FileText className="h-8 w-8" />
              Health Reports
            </h1>
            <p className="text-blue-100 text-lg">
              Download and manage your personalized health analysis reports
            </p>
          </div>
        </div>
      </div>

      {/* Reports Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {reports.map((report) => {
          const IconComponent = report.icon;
          return (
            <Card key={report.id} className="hover:shadow-lg transition-all hover:scale-105">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <div className={`p-3 rounded-full ${report.bgColor}`}>
                      <IconComponent className={`h-6 w-6 ${report.color}`} />
                    </div>
                    <div>
                      <CardTitle className="text-lg">{report.title}</CardTitle>
                      <CardDescription className="mt-1">
                        {report.description}
                      </CardDescription>
                    </div>
                  </div>
                  <Badge 
                    variant={report.status === 'Ready' ? 'default' : 'secondary'}
                    className={report.status === 'Ready' ? 'bg-green-100 text-green-800' : ''}
                  >
                    {report.status}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4 text-sm text-gray-600">
                    <div className="flex items-center gap-1">
                      <Calendar className="h-4 w-4" />
                      {new Date(report.date).toLocaleDateString()}
                    </div>
                    <div className="flex items-center gap-1">
                      <Clock className="h-4 w-4" />
                      Latest
                    </div>
                  </div>
                  <Button
                    size="sm"
                    variant={report.status === 'Ready' ? 'default' : 'secondary'}
                    disabled={report.status !== 'Ready'}
                    onClick={() => handleDownload(report.id, report.title)}
                    className="flex items-center gap-2"
                  >
                    <Download className="h-4 w-4" />
                    {report.status === 'Ready' ? 'Download' : 'Processing...'}
                  </Button>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Information Card */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5 text-blue-600" />
            About Your Reports
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-semibold mb-2">Report Generation</h4>
              <p className="text-sm text-gray-600">
                Reports are automatically generated after your genomic data is processed. 
                They include comprehensive analysis, risk assessments, and personalized recommendations.
              </p>
            </div>
            <div>
              <h4 className="font-semibold mb-2">Data Privacy</h4>
              <p className="text-sm text-gray-600">
                All reports are encrypted and stored securely. You have full control over 
                your data and can delete reports at any time.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
