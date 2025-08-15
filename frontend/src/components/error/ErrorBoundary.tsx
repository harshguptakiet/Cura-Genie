'use client';

import React, { Component, ErrorInfo, ReactNode } from 'react';
import { errorHandler } from '@/lib/error-handler';

interface Props {
    children: ReactNode;
    fallback?: ReactNode;
    onError?: (error: Error, errorInfo: ErrorInfo) => void;
    componentName?: string;
}

interface State {
    hasError: boolean;
    error?: Error;
    errorInfo?: ErrorInfo;
}

export class ErrorBoundary extends Component<Props, State> {
    constructor(props: Props) {
        super(props);
        this.state = { hasError: false };
    }

    static getDerivedStateFromError(error: Error): State {
        return { hasError: true, error };
    }

    componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
        // Log error to our error handler
        const componentName = this.props.componentName || 'UnknownComponent';
        errorHandler.handleError(error, {
            component: componentName,
            action: 'react_error_boundary',
            timestamp: new Date().toISOString(),
            url: typeof window !== 'undefined' ? window.location.href : '',
            user_agent: typeof navigator !== 'undefined' ? navigator.userAgent : '',
        });

        // Call custom error handler if provided
        if (this.props.onError) {
            this.props.onError(error, errorInfo);
        }

        // Update state
        this.setState({
            error,
            errorInfo,
        });
    }

    render(): ReactNode {
        if (this.state.hasError) {
            if (this.props.fallback) {
                return this.props.fallback;
            }

            return (
                <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
                    <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-6">
                        <div className="flex items-center justify-center w-16 h-16 mx-auto mb-4 bg-red-100 rounded-full">
                            <svg
                                className="w-8 h-8 text-red-600"
                                fill="none"
                                stroke="currentColor"
                                viewBox="0 0 24 24"
                            >
                                <path
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    strokeWidth={2}
                                    d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"
                                />
                            </svg>
                        </div>

                        <div className="text-center">
                            <h2 className="text-xl font-semibold text-gray-900 mb-2">
                                Something went wrong
                            </h2>
                            <p className="text-gray-600 mb-6">
                                We're sorry, but something unexpected happened. Our team has been notified.
                            </p>

                            <div className="space-y-3">
                                <button
                                    onClick={() => window.location.reload()}
                                    className="w-full bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors"
                                >
                                    Refresh Page
                                </button>

                                <button
                                    onClick={() => this.setState({ hasError: false, error: undefined, errorInfo: undefined })}
                                    className="w-full bg-gray-200 text-gray-800 px-4 py-2 rounded-md hover:bg-gray-300 transition-colors"
                                >
                                    Try Again
                                </button>

                                <button
                                    onClick={() => window.history.back()}
                                    className="w-full bg-gray-200 text-gray-800 px-4 py-2 rounded-md hover:bg-gray-300 transition-colors"
                                >
                                    Go Back
                                </button>
                            </div>

                            {process.env.NODE_ENV === 'development' && this.state.error && (
                                <details className="mt-6 text-left">
                                    <summary className="cursor-pointer text-sm text-gray-500 hover:text-gray-700">
                                        Show Error Details (Development)
                                    </summary>
                                    <div className="mt-2 p-3 bg-gray-100 rounded text-xs font-mono text-gray-800 overflow-auto">
                                        <div className="mb-2">
                                            <strong>Error:</strong> {this.state.error.toString()}
                                        </div>
                                        {this.state.errorInfo && (
                                            <div>
                                                <strong>Component Stack:</strong>
                                                <pre className="whitespace-pre-wrap mt-1">
                                                    {this.state.errorInfo.componentStack}
                                                </pre>
                                            </div>
                                        )}
                                    </div>
                                </details>
                            )}
                        </div>
                    </div>
                </div>
            );
        }

        return this.props.children;
    }
}

// Higher-order component for wrapping components with error boundaries
export function withErrorBoundary<P extends object>(
    Component: React.ComponentType<P>,
    componentName?: string,
    fallback?: ReactNode
) {
    const WrappedComponent = (props: P) => (
        <ErrorBoundary componentName={componentName} fallback={fallback}>
            <Component {...props} />
        </ErrorBoundary>
    );

    WrappedComponent.displayName = `withErrorBoundary(${Component.displayName || Component.name})`;
    return WrappedComponent;
}

// Hook for handling errors in functional components
export function useErrorHandler() {
    const handleError = React.useCallback((error: Error, context: any) => {
        errorHandler.handleError(error, {
            component: 'FunctionalComponent',
            action: 'useErrorHandler',
            timestamp: new Date().toISOString(),
            url: typeof window !== 'undefined' ? window.location.href : '',
            user_agent: typeof navigator !== 'undefined' ? navigator.userAgent : '',
            ...context,
        });
    }, []);

    return { handleError };
}

// Error display component for showing errors inline
export function ErrorDisplay({
    error,
    className = "",
    showDetails = false
}: {
    error: Error;
    className?: string;
    showDetails?: boolean;
}) {
    return (
        <div className={`bg-red-50 border border-red-200 rounded-md p-4 ${className}`}>
            <div className="flex">
                <div className="flex-shrink-0">
                    <svg
                        className="h-5 w-5 text-red-400"
                        viewBox="0 0 20 20"
                        fill="currentColor"
                    >
                        <path
                            fillRule="evenodd"
                            d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                            clipRule="evenodd"
                        />
                    </svg>
                </div>
                <div className="ml-3">
                    <h3 className="text-sm font-medium text-red-800">
                        An error occurred
                    </h3>
                    <div className="mt-2 text-sm text-red-700">
                        <p>{error.message}</p>
                        {showDetails && error.stack && (
                            <details className="mt-2">
                                <summary className="cursor-pointer text-xs text-red-600 hover:text-red-800">
                                    Show stack trace
                                </summary>
                                <pre className="mt-1 text-xs text-red-600 whitespace-pre-wrap overflow-auto">
                                    {error.stack}
                                </pre>
                            </details>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}
