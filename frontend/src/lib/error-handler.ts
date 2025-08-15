/**
 * Frontend Error Handling and Reporting System
 * Provides consistent error handling, user-friendly messages, and error reporting
 */

export interface ErrorResponse {
    error: boolean;
    error_id: string;
    message: string;
    status_code: number;
    details?: any;
}

export interface ErrorContext {
    component: string;
    action: string;
    user_id?: string;
    timestamp: string;
    url: string;
    user_agent: string;
}

export class CuraGenieError extends Error {
    public readonly errorId: string;
    public readonly statusCode: number;
    public readonly details?: any;
    public readonly context?: ErrorContext;

    constructor(
        message: string,
        errorId: string,
        statusCode: number = 500,
        details?: any,
        context?: ErrorContext
    ) {
        super(message);
        this.name = 'CuraGenieError';
        this.errorId = errorId;
        this.statusCode = statusCode;
        this.details = details;
        this.context = context;
    }
}

export class ValidationError extends CuraGenieError {
    constructor(message: string, details?: any, context?: ErrorContext) {
        super(message, 'VALIDATION_ERROR', 400, details, context);
        this.name = 'ValidationError';
    }
}

export class AuthenticationError extends CuraGenieError {
    constructor(message: string, details?: any, context?: ErrorContext) {
        super(message, 'AUTHENTICATION_ERROR', 401, details, context);
        this.name = 'AuthenticationError';
    }
}

export class ProcessingError extends CuraGenieError {
    constructor(message: string, details?: any, context?: ErrorContext) {
        super(message, 'PROCESSING_ERROR', 422, details, context);
        this.name = 'ProcessingError';
    }
}

export class NetworkError extends CuraGenieError {
    constructor(message: string, details?: any, context?: ErrorContext) {
        super(message, 'NETWORK_ERROR', 0, details, context);
        this.name = 'NetworkError';
    }
}

export class ErrorHandler {
    private static instance: ErrorHandler;
    private errorQueue: Array<{ error: Error; context: ErrorContext }> = [];
    private isReporting = false;

    private constructor() {
        this.setupGlobalErrorHandling();
    }

    public static getInstance(): ErrorHandler {
        if (!ErrorHandler.instance) {
            ErrorHandler.instance = new ErrorHandler();
        }
        return ErrorHandler.instance;
    }

    private setupGlobalErrorHandling(): void {
        // Handle unhandled promise rejections
        window.addEventListener('unhandledrejection', (event) => {
            this.handleError(event.reason, {
                component: 'global',
                action: 'unhandled_promise_rejection',
                timestamp: new Date().toISOString(),
                url: window.location.href,
                user_agent: navigator.userAgent,
            });
        });

        // Handle JavaScript errors
        window.addEventListener('error', (event) => {
            this.handleError(event.error || new Error(event.message), {
                component: 'global',
                action: 'javascript_error',
                timestamp: new Date().toISOString(),
                url: window.location.href,
                user_agent: navigator.userAgent,
            });
        });
    }

    public handleError(error: Error, context: ErrorContext): void {
        console.error('Error handled by CuraGenieErrorHandler:', error, context);

        // Add to error queue for reporting
        this.errorQueue.push({ error, context });

        // Show user-friendly error message
        this.showUserError(error, context);

        // Report error to backend (if configured)
        this.reportError(error, context);

        // Log error for debugging
        this.logError(error, context);
    }

    private showUserError(error: Error, context: ErrorContext): void {
        const message = this.getUserFriendlyMessage(error);

        // Use toast notification system if available
        if (typeof window !== 'undefined' && (window as any).showToast) {
            (window as any).showToast(message, 'error');
        } else {
            // Fallback to console and alert
            console.error('User Error:', message);
            if (process.env.NODE_ENV === 'development') {
                alert(`Error: ${message}`);
            }
        }
    }

    private getUserFriendlyMessage(error: Error): string {
        if (error instanceof CuraGenieError) {
            return error.message;
        }

        // Map common error types to user-friendly messages
        if (error.name === 'TypeError') {
            return 'An unexpected error occurred. Please refresh the page and try again.';
        }

        if (error.name === 'ReferenceError') {
            return 'A system error occurred. Please contact support if the problem persists.';
        }

        if (error.message.includes('fetch')) {
            return 'Unable to connect to the server. Please check your internet connection and try again.';
        }

        if (error.message.includes('timeout')) {
            return 'The request took too long to complete. Please try again.';
        }

        return 'An unexpected error occurred. Please try again or contact support.';
    }

    private async reportError(error: Error, context: ErrorContext): Promise<void> {
        if (this.isReporting) return;

        try {
            this.isReporting = true;

            // Report to backend error tracking endpoint
            await fetch('/api/errors/report', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    error: {
                        name: error.name,
                        message: error.message,
                        stack: error.stack,
                    },
                    context,
                    timestamp: new Date().toISOString(),
                }),
            });
        } catch (reportError) {
            console.error('Failed to report error:', reportError);
        } finally {
            this.isReporting = false;
        }
    }

    private logError(error: Error, context: ErrorContext): void {
        // Log to console with structured format
        console.group(`🚨 Error: ${error.name}`);
        console.error('Message:', error.message);
        console.error('Context:', context);
        if (error.stack) {
            console.error('Stack:', error.stack);
        }
        console.groupEnd();
    }

    public async handleApiError(response: Response, context: ErrorContext): Promise<never> {
        let errorData: ErrorResponse;

        try {
            errorData = await response.json();
        } catch {
            errorData = {
                error: true,
                error_id: 'UNKNOWN',
                message: `HTTP ${response.status}: ${response.statusText}`,
                status_code: response.status,
            };
        }

        // Create appropriate error type based on status code
        let error: CuraGenieError;

        switch (response.status) {
            case 400:
                error = new ValidationError(errorData.message, errorData.details, context);
                break;
            case 401:
                error = new AuthenticationError(errorData.message, errorData.details, context);
                break;
            case 422:
                error = new ProcessingError(errorData.message, errorData.details, context);
                break;
            case 500:
                error = new CuraGenieError(errorData.message, errorData.error_id, 500, errorData.details, context);
                break;
            default:
                error = new CuraGenieError(errorData.message, errorData.error_id, response.status, errorData.details, context);
        }

        throw error;
    }

    public createErrorBoundary(componentName: string) {
        return (error: Error, errorInfo: any) => {
            this.handleError(error, {
                component: componentName,
                action: 'react_error_boundary',
                timestamp: new Date().toISOString(),
                url: window.location.href,
                user_agent: navigator.userAgent,
            });
        };
    }

    public async retryOperation<T>(
        operation: () => Promise<T>,
        maxRetries: number = 3,
        delay: number = 1000
    ): Promise<T> {
        let lastError: Error;

        for (let attempt = 1; attempt <= maxRetries; attempt++) {
            try {
                return await operation();
            } catch (error) {
                lastError = error as Error;

                if (attempt === maxRetries) {
                    throw lastError;
                }

                // Wait before retry with exponential backoff
                await new Promise(resolve => setTimeout(resolve, delay * attempt));
            }
        }

        throw lastError!;
    }

    public getErrorQueue(): Array<{ error: Error; context: ErrorContext }> {
        return [...this.errorQueue];
    }

    public clearErrorQueue(): void {
        this.errorQueue = [];
    }
}

// Export singleton instance
export const errorHandler = ErrorHandler.getInstance();

// Utility functions for common error handling patterns
export const withErrorHandling = <T extends any[], R>(
    fn: (...args: T) => Promise<R>,
    component: string,
    action: string
) => {
    return async (...args: T): Promise<R> => {
        try {
            return await fn(...args);
        } catch (error) {
            errorHandler.handleError(error as Error, {
                component,
                action,
                timestamp: new Date().toISOString(),
                url: window.location.href,
                user_agent: navigator.userAgent,
            });
            throw error;
        }
    };
};

export const createErrorContext = (component: string, action: string): ErrorContext => ({
    component,
    action,
    timestamp: new Date().toISOString(),
    url: window.location.href,
    user_agent: navigator.userAgent,
});

// Error reporting utilities
export const reportUserAction = (action: string, success: boolean, details?: any): void => {
    if (process.env.NODE_ENV === 'development') {
        console.log(`User Action: ${action}`, { success, details });
    }

    // In production, this could send analytics or telemetry data
};

export const reportPerformanceIssue = (operation: string, duration: number, threshold: number = 1000): void => {
    if (duration > threshold) {
        console.warn(`Performance issue detected: ${operation} took ${duration}ms (threshold: ${threshold}ms)`);

        // Report to performance monitoring service
        if (typeof window !== 'undefined' && (window as any).reportPerformanceIssue) {
            (window as any).reportPerformanceIssue(operation, duration, threshold);
        }
    }
};
