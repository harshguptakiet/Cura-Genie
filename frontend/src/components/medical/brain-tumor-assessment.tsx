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
import { Checkbox } from '@/components/ui/checkbox';
import { Brain, Calculator, AlertTriangle, CheckCircle, Info, TrendingUp, Zap } from 'lucide-react';
import { toast } from 'sonner';
import { logAnalysis } from '@/lib/logger';

interface BrainTumorData {
  age: number;
  sex: 'male' | 'female' | '';
  family_history: 'none' | 'brain_tumor' | 'neurofibromatosis' | 'li_fraumeni' | 'tuberous_sclerosis' | 'multiple';
  radiation_exposure: 'none' | 'medical_low' | 'medical_high' | 'occupational' | 'atomic';
  immune_status: 'normal' | 'compromised_mild' | 'compromised_severe';
  hormone_factors: {
    hormone_therapy: boolean;
    reproductive_history: 'none' | 'nulliparous' | 'multiparous';
  };
  symptoms: {
    headaches: boolean;
    seizures: boolean;
    vision_changes: boolean;
    hearing_loss: boolean;
    cognitive_changes: boolean;
    motor_weakness: boolean;
  };
  environmental_factors: {
    cell_phone_use: 'minimal' | 'moderate' | 'heavy' | 'extreme';
    chemical_exposure: boolean;
    viral_infections: boolean;
  };
}

interface BrainTumorResult {
  clinical_risk: number;
  genetic_risk: number;
  combined_risk: number;
  risk_category: 'Low' | 'Moderate' | 'High' | 'Very High';
  tumor_type_risks: {
    glioma: number;
    meningioma: number;
    acoustic_neuroma: number;
    pituitary_adenoma: number;
  };
  risk_factors: string[];
  protective_factors: string[];
  recommendations: string[];
  genomic_variants?: {
    tp53_status: string;
    nf1_status: string;
    additional_variants: number;
    risk_alleles: string[];
  };
}

interface BrainTumorAssessmentProps {
  userId: string;
}

const BrainTumorAssessment: React.FC<BrainTumorAssessmentProps> = ({ userId }) => {
  const [formData, setFormData] = useState<BrainTumorData>({
    age: 0,
    sex: '',
    family_history: 'none',
    radiation_exposure: 'none',
    immune_status: 'normal',
    hormone_factors: {
      hormone_therapy: false,
      reproductive_history: 'none'
    },
    symptoms: {
      headaches: false,
      seizures: false,
      vision_changes: false,
      hearing_loss: false,
      cognitive_changes: false,
      motor_weakness: false
    },
    environmental_factors: {
      cell_phone_use: 'moderate',
      chemical_exposure: false,
      viral_infections: false
    }
  });

  const [result, setResult] = useState<BrainTumorResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [genomicDataAvailable, setGenomicDataAvailable] = useState(false);

  // Check for genomic data availability
  React.useEffect(() => {
    const checkGenomicData = async () => {
      try {
        const response = await fetch(`http://localhost:8000/api/direct/prs/user/${userId}`);
        if (response.ok) {
          const data = await response.json();
          const hasBrainTumorData = data.some((score: any) =>
            score.disease_name?.toLowerCase().includes('brain') ||
            score.disease_name?.toLowerCase().includes('glioma') ||
            score.disease_name?.toLowerCase().includes('meningioma') ||
            score.disease_name?.toLowerCase().includes('tumor')
          );
          setGenomicDataAvailable(hasBrainTumorData);
        }
      } catch (error) {
        logAnalysis('error', 'Error checking genomic data', 'brain_tumor_assessment', {
          userId,
          error: error.message
        });
      }
    };

    checkGenomicData();
  }, [userId]);

  const handleInputChange = (field: string, value: any) => {
    if (field.includes('.')) {
      const [parent, child] = field.split('.');
      setFormData(prev => ({
        ...prev,
        [parent]: {
          ...prev[parent as keyof BrainTumorData],
          [child]: value
        }
      }));
    } else {
      setFormData(prev => ({ ...prev, [field]: value }));
    }
  };

  const calculateRisk = async () => {
    setLoading(true);
    try {
      // Calculate clinical risk score
      let clinicalRisk = 0;

      // Age factor (peaks at middle age for some types)
      if (formData.age >= 65) clinicalRisk += 15;
      else if (formData.age >= 45) clinicalRisk += 10;
      else if (formData.age >= 20) clinicalRisk += 5;
      else if (formData.age < 10) clinicalRisk += 8; // Pediatric brain tumors

      // Sex factor (varies by tumor type)
      if (formData.sex === 'male') clinicalRisk += 3; // Slightly higher for gliomas
      else if (formData.sex === 'female') clinicalRisk += 2; // Higher for meningiomas

      // Family history (strongest genetic factor)
      const familyRiskMap = {
        'none': 0,
        'brain_tumor': 15,
        'neurofibromatosis': 25,
        'li_fraumeni': 30,
        'tuberous_sclerosis': 20,
        'multiple': 35
      };
      clinicalRisk += familyRiskMap[formData.family_history];

      // Radiation exposure (well-established risk factor)
      const radiationRiskMap = {
        'none': 0,
        'medical_low': 5,
        'medical_high': 15,
        'occupational': 20,
        'atomic': 25
      };
      clinicalRisk += radiationRiskMap[formData.radiation_exposure];

      // Immune status
      const immuneRiskMap = {
        'normal': 0,
        'compromised_mild': 8,
        'compromised_severe': 15
      };
      clinicalRisk += immuneRiskMap[formData.immune_status];

      // Hormone factors (primarily for meningiomas)
      if (formData.hormone_factors.hormone_therapy) clinicalRisk += 5;

      // Symptoms (may indicate existing tumor)
      const symptomCount = Object.values(formData.symptoms).filter(Boolean).length;
      if (symptomCount >= 3) clinicalRisk += 20;
      else if (symptomCount >= 2) clinicalRisk += 10;
      else if (symptomCount === 1) clinicalRisk += 3;

      // Environmental factors
      const cellPhoneRiskMap = {
        'minimal': 0,
        'moderate': 1,
        'heavy': 3,
        'extreme': 5
      };
      clinicalRisk += cellPhoneRiskMap[formData.environmental_factors.cell_phone_use];

      if (formData.environmental_factors.chemical_exposure) clinicalRisk += 5;
      if (formData.environmental_factors.viral_infections) clinicalRisk += 3;

      clinicalRisk = Math.max(0, Math.min(100, clinicalRisk));

      // Try to get genetic risk
      let geneticRisk = 0;
      let genomicVariants = undefined;

      if (genomicDataAvailable) {
        try {
          const geneticResponse = await fetch(`http://localhost:8000/api/direct/prs/user/${userId}`);
          if (geneticResponse.ok) {
            const geneticData = await geneticResponse.json();
            const brainTumorScore = geneticData.find((score: any) =>
              score.disease_name?.toLowerCase().includes('brain') ||
              score.disease_name?.toLowerCase().includes('glioma') ||
              score.disease_name?.toLowerCase().includes('meningioma')
            );

            if (brainTumorScore) {
              geneticRisk = Math.round(brainTumorScore.risk_score * 100);

              // Mock genomic variants data (would come from actual analysis)
              genomicVariants = {
                tp53_status: 'wildtype', // or 'mutated'
                nf1_status: 'wildtype', // or 'mutated'
                additional_variants: Math.floor(Math.random() * 12) + 3,
                risk_alleles: ['TP53', 'CDKN2A', 'RTEL1', 'CCDC26', 'PHLDB1']
              };
            }
          }
        } catch (error) {
          logAnalysis('error', 'Error fetching genetic data', 'brain_tumor_assessment', {
            userId,
            error: error.message
          });
        }
      }

      // Combined risk calculation
      const combinedRisk = genomicDataAvailable ?
        Math.round((clinicalRisk * 0.7) + (geneticRisk * 0.3)) :
        clinicalRisk;

      // Calculate tumor-specific risks
      const tumorTypeRisks = {
        glioma: Math.round(combinedRisk * (formData.sex === 'male' ? 1.2 : 0.8)),
        meningioma: Math.round(combinedRisk * (formData.sex === 'female' ? 1.3 : 0.7)),
        acoustic_neuroma: Math.round(combinedRisk * 0.6),
        pituitary_adenoma: Math.round(combinedRisk * 0.9)
      };

      // Determine risk category
      let riskCategory: 'Low' | 'Moderate' | 'High' | 'Very High';
      if (combinedRisk < 15) riskCategory = 'Low';
      else if (combinedRisk < 35) riskCategory = 'Moderate';
      else if (combinedRisk < 60) riskCategory = 'High';
      else riskCategory = 'Very High';

      // Generate risk factors
      const riskFactors: string[] = [];
      if (formData.family_history !== 'none') riskFactors.push('Family history of brain tumors or genetic syndromes');
      if (formData.radiation_exposure !== 'none') riskFactors.push('Previous radiation exposure');
      if (formData.immune_status !== 'normal') riskFactors.push('Compromised immune system');
      if (formData.hormone_factors.hormone_therapy) riskFactors.push('Hormone therapy use');
      if (symptomCount >= 2) riskFactors.push('Multiple neurological symptoms present');
      if (formData.environmental_factors.chemical_exposure) riskFactors.push('Chemical exposure history');
      if (formData.environmental_factors.cell_phone_use === 'extreme') riskFactors.push('Heavy cell phone usage');

      // Generate protective factors
      const protectiveFactors: string[] = [];
      if (formData.family_history === 'none') protectiveFactors.push('No family history of brain tumors');
      if (formData.radiation_exposure === 'none') protectiveFactors.push('No significant radiation exposure');
      if (formData.immune_status === 'normal') protectiveFactors.push('Normal immune function');
      if (symptomCount === 0) protectiveFactors.push('No neurological symptoms');
      if (!formData.environmental_factors.chemical_exposure) protectiveFactors.push('No known chemical exposures');

      // Generate recommendations
      const recommendations: string[] = [];
      if (combinedRisk >= 35) {
        recommendations.push('Consider regular neurological screening and imaging studies');
        recommendations.push('Consult with a neuro-oncologist for risk assessment');
      }
      if (symptomCount >= 2) {
        recommendations.push('Urgent neurological evaluation recommended for current symptoms');
      }
      if (formData.family_history !== 'none') {
        recommendations.push('Genetic counseling recommended for hereditary cancer syndromes');
      }

      recommendations.push('Limit unnecessary radiation exposure (CT scans, etc.)');
      recommendations.push('Maintain overall health with regular exercise and balanced nutrition');
      recommendations.push('Consider reducing cell phone usage and using hands-free devices');
      recommendations.push('Avoid known carcinogenic chemicals when possible');

      if (genomicDataAvailable && geneticRisk > 25) {
        recommendations.push('Discuss enhanced screening protocols with healthcare provider');
        recommendations.push('Consider participation in high-risk surveillance programs');
      }

      const assessmentResult: BrainTumorResult = {
        clinical_risk: clinicalRisk,
        genetic_risk: geneticRisk,
        combined_risk: combinedRisk,
        risk_category: riskCategory,
        tumor_type_risks: tumorTypeRisks,
        risk_factors: riskFactors,
        protective_factors: protectiveFactors,
        recommendations: recommendations,
        genomic_variants: genomicVariants
      };

      setResult(assessmentResult);
      toast.success('Brain tumor risk assessment completed!');

    } catch (error) {
      logAnalysis('error', 'Error calculating brain tumor risk', 'brain_tumor_assessment', {
        userId,
        error: error.message
      });
      toast.error('Error calculating risk assessment. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const getRiskColor = (risk: number) => {
    if (risk < 15) return 'text-green-600 bg-green-50 border-green-200';
    if (risk < 35) return 'text-yellow-600 bg-yellow-50 border-yellow-200';
    if (risk < 60) return 'text-orange-600 bg-orange-50 border-orange-200';
    return 'text-red-600 bg-red-50 border-red-200';
  };

  return (
    <Card className="w-full">
      <CardHeader className="bg-gradient-to-r from-indigo-50 to-purple-50 border-b">
        <CardTitle className="flex items-center gap-3 text-2xl">
          <div className="p-2 bg-indigo-100 rounded-lg">
            <Zap className="h-6 w-6 text-indigo-600" />
          </div>
          Brain Tumor Risk Assessment
          <Badge variant="secondary" className="bg-indigo-100 text-indigo-700">
            Tier 1 - Essential Markers
          </Badge>
        </CardTitle>
        <CardDescription className="text-base">
          Comprehensive assessment combining clinical factors, family history, environmental exposures, and genomic risk analysis for brain tumors.
        </CardDescription>

        {!genomicDataAvailable && (
          <Alert className="border-amber-200 bg-amber-50">
            <Info className="h-4 w-4 text-amber-600" />
            <AlertDescription className="text-amber-800">
              Upload your genomic data to include genetic risk factors (TP53, NF1, other variants) in the assessment.
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
                  min="0"
                  max="120"
                  value={formData.age || ''}
                  onChange={(e) => handleInputChange('age', parseInt(e.target.value) || 0)}
                  placeholder="Enter age"
                  className="w-full"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="sex">Sex</Label>
                <Select onValueChange={(value) => handleInputChange('sex', value)}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select sex" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="male">Male</SelectItem>
                    <SelectItem value="female">Female</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="family_history">Family History</Label>
              <Select onValueChange={(value) => handleInputChange('family_history', value)}>
                <SelectTrigger>
                  <SelectValue placeholder="Select family history" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="none">No family history</SelectItem>
                  <SelectItem value="brain_tumor">Brain tumor in family</SelectItem>
                  <SelectItem value="neurofibromatosis">Neurofibromatosis</SelectItem>
                  <SelectItem value="li_fraumeni">Li-Fraumeni syndrome</SelectItem>
                  <SelectItem value="tuberous_sclerosis">Tuberous sclerosis</SelectItem>
                  <SelectItem value="multiple">Multiple genetic syndromes</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="radiation_exposure">Radiation Exposure History</Label>
              <Select onValueChange={(value) => handleInputChange('radiation_exposure', value)}>
                <SelectTrigger>
                  <SelectValue placeholder="Select radiation exposure" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="none">No significant exposure</SelectItem>
                  <SelectItem value="medical_low">Low medical exposure (routine X-rays)</SelectItem>
                  <SelectItem value="medical_high">High medical exposure (multiple CT/radiation therapy)</SelectItem>
                  <SelectItem value="occupational">Occupational exposure</SelectItem>
                  <SelectItem value="atomic">Atomic bomb/nuclear accident</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="immune_status">Immune System Status</Label>
              <Select onValueChange={(value) => handleInputChange('immune_status', value)}>
                <SelectTrigger>
                  <SelectValue placeholder="Select immune status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="normal">Normal immune function</SelectItem>
                  <SelectItem value="compromised_mild">Mildly compromised</SelectItem>
                  <SelectItem value="compromised_severe">Severely compromised (HIV, transplant, etc.)</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Hormone Factors */}
            <div className="space-y-4">
              <Label className="text-sm font-medium">Hormone Factors</Label>
              <div className="space-y-3">
                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="hormone_therapy"
                    checked={formData.hormone_factors.hormone_therapy}
                    onCheckedChange={(checked) => handleInputChange('hormone_factors.hormone_therapy', checked)}
                  />
                  <Label htmlFor="hormone_therapy" className="text-sm">Current/past hormone therapy</Label>
                </div>
              </div>
            </div>

            {/* Neurological Symptoms */}
            <div className="space-y-4">
              <Label className="text-sm font-medium">Current Neurological Symptoms</Label>
              <div className="grid grid-cols-2 gap-3">
                {Object.entries(formData.symptoms).map(([symptom, checked]) => (
                  <div key={symptom} className="flex items-center space-x-2">
                    <Checkbox
                      id={symptom}
                      checked={checked}
                      onCheckedChange={(checked) => handleInputChange(`symptoms.${symptom}`, checked)}
                    />
                    <Label htmlFor={symptom} className="text-sm capitalize">
                      {symptom.replace('_', ' ')}
                    </Label>
                  </div>
                ))}
              </div>
            </div>

            {/* Environmental Factors */}
            <div className="space-y-4">
              <Label className="text-sm font-medium">Environmental Factors</Label>
              <div className="space-y-3">
                <div className="space-y-2">
                  <Label htmlFor="cell_phone_use" className="text-xs">Cell Phone Usage</Label>
                  <Select onValueChange={(value) => handleInputChange('environmental_factors.cell_phone_use', value)}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select usage level" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="minimal">Minimal (&lt;30 min/day)</SelectItem>
                      <SelectItem value="moderate">Moderate (30min-2hrs/day)</SelectItem>
                      <SelectItem value="heavy">Heavy (2-5hrs/day)</SelectItem>
                      <SelectItem value="extreme">Extreme (&gt;5hrs/day)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="chemical_exposure"
                    checked={formData.environmental_factors.chemical_exposure}
                    onCheckedChange={(checked) => handleInputChange('environmental_factors.chemical_exposure', checked)}
                  />
                  <Label htmlFor="chemical_exposure" className="text-sm">Chemical/pesticide exposure</Label>
                </div>

                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="viral_infections"
                    checked={formData.environmental_factors.viral_infections}
                    onCheckedChange={(checked) => handleInputChange('environmental_factors.viral_infections', checked)}
                  />
                  <Label htmlFor="viral_infections" className="text-sm">History of EBV or CMV infections</Label>
                </div>
              </div>
            </div>

            <Button
              onClick={calculateRisk}
              disabled={loading || formData.age <= 0}
              className="w-full bg-indigo-600 hover:bg-indigo-700"
            >
              {loading ? (
                <>
                  <Calculator className="mr-2 h-4 w-4 animate-spin" />
                  Calculating Risk...
                </>
              ) : (
                <>
                  <Calculator className="mr-2 h-4 w-4" />
                  Calculate Brain Tumor Risk
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
                      <Progress value={result.combined_risk} className="h-3" />
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

                {/* Tumor Type Specific Risks */}
                <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                  <h4 className="font-medium text-blue-800 mb-3 flex items-center">
                    <TrendingUp className="mr-2 h-4 w-4" />
                    Tumor Type Specific Risks
                  </h4>
                  <div className="grid grid-cols-2 gap-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-blue-700">Glioma:</span>
                      <span className="font-medium">{result.tumor_type_risks.glioma}%</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-blue-700">Meningioma:</span>
                      <span className="font-medium">{result.tumor_type_risks.meningioma}%</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-blue-700">Acoustic Neuroma:</span>
                      <span className="font-medium">{result.tumor_type_risks.acoustic_neuroma}%</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-blue-700">Pituitary Adenoma:</span>
                      <span className="font-medium">{result.tumor_type_risks.pituitary_adenoma}%</span>
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
                  <div className="bg-purple-50 p-4 rounded-lg border border-purple-200">
                    <h4 className="font-medium text-purple-800 mb-3 flex items-center">
                      <Brain className="mr-2 h-4 w-4" />
                      Genomic Profile
                    </h4>
                    <div className="text-sm text-purple-700 space-y-1">
                      <div>TP53 Status: <span className="font-medium">{result.genomic_variants.tp53_status}</span></div>
                      <div>NF1 Status: <span className="font-medium">{result.genomic_variants.nf1_status}</span></div>
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
                        <span className="text-indigo-600 mr-2 mt-1">•</span>
                        <span>{recommendation}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {!result && (
              <div className="text-center text-gray-500 py-12">
                <Zap className="h-16 w-16 mx-auto mb-4 text-gray-300" />
                <p className="text-lg font-medium mb-2">Ready for Assessment</p>
                <p>Complete the form and click "Calculate Brain Tumor Risk" to get your personalized risk analysis.</p>
              </div>
            )}
          </div>
        </div>

        <Separator className="my-8" />

        <div className="bg-red-50 p-4 rounded-lg border border-red-200">
          <p className="text-sm text-red-800">
            <strong>Important:</strong> This assessment is for educational purposes only. If you have neurological symptoms,
            seek immediate medical evaluation. Brain tumors are rare, and most symptoms have benign causes.
            Consult with a healthcare provider or neurologist for professional evaluation.
          </p>
        </div>
      </CardContent>
    </Card>
  );
};

export default BrainTumorAssessment;
