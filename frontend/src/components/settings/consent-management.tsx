'use client';

import React, { useState, useEffect } from 'react';
import { Switch } from '@/components/ui/switch';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { toast } from 'sonner';
import { Shield, Info, AlertTriangle } from 'lucide-react';

interface ConsentOption {
  id: string;
  feature: string;
  description: string;
  enabled: boolean;
}

interface ConsentManagementProps {
  userId: string;
}

// Mock API function - replace with actual API call
const fetchConsentOptions = async (userId: string): Promise<ConsentOption[]> => {
  return [
    {
      id: 'feature_1',
      feature: 'Share genomic data for research purposes',
      description: 'Allow researchers to access genomic data for studies.',
      enabled: false
    },
    {
      id: 'feature_2',
      feature: 'Receive personalized health recommendations',
      description: 'Tailored health insights based on your genomic data.',
      enabled: true
    },
    {
      id: 'feature_3',
      feature: 'Participate in genetic studies',
      description: 'Contribute to large-scale genomic research projects.',
      enabled: false
    }
  ];
};

const updateConsentOption = async ({ userId, consentId, enabled }: { userId: string, consentId: string, enabled: boolean }) => {
  // Remove artificial delay - use proper async operations
  return { success: true };
};

export function ConsentManagement({ userId }: ConsentManagementProps) {
  const queryClient = useQueryClient();
  const [localOptions, setLocalOptions] = useState<ConsentOption[]>([]);

  // Fetch consent options using React Query
  const { data: consentOptions = [], isLoading, error } = useQuery({
    queryKey: ['consent-options', userId],
    queryFn: () => fetchConsentOptions(userId),
    enabled: !!userId,
  });

  // Update local state when query data changes
  useEffect(() => {
    if (consentOptions.length > 0) {
      setLocalOptions(consentOptions);
    }
  }, [consentOptions]);

  // Mutation to update consent
  const mutation = useMutation({
    mutationFn: updateConsentOption,
    onSuccess: () => {
      toast.success('Consent preference updated successfully.');
      queryClient.invalidateQueries({ queryKey: ['consent-options', userId] });
    },
    onError: () => {
      toast.error('Failed to update consent preference. Please try again.');
    },
  });

  const handleToggle = (consentId: string, currentState: boolean) => {
    // Optimistically update local state
    setLocalOptions(prev => prev.map(option =>
      option.id === consentId
        ? { ...option, enabled: !currentState }
        : option
    ));

    // Call API
    mutation.mutate({ userId, consentId, enabled: !currentState });
  };

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="h-5 w-5 text-blue-600" />
            Privacy & Consent Settings
          </CardTitle>
          <CardDescription>Manage your data sharing preferences and consent settings</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="animate-pulse space-y-4">
            <div className="h-16 bg-gray-200 rounded"></div>
            <div className="h-16 bg-gray-200 rounded"></div>
            <div className="h-16 bg-gray-200 rounded"></div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <AlertTriangle className="h-5 w-5 text-red-600" />
            Error Loading Settings
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Alert variant="destructive">
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription>
              Unable to load your privacy settings. Please refresh the page or contact support.
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header with important notice */}
      <Card className="bg-blue-50 border-blue-200">
        <CardContent className="p-4">
          <div className="flex items-start gap-3">
            <Info className="h-5 w-5 text-blue-600 mt-0.5" />
            <div>
              <h4 className="font-semibold text-blue-900 mb-1">Your Privacy, Your Choice</h4>
              <p className="text-sm text-blue-800">
                These settings control how your genetic data is used. You can change these preferences at any time.
                Changes take effect immediately and you can withdraw consent at any point.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Main consent settings */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="h-5 w-5 text-green-600" />
            Data Sharing Preferences
          </CardTitle>
          <CardDescription>
            Control how your genomic data is used for research and personalized recommendations
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {localOptions.map((option, index) => {
            const isHighRisk = option.id === 'feature_1'; // Research sharing is higher risk

            return (
              <div
                key={option.id}
                className={`p-4 rounded-lg border transition-colors ${isHighRisk ? 'border-orange-200 bg-orange-50' : 'border-gray-200 bg-gray-50'
                  }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1 pr-4">
                    <div className="flex items-center gap-2 mb-2">
                      <h4 className="font-medium text-gray-900">{option.feature}</h4>
                      {isHighRisk && (
                        <AlertTriangle className="h-4 w-4 text-orange-600" />
                      )}
                    </div>
                    <p className="text-sm text-gray-600 mb-3">{option.description}</p>

                    {isHighRisk && (
                      <div className="bg-orange-100 border border-orange-200 rounded p-2 text-xs text-orange-800">
                        <strong>Privacy Notice:</strong> This shares your genetic data with researchers.
                        Data is anonymized but cannot be completely de-identified.
                      </div>
                    )}

                    {option.id === 'feature_2' && (
                      <div className="bg-green-100 border border-green-200 rounded p-2 text-xs text-green-800">
                        <strong>Recommended:</strong> This helps provide you with personalized health insights
                        based on your genetic data.
                      </div>
                    )}
                  </div>

                  <div className="flex flex-col items-center gap-2">
                    <Switch
                      checked={option.enabled}
                      onCheckedChange={() => handleToggle(option.id, option.enabled)}
                      disabled={mutation.isPending}
                    />
                    <span className="text-xs text-gray-500">
                      {option.enabled ? 'Enabled' : 'Disabled'}
                    </span>
                  </div>
                </div>
              </div>
            );
          })}

          {localOptions.length === 0 && (
            <Alert>
              <Info className="h-4 w-4" />
              <AlertDescription>No consent options are currently available.</AlertDescription>
            </Alert>
          )}
        </CardContent>
      </Card>

      {/* Additional privacy actions */}
      <Card>
        <CardHeader>
          <CardTitle>Additional Privacy Controls</CardTitle>
          <CardDescription>
            More ways to manage your data and privacy
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Button variant="outline" className="justify-start">
              <Shield className="h-4 w-4 mr-2" />
              View Full Privacy Policy
            </Button>

            <Button variant="outline" className="justify-start">
              <Info className="h-4 w-4 mr-2" />
              Download My Data
            </Button>

            <Button variant="outline" className="justify-start text-red-600 border-red-300 hover:bg-red-50">
              <AlertTriangle className="h-4 w-4 mr-2" />
              Delete All My Data
            </Button>

            <Button variant="outline" className="justify-start">
              <Info className="h-4 w-4 mr-2" />
              Contact Privacy Team
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
