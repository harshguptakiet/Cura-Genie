import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { PrsChart } from '@/components/charts/prs-chart';
import { ResultsTimeline } from '@/components/timeline/results-timeline';
import ModernGenomeBrowser from '@/components/genome/modern-genome-browser';
import { CompleteMRIAnalysis } from '@/components/medical/complete-mri-analysis';
import { useAuthStore } from '@/store/auth-store';
import { 
  Brain, 
  BarChart3, 
  Clock, 
  Dna,
  Activity,
  Sparkles,
  ChevronRight,
  TrendingUp,
  Target
} from 'lucide-react';

export default function VisualizationsPage() {
  const { user, isAuthenticated } = useAuthStore();
  const [activeSection, setActiveSection] = useState('mri');
  
  // Get user ID from authenticated user - fallback to '1' for demo
  const userId = user?.id?.toString() || '1';
  
  // Don't render if not authenticated 
  if (!isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-50">
        <Card className="w-full max-w-md mx-4">
          <CardContent className="p-8 text-center">
            <Brain className="h-16 w-16 text-blue-600 mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-gray-900 mb-2">Authentication Required</h2>
            <p className="text-gray-600">Please log in to view your personalized visualizations and analysis results.</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  const visualizationSections = [
    {
      id: 'mri',
      title: 'MRI Brain Analysis',
      description: 'AI-powered brain tumor detection and medical imaging analysis',
      icon: Brain,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
      borderColor: 'border-blue-200'
    },
    {
      id: 'genomics',
      title: 'Genomic Analysis',
      description: 'Polygenic risk scores and genetic variant analysis',
      icon: Dna,
      color: 'text-green-600',
      bgColor: 'bg-green-50',
      borderColor: 'border-green-200'
    },
    {
      id: 'timeline',
      title: 'Results Timeline',
      description: 'Track your health analysis progress over time',
      icon: Clock,
      color: 'text-purple-600',
      bgColor: 'bg-purple-50',
      borderColor: 'border-purple-200'
    },
    {
      id: 'genome-browser',
      title: 'Genome Browser',
      description: 'Interactive exploration of genomic variants',
      icon: BarChart3,
      color: 'text-orange-600',
      bgColor: 'bg-orange-50',
      borderColor: 'border-orange-200'
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50 to-indigo-100">
      {/* Enhanced Header Section */}
      <div className="bg-white/95 backdrop-blur-md border-b border-gray-200/60 sticky top-0 z-20 shadow-sm">
        <div className="max-w-[1600px] mx-auto px-8 py-8">
          <div className="flex items-center justify-between">
            <div className="space-y-3">
              <div className="flex items-center gap-4">
                <div className="p-4 bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 rounded-2xl shadow-lg">
                  <Sparkles className="h-10 w-10 text-white" />
                </div>
                <div>
                  <h1 className="text-5xl font-black text-gray-900 bg-gradient-to-r from-blue-900 to-indigo-900 bg-clip-text text-transparent">
                    Health Visualizations
                  </h1>
                  <p className="text-gray-600 text-xl mt-1 font-medium">Advanced AI-powered comprehensive health data analysis platform</p>
                </div>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <Badge variant="outline" className="text-green-700 border-green-400 bg-green-50 px-4 py-2 text-base font-semibold">
                <Activity className="h-4 w-4 mr-2 animate-pulse" />
                Live Analysis
              </Badge>
              <Badge variant="outline" className="text-blue-700 border-blue-400 bg-blue-50 px-4 py-2 text-base font-semibold">
                <Target className="h-4 w-4 mr-2" />
                AI Powered
              </Badge>
            </div>
          </div>
        </div>
      </div>

      {/* Enhanced Navigation Tabs */}
      <div className="max-w-[1600px] mx-auto px-8 py-6">
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6 mb-8">
          {visualizationSections.map((section) => {
            const IconComponent = section.icon;
            const isActive = activeSection === section.id;
            return (
              <Card 
                key={section.id}
                className={`cursor-pointer transition-all duration-300 hover:shadow-xl hover:scale-[1.02] min-h-[180px] ${
                  isActive 
                    ? `${section.borderColor} border-3 ${section.bgColor} shadow-lg ring-2 ring-offset-2 ring-blue-300` 
                    : 'border-gray-200 hover:border-gray-400 shadow-md'
                }`}
                onClick={() => setActiveSection(section.id)}
              >
                <CardContent className="p-8">
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <div className={`p-4 rounded-2xl transition-colors ${
                        isActive ? section.bgColor : 'bg-gray-100'
                      }`}>
                        <IconComponent className={`h-8 w-8 ${
                          isActive ? section.color : 'text-gray-500'
                        }`} />
                      </div>
                      {isActive && (
                        <div className="flex items-center gap-2">
                          <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                          <span className="text-xs font-medium text-green-600">ACTIVE</span>
                        </div>
                      )}
                    </div>
                    <div className="space-y-2">
                      <h3 className={`font-bold text-lg transition-colors ${
                        isActive ? 'text-gray-900' : 'text-gray-700'
                      }`}>
                        {section.title}
                      </h3>
                      <p className="text-sm text-gray-600 leading-relaxed">
                        {section.description}
                      </p>
                    </div>
                    {isActive && (
                      <div className="flex items-center justify-end">
                        <ChevronRight className="h-5 w-5 text-blue-500" />
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>

        {/* Enhanced Content Sections */}
        <div className="space-y-16">
          {/* MRI Analysis Section */}
          {activeSection === 'mri' && (
            <div className="space-y-10">
              <Card className="border-blue-300 bg-gradient-to-r from-blue-50 via-indigo-50 to-blue-100 shadow-xl border-2">
                <CardHeader className="pb-8 pt-8">
                  <div className="flex items-center gap-6">
                    <div className="p-6 bg-gradient-to-r from-blue-600 to-indigo-700 rounded-3xl shadow-lg">
                      <Brain className="h-16 w-16 text-white" />
                    </div>
                    <div className="space-y-2">
                      <CardTitle className="text-4xl font-black text-blue-900 mb-2">
                        🧠 MRI Brain Scan Analysis
                      </CardTitle>
                      <p className="text-blue-700 text-xl font-medium leading-relaxed max-w-2xl">
                        Advanced AI-powered brain tumor detection with real-time medical imaging analysis and comprehensive diagnostic insights
                      </p>
                      <div className="flex items-center gap-4 pt-2">
                        <Badge className="bg-blue-600 text-white px-3 py-1">
                          Deep Learning
                        </Badge>
                        <Badge className="bg-indigo-600 text-white px-3 py-1">
                          Medical Imaging
                        </Badge>
                        <Badge className="bg-purple-600 text-white px-3 py-1">
                          Neural Networks
                        </Badge>
                      </div>
                    </div>
                  </div>
                </CardHeader>
              </Card>
              
              <div className="bg-white rounded-3xl border-2 border-gray-200 shadow-2xl overflow-hidden min-h-[800px]">
                <div className="p-12">
                  <CompleteMRIAnalysis userId={userId} />
                </div>
              </div>
            </div>
          )}

          {/* Genomic Analysis Section */}
          {activeSection === 'genomics' && (
            <div className="space-y-10">
              <Card className="border-green-300 bg-gradient-to-r from-green-50 via-emerald-50 to-green-100 shadow-xl border-2">
                <CardHeader className="pb-8 pt-8">
                  <div className="flex items-center gap-6">
                    <div className="p-6 bg-gradient-to-r from-green-600 to-emerald-700 rounded-3xl shadow-lg">
                      <TrendingUp className="h-16 w-16 text-white" />
                    </div>
                    <div className="space-y-2">
                      <CardTitle className="text-4xl font-black text-green-900 mb-2">
                        🧬 Genomic Risk Analysis
                      </CardTitle>
                      <p className="text-green-700 text-xl font-medium leading-relaxed max-w-2xl">
                        Comprehensive polygenic risk scores and advanced genetic variant analysis with personalized health insights
                      </p>
                      <div className="flex items-center gap-4 pt-2">
                        <Badge className="bg-green-600 text-white px-3 py-1">
                          Polygenic Scores
                        </Badge>
                        <Badge className="bg-emerald-600 text-white px-3 py-1">
                          Genetic Variants
                        </Badge>
                        <Badge className="bg-teal-600 text-white px-3 py-1">
                          Risk Assessment
                        </Badge>
                      </div>
                    </div>
                  </div>
                </CardHeader>
              </Card>
              
              <div className="bg-white rounded-3xl border-2 border-gray-200 shadow-2xl overflow-hidden min-h-[800px]">
                <div className="p-12">
                  <PrsChart userId={userId} />
                </div>
              </div>
            </div>
          )}

          {/* Timeline Section */}
          {activeSection === 'timeline' && (
            <div className="space-y-10">
              <Card className="border-purple-300 bg-gradient-to-r from-purple-50 via-violet-50 to-purple-100 shadow-xl border-2">
                <CardHeader className="pb-8 pt-8">
                  <div className="flex items-center gap-6">
                    <div className="p-6 bg-gradient-to-r from-purple-600 to-violet-700 rounded-3xl shadow-lg">
                      <Clock className="h-16 w-16 text-white" />
                    </div>
                    <div className="space-y-2">
                      <CardTitle className="text-4xl font-black text-purple-900 mb-2">
                        ⏰ Analysis Timeline
                      </CardTitle>
                      <p className="text-purple-700 text-xl font-medium leading-relaxed max-w-2xl">
                        Track your comprehensive health analysis progress and visualize results evolution over time with detailed insights
                      </p>
                      <div className="flex items-center gap-4 pt-2">
                        <Badge className="bg-purple-600 text-white px-3 py-1">
                          Progress Tracking
                        </Badge>
                        <Badge className="bg-violet-600 text-white px-3 py-1">
                          Historical Data
                        </Badge>
                        <Badge className="bg-indigo-600 text-white px-3 py-1">
                          Trend Analysis
                        </Badge>
                      </div>
                    </div>
                  </div>
                </CardHeader>
              </Card>
              
              <div className="bg-white rounded-3xl border-2 border-gray-200 shadow-2xl overflow-hidden min-h-[800px]">
                <div className="p-12">
                  <ResultsTimeline userId={userId} />
                </div>
              </div>
            </div>
          )}

          {/* Genome Browser Section */}
          {activeSection === 'genome-browser' && (
            <div className="space-y-10">
              <Card className="border-orange-300 bg-gradient-to-r from-orange-50 via-amber-50 to-orange-100 shadow-xl border-2">
                <CardHeader className="pb-8 pt-8">
                  <div className="flex items-center gap-6">
                    <div className="p-6 bg-gradient-to-r from-orange-600 to-amber-700 rounded-3xl shadow-lg">
                      <Dna className="h-16 w-16 text-white" />
                    </div>
                    <div className="space-y-2">
                      <CardTitle className="text-4xl font-black text-orange-900 mb-2">
                        🔬 Interactive Genome Browser
                      </CardTitle>
                      <p className="text-orange-700 text-xl font-medium leading-relaxed max-w-2xl">
                        Explore and analyze genetic variants with advanced interactive visualization tools and genomic data insights
                      </p>
                      <div className="flex items-center gap-4 pt-2">
                        <Badge className="bg-orange-600 text-white px-3 py-1">
                          Interactive Viz
                        </Badge>
                        <Badge className="bg-amber-600 text-white px-3 py-1">
                          Genome Data
                        </Badge>
                        <Badge className="bg-yellow-600 text-white px-3 py-1">
                          Variant Analysis
                        </Badge>
                      </div>
                    </div>
                  </div>
                </CardHeader>
              </Card>
              
              <div className="bg-white rounded-3xl border-2 border-gray-200 shadow-2xl overflow-hidden min-h-[800px]">
                <div className="p-12">
                  <ModernGenomeBrowser userId={userId} />
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
