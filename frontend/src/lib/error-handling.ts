// Comprehensive Error Handling Utilities for Cura-Genie Frontend
// Provides standardized error handling patterns and error creation

import { AppError, ErrorCode } from '@/types';

// ============================================================================
// ERROR CREATION UTILITIES
// ============================================================================

export const createAppError = (
    message: string,
    code: ErrorCode = 'UNKNOWN_ERROR',
    originalError?: unknown,
    context?: Record<string, unknown>
): AppError => {
    const error = new Error(message) as AppError;
    error.code = code;
    error.context = context || {};
    error.timestamp = new Date().toISOString();

    // Preserve original error information if available
    if (originalError instanceof Error) {
        error.name = originalError.name;
        error.stack = originalError.stack;
        error.context.originalError = {
            name: originalError.name,
            message: originalError.message,
            stack: originalError.stack
        };
    } else if (originalError) {
        error.context.originalError = originalError;
    }

    return error;
};

export const createUploadError = (
    message: string,
    originalError?: unknown,
    context?: Record<string, unknown>
): AppError => {
    return createAppError(message, 'UPLOAD_FAILED', originalError, context);
};

export const createProcessingError = (
    message: string,
    originalError?: unknown,
    context?: Record<string, unknown>
): AppError => {
    return createAppError(message, 'PROCESSING_ERROR', originalError, context);
};

export const createNetworkError = (
    message: string,
    originalError?: unknown,
    context?: Record<string, unknown>
): AppError => {
    return createAppError(message, 'NETWORK_ERROR', originalError, context);
};

export const createValidationError = (
    message: string,
    originalError?: unknown,
    context?: Record<string, unknown>
): AppError => {
    return createAppError(message, 'VALIDATION_ERROR', originalError, context);
};

// ============================================================================
// ERROR HANDLING UTILITIES
// ============================================================================

export const handleError = (error: unknown): AppError => {
    if (error instanceof Error) {
        // If it's already an AppError, return it
        if ('code' in error && 'timestamp' in error) {
            return error as AppError;
        }

        // Convert regular Error to AppError
        return createAppError(
            error.message,
            'UNKNOWN_ERROR',
            error,
            { originalName: error.name }
        );
    }

    // Handle non-Error objects
    if (typeof error === 'string') {
        return createAppError(error, 'UNKNOWN_ERROR', error);
    }

    if (typeof error === 'object' && error !== null) {
        return createAppError(
            'An unknown error occurred',
            'UNKNOWN_ERROR',
            error,
            { originalError: error }
        );
    }

    // Fallback for primitive types
    return createAppError(
        'An unknown error occurred',
        'UNKNOWN_ERROR',
        error,
        { originalValue: error }
    );
};

export const handleAsyncError = async <T>(
    asyncFn: () => Promise<T>,
    errorHandler?: (error: AppError) => void
): Promise<T | null> => {
    try {
        return await asyncFn();
    } catch (error) {
        const appError = handleError(error);

        if (errorHandler) {
            errorHandler(appError);
        }

        console.error('Async operation failed:', appError);
        return null;
    }
};

// ============================================================================
// ERROR CLASSIFICATION UTILITIES
// ============================================================================

export const isNetworkError = (error: AppError): boolean => {
    return error.code === 'NETWORK_ERROR' ||
        error.message.includes('fetch') ||
        error.message.includes('network') ||
        error.message.includes('timeout');
};

export const isValidationError = (error: AppError): boolean => {
    return error.code === 'VALIDATION_ERROR' ||
        error.message.includes('validation') ||
        error.message.includes('invalid');
};

export const isAuthenticationError = (error: AppError): boolean => {
    return error.code === 'AUTHENTICATION_ERROR' ||
        error.message.includes('401') ||
        error.message.includes('unauthorized') ||
        error.message.includes('authentication');
};

export const isPermissionError = (error: AppError): boolean => {
    return error.code === 'PERMISSION_DENIED' ||
        error.message.includes('403') ||
        error.message.includes('forbidden') ||
        error.message.includes('permission');
};

export const isResourceNotFoundError = (error: AppError): boolean => {
    return error.code === 'RESOURCE_NOT_FOUND' ||
        error.message.includes('404') ||
        error.message.includes('not found') ||
        error.message.includes('no data');
};

// ============================================================================
// USER-FRIENDLY ERROR MESSAGES
// ============================================================================

export const getUserFriendlyMessage = (error: AppError): string => {
    switch (error.code) {
        case 'UPLOAD_FAILED':
            return 'File upload failed. Please check your file and try again.';

        case 'PROCESSING_ERROR':
            return 'Data processing failed. Please try again later.';

        case 'NETWORK_ERROR':
            return 'Network connection issue. Please check your internet connection and try again.';

        case 'VALIDATION_ERROR':
            return 'Invalid data provided. Please check your input and try again.';

        case 'AUTHENTICATION_ERROR':
            return 'Authentication failed. Please log in again.';

        case 'PERMISSION_DENIED':
            return 'Access denied. You don\'t have permission to perform this action.';

        case 'RESOURCE_NOT_FOUND':
            return 'The requested resource was not found.';

        case 'UNKNOWN_ERROR':
        default:
            return 'An unexpected error occurred. Please try again later.';
    }
};

export const getErrorActionSuggestion = (error: AppError): string | null => {
    switch (error.code) {
        case 'UPLOAD_FAILED':
            return 'Try uploading a smaller file or check the file format.';

        case 'NETWORK_ERROR':
            return 'Check your internet connection and try again.';

        case 'AUTHENTICATION_ERROR':
            return 'Try logging out and logging back in.';

        case 'VALIDATION_ERROR':
            return 'Check your input and ensure all required fields are filled.';

        default:
            return null;
    }
};

// ============================================================================
// ERROR LOGGING UTILITIES
// ============================================================================

export const logError = (error: AppError, context?: string): void => {
    const logData = {
        timestamp: error.timestamp,
        code: error.code,
        message: error.message,
        name: error.name,
        context: context || 'unknown',
        stack: error.stack,
        additionalContext: error.context
    };

    console.error('Application Error:', logData);

    // In production, you might want to send this to an error tracking service
    // like Sentry, LogRocket, or your own error logging endpoint
    if (process.env.NODE_ENV === 'production') {
        // Example: sendToErrorTrackingService(logData);
        console.warn('Error logging to external service would happen here in production');
    }
};

export const logErrorWithContext = (
    error: unknown,
    operation: string,
    additionalContext?: Record<string, unknown>
): AppError => {
    const appError = handleError(error);
    appError.context = {
        ...appError.context,
        operation,
        ...additionalContext
    };

    logError(appError, operation);
    return appError;
};
