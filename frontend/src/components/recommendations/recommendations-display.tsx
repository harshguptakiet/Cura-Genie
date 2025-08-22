'use client';

import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Loader2, Heart, Activity, Utensils, Shield, AlertTriangle, Info } from 'lucide-react';

interface Recommendation {
  id: string;
  title: string;
  description: string;
  category: 'lifestyle' | 'nutrition' | 'exercise' | 'medical' | 'prevention';
  priority: 'high' | 'medium' | 'low';
  basedOn: string[];
  actionItems: string[];
}

interface RecommendationsDisplayProps {
  userId: string;
}

// Use environment variable for API base URL
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

// API function to generate AI recommendations
const fetchRecommendations = async (userId: string): Promise<Recommendation[]> => {
  try {
    // Use the chatbot API to generate recommendations
    const response = await fetch(`${API_BASE_URL}/api/chatbot/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user_id: userId,
        message: 'Generate personalized health recommendations based on my genetic analysis results and PRS scores. Please provide specific, actionable recommendations with categories and priorities.'
      })
    });

    if (!response.ok) {
      throw new Error('Failed to generate recommendations');
    }

    const data = await response.json();
    const aiResponse = data.response || data.message || 'No recommendations available';

    // Parse AI response into structured recommendations
    // For now, return mock structured data since AI response is text
    return [
      {
        id: 'ai_rec_1',
        title: 'AI-Generated Health Recommendations',
        description: aiResponse,
        category: 'medical',
        priority: 'high',
        basedOn: ['Genetic analysis results', 'PRS scores', 'AI health assessment'],
        actionItems: ['Consult with healthcare provider', 'Follow personalized recommendations', 'Monitor health metrics regularly']
      }
    ];
  } catch (error) {
    console.error('Error generating AI recommendations:', error);
    // Return static recommendations as fallback
    return [
      {
        id: 'static_rec_1',
        title: 'General Health Recommendations',
        description: 'Upload a VCF file to receive personalized AI-generated health recommendations based on your genetic profile.',
        category: 'general',
        priority: 'medium',
        basedOn: ['Standard health guidelines'],
        actionItems: ['Upload genomic data for personalized recommendations', 'Maintain healthy lifestyle habits', 'Regular health check-ups']
      }
    ];
  }
};

const getCategoryIcon = (category: string) => {
  switch (category) {
    case 'lifestyle':
      return <Heart className="h-5 w-5" />;
    case 'nutrition':
      return <Utensils className="h-5 w-5" />;
    case 'exercise':
      return <Activity className="h-5 w-5" />;
    case 'medical':
      return <Shield className="h-5 w-5" />;
    case 'prevention':
      return <Shield className="h-5 w-5" />;
    default:
      return <Info className="h-5 w-5" />;
  }
};

const getPriorityVariant = (priority: string) => {
  switch (priority) {
    case 'high':
      return 'destructive';
    case 'medium':
      return 'secondary';
    case 'low':
      return 'default';
    default:
      return 'default';
  }
};

const getPriorityIcon = (priority: string) => {
  switch (priority) {
    case 'high':
      return <AlertTriangle className="h-4 w-4" />;
    case 'medium':
      return <Info className="h-4 w-4" />;
    case 'low':
      return <Info className="h-4 w-4" />;
    default:
      return <Info className="h-4 w-4" />;
  }
};

export function RecommendationsDisplay({ userId }: RecommendationsDisplayProps) {
  const { data: recommendations, isLoading, error } = useQuery({
    queryKey: ['recommendations', userId],
    queryFn: () => fetchRecommendations(userId),
    enabled: !!userId,
  });

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Personalized Recommendations</CardTitle>
          <CardDescription>AI-generated health insights based on your genetic profile</CardDescription>
        </CardHeader>
        <CardContent className="flex items-center justify-center py-8">
          <Loader2 className="h-8 w-8 animate-spin" />
          <span className="ml-2">Loading recommendations...</span>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    // Check if it's a 404 error (no data available)
    const errorMessage = error instanceof Error ? error.message : 'An error occurred while loading recommendations';
    const isNoData = errorMessage.includes('404') || errorMessage.includes('Failed to fetch');

    return (
      <Card>
        <CardHeader>
          <CardTitle>Personalized Recommendations</CardTitle>
          <CardDescription>AI-generated health insights based on your genetic profile</CardDescription>
        </CardHeader>
        <CardContent>
          <Alert variant={isNoData ? "default" : "destructive"}>
            <AlertDescription>
              {isNoData
                ? "No genomic data found. Upload a VCF file to receive personalized health recommendations based on your genetic profile."
                : "Failed to load recommendations. Please try again later."
              }
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="hover:shadow-lg transition-shadow">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="text-2xl font-bold flex items-center gap-2">
              <Heart className="h-6 w-6 text-red-500" />
              Personalized Health Recommendations
            </CardTitle>
            <CardDescription className="mt-1">
              AI-powered insights tailored to your genomic profile
            </CardDescription>
          </div>
          <Badge variant="outline" className="text-purple-600 border-purple-200">
            {recommendations?.length || 0} Insights
          </Badge>
        </div>
      </CardHeader>
      <CardContent>
        {recommendations && recommendations.length > 0 ? (
          <div className="space-y-6">
            {recommendations.map((recommendation) => (
              <div key={recommendation.id} className="border rounded-xl p-6 hover:shadow-md transition-all hover:border-purple-300 bg-gradient-to-br from-white to-gray-50">
                <div className="flex items-start space-x-4">
                  <div className="flex-shrink-0 mt-1 p-2 rounded-full bg-purple-50">
                    {getCategoryIcon(recommendation.category)}
                  </div>
                  <div className="flex-1 space-y-4">
                    <div className="flex items-start justify-between">
                      <h3 className="text-xl font-semibold text-gray-900 leading-tight">{recommendation.title}</h3>
                      <Badge variant={getPriorityVariant(recommendation.priority)} className="flex items-center gap-1 ml-4">
                        {getPriorityIcon(recommendation.priority)}
                        {recommendation.priority.toUpperCase()}
                      </Badge>
                    </div>

                    <div className="bg-white rounded-lg p-4 border border-gray-100">
                      <p className="text-gray-700 leading-relaxed">
                        {recommendation.description}
                      </p>
                    </div>

                    {recommendation.basedOn.length > 0 && (
                      <div className="bg-blue-50 rounded-lg p-4">
                        <h4 className="font-semibold text-sm text-blue-900 mb-3 flex items-center gap-2">
                          <Info className="h-4 w-4" />
                          Analysis Based On:
                        </h4>
                        <ul className="space-y-2">
                          {recommendation.basedOn.map((basis, index) => (
                            <li key={index} className="flex items-center text-sm text-blue-800">
                              <span className="w-2 h-2 bg-blue-500 rounded-full mr-3 flex-shrink-0"></span>
                              {basis}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {recommendation.actionItems.length > 0 && (
                      <div className="bg-green-50 rounded-lg p-4">
                        <h4 className="font-semibold text-sm text-green-900 mb-3 flex items-center gap-2">
                          <Activity className="h-4 w-4" />
                          Recommended Actions:
                        </h4>
                        <ul className="space-y-2">
                          {recommendation.actionItems.map((action, index) => (
                            <li key={index} className="flex items-start text-sm text-green-800">
                              <span className="w-2 h-2 bg-green-500 rounded-full mr-3 mt-2 flex-shrink-0"></span>
                              {action}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    <div className="flex items-center justify-between pt-4 border-t border-gray-100">
                      <div className="flex items-center gap-2">
                        <Badge variant="outline" className="capitalize bg-white">
                          {getCategoryIcon(recommendation.category)}
                          {recommendation.category}
                        </Badge>
                      </div>
                      <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded-full">
                        Personalized Analysis
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <Heart className="h-12 w-12 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500 text-lg font-medium">No recommendations available</p>
            <p className="text-gray-400 text-sm mt-2">Upload genomic data to receive personalized health insights</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
