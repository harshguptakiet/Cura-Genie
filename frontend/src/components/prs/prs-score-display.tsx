'use client';

import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { MedicalDisclaimer } from '@/components/ui/medical-disclaimer';
import { PRSExplainer, RiskLevelExplainer, EducationalContext } from '@/components/ui/plain-english-explainer';
import { Loader2, TrendingUp, TrendingDown, Minus, BarChart3, AlertTriangle, Stethoscope, FileText, HelpCircle } from 'lucide-react';

// Proper interfaces for PRS data
interface PRSItem {
  id: number;
  disease_type: string;
  score: number;
  percentile: number;
  risk_level: string;
  calculated_at: string;
  variants_used?: number;
  confidence?: number;
}

interface PRSChartData {
  condition: string;
  score: number;
  category: string;
  color: string;
  description: string;
  risk_level: string;
}

interface DiseaseMap {
  [key: string]: PRSItem;
}

interface PrsScore {
  id: string;
  condition: string;
  score: number;
  percentile: number;
  riskLevel: 'low' | 'moderate' | 'high';
  description: string;
  calculatedAt?: string;
  variantsUsed?: number;
  confidence?: number;
}

interface PrsScoreDisplayProps {
  userId: string;
}

// Use environment variable for API base URL
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';

// Helper function to get category color
const getCategoryColor = (category: string): string => {
  switch (category.toLowerCase()) {
    case 'high':
      return 'bg-red-500';
    case 'moderate':
      return 'bg-yellow-500';
    case 'low':
      return 'bg-green-500';
    default:
      return 'bg-gray-500';
  }
};

// Helper function to get category description
const getCategoryDescription = (category: string): string => {
  switch (category.toLowerCase()) {
    case 'high':
      return 'Higher than average genetic risk';
    case 'moderate':
      return 'Average genetic risk';
    case 'low':
      return 'Lower than average genetic risk';
    default:
      return 'Unknown risk level';
  }
};

// API function to fetch real PRS scores using direct API
const fetchPrsScores = async (userId: string): Promise<PrsScore[]> => {
  try {
    console.log(`Fetching PRS scores for user: ${userId}`);
    // Use the new direct API endpoint that works
    const response = await fetch(`${API_BASE_URL}/api/direct/prs/user/${userId}`);
    console.log(`Direct PRS scores API response status: ${response.status}`);

    if (!response.ok) {
      if (response.status === 404) {
        console.log('No PRS scores found (404) - this is expected for new users');
        return []; // Return empty array instead of throwing error for 404
      }
      if (response.status === 500) {
        console.log('Server error (500) - backend might need data or have an issue');
        return []; // Return empty array for server errors too
      }
      console.error(`PRS scores API error: ${response.status} - ${response.statusText}`);
      return []; // Return empty array instead of throwing
    }

    const data = await response.json();
    console.log('Direct PRS scores data received:', data);

    // Handle single item response or array response
    const items: PRSItem[] = Array.isArray(data) ? data : [data];

    // Filter to get only the latest score per disease type
    const diseaseMap: DiseaseMap = {};

    items.forEach((item: PRSItem) => {
      const diseaseType = item.disease_type || 'Unknown';
      const calculatedAt = item.calculated_at || '1900-01-01';
      const itemId = item.id || 0;

      // Keep the latest record for each disease (by date, then by ID)
      if (!diseaseMap[diseaseType] ||
        calculatedAt > diseaseMap[diseaseType].calculated_at ||
        (calculatedAt === diseaseMap[diseaseType].calculated_at && itemId > diseaseMap[diseaseType].id)) {
        diseaseMap[diseaseType] = item;
      }
    });

    // Transform the filtered latest data to frontend format
    return Object.values(diseaseMap).map((item: PRSItem): PrsScore => ({
      id: item.id ? item.id.toString() : `prs_${Date.now()}`,
      condition: item.disease_type ? item.disease_type.replace(/_/g, ' ').replace(/\b\w/g, (l: string) => l.toUpperCase()) : 'Unknown Condition',
      score: item.score || 0,
      percentile: item.percentile || Math.round((item.score || 0) * 100),
      riskLevel: item.risk_level ? item.risk_level.toLowerCase() as 'low' | 'moderate' | 'high' : ((item.score || 0) > 0.7 ? 'high' : (item.score || 0) > 0.4 ? 'moderate' : 'low'),
      description: `${item.risk_level || ((item.score || 0) > 0.7 ? 'Higher' : (item.score || 0) > 0.4 ? 'Moderate' : 'Lower')} than average genetic risk for ${item.disease_type ? item.disease_type.replace(/_/g, ' ') : 'this condition'}`,
      calculatedAt: item.calculated_at,
      variantsUsed: item.variants_used || 0,
      confidence: item.confidence || 0
    })).sort((a, b) => new Date(b.calculatedAt || '1900-01-01').getTime() - new Date(a.calculatedAt || '1900-01-01').getTime());
  } catch (error) {
    console.error('Error fetching PRS scores:', error);
    // Return empty array on specific error types
    if (error instanceof TypeError && error.message.includes('fetch')) {
      console.error('Network error occurred while fetching PRS scores');
    } else if (error instanceof SyntaxError) {
      console.error('Invalid JSON response from PRS scores API');
    } else {
      console.error('Unexpected error while processing PRS scores data');
    }
    return [];
  }
};

const getRiskBadgeVariant = (riskLevel: string) => {
  switch (riskLevel) {
    case 'high':
      return 'destructive';
    case 'moderate':
      return 'secondary';
    case 'low':
      return 'default';
    default:
      return 'default';
  }
};

const getRiskIcon = (riskLevel: string) => {
  switch (riskLevel) {
    case 'high':
      return <TrendingUp className="h-4 w-4" />;
    case 'moderate':
      return <Minus className="h-4 w-4" />;
    case 'low':
      return <TrendingDown className="h-4 w-4" />;
    default:
      return <Minus className="h-4 w-4" />;
  }
};

export function PrsScoreDisplay({ userId }: PrsScoreDisplayProps) {
  const [showDisclaimer, setShowDisclaimer] = useState(false);
  const [disclaimerAccepted, setDisclaimerAccepted] = useState(false);

  const { data: prsScores, isLoading, error } = useQuery({
    queryKey: ['prs-scores', userId],
    queryFn: () => fetchPrsScores(userId),
    enabled: !!userId,
  });

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Polygenic Risk Scores</CardTitle>
          <CardDescription>Your genetic risk assessments</CardDescription>
        </CardHeader>
        <CardContent className="flex items-center justify-center py-8">
          <Loader2 className="h-8 w-8 animate-spin" />
          <span className="ml-2">Loading PRS scores...</span>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    // Check if it's a 404 error (no data available)
    const errorMessage = error instanceof Error ? error.message : 'Unknown error';
    const isNoData = errorMessage.includes('404') || errorMessage.includes('Failed to fetch');

    return (
      <Card>
        <CardHeader>
          <CardTitle>Polygenic Risk Scores</CardTitle>
          <CardDescription>Your genetic risk assessments</CardDescription>
        </CardHeader>
        <CardContent>
          <Alert variant={isNoData ? "default" : "destructive"}>
            <AlertDescription>
              {isNoData
                ? "No genomic data found. Please upload a VCF file to see your personalized risk scores."
                : "Failed to load PRS scores. Please try again later."
              }
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>
    );
  }

  return (
    <EducationalContext>
      {/* Medical disclaimer for genetic results */}
      <MedicalDisclaimer variant="banner" />

      {/* Educational context about PRS */}
      <PRSExplainer />

      <Card className="hover:shadow-lg transition-shadow">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-2xl font-bold flex items-center gap-2">
                <BarChart3 className="h-6 w-6 text-blue-600" />
                Your Genetic Risk Scores
                <HelpCircle
                  className="h-4 w-4 text-blue-500 cursor-help"
                  onClick={() => setShowDisclaimer(!showDisclaimer)}
                />
              </CardTitle>
              <CardDescription className="mt-1">
                Educational information about your genetic predispositions
              </CardDescription>
            </div>
            <div className="text-right">
              <Badge variant="outline" className="text-blue-600 border-blue-200 mb-2">
                {prsScores?.length || 0} Conditions Analyzed
              </Badge>
              <br />
              <Badge variant="outline" className="text-purple-600 border-purple-200 bg-purple-50 mb-2">
                Latest Analysis Only
              </Badge>
              <br />
              <Badge variant="outline" className="text-green-700 border-green-300 bg-green-50">
                <AlertTriangle className="h-3 w-3 mr-1" />
                Informational Only
              </Badge>
            </div>
          </div>
        </CardHeader>

        <CardContent>
          {/* Critical Safety Warning */}
          <Alert className="border-red-200 bg-red-50 mb-6">
            <AlertTriangle className="h-4 w-4 text-red-600" />
            <AlertDescription className="text-red-800">
              <strong>Important:</strong> These scores estimate genetic risk based on current scientific knowledge.
              They do NOT predict if you will develop these conditions. Many factors beyond genetics affect your health.
            </AlertDescription>
          </Alert>

          {prsScores && prsScores.length > 0 ? (
            <div className="space-y-6">
              {prsScores.map((score) => (
                <Card key={score.id} className="border-2 hover:shadow-md transition-all">
                  <CardHeader className="pb-3">
                    <div className="flex items-center justify-between">
                      <h3 className="font-bold text-xl text-gray-900">{score.condition}</h3>
                      <div className="flex items-center gap-2">
                        <Badge variant={getRiskBadgeVariant(score.riskLevel)} className="flex items-center gap-1">
                          {getRiskIcon(score.riskLevel)}
                          {score.riskLevel.charAt(0).toUpperCase() + score.riskLevel.slice(1)} Genetic Risk
                        </Badge>
                      </div>
                    </div>
                  </CardHeader>

                  <CardContent className="space-y-6">
                    {/* Score Display */}
                    <div className="grid grid-cols-2 gap-4">
                      <div className="text-center p-4 bg-blue-50 rounded-lg">
                        <div className="text-3xl font-bold text-blue-900">{score.score.toFixed(2)}</div>
                        <div className="text-sm text-blue-700">Risk Score</div>
                        <div className="text-xs text-blue-600 mt-1">Range: 0.0 - 1.0</div>
                      </div>
                      <div className="text-center p-4 bg-gray-50 rounded-lg">
                        <div className="text-3xl font-bold text-gray-900">{score.percentile}th</div>
                        <div className="text-sm text-gray-700">Percentile</div>
                        <div className="text-xs text-gray-600 mt-1">vs. Population</div>
                      </div>
                    </div>

                    {/* Visual Risk Bar */}
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm font-medium text-gray-700">
                        <span>Lower Genetic Risk</span>
                        <span>Higher Genetic Risk</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-4 relative">
                        <div
                          className={`h-4 rounded-full transition-all duration-500 ${score.riskLevel === 'high'
                              ? 'bg-gradient-to-r from-red-400 to-red-600'
                              : score.riskLevel === 'moderate'
                                ? 'bg-gradient-to-r from-yellow-400 to-orange-500'
                                : 'bg-gradient-to-r from-green-400 to-green-600'
                            }`}
                          style={{ width: `${Math.min(score.percentile, 100)}%` }}
                        />
                        <div
                          className="absolute top-0 w-1 h-4 bg-gray-700 rounded"
                          style={{ left: '50%', transform: 'translateX(-50%)' }}
                          title="Population Average"
                        />
                      </div>
                      <div className="text-center">
                        <span className="text-xs text-gray-500">↑ Population Average (50th percentile)</span>
                      </div>
                    </div>

                    {/* Plain English Explanation */}
                    <RiskLevelExplainer level={score.riskLevel} />

                    {/* What This Means for You */}
                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                      <h4 className="font-semibold text-blue-900 mb-2 flex items-center gap-2">
                        <FileText className="h-4 w-4" />
                        What This Score Means for You
                      </h4>
                      <p className="text-sm text-blue-800 mb-3">{score.description}</p>

                      <div className={`p-3 rounded-lg ${score.riskLevel === 'high'
                          ? 'bg-red-100 border border-red-200'
                          : score.riskLevel === 'moderate'
                            ? 'bg-yellow-100 border border-yellow-200'
                            : 'bg-green-100 border border-green-200'
                        }`}>
                        <h5 className={`font-medium mb-2 ${score.riskLevel === 'high'
                            ? 'text-red-900'
                            : score.riskLevel === 'moderate'
                              ? 'text-yellow-900'
                              : 'text-green-900'
                          }`}>Recommended Next Steps:</h5>
                        <ul className={`text-sm space-y-1 ml-4 list-disc ${score.riskLevel === 'high'
                            ? 'text-red-800'
                            : score.riskLevel === 'moderate'
                              ? 'text-yellow-800'
                              : 'text-green-800'
                          }`}>
                          {score.riskLevel === 'high' ? (
                            <>
                              <li>Discuss these results with your healthcare provider</li>
                              <li>Ask about enhanced screening or prevention strategies</li>
                              <li>Consider lifestyle modifications that may reduce risk</li>
                              <li>Remember: Higher genetic risk does NOT mean you will develop this condition</li>
                            </>
                          ) : score.riskLevel === 'moderate' ? (
                            <>
                              <li>Share these results at your next medical appointment</li>
                              <li>Continue standard prevention and screening guidelines</li>
                              <li>Maintain healthy lifestyle habits</li>
                              <li>Stay informed about new prevention strategies</li>
                            </>
                          ) : (
                            <>
                              <li>Continue regular preventive care and health screenings</li>
                              <li>Maintain healthy lifestyle habits</li>
                              <li>Lower genetic risk doesn't guarantee you won't develop this condition</li>
                              <li>Share results with your doctor for complete health picture</li>
                            </>
                          )}
                        </ul>
                      </div>
                    </div>

                    {/* Talk to Your Doctor Button */}
                    <div className="flex justify-center pt-4">
                      <Button variant="outline" className="flex items-center gap-2">
                        <Stethoscope className="h-4 w-4" />
                        Discuss with Healthcare Provider
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <BarChart3 className="h-16 w-16 text-gray-300 mx-auto mb-6" />
              <h3 className="text-xl font-semibold text-gray-700 mb-2">No Genetic Data Available</h3>
              <p className="text-gray-500 max-w-md mx-auto mb-6">
                Upload your genomic data (VCF file) to receive personalized genetic risk assessments
                and educational information about your genetic predispositions.
              </p>
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 max-w-md mx-auto">
                <h4 className="font-medium text-blue-900 mb-2">Supported File Types:</h4>
                <ul className="text-sm text-blue-800 space-y-1">
                  <li>• VCF files from genetic testing companies</li>
                  <li>• Files from 23andMe, AncestryDNA (with conversion)</li>
                  <li>• Clinical genetic testing results</li>
                </ul>
              </div>
            </div>
          )}

          {/* Accuracy & Validation Info */}
          {prsScores && prsScores.length > 0 && (
            <Card className="mt-6 bg-gray-50">
              <CardContent className="p-4">
                <h4 className="font-semibold text-gray-900 mb-2 flex items-center gap-2">
                  <AlertTriangle className="h-4 w-4 text-gray-600" />
                  About These Risk Scores
                </h4>
                <div className="grid md:grid-cols-2 gap-4 text-sm text-gray-700">
                  <div>
                    <h5 className="font-medium mb-1">Scientific Basis:</h5>
                    <ul className="space-y-1 text-xs">
                      <li>• Based on large-scale genetic studies</li>
                      <li>• Validated on diverse populations</li>
                      <li>• Updated with latest research</li>
                    </ul>
                  </div>
                  <div>
                    <h5 className="font-medium mb-1">Limitations:</h5>
                    <ul className="space-y-1 text-xs">
                      <li>• Estimates only, not definitive predictions</li>
                      <li>• Based on available genetic variants</li>
                      <li>• Environmental factors not included</li>
                    </ul>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </CardContent>
      </Card>
    </EducationalContext>
  );
}
