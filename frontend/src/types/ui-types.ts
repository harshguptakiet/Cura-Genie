// UI Component Type Definitions
// This file contains proper TypeScript interfaces for UI component data
// to replace all 'any' types and improve type safety

// File Upload Interfaces
export interface UploadSuccessData {
    file_id: string;
    file_name: string;
    file_size: number;
    upload_date: string;
    file_url?: string;
    metadata?: Record<string, unknown>;
}

export interface UploadError {
    message: string;
    code?: string;
    details?: Record<string, unknown>;
}

export interface UploadResponse {
    success: boolean;
    message: string;
    fileId?: string;
}

// Progress Interfaces
export interface ProgressStep {
    id: string;
    title: string;
    description: string;
    status: 'pending' | 'in_progress' | 'completed' | 'error';
    icon: React.ComponentType<{ className?: string; size?: number }>;
    progress?: number;
}

export interface AnalysisStep {
    id: string;
    name: string;
    description: string;
    status: 'pending' | 'in-progress' | 'completed' | 'error';
    icon: React.ComponentType<{ className?: string; size?: number }>;
    estimatedTime: string;
    details?: string;
}

// Timeline Interfaces
export interface TimelineItem {
    id: string;
    title: string;
    description: string;
    timestamp: string;
    type: 'upload' | 'analysis' | 'report' | 'recommendation';
    status: 'pending' | 'completed' | 'error';
    metadata: Record<string, string | number | boolean>;
}

export interface TimelineEvent {
    id: string;
    type: 'upload' | 'analysis' | 'report' | 'consultation' | 'alert' | 'milestone';
    title: string;
    description: string;
    timestamp: string;
    status: 'completed' | 'in-progress' | 'pending' | 'failed';
    metadata?: {
        fileType?: string;
        analysisType?: string;
        severity?: 'low' | 'medium' | 'high';
        [key: string]: string | number | boolean;
    };
}

// Patient Interfaces
export interface Patient {
    id: string;
    name: string;
    email: string;
    age: number;
    gender: 'male' | 'female' | 'other' | 'unknown';
    last_visit: string;
    status: 'active' | 'inactive' | 'pending';
    riskLevel: 'low' | 'moderate' | 'high';
    analysisStatus: 'completed' | 'in-progress' | 'pending';
    highRiskConditions: number;
    totalConditions: number;
}

// Genomic Data Interfaces
export interface GenomicDataPoint {
    chromosome: string;
    position: number;
    reference: string;
    alternate: string;
    quality: number;
    filter: string;
    info: Record<string, string | number>;
    ref?: string;
    importance?: number;
}

export interface GenomicDataArray extends Array<GenomicDataPoint> { }

// Component Props Interfaces
export interface FileUploadProps {
    onUploadSuccess?: (data: UploadSuccessData) => void;
}

export interface ClinicalFileUploadProps {
    onUploadSuccess?: (data: UploadSuccessData) => void;
    assessmentType: 'general' | 'diabetes' | 'alzheimer' | 'brain-tumor';
}

export interface AnalysisTrackerProps {
    uploadId?: string;
    isProcessing: boolean;
    onComplete?: () => void;
}

export interface ResultsTimelineProps {
    userId: string;
}

export interface PatientListProps {
    doctorId?: string;
}

export interface EnhancedDNAVisualizationProps {
    height?: number;
    width?: number;
    showControls?: boolean;
    genomicData?: GenomicDataArray;
}

// Particle System Interface
export interface Particle {
    x: number;
    y: number;
    vx: number;
    vy: number;
    life: number;
    maxLife: number;
    color: string;
}

// DNA Base Interface
export interface DNABase {
    x: number;
    y: number;
    z: number;
    type: string;
    pair: string;
    importance: number;
    position: number;
    chromosome: string;
}
