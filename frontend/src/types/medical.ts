// Medical Data Type Definitions
// This file contains all the type definitions for medical data structures
// used across the medical assessment components

export interface MRIAnalysisResult {
  success: boolean;
  image_id: string;
  analysis: {
    detected_regions: Array<{
      id: string;
      type: string;
      confidence: number;
      coordinates: { x: number; y: number; width: number; height: number };
      location: string;
      risk_level: string;
    }>;
    overall_confidence: number;
    processing_time: number;
    annotated_image?: string;
  };
}

export interface ProcessedMRIData {
  image_url: string;
  analysis_results: MRIAnalysisResult;
  metadata: {
    upload_date: string;
    file_size: number;
    user_id: string;
  };
}

export interface GeneticScore {
  disease_name: string;
  disease_type: string;
  risk_score: number;
  percentile: number;
  category: string;
  confidence: number;
  user_id: string;
  created_at: string;
}

export interface MRIImageUploadProps {
  onUploadSuccess?: (data: ProcessedMRIData) => void;
  onImageProcessed?: (processedData: MRIAnalysisResult) => void;
  onCompleteAnalysis?: (uploadResult: MRIAnalysisResult, file: File) => void;
  userId: string;
  compact?: boolean;
}

export interface UploadedFile {
  file: File;
  preview: string;
  id: string;
  status: 'uploading' | 'processing' | 'completed' | 'error';
  progress: number;
  analysisResult?: MRIAnalysisResult;
}

export interface SimpleUploadInterfaceProps {
  userId: string;
  onCompleteAnalysis: (uploadResult: MRIAnalysisResult, file: File) => void;
}

export interface BrainTumorData {
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

export interface AlzheimerData {
  age: number;
  education_years: number;
  family_history: 'none' | 'one_parent' | 'both_parents' | 'siblings' | 'multiple';
  cognitive_score: number; // MoCA or MMSE score (0-30)
  apoe_status?: 'unknown' | 'e2_e2' | 'e2_e3' | 'e2_e4' | 'e3_e3' | 'e3_e4' | 'e4_e4';
  cardiovascular_risk: 'low' | 'moderate' | 'high';
  physical_activity: 'sedentary' | 'light' | 'moderate' | 'vigorous';
}

export interface DiabetesInputs {
  hba1c: number | null;
  fastingGlucose: number | null;
  bmi: number | null;
  age: number | null;
}

export interface DiabetesResult {
  overallRisk: number;
  riskLevel: 'low' | 'moderate' | 'high' | 'very-high';
  geneticComponent: number;
  clinicalComponent: number;
  recommendations: string[];
  warningFlags: string[];
}

export interface DiabetesAssessmentProps {
  userId?: string;
  geneticData?: GeneticScore[];
}
