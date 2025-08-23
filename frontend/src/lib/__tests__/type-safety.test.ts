// Type Safety Tests for Cura-Genie Frontend
// Tests all the type safety improvements and validation functions

import {
    isUploadSuccessData,
    isGenomicVariant,
    isHealthRecommendation,
    isPRSScore,
    UploadSuccessData,
    GenomicVariant,
    HealthRecommendation,
    PRSScore,
    VCFUploadResult
} from '@/types';

import {
    handleError,
    createAppError,
    createUploadError,
    getUserFriendlyMessage,
    isNetworkError,
    isValidationError
} from '@/lib/error-handling';

import {
    validateGenomicVariant,
    validateHealthRecommendation,
    validatePRSScore,
    validateUploadSuccessData,
    validateVCFUploadResult,
    validateGenomicVariants,
    validateHealthRecommendations,
    validatePRSScores
} from '@/lib/validation';

// ============================================================================
// TYPE GUARD TESTS
// ============================================================================

describe('Type Guards', () => {
    describe('isUploadSuccessData', () => {
        it('should return true for valid UploadSuccessData', () => {
            const validData: UploadSuccessData = {
                file_id: 'test-123',
                file_name: 'test.vcf',
                file_size: 1024,
                upload_date: '2024-01-01T00:00:00Z',
                processing_status: 'completed'
            };

            expect(isUploadSuccessData(validData)).toBe(true);
        });

        it('should return false for invalid data', () => {
            const invalidData = {
                file_id: 'test-123',
                // missing required fields
            };

            expect(isUploadSuccessData(invalidData)).toBe(false);
        });

        it('should return false for null/undefined', () => {
            expect(isUploadSuccessData(null)).toBe(false);
            expect(isUploadSuccessData(undefined)).toBe(false);
        });
    });

    describe('isGenomicVariant', () => {
        it('should return true for valid GenomicVariant', () => {
            const validVariant: GenomicVariant = {
                variant_id: 'rs123456',
                chromosome: '1',
                position: 1000000,
                reference: 'A',
                alternative: 'T',
                quality: 99.9,
                filter: 'PASS',
                variant_type: 'SNP',
                info: { 'AF': 0.1 }
            };

            expect(isGenomicVariant(validVariant)).toBe(true);
        });

        it('should return false for invalid data', () => {
            const invalidVariant = {
                variant_id: 'rs123456',
                // missing required fields
            };

            expect(isGenomicVariant(invalidVariant)).toBe(false);
        });
    });

    describe('isHealthRecommendation', () => {
        it('should return true for valid HealthRecommendation', () => {
            const validRecommendation: HealthRecommendation = {
                id: 'rec-123',
                title: 'Test Recommendation',
                description: 'This is a test recommendation',
                category: 'lifestyle',
                priority: 'high',
                basedOn: ['genetic data'],
                actionItems: ['action 1'],
                evidence_level: 'strong',
                created_at: '2024-01-01T00:00:00Z',
                updated_at: '2024-01-01T00:00:00Z'
            };

            expect(isHealthRecommendation(validRecommendation)).toBe(true);
        });
    });

    describe('isPRSScore', () => {
        it('should return true for valid PRSScore', () => {
            const validScore: PRSScore = {
                id: 'prs-123',
                disease_name: 'Diabetes',
                risk_score: 75.5,
                risk_percentage: 75.5,
                risk_category: 'high',
                confidence_interval: [70, 80],
                population_percentile: 85,
                genetic_markers_count: 100,
                last_updated: '2024-01-01T00:00:00Z'
            };

            expect(isPRSScore(validScore)).toBe(true);
        });
    });
});

// ============================================================================
// ERROR HANDLING TESTS
// ============================================================================

describe('Error Handling', () => {
    describe('createAppError', () => {
        it('should create an AppError with correct properties', () => {
            const error = createAppError('Test error', 'UPLOAD_FAILED');

            expect(error).toBeInstanceOf(Error);
            expect(error.message).toBe('Test error');
            expect(error.code).toBe('UPLOAD_FAILED');
            expect(error.timestamp).toBeDefined();
            expect(error.context).toEqual({});
        });

        it('should preserve original error information', () => {
            const originalError = new Error('Original error');
            const appError = createAppError('Wrapped error', 'PROCESSING_ERROR', originalError);

            expect(appError.name).toBe('Original error');
            expect(appError.stack).toBe(originalError.stack);
            expect(appError.context.originalError).toBeDefined();
        });
    });

    describe('handleError', () => {
        it('should convert regular Error to AppError', () => {
            const regularError = new Error('Regular error');
            const appError = handleError(regularError);

            expect(appError).toBeInstanceOf(Error);
            expect(appError.code).toBe('UNKNOWN_ERROR');
            expect(appError.timestamp).toBeDefined();
        });

        it('should handle string errors', () => {
            const stringError = 'String error';
            const appError = handleError(stringError);

            expect(appError.message).toBe('String error');
            expect(appError.code).toBe('UNKNOWN_ERROR');
        });

        it('should handle object errors', () => {
            const objectError = { message: 'Object error' };
            const appError = handleError(objectError);

            expect(appError.message).toBe('An unknown error occurred');
            expect(appError.context.originalError).toEqual(objectError);
        });
    });

    describe('getUserFriendlyMessage', () => {
        it('should return user-friendly messages for different error codes', () => {
            const uploadError = createAppError('Upload failed', 'UPLOAD_FAILED');
            const networkError = createAppError('Network error', 'NETWORK_ERROR');

            expect(getUserFriendlyMessage(uploadError)).toBe('File upload failed. Please check your file and try again.');
            expect(getUserFriendlyMessage(networkError)).toBe('Network connection issue. Please check your internet connection and try again.');
        });
    });

    describe('Error Classification', () => {
        it('should correctly classify network errors', () => {
            const networkError = createAppError('Network timeout', 'NETWORK_ERROR');
            const uploadError = createAppError('Upload failed', 'UPLOAD_FAILED');

            expect(isNetworkError(networkError)).toBe(true);
            expect(isNetworkError(uploadError)).toBe(false);
        });

        it('should correctly classify validation errors', () => {
            const validationError = createAppError('Invalid input', 'VALIDATION_ERROR');
            const uploadError = createAppError('Upload failed', 'UPLOAD_FAILED');

            expect(isValidationError(validationError)).toBe(true);
            expect(isValidationError(uploadError)).toBe(false);
        });
    });
});

// ============================================================================
// VALIDATION TESTS
// ============================================================================

describe('Validation Functions', () => {
    describe('validateGenomicVariant', () => {
        it('should validate correct GenomicVariant data', () => {
            const validVariant: GenomicVariant = {
                variant_id: 'rs123456',
                chromosome: '1',
                position: 1000000,
                reference: 'A',
                alternative: 'T',
                quality: 99.9,
                filter: 'PASS',
                variant_type: 'SNP',
                info: { 'AF': 0.1 }
            };

            expect(validateGenomicVariant(validVariant)).toBe(true);
        });

        it('should reject invalid GenomicVariant data', () => {
            const invalidVariant = {
                variant_id: '', // Empty string
                chromosome: '1',
                position: 1000000,
                reference: 'A',
                alternative: 'T',
                quality: 99.9,
                filter: 'PASS',
                variant_type: 'SNP',
                info: { 'AF': 0.1 }
            };

            expect(validateGenomicVariant(invalidVariant)).toBe(false);
        });
    });

    describe('validateHealthRecommendation', () => {
        it('should validate correct HealthRecommendation data', () => {
            const validRecommendation: HealthRecommendation = {
                id: 'rec-123',
                title: 'Test Recommendation',
                description: 'This is a test recommendation',
                category: 'lifestyle',
                priority: 'high',
                basedOn: ['genetic data'],
                actionItems: ['action 1'],
                evidence_level: 'strong',
                created_at: '2024-01-01T00:00:00Z',
                updated_at: '2024-01-01T00:00:00Z'
            };

            expect(validateHealthRecommendation(validRecommendation)).toBe(true);
        });
    });

    describe('validatePRSScore', () => {
        it('should validate correct PRSScore data', () => {
            const validScore: PRSScore = {
                id: 'prs-123',
                disease_name: 'Diabetes',
                risk_score: 75.5,
                risk_percentage: 75.5,
                risk_category: 'high',
                confidence_interval: [70, 80],
                population_percentile: 85,
                genetic_markers_count: 100,
                last_updated: '2024-01-01T00:00:00Z'
            };

            expect(validatePRSScore(validScore)).toBe(true);
        });

        it('should reject PRSScore with invalid risk percentage', () => {
            const invalidScore = {
                id: 'prs-123',
                disease_name: 'Diabetes',
                risk_score: 75.5,
                risk_percentage: 150, // Invalid: > 100
                risk_category: 'high',
                confidence_interval: [70, 80],
                population_percentile: 85,
                genetic_markers_count: 100,
                last_updated: '2024-01-01T00:00:00Z'
            };

            expect(validatePRSScore(invalidScore)).toBe(false);
        });
    });

    describe('validateUploadSuccessData', () => {
        it('should validate correct UploadSuccessData', () => {
            const validData: UploadSuccessData = {
                file_id: 'test-123',
                file_name: 'test.vcf',
                file_size: 1024,
                upload_date: '2024-01-01T00:00:00Z',
                processing_status: 'completed'
            };

            expect(validateUploadSuccessData(validData)).toBe(true);
        });
    });

    describe('validateVCFUploadResult', () => {
        it('should validate correct VCFUploadResult', () => {
            const validResult: VCFUploadResult = {
                path: '/path/to/file.vcf',
                file_id: 'test-123',
                upload_status: 'success'
            };

            expect(validateVCFUploadResult(validResult)).toBe(true);
        });

        it('should reject invalid upload status', () => {
            const invalidResult = {
                path: '/path/to/file.vcf',
                file_id: 'test-123',
                upload_status: 'invalid_status' // Invalid status
            };

            expect(validateVCFUploadResult(invalidResult)).toBe(false);
        });
    });

    describe('Batch Validation', () => {
        it('should filter out invalid items and return valid ones', () => {
            const mixedData = [
                { variant_id: 'rs123', chromosome: '1', position: 1000000, reference: 'A', alternative: 'T', quality: 99, filter: 'PASS', variant_type: 'SNP', info: {} },
                { variant_id: '', chromosome: '1', position: 1000000, reference: 'A', alternative: 'T', quality: 99, filter: 'PASS', variant_type: 'SNP', info: {} }, // Invalid
                { variant_id: 'rs456', chromosome: '2', position: 2000000, reference: 'C', alternative: 'G', quality: 98, filter: 'PASS', variant_type: 'SNP', info: {} }
            ];

            const validVariants = validateGenomicVariants(mixedData);

            expect(validVariants).toHaveLength(2);
            expect(validVariants[0].variant_id).toBe('rs123');
            expect(validVariants[1].variant_id).toBe('rs456');
        });
    });
});

// ============================================================================
// INTEGRATION TESTS
// ============================================================================

describe('Type Safety Integration', () => {
    it('should provide end-to-end type safety for data flow', () => {
        // Simulate data coming from API
        const apiResponse = {
            data: [
                {
                    variant_id: 'rs123456',
                    chromosome: '1',
                    position: 1000000,
                    reference: 'A',
                    alternative: 'T',
                    quality: 99.9,
                    filter: 'PASS',
                    variant_type: 'SNP',
                    info: { 'AF': 0.1 }
                }
            ]
        };

        // Type guard should work
        expect(isGenomicVariant(apiResponse.data[0])).toBe(true);

        // Validation should work
        expect(validateGenomicVariant(apiResponse.data[0])).toBe(true);

        // Batch validation should work
        const validVariants = validateGenomicVariants(apiResponse.data);
        expect(validVariants).toHaveLength(1);
        expect(validVariants[0].variant_id).toBe('rs123456');
    });

    it('should handle error scenarios gracefully', () => {
        // Simulate an error
        const error = new Error('API request failed');
        const appError = handleError(error);

        // Should be properly typed
        expect(appError.code).toBeDefined();
        expect(appError.timestamp).toBeDefined();

        // Should provide user-friendly message
        const userMessage = getUserFriendlyMessage(appError);
        expect(typeof userMessage).toBe('string');
        expect(userMessage.length).toBeGreaterThan(0);
    });
});
