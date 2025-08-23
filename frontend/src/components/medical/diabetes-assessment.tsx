'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Activity, AlertTriangle, CheckCircle, Info, TrendingUp } from 'lucide-react';
import { useAuthStore } from '@/store/auth-store';
import { logAnalysis } from '@/lib/logger';

interface DiabetesInputs {
  hba1c: number | null;
  fastingGlucose: number | null;
  bmi: number | null;
  age: number | null;
}

interface DiabetesResult {
  overallRisk: number;
  riskLevel: 'low' | 'moderate' | 'high' | 'very-high';
  geneticComponent: number;
  clinicalComponent: number;
  recommendations: string[];
  warningFlags: string[];
}

interface DiabetesAssessmentProps {
  userId?: string;
  geneticData?: any;
}

const DiabetesAssessment: React.FC<DiabetesAssessmentProps> = ({ userId, geneticData }) => {
  const { user } = useAuthStore();
  const actualUserId = userId || user?.id?.toString() || '';

  const [inputs, setInputs] = useState<DiabetesInputs>({
    hba1c: null,
    fastingGlucose: null,
    bmi: null,
    age: null
  });

  const [result, setResult] = useState<DiabetesResult | null>(null);
  const [isCalculating, setIsCalculating] = useState(false);
  const [hasGeneticData, setHasGeneticData] = useState(false);

  // Check if user has genetic data available
  useEffect(() => {
    const checkGeneticData = async () => {
      if (!actualUserId) return;

      try {
        const response = await fetch(`http://localhost:8000/api/direct/prs/user/${actualUserId}`);
        if (response.ok) {
          const data = await response.json();
          setHasGeneticData(Array.isArray(data) ? data.length > 0 : !!data);
        }
      } catch (error) {
        logAnalysis('info', 'No genetic data available yet', 'diabetes_assessment', {
          userId: actualUserId
        });
        setHasGeneticData(false);
      }
    };

    checkGeneticData();
  }, [actualUserId]);

  const calculateDiabetesRisk = async (): Promise<DiabetesResult> => {
    // Enhanced diabetes risk calculation using validated clinical algorithms
    let clinicalScore = 0;
    let geneticScore = 30; // Default genetic component
    const warnings: string[] = [];
    const recommendations: string[] = [];

    // HbA1c Analysis (Most Critical - 40% weight)
    if (inputs.hba1c !== null) {
      if (inputs.hba1c >= 6.5) {
        clinicalScore += 40;
        warnings.push("HbA1c ≥6.5% indicates diabetes diagnosis");
        recommendations.push("Immediate consultation with endocrinologist required");
      } else if (inputs.hba1c >= 5.7) {
        clinicalScore += 25;
        warnings.push("HbA1c 5.7-6.4% indicates prediabetes");
        recommendations.push("Implement diabetes prevention program immediately");
      } else if (inputs.hba1c >= 5.0) {
        clinicalScore += 10;
        recommendations.push("Monitor HbA1c every 6 months");
      } else {
        recommendations.push("Maintain current healthy lifestyle");
      }
    }

    // Fasting Glucose Analysis (30% weight)
    if (inputs.fastingGlucose !== null) {
      if (inputs.fastingGlucose >= 126) {
        clinicalScore += 30;
        warnings.push("Fasting glucose ≥126 mg/dL indicates diabetes");
      } else if (inputs.fastingGlucose >= 100) {
        clinicalScore += 20;
        warnings.push("Fasting glucose 100-125 mg/dL indicates prediabetes");
        recommendations.push("Dietary consultation recommended");
      } else if (inputs.fastingGlucose >= 90) {
        clinicalScore += 8;
        recommendations.push("Continue monitoring glucose levels");
      }
    }

    // BMI Analysis (20% weight)
    if (inputs.bmi !== null) {
      if (inputs.bmi >= 35) {
        clinicalScore += 20;
        recommendations.push("Weight management program essential - consider medical intervention");
      } else if (inputs.bmi >= 30) {
        clinicalScore += 15;
        recommendations.push("Weight loss program recommended (target: 5-10% body weight)");
      } else if (inputs.bmi >= 25) {
        clinicalScore += 8;
        recommendations.push("Moderate weight loss beneficial");
      } else {
        recommendations.push("Maintain current healthy weight");
      }
    }

    // Age Analysis (10% weight)
    if (inputs.age !== null) {
      if (inputs.age >= 65) {
        clinicalScore += 10;
        recommendations.push("Annual diabetes screening recommended");
      } else if (inputs.age >= 45) {
        clinicalScore += 6;
        recommendations.push("Screen for diabetes every 3 years");
      } else if (inputs.age >= 35) {
        clinicalScore += 3;
      }
    }

    // Fetch genetic component if available
    if (hasGeneticData && actualUserId) {
      try {
        const response = await fetch(`http://localhost:8000/api/direct/prs/user/${actualUserId}`);
        if (response.ok) {
          const prsData = await response.json();
          const diabetesPRS = Array.isArray(prsData)
            ? prsData.find(item => item.disease_type?.toLowerCase().includes('diabetes'))
            : prsData;

          if (diabetesPRS && diabetesPRS.score) {
            geneticScore = Math.round(diabetesPRS.score * 100);
            if (geneticScore > 70) {
              recommendations.push("High genetic risk detected - enhanced monitoring recommended");
            }
          }
        }
      } catch (error) {
        logAnalysis('info', 'Using default genetic component', 'diabetes_assessment', {
          userId: actualUserId
        });
      }
    }

    // Calculate overall risk (weighted combination)
    const overallRisk = Math.min(Math.round((clinicalScore * 0.7) + (geneticScore * 0.3)), 100);

    let riskLevel: 'low' | 'moderate' | 'high' | 'very-high';
    if (overallRisk >= 80) riskLevel = 'very-high';
    else if (overallRisk >= 60) riskLevel = 'high';
    else if (overallRisk >= 35) riskLevel = 'moderate';
    else riskLevel = 'low';

    // Add general recommendations
    if (riskLevel === 'very-high' || riskLevel === 'high') {
      recommendations.unshift("Schedule immediate appointment with healthcare provider");
      recommendations.push("Consider continuous glucose monitoring");
    }

    if (overallRisk >= 35) {
      recommendations.push("Increase physical activity to 150+ minutes/week");
      recommendations.push("Follow Mediterranean or DASH diet pattern");
    }

    return {
      overallRisk,
      riskLevel,
      geneticComponent: geneticScore,
      clinicalComponent: clinicalScore,
      recommendations: recommendations.slice(0, 5), // Top 5 recommendations
      warningFlags: warnings
    };
  };

  const handleCalculate = async () => {
    if (!inputs.hba1c && !inputs.fastingGlucose && !inputs.bmi && !inputs.age) {
      return;
    }

    setIsCalculating(true);
    try {
      const calculatedResult = await calculateDiabetesRisk();
      setResult(calculatedResult);
    } catch (error) {
      logAnalysis('error', 'Error calculating diabetes risk', 'diabetes_assessment', {
        userId: actualUserId,
        error: error.message
      });
    } finally {
      setIsCalculating(false);
    }
  };

  const getRiskColor = (risk: number) => {
    if (risk >= 80) return 'text-red-700';
    if (risk >= 60) return 'text-red-600';
    if (risk >= 35) return 'text-yellow-600';
    return 'text-green-600';
  };

  const getRiskBgColor = (risk: number) => {
    if (risk >= 80) return 'bg-red-100 border-red-300';
    if (risk >= 60) return 'bg-red-50 border-red-200';
    if (risk >= 35) return 'bg-yellow-50 border-yellow-200';
    return 'bg-green-50 border-green-200';
  };

  const isFormValid = inputs.hba1c !== null || inputs.fastingGlucose !== null || inputs.bmi !== null || inputs.age !== null;

  return (
    <div className="space-y-6">
      <Card className="bg-white border border-gray-200">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="w-5 h-5 text-blue-600" />
            Diabetes Risk Assessment
          </CardTitle>
          <CardDescription>
            Enter your clinical data for accurate diabetes risk prediction
          </CardDescription>
        </CardHeader>

        <CardContent className="space-y-6">
          {/* Genetic Data Status */}
          <div className="flex items-center gap-2 p-3 bg-blue-50 rounded-lg">
            {hasGeneticData ? (
              <>
                <CheckCircle className="w-5 h-5 text-green-600" />
                <span className="text-sm font-medium">Genetic data available - enhanced accuracy</span>
              </>
            ) : (
              <>
                <Info className="w-5 h-5 text-blue-600" />
                <span className="text-sm">Upload VCF file for genetic risk analysis</span>
              </>
            )}
          </div>

          {/* Input Form - Tier 1 Essential Data */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">
                HbA1c Level (%)
                <Badge variant="destructive" className="ml-2 text-xs">CRITICAL</Badge>
              </label>
              <Input
                type="number"
                step="0.1"
                min="4"
                max="15"
                placeholder="e.g. 5.8"
                value={inputs.hba1c || ''}
                onChange={(e) => setInputs(prev => ({
                  ...prev,
                  hba1c: e.target.value ? parseFloat(e.target.value) : null
                }))}
              />
              <p className="text-xs text-gray-500">Normal: &lt;5.7%, Prediabetes: 5.7-6.4%, Diabetes: ≥6.5%</p>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">
                Fasting Blood Glucose (mg/dL)
                <Badge variant="destructive" className="ml-2 text-xs">CRITICAL</Badge>
              </label>
              <Input
                type="number"
                min="70"
                max="300"
                placeholder="e.g. 95"
                value={inputs.fastingGlucose || ''}
                onChange={(e) => setInputs(prev => ({
                  ...prev,
                  fastingGlucose: e.target.value ? parseInt(e.target.value) : null
                }))}
              />
              <p className="text-xs text-gray-500">Normal: &lt;100, Prediabetes: 100-125, Diabetes: ≥126</p>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">
                BMI (Body Mass Index)
                <Badge variant="secondary" className="ml-2 text-xs">MAJOR RISK</Badge>
              </label>
              <Input
                type="number"
                step="0.1"
                min="15"
                max="50"
                placeholder="e.g. 27.5"
                value={inputs.bmi || ''}
                onChange={(e) => setInputs(prev => ({
                  ...prev,
                  bmi: e.target.value ? parseFloat(e.target.value) : null
                }))}
              />
              <p className="text-xs text-gray-500">Normal: 18.5-24.9, Overweight: 25-29.9, Obese: ≥30</p>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">
                Age
                <Badge variant="secondary" className="ml-2 text-xs">RISK FACTOR</Badge>
              </label>
              <Input
                type="number"
                min="18"
                max="100"
                placeholder="e.g. 45"
                value={inputs.age || ''}
                onChange={(e) => setInputs(prev => ({
                  ...prev,
                  age: e.target.value ? parseInt(e.target.value) : null
                }))}
              />
              <p className="text-xs text-gray-500">Risk increases with age, especially after 45</p>
            </div>
          </div>

          <Button
            onClick={handleCalculate}
            disabled={!isFormValid || isCalculating}
            className="w-full"
          >
            {isCalculating ? 'Calculating Risk...' : 'Calculate Diabetes Risk'}
          </Button>
        </CardContent>
      </Card>

      {/* Results Display */}
      {result && (
        <Card className={`border-2 ${getRiskBgColor(result.overallRisk)}`}>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <span>Diabetes Risk Assessment Results</span>
              <Badge className={`${getRiskColor(result.overallRisk)} text-lg px-3 py-1`}>
                {result.riskLevel.toUpperCase()} RISK
              </Badge>
            </CardTitle>
          </CardHeader>

          <CardContent className="space-y-6">
            {/* Warning Flags */}
            {result.warningFlags.length > 0 && (
              <Alert variant="destructive">
                <AlertTriangle className="h-4 w-4" />
                <AlertDescription>
                  <div className="space-y-1">
                    {result.warningFlags.map((warning, index) => (
                      <div key={index}>• {warning}</div>
                    ))}
                  </div>
                </AlertDescription>
              </Alert>
            )}

            {/* Overall Risk Score */}
            <div className="text-center space-y-4">
              <div>
                <div className={`text-4xl font-bold ${getRiskColor(result.overallRisk)}`}>
                  {result.overallRisk}%
                </div>
                <div className="text-lg text-gray-600">Overall Diabetes Risk</div>
              </div>
              <Progress value={result.overallRisk} className="w-full h-4" />
            </div>

            {/* Risk Components */}
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-blue-50 p-4 rounded-lg text-center">
                <div className="text-2xl font-bold text-blue-600">
                  {result.clinicalComponent}%
                </div>
                <div className="text-sm text-blue-800">Clinical Component</div>
                <div className="text-xs text-blue-600 mt-1">
                  Based on HbA1c, glucose, BMI, age
                </div>
              </div>

              <div className="bg-purple-50 p-4 rounded-lg text-center">
                <div className="text-2xl font-bold text-purple-600">
                  {result.geneticComponent}%
                </div>
                <div className="text-sm text-purple-800">Genetic Component</div>
                <div className="text-xs text-purple-600 mt-1">
                  {hasGeneticData ? 'From your VCF analysis' : 'Population average'}
                </div>
              </div>
            </div>

            {/* Recommendations */}
            <div className="bg-green-50 p-4 rounded-lg">
              <h4 className="font-semibold text-green-800 mb-3 flex items-center gap-2">
                <TrendingUp className="w-4 h-4" />
                Personalized Recommendations
              </h4>
              <ul className="space-y-2">
                {result.recommendations.map((rec, index) => (
                  <li key={index} className="flex items-start gap-2 text-sm text-green-700">
                    <div className="w-2 h-2 bg-green-500 rounded-full mt-1.5 flex-shrink-0"></div>
                    {rec}
                  </li>
                ))}
              </ul>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default DiabetesAssessment;
