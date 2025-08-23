'use client';

import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Loader2, Dna, Activity, Target, TrendingUp, BarChart3, MapPin } from 'lucide-react';
import { logAnalysis } from '@/lib/logger';

interface Variant {
  id: number;
  chromosome: string;
  position: number;
  reference: string;
  alternative: string;
  variant_type: string;
  quality: number;
  variant_id: string;
  is_real_data: boolean;
}

interface GenomeBrowserProps {
  userId: string;
}

// API function to fetch real genomic variants
const fetchGenomicVariants = async (userId: string): Promise<Variant[]> => {
  const url = `http://127.0.0.1:8000/api/genomic/variants/${userId}`;

  logAnalysis('debug', 'Fetching genomic variants', 'genomic_variants', { userId, url });

  const response = await fetch(url);

  if (!response.ok) {
    logAnalysis('error', 'Failed to fetch genomic variants', 'genomic_variants', {
      userId,
      status: response.status,
      statusText: response.statusText
    });
    throw new Error(`Failed to fetch genomic variants: ${response.status}`);
  }

  const data = await response.json();
  logAnalysis('info', 'Genomic variants fetched successfully', 'genomic_variants', {
    userId,
    totalVariants: data.length
  });

  return data;
};

const ModernGenomeBrowser: React.FC<GenomeBrowserProps> = ({ userId }) => {
  const { data: variants, isLoading, error } = useQuery({
    queryKey: ['genomic-variants', userId],
    queryFn: () => fetchGenomicVariants(userId),
    enabled: !!userId,
    retry: 1
  });

  const diseaseSnps = ['rs7903146', 'rs1801282', 'rs5219', 'rs13266634', 'rs12255372'];

  // Calculate stats
  const chromosomes = React.useMemo(() => {
    if (!variants) return [];
    return Array.from(new Set(variants.map(v => v.chromosome))).sort((a, b) => {
      const numA = parseInt(a);
      const numB = parseInt(b);
      if (!isNaN(numA) && !isNaN(numB)) return numA - numB;
      if (!isNaN(numA)) return -1;
      if (!isNaN(numB)) return 1;
      return a.localeCompare(b);
    });
  }, [variants]);

  const variantsByChromosome = React.useMemo(() => {
    if (!variants) return {};
    return variants.reduce((acc, variant) => {
      if (!acc[variant.chromosome]) {
        acc[variant.chromosome] = [];
      }
      acc[variant.chromosome].push(variant);
      return acc;
    }, {} as Record<string, Variant[]>);
  }, [variants]);

  const avgQuality = React.useMemo(() => {
    if (!variants || variants.length === 0) return 0;
    return Math.round(variants.reduce((sum, v) => sum + v.quality, 0) / variants.length);
  }, [variants]);

  const diseaseVariantsCount = React.useMemo(() => {
    if (!variants) return 0;
    return variants.filter(v => diseaseSnps.includes(v.variant_id)).length;
  }, [variants, diseaseSnps]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="text-center space-y-4">
          <Loader2 className="h-12 w-12 animate-spin text-orange-600 mx-auto" />
          <p className="text-lg font-medium text-gray-700">Loading genomic variants...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-20">
        <Alert variant="destructive">
          <AlertDescription>
            Error loading genomic variants. Please try again later.
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  if (!variants || variants.length === 0) {
    return (
      <div className="text-center py-20 space-y-6">
        <Dna className="h-20 w-20 text-gray-400 mx-auto animate-pulse" />
        <div>
          <p className="text-xl font-semibold text-gray-700">No genomic variants found</p>
          <p className="text-gray-500 mt-2">Upload your genomic data to see variant analysis</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Genomic Variants Chart */}
      <Card className="bg-gradient-to-br from-orange-50 to-amber-50 border-orange-200">
        <CardHeader>
          <CardTitle className="flex items-center gap-3">
            <BarChart3 className="h-6 w-6 text-orange-600" />
            Genomic Variants Distribution
          </CardTitle>
          <CardDescription>
            Visual distribution of variants across chromosomes with quality indicators
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-6">
            {/* Chart Area */}
            <div className="bg-white rounded-xl p-6 shadow-sm border">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">

                {/* Bar Chart - Variants per Chromosome */}
                <div>
                  <h3 className="text-lg font-semibold text-gray-800 mb-4">Variants per Chromosome</h3>
                  <div className="space-y-3">
                    {chromosomes.map((chr) => {
                      const chrVariants = variantsByChromosome[chr] || [];
                      const maxVariants = Math.max(...chromosomes.map(c => variantsByChromosome[c]?.length || 0));
                      const width = (chrVariants.length / maxVariants) * 100;
                      const diseaseCount = chrVariants.filter(v => diseaseSnps.includes(v.variant_id)).length;

                      return (
                        <div key={chr} className="flex items-center gap-3">
                          <div className="w-12 text-sm font-medium text-gray-600">Chr {chr}</div>
                          <div className="flex-1 relative">
                            <div className="h-8 bg-gray-100 rounded-lg overflow-hidden">
                              <div
                                className="h-full bg-gradient-to-r from-orange-400 to-orange-600 rounded-lg transition-all duration-500 flex items-center justify-end pr-2"
                                style={{ width: `${width}%` }}
                              >
                                {chrVariants.length > 0 && (
                                  <span className="text-white text-xs font-medium">
                                    {chrVariants.length}
                                  </span>
                                )}
                              </div>
                              {diseaseCount > 0 && (
                                <div className="absolute top-0 right-0 h-8 w-2 bg-red-500 rounded-r-lg opacity-80"></div>
                              )}
                            </div>
                          </div>
                          <div className="w-16 text-xs text-gray-500">
                            {diseaseCount > 0 && (
                              <span className="text-red-600 font-medium">{diseaseCount} disease</span>
                            )}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>

                {/* Quality Distribution Pie-like Visualization */}
                <div>
                  <h3 className="text-lg font-semibold text-gray-800 mb-4">Quality Score Ranges</h3>
                  <div className="space-y-3">
                    {[
                      { range: '80-100', color: 'from-green-400 to-green-600', threshold: 80 },
                      { range: '60-79', color: 'from-blue-400 to-blue-600', threshold: 60 },
                      { range: '40-59', color: 'from-yellow-400 to-yellow-600', threshold: 40 },
                      { range: '20-39', color: 'from-orange-400 to-orange-600', threshold: 20 },
                      { range: '0-19', color: 'from-red-400 to-red-600', threshold: 0 }
                    ].map(({ range, color, threshold }) => {
                      const count = variants.filter(v => {
                        if (threshold === 80) return v.quality >= 80;
                        if (threshold === 60) return v.quality >= 60 && v.quality < 80;
                        if (threshold === 40) return v.quality >= 40 && v.quality < 60;
                        if (threshold === 20) return v.quality >= 20 && v.quality < 40;
                        return v.quality < 20;
                      }).length;
                      const percentage = ((count / variants.length) * 100);

                      return (
                        <div key={range} className="flex items-center gap-3">
                          <div className="w-16 text-sm font-medium text-gray-600">Q {range}</div>
                          <div className="flex-1 relative">
                            <div className="h-6 bg-gray-100 rounded-full overflow-hidden">
                              <div
                                className={`h-full bg-gradient-to-r ${color} rounded-full transition-all duration-700 flex items-center justify-center`}
                                style={{ width: `${percentage}%` }}
                              >
                                {count > 0 && percentage > 15 && (
                                  <span className="text-white text-xs font-medium">
                                    {count}
                                  </span>
                                )}
                              </div>
                            </div>
                          </div>
                          <div className="w-12 text-xs text-gray-500 text-right">
                            {percentage.toFixed(0)}%
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>

              {/* Chart Legend */}
              <div className="mt-6 pt-4 border-t border-gray-100">
                <div className="flex flex-wrap items-center gap-6 text-sm">
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 bg-gradient-to-r from-orange-400 to-orange-600 rounded"></div>
                    <span className="text-gray-600">Standard Variants</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 bg-red-500 rounded"></div>
                    <span className="text-gray-600">Disease-Associated</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 bg-gradient-to-r from-green-400 to-green-600 rounded"></div>
                    <span className="text-gray-600">High Quality (80+)</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Overview Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card className="bg-gradient-to-br from-blue-500 to-blue-600 text-white">
          <CardContent className="p-6">
            <div className="flex items-center gap-4">
              <BarChart3 className="h-8 w-8" />
              <div>
                <div className="text-3xl font-bold">{variants.length}</div>
                <div className="text-sm opacity-90">Total Variants</div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-green-500 to-green-600 text-white">
          <CardContent className="p-6">
            <div className="flex items-center gap-4">
              <MapPin className="h-8 w-8" />
              <div>
                <div className="text-3xl font-bold">{chromosomes.length}</div>
                <div className="text-sm opacity-90">Chromosomes</div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-purple-500 to-purple-600 text-white">
          <CardContent className="p-6">
            <div className="flex items-center gap-4">
              <TrendingUp className="h-8 w-8" />
              <div>
                <div className="text-3xl font-bold">{avgQuality}</div>
                <div className="text-sm opacity-90">Avg Quality</div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-red-500 to-red-600 text-white">
          <CardContent className="p-6">
            <div className="flex items-center gap-4">
              <Target className="h-8 w-8" />
              <div>
                <div className="text-3xl font-bold">{diseaseVariantsCount}</div>
                <div className="text-sm opacity-90">Disease SNPs</div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Chromosome Distribution */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-3">
            <Dna className="h-6 w-6 text-orange-600" />
            Variant Distribution by Chromosome
          </CardTitle>
          <CardDescription>
            Distribution of genomic variants across chromosomes
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {chromosomes.map((chr) => {
              const chrVariants = variantsByChromosome[chr] || [];
              const diseaseVariantsInChr = chrVariants.filter(v => diseaseSnps.includes(v.variant_id)).length;
              return (
                <Card key={chr} className="border-2 hover:shadow-lg transition-shadow">
                  <CardContent className="p-4">
                    <div className="text-center space-y-2">
                      <div className="text-lg font-bold text-orange-600">Chr {chr}</div>
                      <div className="text-2xl font-bold text-gray-800">{chrVariants.length}</div>
                      <div className="text-sm text-gray-500">variants</div>
                      {diseaseVariantsInChr > 0 && (
                        <Badge className="bg-red-100 text-red-800 text-xs">
                          {diseaseVariantsInChr} disease
                        </Badge>
                      )}
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* Variant Quality Distribution */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-3">
            <Activity className="h-6 w-6 text-green-600" />
            Quality Score Distribution
          </CardTitle>
          <CardDescription>
            Distribution of variant quality scores across all detected variants
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            {[0, 20, 40, 60, 80].map((threshold) => {
              const count = variants.filter(v => v.quality >= threshold && v.quality < threshold + 20).length;
              const percentage = ((count / variants.length) * 100).toFixed(1);
              return (
                <div key={threshold} className="text-center p-4 border rounded-lg">
                  <div className="text-2xl font-bold text-blue-600">{count}</div>
                  <div className="text-sm text-gray-600">Quality {threshold}-{threshold + 19}</div>
                  <div className="text-xs text-gray-500">{percentage}%</div>
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* Recent High-Quality Variants */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-3">
            <Target className="h-6 w-6 text-purple-600" />
            High-Quality Variants
          </CardTitle>
          <CardDescription>
            Top genomic variants with highest quality scores
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {variants
              .sort((a, b) => b.quality - a.quality)
              .slice(0, 8)
              .map((variant, index) => {
                const isDisease = diseaseSnps.includes(variant.variant_id);
                return (
                  <div key={variant.id} className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50">
                    <div className="flex items-center gap-4">
                      <div className="w-8 h-8 bg-orange-100 rounded-full flex items-center justify-center text-orange-600 font-bold text-sm">
                        {index + 1}
                      </div>
                      <div>
                        <div className="font-semibold">{variant.variant_id || `Variant ${variant.id}`}</div>
                        <div className="text-sm text-gray-600">
                          Chr {variant.chromosome}:{variant.position.toLocaleString()}
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <Badge className="bg-blue-100 text-blue-800">
                        {variant.reference} → {variant.alternative}
                      </Badge>
                      <Badge className="bg-green-100 text-green-800">
                        Q{variant.quality}
                      </Badge>
                      {isDisease && (
                        <Badge className="bg-red-100 text-red-800">
                          Disease
                        </Badge>
                      )}
                    </div>
                  </div>
                );
              })
            }
          </div>
        </CardContent>
      </Card>
    </div>
  );
};


export default ModernGenomeBrowser;
