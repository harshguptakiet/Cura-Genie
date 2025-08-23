/**
 * Environment-based logging utility for Cura-Genie
 * Provides structured logging with environment awareness
 */

export interface LogContext {
    userId?: string;
    operation: string;
    timestamp: string;
    metadata?: Record<string, unknown>;
    error?: Error;
}

export interface Logger {
    debug: (message: string, context?: Partial<LogContext>) => void;
    info: (message: string, context?: Partial<LogContext>) => void;
    warn: (message: string, context?: Partial<LogContext>) => void;
    error: (message: string, context?: Partial<LogContext>) => void;
}

class LoggerImpl implements Logger {
    private isDevelopment = process.env.NODE_ENV === 'development';
    private isProduction = process.env.NODE_ENV === 'production';

    private formatMessage(level: string, message: string, context?: Partial<LogContext>): string {
        const timestamp = new Date().toISOString();
        const baseMessage = `[${level.toUpperCase()}] ${timestamp} - ${message}`;

        if (!context || Object.keys(context).length === 0) {
            return baseMessage;
        }

        // Sanitize sensitive data
        const sanitizedContext = this.sanitizeContext(context);
        return `${baseMessage} | ${JSON.stringify(sanitizedContext, null, 2)}`;
    }

    private sanitizeContext(context: Partial<LogContext>): Partial<LogContext> {
        const sanitized = { ...context };

        // Remove sensitive fields
        if (sanitized.metadata) {
            const sensitiveKeys = ['password', 'token', 'access_token', 'refresh_token', 'secret'];
            sensitiveKeys.forEach(key => {
                if (sanitized.metadata && key in sanitized.metadata) {
                    sanitized.metadata[key] = '[REDACTED]';
                }
            });
        }

        // Sanitize error objects
        if (sanitized.error) {
            sanitized.error = {
                name: sanitized.error.name,
                message: sanitized.error.message,
                stack: this.isDevelopment ? sanitized.error.stack : undefined
            } as Error;
        }

        return sanitized;
    }

    debug(message: string, context?: Partial<LogContext>): void {
        if (this.isDevelopment) {
            console.log(this.formatMessage('DEBUG', message, context));
        }
    }

    info(message: string, context?: Partial<LogContext>): void {
        if (this.isDevelopment) {
            console.info(this.formatMessage('INFO', message, context));
        }
    }

    warn(message: string, context?: Partial<LogContext>): void {
        if (this.isDevelopment) {
            console.warn(this.formatMessage('WARN', message, context));
        }
    }

    error(message: string, context?: Partial<LogContext>): void {
        // Always log errors, but with proper formatting
        const formattedMessage = this.formatMessage('ERROR', message, context);

        if (this.isDevelopment) {
            console.error(formattedMessage);
        } else {
            // In production, log to console but could also send to error tracking service
            console.error(formattedMessage);

            // TODO: Integrate with error tracking service (e.g., Sentry) in production
            // if (this.isProduction && context?.error) {
            //   // Send to error tracking service
            // }
        }
    }

    // Helper method for operation logging
    logOperation(level: 'debug' | 'info' | 'warn' | 'error', message: string, context: Partial<LogContext>): void {
        const logContext: LogContext = {
            ...context,
            timestamp: new Date().toISOString()
        };

        this[level](message, logContext);
    }
}

// Create singleton instance
export const logger = new LoggerImpl();

// Convenience functions for common logging patterns
export const logAuth = (level: 'debug' | 'info' | 'warn' | 'error', message: string, userId?: string, metadata?: Record<string, unknown>) => {
    logger.logOperation(level, message, {
        operation: 'authentication',
        userId,
        metadata
    });
};

export const logApi = (level: 'debug' | 'info' | 'warn' | 'error', message: string, endpoint?: string, metadata?: Record<string, unknown>) => {
    logger.logOperation(level, message, {
        operation: 'api_call',
        metadata: {
            endpoint,
            ...metadata
        }
    });
};

export const logUpload = (level: 'debug' | 'info' | 'warn' | 'error', message: string, fileType?: string, metadata?: Record<string, unknown>) => {
    logger.logOperation(level, message, {
        operation: 'file_upload',
        metadata: {
            fileType,
            ...metadata
        }
    });
};

export const logAnalysis = (level: 'debug' | 'info' | 'warn' | 'error', message: string, analysisType?: string, metadata?: Record<string, unknown>) => {
    logger.logOperation(level, message, {
        operation: 'analysis',
        metadata: {
            analysisType,
            ...metadata
        }
    });
};

// Export default logger instance
export default logger;
