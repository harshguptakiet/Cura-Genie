'use client';

import React, { useState } from 'react';
import { useQueryClient, useQuery } from '@tanstack/react-query';
import { useAuthStore } from '@/store/auth-store';
import { FileUpload } from '@/components/ui/file-upload';
import { ClinicalFileUpload } from '@/components/ui/clinical-file-upload';
import { PrsScoreDisplay } from '@/components/prs/prs-score-display';
import { RecommendationsDisplay } from '@/components/recommendations/recommendations-display';
import DiabetesAssessment from '@/components/medical/diabetes-assessment';
import AlzheimerAssessment from '@/components/medical/alzheimer-assessment';
import BrainTumorAssessment from '@/components/medical/brain-tumor-assessment';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { toast } from 'sonner';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  CheckCircle,
  Clock,
  Upload,
  BarChart3,
  Brain,
  FileText,
  TrendingUp,
  Heart,
  Shield,
  Activity,
  Sparkles,
  ArrowRight,
  Zap,
  Users,
  ChevronDown,
  ChevronUp,
  Lightbulb,
  Target,
  Stethoscope
} from 'lucide-react';
import Link from 'next/link';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';

// Fetch PRS data and dashboard stats using direct API endpoints
const fetchDashboardStats = async (userId: string) => {
  try {
    console.log(`Fetching dashboard stats for user: ${userId}`);

    // Use the API base URL from environment
    const statsResponse = await fetch(`${API_BASE_URL}/api/direct/dashboard-stats/user/${userId}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    console.log(`Dashboard Stats API Response status: ${statsResponse.status}`);

    if (statsResponse.ok) {
      const statsData = await statsResponse.json();
      console.log('Dashboard stats received:', statsData);

      // Also fetch detailed PRS scores for the components
      try {
        const prsResponse = await fetch(`${API_BASE_URL}/api/direct/prs/user/${userId}`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        });

        if (prsResponse.ok) {
          const prsData = await prsResponse.json();
          console.log(`PRS scores received: ${prsData.length} records`);

          // Combine the data for dashboard display
          return {
            prsScores: prsData,
            stats: statsData,
            hasData: statsData.has_data,
            totalScores: statsData.total_prs_scores,
            averageScore: statsData.average_risk_score,
            diseasesAnalyzed: statsData.diseases_analyzed
          };
        } else {
          // Return stats data even if PRS details fail
          return {
            prsScores: [],
            stats: statsData,
            hasData: statsData.has_data,
            totalScores: statsData.total_prs_scores,
            averageScore: statsData.average_risk_score,
            diseasesAnalyzed: statsData.diseases_analyzed
          };
        }
      } catch (prsError) {
        console.warn('Failed to fetch PRS data, using stats only:', prsError);
        return {
          prsScores: [],
          stats: statsData,
          hasData: statsData.has_data,
          totalScores: statsData.total_prs_scores,
          averageScore: statsData.average_risk_score,
          diseasesAnalyzed: statsData.diseases_analyzed
        };
      }
    } else if (statsResponse.status === 404) {
      console.log('No dashboard data found for user');
      return { prsScores: [], stats: null, hasData: false, totalScores: 0, averageScore: 0, diseasesAnalyzed: 0 };
    } else {
      console.warn(`Dashboard Stats API error: ${statsResponse.status} - ${statsResponse.statusText}`);
      return { prsScores: [], stats: null, hasData: false, totalScores: 0, averageScore: 0, diseasesAnalyzed: 0 };
    }
  } catch (error) {
    console.warn('Backend not available, using fallback data:', error);
    // Return fallback data when backend is not available
    return {
      prsScores: [],
      stats: null,
      hasData: false,
      totalScores: 0,
      averageScore: 0,
      diseasesAnalyzed: 0,
      isOffline: true
    };
  }
};

export default function DashboardPage() {
  const { user } = useAuthStore();
  const userId = user?.id?.toString() || "1";
  const [hasUploadedFile, setHasUploadedFile] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const queryClient = useQueryClient();

  // Fetch dashboard stats
  const { data: dashboardData = { prsScores: [], hasData: false, totalScores: 0, averageScore: 0, diseasesAnalyzed: 0 } } = useQuery({
    queryKey: ['dashboard-stats', userId],
    queryFn: () => fetchDashboardStats(userId),
    enabled: !!userId,
    retry: 1, // Only retry once
    retryDelay: 1000, // Wait 1 second before retry
  });

  const handleUploadSuccess = async (data: any) => {
    console.log('File uploaded successfully:', data);
    setHasUploadedFile(true);
    setIsProcessing(true);

    toast.success('File uploaded! Processing your genomic data...');

    // Refresh data immediately after upload
    try {
      console.log('Starting data refresh after upload...');

      // Invalidate and refetch the data with individual error handling
      const refreshPromises = [];

      try {
        refreshPromises.push(queryClient.invalidateQueries({ queryKey: ['prs-scores', userId] }));
        console.log('PRS scores query invalidated');
      } catch (error) {
        console.warn('Failed to invalidate PRS scores query:', error);
      }

      try {
        refreshPromises.push(queryClient.invalidateQueries({ queryKey: ['recommendations', userId] }));
        console.log('Recommendations query invalidated');
      } catch (error) {
        console.warn('Failed to invalidate recommendations query:', error);
      }

      try {
        refreshPromises.push(queryClient.invalidateQueries({ queryKey: ['dashboard-stats', userId] }));
        console.log('Dashboard stats query invalidated');
      } catch (error) {
        console.warn('Failed to invalidate dashboard stats query:', error);
      }

      // Wait for all invalidations to complete (but don't fail if some fail)
      await Promise.allSettled(refreshPromises);

      setIsProcessing(false);
      console.log('Data refresh completed successfully');
      toast.success('Analysis complete! Your results are now available. You can upload another file if needed.');

      // Reset upload state immediately
      setHasUploadedFile(false);

    } catch (error) {
      console.error('Error during post-upload processing:', error);
      setIsProcessing(false);

      // Still show success since upload worked, just refresh failed
      toast.success('File uploaded successfully! Please refresh the page to see new results.');

      // Reset upload state even on error
      setHasUploadedFile(false);
    }
  };

  // Use data from the new dashboard stats structure
  const hasData = dashboardData.hasData || hasUploadedFile;
  const averageScore = dashboardData.averageScore || 0;
  const totalScores = dashboardData.totalScores || 0;
  const diseasesAnalyzed = dashboardData.diseasesAnalyzed || 0;

  const quickStats = [
    {
      title: "Genomic Analysis",
      value: hasData ? "Complete" : "Pending",
      icon: BarChart3,
      color: hasData ? "text-green-600" : "text-gray-400",
      bgColor: hasData ? "bg-green-50" : "bg-gray-50"
    },
    {
      title: "Conditions Analyzed",
      value: diseasesAnalyzed > 0 ? diseasesAnalyzed.toString() : "0",
      icon: Shield,
      color: diseasesAnalyzed > 0 ? "text-blue-600" : "text-gray-400",
      bgColor: diseasesAnalyzed > 0 ? "bg-blue-50" : "bg-gray-50"
    },
    {
      title: "Average Risk Score",
      value: averageScore > 0 ? `${averageScore}%` : "N/A",
      icon: Heart,
      color: averageScore > 70 ? "text-red-500" : averageScore > 40 ? "text-yellow-500" : averageScore > 0 ? "text-green-500" : "text-gray-400",
      bgColor: averageScore > 70 ? "bg-red-50" : averageScore > 40 ? "bg-yellow-50" : averageScore > 0 ? "bg-green-50" : "bg-gray-50"
    },
    {
      title: "AI Insights",
      value: hasData ? "Ready" : "Pending",
      icon: Brain,
      color: hasData ? "text-purple-600" : "text-gray-400",
      bgColor: hasData ? "bg-purple-50" : "bg-gray-50"
    }
  ];

  const quickActions = [
    {
      title: "Upload Genomic Data",
      description: "Upload your VCF file for personalized analysis",
      icon: Upload,
      href: "#upload",
      color: "bg-blue-600 hover:bg-blue-700"
    },
    {
      title: "View Analysis",
      description: "Explore your genomic visualizations",
      icon: BarChart3,
      href: "/dashboard/visualizations",
      color: "bg-green-600 hover:bg-green-700"
    },
    {
      title: "AI Assistant",
      description: "Chat with your AI health advisor",
      icon: Brain,
      href: "/dashboard/chatbot",
      color: "bg-purple-600 hover:bg-purple-700"
    },
    {
      title: "Health Reports",
      description: "Download comprehensive reports",
      icon: FileText,
      href: "/dashboard/reports",
      color: "bg-orange-600 hover:bg-orange-700"
    }
  ];

  return (
    <div className="space-y-8">
      {/* Offline Indicator - Subtle */}
      {dashboardData.isOffline && (
        <div className="flex items-center gap-2 text-orange-600 bg-orange-50 rounded-lg px-4 py-2 text-sm border border-orange-200">
          <Activity className="h-3 w-3" />
          <span><strong>Demo Mode:</strong> Backend offline - interface testing available</span>
        </div>
      )}

      {/* Welcome Header */}
      <div className="relative bg-gradient-to-br from-blue-600 via-indigo-600 to-purple-700 text-white rounded-2xl p-8 overflow-hidden shadow-2xl">
        <div className="absolute inset-0 bg-gradient-to-r from-blue-600/20 to-purple-600/20 backdrop-blur-sm"></div>
        <div className="absolute top-0 right-0 w-32 h-32 bg-white/10 rounded-full -translate-y-16 translate-x-16"></div>
        <div className="absolute bottom-0 left-0 w-24 h-24 bg-white/5 rounded-full translate-y-12 -translate-x-12"></div>

        <div className="relative z-10 flex items-center justify-between">
          <div className="space-y-4">
            <div className="flex items-center gap-3">
              <h1 className="text-4xl font-bold mb-2 bg-gradient-to-r from-white to-blue-100 bg-clip-text text-transparent">
                Welcome back, {user?.username || 'User'}!
              </h1>
              <div className="animate-bounce">
                <span className="text-3xl">👋</span>
              </div>
            </div>
            <p className="text-blue-100 text-xl max-w-2xl leading-relaxed">
              Your personalized genomics dashboard is ready to help you understand your health better.
            </p>
            <div className="flex items-center gap-4 pt-2">
              <div className="flex items-center gap-2 text-blue-200">
                <Shield className="h-4 w-4" />
                <span className="text-sm">Secure & Private</span>
              </div>
              <div className="flex items-center gap-2 text-blue-200">
                <Zap className="h-4 w-4" />
                <span className="text-sm">AI-Powered</span>
              </div>
            </div>
          </div>
          <div className="hidden lg:block">
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-r from-blue-400 to-purple-500 rounded-full blur-xl opacity-30 animate-pulse"></div>
              <Sparkles className="h-20 w-20 text-blue-200 relative z-10 animate-pulse" />
            </div>
          </div>
        </div>
      </div>

      {/* Processing Status - Subtle */}
      {hasUploadedFile && (
        <div className={`flex items-center gap-3 rounded-xl px-4 py-3 text-sm ${isProcessing
            ? "bg-gradient-to-r from-amber-50 to-yellow-50 border border-amber-200 text-amber-800"
            : "bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200 text-green-800"
          }`}>
          {isProcessing ? (
            <>
              <Clock className="h-4 w-4 text-amber-600 animate-spin" />
              <span className="font-medium">🧬 Processing genomic data...</span>
            </>
          ) : (
            <>
              <CheckCircle className="h-4 w-4 text-green-600" />
              <span className="font-medium">✅ Analysis complete! Check your results in the navigation.</span>
            </>
          )}
        </div>
      )}

      {/* Quick Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mt-8">
        {quickStats.map((stat, index) => {
          const IconComponent = stat.icon;
          return (
            <Card key={index} className="hover:shadow-lg transition-all duration-300 hover:translate-y-[-4px] border border-gray-100 overflow-hidden">
              <div className="absolute h-1 top-0 left-0 right-0 bg-gradient-to-r from-blue-500 to-indigo-600 opacity-75"></div>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">{stat.title}</p>
                    <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
                  </div>
                  <div className={`p-3 rounded-full ${stat.bgColor}`}>
                    <IconComponent className={`h-6 w-6 ${stat.color}`} />
                  </div>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Getting Started Section */}
      {!hasData && (
        <Card className="border-2 border-dashed border-blue-200 bg-blue-50/30 hover:border-blue-300 hover:bg-blue-50/50 transition-all duration-300 shadow-sm hover:shadow-md">
          <CardContent className="p-8 text-center">
            <div className="flex flex-col items-center space-y-4">
              <div className="p-4 bg-blue-100 rounded-full">
                <Upload className="h-8 w-8 text-blue-600" />
              </div>
              <div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  Ready to Get Started?
                </h3>
                <p className="text-gray-600 mb-4 max-w-md">
                  Upload your genomic data to unlock personalized health insights.
                </p>
                <Button
                  onClick={() => {
                    const uploadSection = document.getElementById('upload');
                    if (uploadSection) {
                      uploadSection.scrollIntoView({ behavior: 'smooth' });
                    }
                  }}
                  className="bg-blue-600 hover:bg-blue-700 transition-all duration-300 transform hover:scale-105 shadow-md hover:shadow-lg"
                >
                  <Upload className="h-4 w-4 mr-2" />
                  Upload Your Data
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Main Actions */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-10">
        <Card className="hover:shadow-lg transition-all duration-300 hover:translate-y-[-4px] bg-gradient-to-br from-white to-blue-50 border border-blue-100">
          <CardContent className="p-6">
            <div className="flex items-start space-x-4">
              <div className="p-3 bg-blue-100 rounded-lg shadow-inner">
                <Upload className="h-6 w-6 text-blue-600" />
              </div>
              <div className="flex-1">
                <h3 className="font-semibold text-gray-900 mb-1">Upload & Analyze</h3>
                <p className="text-sm text-gray-600 mb-3">
                  Upload your genomic data for personalized health insights
                </p>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    const uploadSection = document.getElementById('upload');
                    if (uploadSection) {
                      uploadSection.scrollIntoView({ behavior: 'smooth' });
                    }
                  }}
                >
                  Get Started <ArrowRight className="h-3 w-3 ml-1" />
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="hover:shadow-lg transition-all duration-300 hover:translate-y-[-4px] bg-gradient-to-br from-white to-green-50 border border-green-100">
          <CardContent className="p-6">
            <div className="flex items-start space-x-4">
              <div className="p-3 bg-green-100 rounded-lg shadow-inner">
                <BarChart3 className="h-6 w-6 text-green-600" />
              </div>
              <div className="flex-1">
                <h3 className="font-semibold text-gray-900 mb-1">Explore Results</h3>
                <p className="text-sm text-gray-600 mb-3">
                  {hasData ? "View your personalized genomic analysis" : "Results will appear here after upload"}
                </p>
                <Link href="/dashboard/visualizations">
                  <Button
                    variant="outline"
                    size="sm"
                    disabled={!hasData}
                  >
                    View Analysis <ArrowRight className="h-3 w-3 ml-1" />
                  </Button>
                </Link>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Upload Section */}
      <div id="upload" className="mt-12">
        <Tabs defaultValue="genomic" className="w-full">
          <TabsList className="grid grid-cols-2 w-full mb-6">
            <TabsTrigger value="genomic" className="flex items-center gap-2">
              <Upload className="h-4 w-4" />
              Genomic Data (VCF)
            </TabsTrigger>
            <TabsTrigger value="clinical" className="flex items-center gap-2">
              <FileText className="h-4 w-4" />
              Clinical Files
            </TabsTrigger>
          </TabsList>

          <TabsContent value="genomic">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Zap className="h-5 w-5 text-orange-500" />
                  Upload Your Genomic Data
                </CardTitle>
                <CardDescription>
                  Upload your VCF file to get started with personalized genomic analysis
                </CardDescription>
              </CardHeader>
              <CardContent>
                <FileUpload onUploadSuccess={handleUploadSuccess} />
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="clinical">
            <ClinicalFileUpload onUploadSuccess={handleUploadSuccess} assessmentType="general" />
          </TabsContent>
        </Tabs>
      </div>

      {/* Results & Analysis Section - Only show when data exists */}
      {hasData && (
        <Card className="mt-12 border border-gray-100 shadow-md hover:shadow-lg transition-all duration-300">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Target className="h-5 w-5 text-blue-600" />
              Your Genomic Analysis Results
            </CardTitle>
            <CardDescription>
              Explore your personalized genomic insights, risk scores, and health recommendations
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Tabs defaultValue="scores" className="w-full">
              <TabsList className="grid grid-cols-3 w-full">
                <TabsTrigger value="scores" className="flex items-center gap-2">
                  <BarChart3 className="h-4 w-4" />
                  Risk Scores
                </TabsTrigger>
                <TabsTrigger value="recommendations" className="flex items-center gap-2">
                  <Lightbulb className="h-4 w-4" />
                  Recommendations
                </TabsTrigger>
                <TabsTrigger value="assessments" className="flex items-center gap-2">
                  <Stethoscope className="h-4 w-4" />
                  Health Assessments
                </TabsTrigger>
              </TabsList>

              <TabsContent value="scores" className="mt-6">
                <div className="space-y-4">
                  <div className="border-l-4 border-blue-500 pl-4">
                    <h4 className="font-semibold text-gray-900 mb-1">Polygenic Risk Scores (PRS)</h4>
                    <p className="text-sm text-gray-600">
                      Your personalized risk scores based on genetic variants across multiple conditions.
                    </p>
                  </div>
                  <PrsScoreDisplay userId={userId} key={hasUploadedFile ? 'uploaded' : 'initial'} />
                </div>
              </TabsContent>

              <TabsContent value="recommendations" className="mt-6">
                <div className="space-y-4">
                  <div className="border-l-4 border-green-500 pl-4">
                    <h4 className="font-semibold text-gray-900 mb-1">Personalized Health Recommendations</h4>
                    <p className="text-sm text-gray-600">
                      AI-powered insights and actionable recommendations based on your genetic profile.
                    </p>
                  </div>
                  <RecommendationsDisplay userId={userId} key={hasUploadedFile ? 'uploaded-rec' : 'initial-rec'} />
                </div>
              </TabsContent>

              <TabsContent value="assessments" className="mt-6">
                <div className="space-y-6">
                  <div className="border-l-4 border-purple-500 pl-4 mb-6">
                    <h4 className="font-semibold text-gray-900 mb-1">Clinical Risk Assessments</h4>
                    <p className="text-sm text-gray-600">
                      Comprehensive analysis for specific health conditions based on your genomic data.
                    </p>
                  </div>

                  <div className="grid gap-6">
                    <Card className="border-left-accent border-l-red-400">
                      <CardHeader className="pb-3">
                        <CardTitle className="text-lg flex items-center gap-2">
                          <Heart className="h-5 w-5 text-red-500" />
                          Diabetes Risk Assessment
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        <Tabs defaultValue="assessment" className="w-full">
                          <TabsList className="grid grid-cols-2 w-full mb-4">
                            <TabsTrigger value="assessment">Assessment</TabsTrigger>
                            <TabsTrigger value="upload">Upload Data</TabsTrigger>
                          </TabsList>
                          <TabsContent value="assessment">
                            <DiabetesAssessment userId={userId} />
                          </TabsContent>
                          <TabsContent value="upload">
                            <ClinicalFileUpload onUploadSuccess={handleUploadSuccess} assessmentType="diabetes" />
                          </TabsContent>
                        </Tabs>
                      </CardContent>
                    </Card>

                    <Card className="border-left-accent border-l-purple-400">
                      <CardHeader className="pb-3">
                        <CardTitle className="text-lg flex items-center gap-2">
                          <Brain className="h-5 w-5 text-purple-500" />
                          Alzheimer's Risk Assessment
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        <Tabs defaultValue="assessment" className="w-full">
                          <TabsList className="grid grid-cols-2 w-full mb-4">
                            <TabsTrigger value="assessment">Assessment</TabsTrigger>
                            <TabsTrigger value="upload">Upload Data</TabsTrigger>
                          </TabsList>
                          <TabsContent value="assessment">
                            <AlzheimerAssessment userId={userId} />
                          </TabsContent>
                          <TabsContent value="upload">
                            <ClinicalFileUpload onUploadSuccess={handleUploadSuccess} assessmentType="alzheimer" />
                          </TabsContent>
                        </Tabs>
                      </CardContent>
                    </Card>

                    <Card className="border-left-accent border-l-orange-400">
                      <CardHeader className="pb-3">
                        <CardTitle className="text-lg flex items-center gap-2">
                          <Activity className="h-5 w-5 text-orange-500" />
                          Brain Tumor Risk Assessment
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        <Tabs defaultValue="assessment" className="w-full">
                          <TabsList className="grid grid-cols-2 w-full mb-4">
                            <TabsTrigger value="assessment">Assessment</TabsTrigger>
                            <TabsTrigger value="upload">Upload Data</TabsTrigger>
                          </TabsList>
                          <TabsContent value="assessment">
                            <BrainTumorAssessment userId={userId} />
                          </TabsContent>
                          <TabsContent value="upload">
                            <ClinicalFileUpload onUploadSuccess={handleUploadSuccess} assessmentType="brain-tumor" />
                          </TabsContent>
                        </Tabs>
                      </CardContent>
                    </Card>
                  </div>
                </div>
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>
      )}

      {/* Feature Highlights */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-16">
        <Card className="text-center p-6 border border-gray-100 hover:shadow-xl transition-all duration-300 hover:translate-y-[-6px]">
          <div className="relative w-24 h-24 mx-auto mb-6">
            <div className="absolute inset-0 bg-purple-200 rounded-full animate-pulse opacity-50"></div>
            <div className="relative flex items-center justify-center h-full">
              <Brain className="h-12 w-12 text-purple-600" />
            </div>
          </div>
          <h3 className="font-semibold text-gray-900 mb-2">AI-Powered Analysis</h3>
          <p className="text-sm text-gray-600">
            Get personalized health insights powered by advanced AI algorithms
          </p>
          <Link href="/dashboard/chatbot">
            <Button variant="ghost" size="sm" className="mt-3">
              Try AI Assistant <ArrowRight className="h-3 w-3 ml-1" />
            </Button>
          </Link>
        </Card>

        <Card className="text-center p-6 border border-gray-100 hover:shadow-xl transition-all duration-300 hover:translate-y-[-6px]">
          <div className="relative w-24 h-24 mx-auto mb-6">
            <div className="absolute inset-0 bg-green-200 rounded-full animate-pulse opacity-50"></div>
            <div className="relative flex items-center justify-center h-full">
              <Shield className="h-12 w-12 text-green-600" />
            </div>
          </div>
          <h3 className="font-semibold text-gray-900 mb-2">Privacy First</h3>
          <p className="text-sm text-gray-600">
            Your genetic data is encrypted and never shared without your consent
          </p>
          <Link href="/dashboard/privacy-policy">
            <Button variant="ghost" size="sm" className="mt-3">
              Learn More <ArrowRight className="h-3 w-3 ml-1" />
            </Button>
          </Link>
        </Card>

        <Card className="text-center p-6 border border-gray-100 hover:shadow-xl transition-all duration-300 hover:translate-y-[-6px]">
          <div className="relative w-24 h-24 mx-auto mb-6">
            <div className="absolute inset-0 bg-blue-200 rounded-full animate-pulse opacity-50"></div>
            <div className="relative flex items-center justify-center h-full">
              <FileText className="h-12 w-12 text-blue-600" />
            </div>
          </div>
          <h3 className="font-semibold text-gray-900 mb-2">Detailed Reports</h3>
          <p className="text-sm text-gray-600">
            Download comprehensive health reports to share with your doctor
          </p>
          <Link href="/dashboard/reports">
            <Button variant="ghost" size="sm" className="mt-3">
              View Reports <ArrowRight className="h-3 w-3 ml-1" />
            </Button>
          </Link>
        </Card>
      </div>
    </div>
  );
}
