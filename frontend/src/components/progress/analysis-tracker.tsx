'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import {
  CheckCircle,
  Clock,
  Upload,
  Brain,
  BarChart3,
  FileText,
  AlertCircle,
  Zap,
  Lightbulb,
  Activity,
  Target
} from 'lucide-react';
import { useTimer } from '@/lib/hooks/useTimer';
import { PROGRESS_INTERVALS } from '@/lib/constants/timing';

interface AnalysisStep {
  id: string;
  name: string;
  description: string;
  status: 'pending' | 'in-progress' | 'completed' | 'error';
  icon: React.ComponentType<any>;
  estimatedTime: string;
  details?: string;
}

interface AnalysisTrackerProps {
  uploadId?: string;
  isProcessing: boolean;
  onComplete?: () => void;
}

export function AnalysisTracker({ uploadId, isProcessing, onComplete }: AnalysisTrackerProps) {
  const { setTimeout, clearAllTimers } = useTimer();
  const [currentStep, setCurrentStep] = useState(0);
  const [steps, setSteps] = useState<AnalysisStep[]>([
    {
      id: 'upload',
      name: 'File Upload',
      description: 'Receiving and validating your genetic data file',
      status: 'completed',
      icon: Upload,
      estimatedTime: '~1 minute',
      details: 'VCF file successfully uploaded and validated'
    },
    {
      id: 'parsing',
      name: 'Data Processing',
      description: 'Parsing genetic variants and quality control',
      status: 'in-progress',
      icon: Activity,
      estimatedTime: '~3-5 minutes',
      details: 'Analyzing genetic variants and checking data quality'
    },
    {
      id: 'analysis',
      name: 'Risk Analysis',
      description: 'Calculating polygenic risk scores',
      status: 'pending',
      icon: Brain,
      estimatedTime: '~5-7 minutes',
      details: 'Running AI models to calculate health risk scores'
    },
    {
      id: 'recommendations',
      name: 'Generating Insights',
      description: 'Creating personalized health recommendations',
      status: 'pending',
      icon: Lightbulb,
      estimatedTime: '~2-3 minutes',
      details: 'AI is generating personalized health insights'
    },
    {
      id: 'reports',
      name: 'Finalizing Results',
      description: 'Preparing your comprehensive health report',
      status: 'pending',
      icon: FileText,
      estimatedTime: '~1-2 minutes',
      details: 'Creating downloadable reports and visualizations'
    }
  ]);

  // Simulate processing steps
  useEffect(() => {
    if (!isProcessing) return;

    // Step 2: Data Processing (2 seconds)
    setTimeout(() => {
      setSteps(prev => prev.map(step =>
        step.id === 'parsing'
          ? { ...step, status: 'completed' as const }
          : step.id === 'analysis'
            ? { ...step, status: 'in-progress' as const }
            : step
      ));
      setCurrentStep(2);
    }, PROGRESS_INTERVALS.FAST * 2);

    // Step 3: Risk Analysis (5 seconds)
    setTimeout(() => {
      setSteps(prev => prev.map(step =>
        step.id === 'analysis'
          ? { ...step, status: 'completed' as const }
          : step.id === 'recommendations'
            ? { ...step, status: 'in-progress' as const }
            : step
      ));
      setCurrentStep(3);
    }, PROGRESS_INTERVALS.FAST * 5);

    // Step 4: Generating Insights (8 seconds)
    setTimeout(() => {
      setSteps(prev => prev.map(step =>
        step.id === 'recommendations'
          ? { ...step, status: 'completed' as const }
          : step.id === 'reports'
            ? { ...step, status: 'in-progress' as const }
            : step
      ));
      setCurrentStep(4);
    }, PROGRESS_INTERVALS.FAST * 8);

    // Step 5: Complete (10 seconds)
    setTimeout(() => {
      setSteps(prev => prev.map(step =>
        step.id === 'reports'
          ? { ...step, status: 'completed' as const }
          : step
      ));
      setCurrentStep(5);
      onComplete?.();
    }, PROGRESS_INTERVALS.FAST * 10);

    return () => {
      clearAllTimers();
    };
  }, [isProcessing, onComplete, setTimeout, clearAllTimers]);

  const getStatusIcon = (status: AnalysisStep['status']) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-5 w-5 text-green-600" />;
      case 'in-progress':
        return <Clock className="h-5 w-5 text-blue-600 animate-pulse" />;
      case 'error':
        return <AlertCircle className="h-5 w-5 text-red-600" />;
      default:
        return <Clock className="h-5 w-5 text-gray-400" />;
    }
  };

  const getStatusColor = (status: AnalysisStep['status']) => {
    switch (status) {
      case 'completed':
        return 'text-green-600 bg-green-50 border-green-200';
      case 'in-progress':
        return 'text-blue-600 bg-blue-50 border-blue-200';
      case 'error':
        return 'text-red-600 bg-red-50 border-red-200';
      default:
        return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const completedSteps = steps.filter(step => step.status === 'completed').length;
  const progressPercentage = Math.round((completedSteps / steps.length) * 100);

  return (
    <Card className="w-full max-w-2xl">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Target className="h-5 w-5 text-blue-600" />
          Analysis Progress
        </CardTitle>
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span>Overall Progress</span>
            <span className="font-medium">{progressPercentage}% Complete</span>
          </div>
          <Progress value={progressPercentage} className="h-2" />
          <p className="text-sm text-gray-600">
            {completedSteps} of {steps.length} steps completed
          </p>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {steps.map((step, index) => {
          const IconComponent = step.icon;
          const isActive = step.status === 'in-progress';

          return (
            <div
              key={step.id}
              className={`p-4 rounded-lg border transition-all duration-300 ${isActive ? 'ring-2 ring-blue-200 shadow-sm' : ''
                } ${getStatusColor(step.status)}`}
            >
              <div className="flex items-start gap-4">
                <div className="flex-shrink-0">
                  <div className={`p-2 rounded-full ${step.status === 'completed' ? 'bg-green-100' :
                      step.status === 'in-progress' ? 'bg-blue-100' :
                        step.status === 'error' ? 'bg-red-100' :
                          'bg-gray-100'
                    }`}>
                    <IconComponent className={`h-4 w-4 ${step.status === 'completed' ? 'text-green-600' :
                        step.status === 'in-progress' ? 'text-blue-600' :
                          step.status === 'error' ? 'text-red-600' :
                            'text-gray-400'
                      }`} />
                  </div>
                </div>

                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between mb-1">
                    <h4 className="font-medium">{step.name}</h4>
                    <div className="flex items-center gap-2">
                      <Badge
                        variant="outline"
                        className={`text-xs ${getStatusColor(step.status)}`}
                      >
                        {step.status === 'in-progress' ? 'Processing...' :
                          step.status === 'completed' ? 'Complete' :
                            step.status === 'error' ? 'Error' : 'Pending'}
                      </Badge>
                      {getStatusIcon(step.status)}
                    </div>
                  </div>

                  <p className="text-sm text-gray-600 mb-2">{step.description}</p>

                  {step.status === 'in-progress' && (
                    <div className="bg-white/50 rounded p-2 text-xs">
                      <div className="flex items-center gap-2">
                        <Zap className="h-3 w-3 text-orange-500" />
                        <span className="text-gray-700">{step.details}</span>
                      </div>
                      <div className="flex items-center gap-2 mt-1 text-gray-500">
                        <Clock className="h-3 w-3" />
                        <span>Estimated time: {step.estimatedTime}</span>
                      </div>
                    </div>
                  )}

                  {step.status === 'completed' && step.details && (
                    <div className="bg-white/50 rounded p-2 text-xs text-green-700">
                      ✓ {step.details}
                    </div>
                  )}
                </div>
              </div>
            </div>
          );
        })}

        {/* Current Status Summary */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mt-6">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-100 rounded-full">
              {isProcessing ? (
                <Clock className="h-5 w-5 text-blue-600 animate-pulse" />
              ) : (
                <CheckCircle className="h-5 w-5 text-green-600" />
              )}
            </div>
            <div>
              <h4 className="font-medium text-blue-900">
                {isProcessing ? 'Analysis in Progress' : 'Analysis Complete!'}
              </h4>
              <p className="text-sm text-blue-800">
                {isProcessing
                  ? 'Please keep this page open while we process your genetic data. You can navigate to other sections if needed.'
                  : 'Your genomic analysis is complete! You can now view your results in the dashboard.'
                }
              </p>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
