'use client';

import React, { useState } from 'react';
import { errorHandler } from '@/lib/error-handler';
import { useToast } from '@/components/ui/toast-notifications';

interface ErrorReporterProps {
  error?: Error;
  className?: string;
  showDetails?: boolean;
  onReport?: (error: Error, details: string) => void;
}

export function ErrorReporter({ 
  error, 
  className = "", 
  showDetails = false,
  onReport 
}: ErrorReporterProps) {
  const [isReporting, setIsReporting] = useState(false);
  const [userDetails, setUserDetails] = useState('');
  const [showForm, setShowForm] = useState(false);
  const { showSuccess, showError } = useToast();

  const handleReportError = async () => {
    if (!error || !userDetails.trim()) return;

    setIsReporting(true);
    try {
      // Report to our error handler
      errorHandler.handleError(error, {
        component: 'ErrorReporter',
        action: 'user_error_report',
        timestamp: new Date().toISOString(),
        url: typeof window !== 'undefined' ? window.location.href : '',
        user_agent: typeof navigator !== 'undefined' ? navigator.userAgent : '',
      });

      // Call custom report handler if provided
      if (onReport) {
        onReport(error, userDetails);
      }

      showSuccess('Error Reported', 'Thank you for reporting this issue. Our team will investigate.');
      setShowForm(false);
      setUserDetails('');
    } catch (reportError) {
      showError('Report Failed', 'Failed to report the error. Please try again.');
    } finally {
      setIsReporting(false);
    }
  };

  const copyErrorDetails = () => {
    if (!error) return;

    const errorDetails = `
Error: ${error.name}
Message: ${error.message}
Stack: ${error.stack || 'No stack trace available'}
URL: ${typeof window !== 'undefined' ? window.location.href : 'Unknown'}
User Agent: ${typeof navigator !== 'undefined' ? navigator.userAgent : 'Unknown'}
Timestamp: ${new Date().toISOString()}
    `.trim();

    navigator.clipboard.writeText(errorDetails).then(() => {
      showSuccess('Copied', 'Error details copied to clipboard');
    }).catch(() => {
      showError('Copy Failed', 'Failed to copy error details');
    });
  };

  if (!error) return null;

  return (
    <div className={`bg-red-50 border border-red-200 rounded-lg p-4 ${className}`}>
      <div className="flex items-start">
        <div className="flex-shrink-0">
          <svg className="w-5 h-5 text-red-400" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
          </svg>
        </div>
        
        <div className="ml-3 flex-1">
          <h3 className="text-sm font-medium text-red-800">
            An error occurred
          </h3>
          
          <div className="mt-2 text-sm text-red-700">
            <p className="mb-2">{error.message}</p>
            
            {showDetails && error.stack && (
              <details className="mt-2">
                <summary className="cursor-pointer text-xs text-red-600 hover:text-red-800 font-medium">
                  Show technical details
                </summary>
                <pre className="mt-2 text-xs text-red-600 whitespace-pre-wrap overflow-auto bg-red-100 p-2 rounded">
                  {error.stack}
                </pre>
              </details>
            )}
          </div>

          <div className="mt-4 flex flex-wrap gap-2">
            <button
              onClick={() => setShowForm(!showForm)}
              className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-red-700 bg-red-100 hover:bg-red-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 transition-colors"
            >
              {showForm ? 'Cancel Report' : 'Report This Error'}
            </button>
            
            <button
              onClick={copyErrorDetails}
              className="inline-flex items-center px-3 py-2 border border-gray-300 text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
            >
              Copy Details
            </button>
            
            <button
              onClick={() => window.location.reload()}
              className="inline-flex items-center px-3 py-2 border border-gray-300 text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
            >
              Refresh Page
            </button>
          </div>

          {showForm && (
            <div className="mt-4 p-4 bg-white rounded-lg border border-red-200">
              <h4 className="text-sm font-medium text-gray-900 mb-2">
                Help us fix this error
              </h4>
              
              <p className="text-sm text-gray-600 mb-3">
                Please describe what you were doing when this error occurred. This helps our team understand and fix the issue.
              </p>
              
              <textarea
                value={userDetails}
                onChange={(e) => setUserDetails(e.target.value)}
                placeholder="Describe what you were doing when the error occurred..."
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
                rows={3}
                disabled={isReporting}
              />
              
              <div className="mt-3 flex justify-end">
                <button
                  onClick={handleReportError}
                  disabled={isReporting || !userDetails.trim()}
                  className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  {isReporting ? 'Reporting...' : 'Submit Report'}
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// Standalone error reporter for use in error boundaries
export function StandaloneErrorReporter({ error }: { error: Error }) {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
      <div className="max-w-2xl w-full">
        <div className="bg-white rounded-lg shadow-lg p-6">
          <div className="text-center mb-6">
            <div className="flex items-center justify-center w-16 h-16 mx-auto mb-4 bg-red-100 rounded-full">
              <svg className="w-8 h-8 text-red-600" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
            </div>
            
            <h1 className="text-2xl font-bold text-gray-900 mb-2">
              Something went wrong
            </h1>
            
            <p className="text-gray-600">
              We're sorry, but something unexpected happened. Please report this error so we can fix it.
            </p>
          </div>
          
          <ErrorReporter 
            error={error} 
            showDetails={process.env.NODE_ENV === 'development'}
            className="mb-6"
          />
          
          <div className="text-center">
            <p className="text-sm text-gray-500">
              If this problem persists, please contact our support team.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
