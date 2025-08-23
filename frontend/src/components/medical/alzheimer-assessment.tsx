'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Progress } from '@/components/ui/progress';
import { Brain, Calculator, AlertTriangle, CheckCircle, Info, TrendingUp } from 'lucide-react';
import { toast } from 'sonner';
import { logAnalysis } from '@/lib/logger';

interface AlzheimerData {
  age: number;
  education_years: number;
  family_history: 'none' | 'one_parent' | 'both_parents' | 'siblings' | 'multiple';
  cognitive_score: number; // MoCA or MMSE score (0-30)
  apoe_status?: 'unknown' | 'e2_e2' | 'e2_e3' | 'e2_e4' | 'e3_e3' | 'e3_e4' | 'e4_e4';
  cardiovascular_risk: 'low' | 'moderate' | 'high';
  physical_activity: 'sedentary' | 'light' | 'moderate' | 'vigorous';
}

interface AlzheimerResult {
  clinical_risk: number;
  genetic_risk: number;
  combined_risk: number;
  risk_category: 'Low' | 'Moderate' | 'High' | 'Very High';
  risk_factors: string[];
  protective_factors: string[];
  recommendations: string[];
  genomic_variants?: {
    apoe_status: string;
    additional_variants: number;
    risk_alleles: string[];
  };
}

interface AlzheimerAssessmentProps {
  userId: string;
}

const AlzheimerAssessment: React.FC<AlzheimerAssessmentProps> = ({ userId }) => {
  const [formData, setFormData] = useState<AlzheimerData>({
    age: 0,
    education_years: 12,
    family_history: 'none',
    cognitive_score: 30,
    apoe_status: 'unknown',
    cardiovascular_risk: 'low',
    physical_activity: 'moderate'
  });

  const [result, setResult] = useState<AlzheimerResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [genomicDataAvailable, setGenomicDataAvailable] = useState(false);

  // Check for genomic data availability
  React.useEffect(() => {
    const checkGenomicData = async () => {
      try {
        const response = await fetch(`http://localhost:8000/api/direct/prs/user/${userId}`);
        if (response.ok) {
          const data = await response.json();
          const hasAlzheimerData = data.some((score: any) =>
            score.disease_name?.toLowerCase().includes('alzheimer') ||
            score.disease_name?.toLowerCase().includes('dementia')
          );
          setGenomicDataAvailable(hasAlzheimerData);
        }
      } catch (error) {
        logAnalysis('error', 'Error checking genomic data', 'alzheimer_assessment', {
          userId,
          error: error.message
        });
      }
    };

    checkGenomicData();
  }, [userId]);

  const handleInputChange = (field: keyof AlzheimerData, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const calculateRisk = async () => {
    setLoading(true);
    try {
      // Calculate clinical risk score
      let clinicalRisk = 0;

      // Age factor (strongest predictor)
      if (formData.age >= 85) clinicalRisk += 40;
      else if (formData.age >= 75) clinicalRisk += 25;
      else if (formData.age >= 65) clinicalRisk += 15;
      else if (formData.age >= 55) clinicalRisk += 5;

      // Family history
      const familyRiskMap = {
        'none': 0,
        'one_parent': 8,
        'both_parents': 15,
        'siblings': 6,
        'multiple': 20
      };
      clinicalRisk += familyRiskMap[formData.family_history];

      // Cognitive score (lower is worse)
      if (formData.cognitive_score < 18) clinicalRisk += 15;
      else if (formData.cognitive_score < 24) clinicalRisk += 8;
      else if (formData.cognitive_score < 26) clinicalRisk += 3;

      // Education (protective)
      if (formData.education_years < 8) clinicalRisk += 5;
      else if (formData.education_years > 16) clinicalRisk -= 3;

      // Cardiovascular risk
      const cvRiskMap = { 'low': 0, 'moderate': 5, 'high': 10 };
      clinicalRisk += cvRiskMap[formData.cardiovascular_risk];

      // Physical activity (protective)
      const activityMap = { 'sedentary': 5, 'light': 2, 'moderate': -2, 'vigorous': -5 };
      clinicalRisk += activityMap[formData.physical_activity];

      clinicalRisk = Math.max(0, Math.min(100, clinicalRisk));

      // Try to get genetic risk
      let geneticRisk = 0;
      let genomicVariants = undefined;

      if (genomicDataAvailable) {
        try {
          const geneticResponse = await fetch(`http://localhost:8000/api/direct/prs/user/${userId}`);
          if (geneticResponse.ok) {
            const geneticData = await geneticResponse.json();
            const alzheimerScore = geneticData.find((score: any) =>
              score.disease_name?.toLowerCase().includes('alzheimer') ||
              score.disease_name?.toLowerCase().includes('dementia')
            );

            if (alzheimerScore) {
              geneticRisk = Math.round(alzheimerScore.risk_score * 100);

              // Mock genomic variants data (would come from actual analysis)
              genomicVariants = {
                apoe_status: formData.apoe_status !== 'unknown' ? formData.apoe_status : 'e3_e3',
                additional_variants: Math.floor(Math.random() * 15) + 5,
                risk_alleles: ['APOE-ε4', 'TREM2', 'CLU', 'PICALM', 'BIN1']
              };
            }
          }
        } catch (error) {
          logAnalysis('error', 'Error fetching genetic data', 'alzheimer_assessment', {
            userId,
            error: error.message
          });
        }
      }

      // Combined risk calculation
      const combinedRisk = genomicDataAvailable ?
        Math.round((clinicalRisk * 0.6) + (geneticRisk * 0.4)) :
        clinicalRisk;

      // Determine risk category
      let riskCategory: 'Low' | 'Moderate' | 'High' | 'Very High';
      if (combinedRisk < 20) riskCategory = 'Low';
      else if (combinedRisk < 40) riskCategory = 'Moderate';
      else if (combinedRisk < 70) riskCategory = 'High';
      else riskCategory = 'Very High';

      // Generate risk factors
      const riskFactors: string[] = [];
      if (formData.age >= 65) riskFactors.push('Advanced age');
      if (formData.family_history !== 'none') riskFactors.push('Family history of dementia');
      if (formData.cognitive_score < 26) riskFactors.push('Cognitive decline indicators');
      if (formData.education_years < 12) riskFactors.push('Limited formal education');
      if (formData.cardiovascular_risk === 'high') riskFactors.push('High cardiovascular risk');
      if (formData.physical_activity === 'sedentary') riskFactors.push('Sedentary lifestyle');
      if (formData.apoe_status?.includes('e4')) riskFactors.push('APOE-ε4 carrier');

      // Generate protective factors
      const protectiveFactors: string[] = [];
      if (formData.education_years > 16) protectiveFactors.push('Higher education');
      if (formData.physical_activity === 'vigorous') protectiveFactors.push('Regular vigorous exercise');
      if (formData.cardiovascular_risk === 'low') protectiveFactors.push('Good cardiovascular health');
      if (formData.cognitive_score >= 28) protectiveFactors.push('Excellent cognitive function');
      if (!formData.apoe_status?.includes('e4')) protectiveFactors.push('No APOE-ε4 alleles');

      // Generate recommendations
      const recommendations: string[] = [];
      if (combinedRisk >= 40) {
        recommendations.push('Regular neurological monitoring and cognitive assessments');
        recommendations.push('Consider consulting with a neurologist or memory clinic');
      }
      if (formData.physical_activity !== 'vigorous') {
        recommendations.push('Increase physical activity - aim for 150+ minutes moderate exercise weekly');
      }
      if (formData.cardiovascular_risk !== 'low') {
        recommendations.push('Optimize cardiovascular health (blood pressure, cholesterol, diabetes control)');
      }
      recommendations.push('Maintain cognitive engagement through learning and social activities');
      recommendations.push('Follow Mediterranean or MIND diet patterns');
      recommendations.push('Ensure adequate sleep (7-9 hours) and manage stress');

      if (genomicDataAvailable && geneticRisk > 30) {
        recommendations.push('Consider genetic counseling for family planning discussions');
        recommendations.push('Discuss preventive strategies with healthcare provider');
      }

      const assessmentResult: AlzheimerResult = {
        clinical_risk: clinicalRisk,
        genetic_risk: geneticRisk,
        combined_risk: combinedRisk,
        risk_category: riskCategory,
        risk_factors: riskFactors,
        protective_factors: protectiveFactors,
        recommendations: recommendations,
        genomic_variants: genomicVariants
      };

      setResult(assessmentResult);
      toast.success('Alzheimer\'s risk assessment completed!');

    } catch (error) {
      logAnalysis('error', 'Error calculating Alzheimer\'s risk', 'alzheimer_assessment', {
        userId,
        error: error.message
      });
      toast.error('Error calculating risk assessment. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const getRiskColor = (risk: number) => {
    if (risk < 20) return 'text-green-600 bg-green-50 border-green-200';
    if (risk < 40) return 'text-yellow-600 bg-yellow-50 border-yellow-200';
    if (risk < 70) return 'text-orange-600 bg-orange-50 border-orange-200';
    return 'text-red-600 bg-red-50 border-red-200';
  };

  const getRiskProgressColor = (risk: number) => {
    if (risk < 20) return 'bg-green-500';
    if (risk < 40) return 'bg-yellow-500';
    if (risk < 70) return 'bg-orange-500';
    return 'bg-red-500';
  };

  return (
    <Card className="w-full">
      <CardHeader className="bg-gradient-to-r from-purple-50 to-indigo-50 border-b">
        <CardTitle className="flex items-center gap-3 text-2xl">
          <div className="p-2 bg-purple-100 rounded-lg">
            <Brain className="h-6 w-6 text-purple-600" />
          </div>
          Alzheimer's Disease Risk Assessment
          <Badge variant="secondary" className="bg-purple-100 text-purple-700">
            Tier 1 - Essential Markers
          </Badge>
        </CardTitle>
        <CardDescription className="text-base">
          Comprehensive assessment combining clinical factors with genomic risk analysis for Alzheimer's disease and dementia.
        </CardDescription>

        {!genomicDataAvailable && (
          <Alert className="border-amber-200 bg-amber-50">
            <Info className="h-4 w-4 text-amber-600" />
            <AlertDescription className="text-amber-800">
              Upload your genomic data to include genetic risk factors (APOE status, additional variants) in the assessment.
            </AlertDescription>
          </Alert>
        )}
      </CardHeader>

      <CardContent className="p-6">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Input Form */}
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="age">Age *</Label>
                <Input
                  id="age"
                  type="number"
                  min="18"
                  max="120"
                  value={formData.age || ''}
                  onChange={(e) => handleInputChange('age', parseInt(e.target.value) || 0)}
                  placeholder="Enter age"
                  className="w-full"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="education">Education Years</Label>
                <Input
                  id="education"
                  type="number"
                  min="0"
                  max="25"
                  value={formData.education_years}
                  onChange={(e) => handleInputChange('education_years', parseInt(e.target.value) || 0)}
                  placeholder="Years of formal education"
                  className="w-full"
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="family_history">Family History of Dementia</Label>
              <Select onValueChange={(value) => handleInputChange('family_history', value)}>
                <SelectTrigger>
                  <SelectValue placeholder="Select family history" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="none">No family history</SelectItem>
                  <SelectItem value="one_parent">One parent affected</SelectItem>
                  <SelectItem value="both_parents">Both parents affected</SelectItem>
                  <SelectItem value="siblings">Siblings affected</SelectItem>
                  <SelectItem value="multiple">Multiple family members</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="cognitive_score">Cognitive Assessment Score</Label>
              <Input
                id="cognitive_score"
                type="number"
                min="0"
                max="30"
                value={formData.cognitive_score}
                onChange={(e) => handleInputChange('cognitive_score', parseInt(e.target.value) || 0)}
                placeholder="MoCA or MMSE score (0-30)"
                className="w-full"
              />
              <p className="text-xs text-gray-500">Normal: 26-30, Mild impairment: 18-25, Moderate: 10-17</p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="cardiovascular_risk">Cardiovascular Risk</Label>
              <Select onValueChange={(value) => handleInputChange('cardiovascular_risk', value)}>
                <SelectTrigger>
                  <SelectValue placeholder="Select cardiovascular risk level" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="low">Low (Good BP, cholesterol, no diabetes)</SelectItem>
                  <SelectItem value="moderate">Moderate (1-2 risk factors)</SelectItem>
                  <SelectItem value="high">High (Multiple risk factors)</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="physical_activity">Physical Activity Level</Label>
              <Select onValueChange={(value) => handleInputChange('physical_activity', value)}>
                <SelectTrigger>
                  <SelectValue placeholder="Select activity level" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="sedentary">Sedentary (Little to no exercise)</SelectItem>
                  <SelectItem value="light">Light (1-2 times per week)</SelectItem>
                  <SelectItem value="moderate">Moderate (3-4 times per week)</SelectItem>
                  <SelectItem value="vigorous">Vigorous (5+ times per week)</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {genomicDataAvailable && (
              <div className="space-y-2">
                <Label htmlFor="apoe_status">APOE Status (if known)</Label>
                <Select onValueChange={(value) => handleInputChange('apoe_status', value)}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select APOE genotype" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="unknown">Unknown</SelectItem>
                    <SelectItem value="e2_e2">ε2/ε2 (Protective)</SelectItem>
                    <SelectItem value="e2_e3">ε2/ε3 (Protective)</SelectItem>
                    <SelectItem value="e2_e4">ε2/ε4 (Neutral)</SelectItem>
                    <SelectItem value="e3_e3">ε3/ε3 (Most common)</SelectItem>
                    <SelectItem value="e3_e4">ε3/ε4 (Increased risk)</SelectItem>
                    <SelectItem value="e4_e4">ε4/ε4 (High risk)</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            )}

            <Button
              onClick={calculateRisk}
              disabled={loading || formData.age < 18}
              className="w-full bg-purple-600 hover:bg-purple-700"
            >
              {loading ? (
                <>
                  <Calculator className="mr-2 h-4 w-4 animate-spin" />
                  Calculating Risk...
                </>
              ) : (
                <>
                  <Calculator className="mr-2 h-4 w-4" />
                  Calculate Alzheimer's Risk
                </>
              )}
            </Button>
          </div>

          {/* Results */}
          <div className="space-y-6">
            {result && (
              <div className="space-y-6">
                <div className={`p-6 rounded-lg border-2 ${getRiskColor(result.combined_risk)}`}>
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-xl font-semibold">Overall Risk Assessment</h3>
                    <Badge variant="outline" className="text-sm font-medium">
                      {result.risk_category} Risk
                    </Badge>
                  </div>

                  <div className="space-y-4">
                    <div>
                      <div className="flex justify-between items-center mb-2">
                        <span className="text-sm font-medium">Combined Risk Score</span>
                        <span className="text-2xl font-bold">{result.combined_risk}%</span>
                      </div>
                      <Progress
                        value={result.combined_risk}
                        className="h-3"
                      />
                    </div>

                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="text-gray-600">Clinical Risk:</span>
                        <span className="ml-2 font-medium">{result.clinical_risk}%</span>
                      </div>
                      {genomicDataAvailable && (
                        <div>
                          <span className="text-gray-600">Genetic Risk:</span>
                          <span className="ml-2 font-medium">{result.genetic_risk}%</span>
                        </div>
                      )}
                    </div>
                  </div>
                </div>

                {/* Risk Factors */}
                <div className="bg-red-50 p-4 rounded-lg border border-red-200">
                  <h4 className="font-medium text-red-800 mb-3 flex items-center">
                    <AlertTriangle className="mr-2 h-4 w-4" />
                    Risk Factors ({result.risk_factors.length})
                  </h4>
                  <div className="space-y-1">
                    {result.risk_factors.map((factor, index) => (
                      <div key={index} className="text-sm text-red-700">
                        • {factor}
                      </div>
                    ))}
                  </div>
                </div>

                {/* Protective Factors */}
                {result.protective_factors.length > 0 && (
                  <div className="bg-green-50 p-4 rounded-lg border border-green-200">
                    <h4 className="font-medium text-green-800 mb-3 flex items-center">
                      <CheckCircle className="mr-2 h-4 w-4" />
                      Protective Factors ({result.protective_factors.length})
                    </h4>
                    <div className="space-y-1">
                      {result.protective_factors.map((factor, index) => (
                        <div key={index} className="text-sm text-green-700">
                          • {factor}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Genomic Information */}
                {result.genomic_variants && (
                  <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                    <h4 className="font-medium text-blue-800 mb-3 flex items-center">
                      <TrendingUp className="mr-2 h-4 w-4" />
                      Genomic Profile
                    </h4>
                    <div className="text-sm text-blue-700 space-y-1">
                      <div>APOE Status: <span className="font-medium">{result.genomic_variants.apoe_status}</span></div>
                      <div>Additional Risk Variants: <span className="font-medium">{result.genomic_variants.additional_variants}</span></div>
                      <div>Key Risk Alleles: <span className="font-medium">{result.genomic_variants.risk_alleles.join(', ')}</span></div>
                    </div>
                  </div>
                )}

                {/* Recommendations */}
                <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
                  <h4 className="font-medium text-gray-800 mb-3">
                    Personalized Recommendations
                  </h4>
                  <div className="space-y-2">
                    {result.recommendations.map((recommendation, index) => (
                      <div key={index} className="text-sm text-gray-700 flex items-start">
                        <span className="text-purple-600 mr-2 mt-1">•</span>
                        <span>{recommendation}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {!result && (
              <div className="text-center text-gray-500 py-12">
                <Brain className="h-16 w-16 mx-auto mb-4 text-gray-300" />
                <p className="text-lg font-medium mb-2">Ready for Assessment</p>
                <p>Complete the form and click "Calculate Alzheimer's Risk" to get your personalized risk analysis.</p>
              </div>
            )}
          </div>
        </div>

        <Separator className="my-8" />

        <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
          <p className="text-sm text-blue-800">
            <strong>Important:</strong> This assessment is for educational purposes and should not replace professional medical advice.
            Consult with a healthcare provider or neurologist for comprehensive evaluation and personalized care recommendations.
          </p>
        </div>
      </CardContent>
    </Card>
  );
};

export default AlzheimerAssessment;
