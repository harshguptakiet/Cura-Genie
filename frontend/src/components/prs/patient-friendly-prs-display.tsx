'use client';

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import {
  TrendingUp,
  TrendingDown,
  Heart,
  Info,
  AlertTriangle,
  CheckCircle,
  Users,
  Lightbulb,
  ArrowRight
} from 'lucide-react';

// Updated interface to match the main PRS component
interface PrsScore {
  id: string;
  condition: string;
  score: number;
  percentile: number;
  riskLevel: 'low' | 'moderate' | 'high';
  description?: string;
  calculatedAt?: string;
  variantsUsed?: number;
  confidence?: number;
}

interface PatientFriendlyPrsDisplayProps {
  scores: PrsScore[];
  isLoading?: boolean;
}

const getRiskExplanation = (disease: string, score: number, percentile: number, riskLevel: string) => {
  const explanations = {
    low: {
      color: 'text-green-600',
      bgColor: 'bg-green-50',
      borderColor: 'border-green-200',
      icon: CheckCircle,
      title: 'Lower Risk',
      description: `Your genetic makeup suggests you have a lower chance of developing ${disease} compared to most people.`,
      meaning: `This means your risk is below average based on the genetic variants we analyzed.`,
      action: 'Continue with regular health checkups and maintain healthy lifestyle habits.'
    },
    moderate: {
      color: 'text-yellow-600',
      bgColor: 'bg-yellow-50',
      borderColor: 'border-yellow-200',
      icon: Info,
      title: 'Average Risk',
      description: `Your genetic risk for ${disease} is around the population average.`,
      meaning: `Many factors beyond genetics affect your actual risk, including lifestyle and environment.`,
      action: 'Focus on preventive measures and discuss screening with your healthcare provider.'
    },
    high: {
      color: 'text-red-600',
      bgColor: 'bg-red-50',
      borderColor: 'border-red-200',
      icon: AlertTriangle,
      title: 'Higher Risk',
      description: `Your genetic makeup suggests a higher chance of developing ${disease}, but this does NOT mean you will definitely get it.`,
      meaning: `Higher genetic risk means you may benefit more from prevention strategies.`,
      action: 'Talk to your doctor about enhanced screening and prevention strategies.'
    }
  };

  return explanations[riskLevel as keyof typeof explanations] || explanations.moderate;
};

const ScoreVisualization = ({ score, percentile }: { score: number; percentile: number }) => {
  return (
    <div className="space-y-3">
      <div>
        <div className="flex justify-between text-sm mb-1">
          <span>Your Score: <strong>{score.toFixed(2)}</strong></span>
          <span>Population Average: <strong>0.50</strong></span>
        </div>
        <Progress value={score * 100} className="h-2" />
      </div>

      <div className="flex items-center justify-center bg-blue-50 rounded-lg p-3">
        <Users className="h-4 w-4 text-blue-600 mr-2" />
        <span className="text-sm text-blue-800">
          You score higher than <strong>{percentile}%</strong> of people
        </span>
      </div>
    </div>
  );
};

export function PatientFriendlyPrsDisplay({ scores, isLoading }: PatientFriendlyPrsDisplayProps) {
  if (isLoading) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="animate-pulse space-y-4">
            <div className="h-4 bg-gray-200 rounded w-3/4"></div>
            <div className="h-4 bg-gray-200 rounded w-1/2"></div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!scores || scores.length === 0) {
    return (
      <Card>
        <CardContent className="p-6 text-center">
          <Lightbulb className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No Results Yet</h3>
          <p className="text-gray-600">
            Upload your genetic data to see your personalized risk scores.
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Overview Summary */}
      <Card className="bg-gradient-to-r from-blue-50 to-indigo-50 border-blue-200">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Heart className="h-5 w-5 text-blue-600" />
            Your Genetic Risk Summary
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-blue-800 mb-4">
            We analyzed {scores.length} health conditions based on your genetic data.
            Here's what your results mean in simple terms:
          </p>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {['low', 'moderate', 'high'].map(level => {
              const count = scores.filter(s => s.riskLevel === level).length;
              const config = getRiskExplanation('', 0, 0, level);
              const IconComponent = config.icon;

              return (
                <div key={level} className={`${config.bgColor} ${config.borderColor} border rounded-lg p-3`}>
                  <div className="flex items-center gap-2 mb-1">
                    <IconComponent className={`h-4 w-4 ${config.color}`} />
                    <span className={`font-medium ${config.color}`}>{config.title}</span>
                  </div>
                  <div className="text-2xl font-bold text-gray-900">{count}</div>
                  <div className="text-xs text-gray-600">condition{count !== 1 ? 's' : ''}</div>
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* Individual Condition Results */}
      <div className="space-y-4">
        {scores.map((scoreData, index) => {
          const config = getRiskExplanation(
            scoreData.condition,
            scoreData.score,
            scoreData.percentile,
            scoreData.riskLevel
          );
          const IconComponent = config.icon;

          return (
            <Card key={`${scoreData.id}-${index}`} className={`${config.borderColor} border-l-4`}>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className={`p-2 ${config.bgColor} rounded-full`}>
                      <IconComponent className={`h-5 w-5 ${config.color}`} />
                    </div>
                    <div>
                      <CardTitle className="text-xl">{scoreData.condition}</CardTitle>
                      <Badge
                        variant="outline"
                        className={`${config.color} ${config.borderColor} ${config.bgColor} mt-1`}
                      >
                        {config.title}
                      </Badge>
                    </div>
                  </div>
                </div>
              </CardHeader>

              <CardContent className="space-y-4">
                {/* Simple Explanation */}
                <div className={`${config.bgColor} ${config.borderColor} border rounded-lg p-4`}>
                  <h4 className={`font-semibold ${config.color} mb-2`}>What this means:</h4>
                  <p className="text-gray-800 mb-2">{config.description}</p>
                  <p className="text-gray-700 text-sm">{config.meaning}</p>
                </div>

                {/* Score Visualization */}
                <ScoreVisualization score={scoreData.score} percentile={scoreData.percentile} />

                {/* Actionable Recommendations */}
                <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                  <h4 className="font-semibold text-gray-900 mb-2 flex items-center gap-2">
                    <Lightbulb className="h-4 w-4 text-yellow-600" />
                    What you can do:
                  </h4>
                  <p className="text-gray-700 mb-3">{config.action}</p>

                  <div className="flex gap-2">
                    <Button variant="outline" size="sm">
                      <Info className="h-3 w-3 mr-1" />
                      Learn More
                    </Button>
                    <Button variant="outline" size="sm">
                      <ArrowRight className="h-3 w-3 mr-1" />
                      Talk to Doctor
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Educational Footer */}
      <Card className="bg-yellow-50 border-yellow-200">
        <CardContent className="p-6">
          <div className="flex items-start gap-3">
            <AlertTriangle className="h-5 w-5 text-yellow-600 mt-0.5" />
            <div>
              <h4 className="font-semibold text-yellow-900 mb-2">Important Reminders</h4>
              <ul className="text-yellow-800 text-sm space-y-1 ml-4 list-disc">
                <li>Genetics is just one factor - lifestyle, environment, and family history also matter</li>
                <li>High genetic risk does not mean you will definitely develop the condition</li>
                <li>Low genetic risk does not guarantee you won't develop the condition</li>
                <li>Always discuss these results with your healthcare provider</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
