// Comprehensive Type Definitions for Cura-Genie Frontend
// This file provides type safety across all components and data flows

// ============================================================================
// ERROR HANDLING TYPES
// ============================================================================

export interface AppError extends Error {
    code?: string;
    context?: Record<string, unknown>;
    timestamp: string;
    userMessage?: string;
}

export type ErrorCode =
    | 'UPLOAD_FAILED'
    | 'PROCESSING_ERROR'
    | 'NETWORK_ERROR'
    | 'VALIDATION_ERROR'
    | 'AUTHENTICATION_ERROR'
    | 'PERMISSION_DENIED'
    | 'RESOURCE_NOT_FOUND'
    | 'UNKNOWN_ERROR';

// ============================================================================
// UPLOAD AND FILE TYPES
// ============================================================================

export interface UploadSuccessData {
    file_id: string;
    file_name: string;
    file_size: number;
    upload_date: string;
    processing_status: 'pending' | 'processing' | 'completed' | 'error';
    file_url?: string;
    metadata?: Record<string, unknown>;
    path?: string;
}

export interface VCFUploadResult {
    path: string;
    file_id: string;
    upload_status: 'success' | 'failed';
    error_message?: string;
    file_size?: number;
    upload_timestamp?: string;
}

export interface FileUploadProgress {
    loaded: number;
    total: number;
    percentage: number;
    status: 'uploading' | 'processing' | 'completed' | 'error';
}

// ============================================================================
// GENOMIC DATA TYPES
// ============================================================================

export interface GenomicVariant {
    variant_id: string;
    chromosome: string;
    position: number;
    reference: string;
    alternative: string;
    quality: number;
    filter: string;
    variant_type: string;
    info: Record<string, string | number>;
}

export interface VariantDisplayData {
    variant_id: string;
    display_name: string;
    significance: 'pathogenic' | 'likely_pathogenic' | 'uncertain' | 'likely_benign' | 'benign';
    clinical_impact: 'high' | 'moderate' | 'low' | 'modifier';
    chromosome: string;
    position: number;
    reference: string;
    alternative: string;
    quality: number;
}

export interface ChromosomeData {
    chromosome: string;
    variants: GenomicVariant[];
    length: number;
    centromere_position?: number;
}

// ============================================================================
// RECOMMENDATIONS TYPES
// ============================================================================

export interface HealthRecommendation {
    id: string;
    title: string;
    description: string;
    category: 'lifestyle' | 'medical' | 'dietary' | 'screening' | 'prevention';
    priority: 'high' | 'medium' | 'low';
    basedOn: string[];
    actionItems: string[];
    evidence_level: 'strong' | 'moderate' | 'weak';
    created_at: string;
    updated_at: string;
}

export type RecommendationCategory = 'lifestyle' | 'medical' | 'dietary' | 'screening' | 'prevention';
export type RecommendationPriority = 'high' | 'medium' | 'low';
export type EvidenceLevel = 'strong' | 'moderate' | 'weak';

// ============================================================================
// PRS (POLYGENIC RISK SCORE) TYPES
// ============================================================================

export interface PRSScore {
    id: string;
    disease_name: string;
    risk_score: number;
    risk_percentage: number;
    risk_category: 'low' | 'moderate' | 'high' | 'very_high';
    confidence_interval: [number, number];
    population_percentile: number;
    genetic_markers_count: number;
    last_updated: string;
}

export type RiskCategory = 'low' | 'moderate' | 'high' | 'very_high';

// ============================================================================
// DASHBOARD AND STATS TYPES
// ============================================================================

export interface DashboardStats {
    hasData: boolean;
    averageScore: number;
    totalScores: number;
    diseasesAnalyzed: number;
    lastAnalysisDate?: string;
    totalVariants?: number;
    qualityMetrics?: {
        averageQuality: number;
        lowQualityVariants: number;
        highQualityVariants: number;
    };
}

export interface QuickStat {
    title: string;
    value: string;
    icon: React.ComponentType<{ className?: string }>;
    color: string;
    bgColor: string;
}

// ============================================================================
// USER AND AUTH TYPES
// ============================================================================

export interface UserProfile {
    id: string;
    email: string;
    name?: string;
    date_of_birth?: string;
    gender?: 'male' | 'female' | 'other' | 'prefer_not_to_say';
    consent_given: boolean;
    consent_date?: string;
    created_at: string;
    updated_at: string;
}

export interface AuthState {
    user: UserProfile | null;
    isAuthenticated: boolean;
    isLoading: boolean;
    error: AppError | null;
}

// ============================================================================
// API RESPONSE TYPES
// ============================================================================

export interface ApiResponse<T> {
    data: T;
    success: boolean;
    message?: string;
    error?: AppError;
    timestamp: string;
}

export interface PaginatedResponse<T> {
    data: T[];
    pagination: {
        page: number;
        limit: number;
        total: number;
        totalPages: number;
    };
}

// ============================================================================
// TYPE GUARDS AND VALIDATION
// ============================================================================

export const isUploadSuccessData = (data: unknown): data is UploadSuccessData => {
    return (
        typeof data === 'object' &&
        data !== null &&
        'file_id' in data &&
        'file_name' in data &&
        'file_size' in data &&
        'upload_date' in data
    );
};

export const isGenomicVariant = (data: unknown): data is GenomicVariant => {
    return (
        typeof data === 'object' &&
        data !== null &&
        'variant_id' in data &&
        'chromosome' in data &&
        'position' in data &&
        'reference' in data &&
        'alternative' in data
    );
};

export const isHealthRecommendation = (data: unknown): data is HealthRecommendation => {
    return (
        typeof data === 'object' &&
        data !== null &&
        'id' in data &&
        'title' in data &&
        'description' in data &&
        'category' in data &&
        'priority' in data
    );
};

export const isPRSScore = (data: unknown): data is PRSScore => {
    return (
        typeof data === 'object' &&
        data !== null &&
        'id' in data &&
        'disease_name' in data &&
        'risk_score' in data &&
        'risk_percentage' in data
    );
};

// ============================================================================
// UTILITY TYPES
// ============================================================================

export type NonNullableFields<T> = {
    [P in keyof T]: NonNullable<T[P]>;
};

export type DeepPartial<T> = {
    [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P];
};

export type RequireFields<T, K extends keyof T> = T & Required<Pick<T, K>>;

export type OptionalFields<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>;
