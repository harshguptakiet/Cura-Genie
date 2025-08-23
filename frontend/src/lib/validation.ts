// Comprehensive Validation Utilities for Cura-Genie Frontend
// Provides runtime type checking and data validation for critical data flows

import {
    GenomicVariant,
    HealthRecommendation,
    PRSScore,
    UploadSuccessData,
    VCFUploadResult,
    isGenomicVariant,
    isHealthRecommendation,
    isPRSScore,
    isUploadSuccessData
} from '@/types';

// ============================================================================
// CORE VALIDATION FUNCTIONS
// ============================================================================

export const validateRequired = (value: unknown, fieldName: string): boolean => {
    if (value === null || value === undefined) {
        console.warn(`Validation failed: ${fieldName} is required but was ${value}`);
        return false;
    }

    if (typeof value === 'string' && value.trim() === '') {
        console.warn(`Validation failed: ${fieldName} cannot be empty`);
        return false;
    }

    return true;
};

export const validateString = (value: unknown, fieldName: string, minLength = 1, maxLength?: number): boolean => {
    if (!validateRequired(value, fieldName)) return false;

    if (typeof value !== 'string') {
        console.warn(`Validation failed: ${fieldName} must be a string, got ${typeof value}`);
        return false;
    }

    if (value.length < minLength) {
        console.warn(`Validation failed: ${fieldName} must be at least ${minLength} characters long`);
        return false;
    }

    if (maxLength && value.length > maxLength) {
        console.warn(`Validation failed: ${fieldName} must be at most ${maxLength} characters long`);
        return false;
    }

    return true;
};

export const validateNumber = (value: unknown, fieldName: string, min?: number, max?: number): boolean => {
    if (!validateRequired(value, fieldName)) return false;

    if (typeof value !== 'number' || isNaN(value)) {
        console.warn(`Validation failed: ${fieldName} must be a valid number, got ${typeof value}`);
        return false;
    }

    if (min !== undefined && value < min) {
        console.warn(`Validation failed: ${fieldName} must be at least ${min}, got ${value}`);
        return false;
    }

    if (max !== undefined && value > max) {
        console.warn(`Validation failed: ${fieldName} must be at most ${max}, got ${value}`);
        return false;
    }

    return true;
};

export const validateArray = (value: unknown, fieldName: string, minLength = 0): boolean => {
    if (!validateRequired(value, fieldName)) return false;

    if (!Array.isArray(value)) {
        console.warn(`Validation failed: ${fieldName} must be an array, got ${typeof value}`);
        return false;
    }

    if (value.length < minLength) {
        console.warn(`Validation failed: ${fieldName} must have at least ${minLength} items, got ${value.length}`);
        return false;
    }

    return true;
};

export const validateEnum = <T extends string>(
    value: unknown,
    fieldName: string,
    allowedValues: readonly T[]
): value is T => {
    if (!validateRequired(value, fieldName)) return false;

    if (typeof value !== 'string') {
        console.warn(`Validation failed: ${fieldName} must be a string, got ${typeof value}`);
        return false;
    }

    if (!allowedValues.includes(value as T)) {
        console.warn(`Validation failed: ${fieldName} must be one of [${allowedValues.join(', ')}], got ${value}`);
        return false;
    }

    return true;
};

// ============================================================================
// SPECIFIC DATA TYPE VALIDATION
// ============================================================================

export const validateGenomicVariant = (data: unknown): data is GenomicVariant => {
    if (!isGenomicVariant(data)) {
        console.warn('Validation failed: Invalid GenomicVariant data structure');
        return false;
    }

    // Additional validation for specific fields
    if (!validateString(data.variant_id, 'variant_id', 1, 100)) return false;
    if (!validateString(data.chromosome, 'chromosome', 1, 10)) return false;
    if (!validateNumber(data.position, 'position', 1)) return false;
    if (!validateString(data.reference, 'reference', 1, 100)) return false;
    if (!validateString(data.alternative, 'alternative', 1, 100)) return false;
    if (!validateNumber(data.quality, 'quality', 0)) return false;

    return true;
};

export const validateHealthRecommendation = (data: unknown): data is HealthRecommendation => {
    if (!isHealthRecommendation(data)) {
        console.warn('Validation failed: Invalid HealthRecommendation data structure');
        return false;
    }

    // Additional validation for specific fields
    if (!validateString(data.id, 'id', 1, 100)) return false;
    if (!validateString(data.title, 'title', 1, 200)) return false;
    if (!validateString(data.description, 'description', 1, 1000)) return false;
    if (!validateArray(data.basedOn, 'basedOn', 0)) return false;
    if (!validateArray(data.actionItems, 'actionItems', 0)) return false;

    return true;
};

export const validatePRSScore = (data: unknown): data is PRSScore => {
    if (!isPRSScore(data)) {
        console.warn('Validation failed: Invalid PRSScore data structure');
        return false;
    }

    // Additional validation for specific fields
    if (!validateString(data.id, 'id', 1, 100)) return false;
    if (!validateString(data.disease_name, 'disease_name', 1, 200)) return false;
    if (!validateNumber(data.risk_score, 'risk_score', 0, 100)) return false;
    if (!validateNumber(data.risk_percentage, 'risk_percentage', 0, 100)) return false;

    return true;
};

export const validateUploadSuccessData = (data: unknown): data is UploadSuccessData => {
    if (!isUploadSuccessData(data)) {
        console.warn('Validation failed: Invalid UploadSuccessData structure');
        return false;
    }

    // Additional validation for specific fields
    if (!validateString(data.file_id, 'file_id', 1, 100)) return false;
    if (!validateString(data.file_name, 'file_name', 1, 200)) return false;
    if (!validateNumber(data.file_size, 'file_size', 1)) return false;
    if (!validateString(data.upload_date, 'upload_date', 1)) return false;

    return true;
};

export const validateVCFUploadResult = (data: unknown): data is VCFUploadResult => {
    if (typeof data !== 'object' || data === null) {
        console.warn('Validation failed: VCFUploadResult must be an object');
        return false;
    }

    const result = data as Record<string, unknown>;

    if (!validateString(result.path, 'path', 1)) return false;
    if (!validateString(result.file_id, 'file_id', 1)) return false;
    if (!validateEnum(result.upload_status, 'upload_status', ['success', 'failed'] as const)) return false;

    return true;
};

// ============================================================================
// BATCH VALIDATION FUNCTIONS
// ============================================================================

export const validateGenomicVariants = (data: unknown[]): GenomicVariant[] => {
    const validVariants: GenomicVariant[] = [];
    const invalidVariants: unknown[] = [];

    data.forEach((item, index) => {
        if (validateGenomicVariant(item)) {
            validVariants.push(item);
        } else {
            invalidVariants.push({ item, index });
        }
    });

    if (invalidVariants.length > 0) {
        console.warn(`Validation: ${invalidVariants.length} invalid variants found and filtered out:`, invalidVariants);
    }

    return validVariants;
};

export const validateHealthRecommendations = (data: unknown[]): HealthRecommendation[] => {
    const validRecommendations: HealthRecommendation[] = [];
    const invalidRecommendations: unknown[] = [];

    data.forEach((item, index) => {
        if (validateHealthRecommendation(item)) {
            validRecommendations.push(item);
        } else {
            invalidRecommendations.push({ item, index });
        }
    });

    if (invalidRecommendations.length > 0) {
        console.warn(`Validation: ${invalidRecommendations.length} invalid recommendations found and filtered out:`, invalidRecommendations);
    }

    return validRecommendations;
};

export const validatePRSScores = (data: unknown[]): PRSScore[] => {
    const validScores: PRSScore[] = [];
    const invalidScores: unknown[] = [];

    data.forEach((item, index) => {
        if (validatePRSScore(item)) {
            validScores.push(item);
        } else {
            invalidScores.push({ item, index });
        }
    });

    if (invalidScores.length > 0) {
        console.warn(`Validation: ${invalidScores.length} invalid PRS scores found and filtered out:`, invalidScores);
    }

    return validScores;
};

// ============================================================================
// VALIDATION HELPERS
// ============================================================================

export const createValidationError = (message: string, field?: string, value?: unknown): Error => {
    const errorMessage = field
        ? `Validation error in field '${field}': ${message}${value !== undefined ? ` (value: ${JSON.stringify(value)})` : ''}`
        : `Validation error: ${message}`;

    const error = new Error(errorMessage);
    error.name = 'ValidationError';
    return error;
};

export const validateAndTransform = <T>(
    data: unknown,
    validator: (data: unknown) => data is T,
    transform?: (data: T) => T
): T => {
    if (!validator(data)) {
        throw createValidationError('Data validation failed');
    }

    if (transform) {
        return transform(data);
    }

    return data;
};

// ============================================================================
// SCHEMA VALIDATION
// ============================================================================

export interface ValidationSchema<T> {
    [K in keyof T]: (value: unknown) => boolean;
}

export const validateSchema = <T extends Record<string, unknown>>(
    data: unknown,
    schema: ValidationSchema<T>
): data is T => {
    if (typeof data !== 'object' || data === null) {
        return false;
    }

    const obj = data as Record<string, unknown>;

    for (const [key, validator] of Object.entries(schema)) {
        if (!validator(obj[key])) {
            console.warn(`Schema validation failed for field '${key}'`);
            return false;
        }
    }

    return true;
};
