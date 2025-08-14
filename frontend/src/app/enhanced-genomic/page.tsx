'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import {
    FileText,
    Activity,
    Brain,
    Heart,
    AlertTriangle,
    CheckCircle,
    Clock,
    Zap,
    BarChart3,
    Shield,
    Target,
    TrendingUp
} from 'lucide-react';
import { enhancedGenomicService, type SystemCapabilities, type AnalysisStatus, type ReportResponse } from '@/lib/enhanced-genomic-service';

export default function EnhancedGenomicPage() {
    const [vcfContent, setVcfContent] = useState('');
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [analysisId, setAnalysisId] = useState<string | null>(null);
    const [analysisStatus, setAnalysisStatus] = useState<AnalysisStatus | null>(null);
    const [analysisResults, setAnalysisResults] = useState<ReportResponse | null>(null);
    const [capabilities, setCapabilities] = useState<SystemCapabilities | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [backendHealth, setBackendHealth] = useState<boolean | null>(null);

    // Sample VCF content for testing
    const sampleVCF = `##fileformat=VCFv4.2
##source=SampleData
#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO
chr1\t1000\t.\tA\tT\t100\tPASS\t.
chr2\t2000\t.\tAT\tA\t100\tPASS\t.
chr3\t3000\t.\tC\tG\t100\tPASS\t.
chr1\t4000\t.\tG\tC\t100\tPASS\t.
chr2\t5000\t.\tT\tA\t100\tPASS\t.`;

    useEffect(() => {
        // Check backend health and load capabilities on component mount
        checkBackendHealth();
        loadCapabilities();
    }, []);

    const checkBackendHealth = async () => {
        try {
            const health = await enhancedGenomicService.healthCheck();
            setBackendHealth(true);
        } catch (error) {
            setBackendHealth(false);
            setError('Backend service is not available. Please ensure the backend is running.');
        }
    };

    const loadCapabilities = async () => {
        try {
            const caps = await enhancedGenomicService.getCapabilities();
            setCapabilities(caps);
        } catch (error) {
            console.error('Failed to load capabilities:', error);
        }
    };

    const startAnalysis = async () => {
        if (!vcfContent.trim()) {
            setError('Please enter VCF content to analyze');
            return;
        }

        setIsAnalyzing(true);
        setError(null);
        setAnalysisResults(null);

        try {
            const response = await enhancedGenomicService.analyzeVCF(vcfContent);

            if (response.success && response.analysis_id) {
                setAnalysisId(response.analysis_id);

                // Start polling for status updates
                pollAnalysisStatus(response.analysis_id);
            } else {
                throw new Error(response.message || 'Failed to start analysis');
            }
        } catch (error) {
            setError(`Failed to start analysis: ${error instanceof Error ? error.message : 'Unknown error'}`);
            setIsAnalyzing(false);
        }
    };

    const pollAnalysisStatus = async (id: string) => {
        try {
            const finalStatus = await enhancedGenomicService.pollAnalysisStatus(id, (status) => {
                setAnalysisStatus(status);
            });

            if (finalStatus.status === 'completed') {
                // Get the results
                const results = await enhancedGenomicService.getAnalysisResults(id);
                setAnalysisResults(results);
            } else {
                setError('Analysis failed');
            }
        } catch (error) {
            setError(`Analysis error: ${error instanceof Error ? error.message : 'Unknown error'}`);
        } finally {
            setIsAnalyzing(false);
        }
    };

    const loadSampleData = () => {
        setVcfContent(sampleVCF);
    };

    const clearData = () => {
        setVcfContent('');
        setAnalysisId(null);
        setAnalysisStatus(null);
        setAnalysisResults(null);
        setError(null);
    };

    const formatTime = (seconds: number) => {
        if (seconds < 60) return `${seconds.toFixed(1)}s`;
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = seconds % 60;
        return `${minutes}m ${remainingSeconds.toFixed(0)}s`;
    };

    return (
        <div className="container mx-auto p-6 space-y-6">
            {/* Header */}
            <div className="text-center space-y-4">
                <h1 className="text-4xl font-bold text-primary">Enhanced Genomic Analysis</h1>
                <p className="text-xl text-muted-foreground">
                    Real-time prediction model for Diabetes, Alzheimer's, and Brain Tumors from VCF data
                </p>

                {/* Backend Status */}
                <div className="flex justify-center">
                    {backendHealth === true ? (
                        <Badge variant="default" className="bg-green-100 text-green-800">
                            <CheckCircle className="w-4 h-4 mr-2" />
                            Backend Connected
                        </Badge>
                    ) : backendHealth === false ? (
                        <Badge variant="destructive">
                            <AlertTriangle className="w-4 h-4 mr-2" />
                            Backend Disconnected
                        </Badge>
                    ) : (
                        <Badge variant="secondary">
                            <Clock className="w-4 h-4 mr-2" />
                            Checking Connection...
                        </Badge>
                    )}
                </div>
            </div>

            {/* Main Content */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Left Column - Input & Controls */}
                <div className="lg:col-span-1 space-y-6">
                    {/* VCF Input */}
                    <Card>
                        <CardHeader>
                            <CardTitle className="flex items-center gap-2">
                                <FileText className="w-5 h-5" />
                                VCF Data Input
                            </CardTitle>
                            <CardDescription>
                                Paste your VCF content or use sample data for testing
                            </CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div className="space-y-2">
                                <Label htmlFor="vcf-content">VCF Content</Label>
                                <Textarea
                                    id="vcf-content"
                                    placeholder="Paste VCF content here..."
                                    value={vcfContent}
                                    onChange={(e) => setVcfContent(e.target.value)}
                                    rows={10}
                                    className="font-mono text-sm"
                                />
                            </div>

                            <div className="flex gap-2">
                                <Button onClick={loadSampleData} variant="outline" size="sm">
                                    Load Sample Data
                                </Button>
                                <Button onClick={clearData} variant="outline" size="sm">
                                    Clear
                                </Button>
                            </div>

                            <Button
                                onClick={startAnalysis}
                                disabled={isAnalyzing || !vcfContent.trim() || backendHealth === false}
                                className="w-full"
                            >
                                {isAnalyzing ? (
                                    <>
                                        <Activity className="w-4 h-4 mr-2 animate-spin" />
                                        Analyzing...
                                    </>
                                ) : (
                                    <>
                                        <Zap className="w-4 h-4 mr-2" />
                                        Start Analysis
                                    </>
                                )}
                            </Button>
                        </CardContent>
                    </Card>

                    {/* System Capabilities */}
                    {capabilities && (
                        <Card>
                            <CardHeader>
                                <CardTitle className="flex items-center gap-2">
                                    <Shield className="w-5 h-5" />
                                    System Capabilities
                                </CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                <div>
                                    <Label className="text-sm font-medium">Supported Diseases</Label>
                                    <div className="flex flex-wrap gap-1 mt-2">
                                        {capabilities.supported_diseases.map((disease) => (
                                            <Badge key={disease} variant="secondary">
                                                {disease}
                                            </Badge>
                                        ))}
                                    </div>
                                </div>

                                <div>
                                    <Label className="text-sm font-medium">Performance Target</Label>
                                    <p className="text-sm text-muted-foreground mt-1">
                                        {capabilities.performance_target}
                                    </p>
                                </div>
                            </CardContent>
                        </Card>
                    )}
                </div>

                {/* Right Column - Results & Status */}
                <div className="lg:col-span-2 space-y-6">
                    {/* Error Display */}
                    {error && (
                        <Alert variant="destructive">
                            <AlertTriangle className="h-4 w-4" />
                            <AlertDescription>{error}</AlertDescription>
                        </Alert>
                    )}

                    {/* Analysis Status */}
                    {analysisStatus && (
                        <Card>
                            <CardHeader>
                                <CardTitle className="flex items-center gap-2">
                                    <Activity className="w-5 h-5" />
                                    Analysis Status
                                </CardTitle>
                                <CardDescription>
                                    Analysis ID: {analysisStatus.analysis_id}
                                </CardDescription>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                <div className="space-y-2">
                                    <div className="flex justify-between text-sm">
                                        <span>Progress</span>
                                        <span>{analysisStatus.progress}%</span>
                                    </div>
                                    <Progress value={analysisStatus.progress} className="w-full" />
                                </div>

                                <div className="grid grid-cols-2 gap-4 text-sm">
                                    <div>
                                        <span className="text-muted-foreground">Status:</span>
                                        <Badge
                                            variant={analysisStatus.status === 'completed' ? 'default' : 'secondary'}
                                            className="ml-2"
                                        >
                                            {analysisStatus.status}
                                        </Badge>
                                    </div>
                                    <div>
                                        <span className="text-muted-foreground">Elapsed Time:</span>
                                        <span className="ml-2 font-medium">
                                            {formatTime(analysisStatus.elapsed_time)}
                                        </span>
                                    </div>
                                </div>
                            </CardContent>
                        </Card>
                    )}

                    {/* Analysis Results */}
                    {analysisResults && analysisResults.success && analysisResults.report && (
                        <Card>
                            <CardHeader>
                                <CardTitle className="flex items-center gap-2">
                                    <BarChart3 className="w-5 h-5" />
                                    Analysis Results
                                </CardTitle>
                                <CardDescription>
                                    Comprehensive genomic risk assessment completed
                                </CardDescription>
                            </CardHeader>
                            <CardContent>
                                <Tabs defaultValue="summary" className="w-full">
                                    <TabsList className="grid w-full grid-cols-4">
                                        <TabsTrigger value="summary">Summary</TabsTrigger>
                                        <TabsTrigger value="diseases">Diseases</TabsTrigger>
                                        <TabsTrigger value="variants">Variants</TabsTrigger>
                                        <TabsTrigger value="technical">Technical</TabsTrigger>
                                    </TabsList>

                                    <TabsContent value="summary" className="space-y-4">
                                        {analysisResults.report.executive_summary && (
                                            <div className="space-y-4">
                                                <div className="grid grid-cols-3 gap-4">
                                                    <div className="text-center p-4 bg-muted rounded-lg">
                                                        <div className="text-2xl font-bold text-primary">
                                                            {analysisResults.report.executive_summary.overall_risk}
                                                        </div>
                                                        <div className="text-sm text-muted-foreground">Overall Risk</div>
                                                    </div>
                                                    <div className="text-center p-4 bg-muted rounded-lg">
                                                        <div className="text-2xl font-bold text-orange-600">
                                                            {analysisResults.report.executive_summary.primary_concern}
                                                        </div>
                                                        <div className="text-sm text-muted-foreground">Primary Concern</div>
                                                    </div>
                                                    <div className="text-center p-4 bg-muted rounded-lg">
                                                        <div className="text-2xl font-bold text-blue-600">
                                                            {analysisResults.report.executive_summary.highest_risk_score}
                                                        </div>
                                                        <div className="text-sm text-muted-foreground">Risk Score</div>
                                                    </div>
                                                </div>
                                                <p className="text-muted-foreground">
                                                    {analysisResults.report.executive_summary.summary}
                                                </p>
                                            </div>
                                        )}
                                    </TabsContent>

                                    <TabsContent value="diseases" className="space-y-4">
                                        {analysisResults.report.disease_assessments && (
                                            <div className="space-y-4">
                                                {analysisResults.report.disease_assessments.map((assessment: any, index: number) => (
                                                    <div key={index} className="p-4 border rounded-lg">
                                                        <div className="flex items-center justify-between mb-2">
                                                            <h4 className="font-semibold">{assessment.disease}</h4>
                                                            <Badge
                                                                variant={
                                                                    assessment.risk_category === 'High' ? 'destructive' :
                                                                        assessment.risk_category === 'Moderate' ? 'default' : 'secondary'
                                                                }
                                                            >
                                                                {assessment.risk_category} Risk
                                                            </Badge>
                                                        </div>
                                                        <div className="grid grid-cols-2 gap-4 text-sm">
                                                            <div>
                                                                <span className="text-muted-foreground">Risk Score:</span>
                                                                <span className="ml-2 font-medium">{assessment.risk_score}</span>
                                                            </div>
                                                            <div>
                                                                <span className="text-muted-foreground">Confidence:</span>
                                                                <span className="ml-2 font-medium">{assessment.confidence}</span>
                                                            </div>
                                                        </div>
                                                        <div className="mt-2">
                                                            <span className="text-muted-foreground text-sm">Key Factors:</span>
                                                            <div className="flex flex-wrap gap-1 mt-1">
                                                                {assessment.key_factors.map((factor: string, i: number) => (
                                                                    <Badge key={i} variant="outline" className="text-xs">
                                                                        {factor}
                                                                    </Badge>
                                                                ))}
                                                            </div>
                                                        </div>
                                                    </div>
                                                ))}
                                            </div>
                                        )}
                                    </TabsContent>

                                    <TabsContent value="variants" className="space-y-4">
                                        {analysisResults.report.variant_analysis && (
                                            <div className="space-y-4">
                                                <div className="grid grid-cols-2 gap-4">
                                                    <div className="text-center p-4 bg-muted rounded-lg">
                                                        <div className="text-2xl font-bold">
                                                            {analysisResults.report.variant_analysis.total_variants}
                                                        </div>
                                                        <div className="text-sm text-muted-foreground">Total Variants</div>
                                                    </div>
                                                    <div className="text-center p-4 bg-muted rounded-lg">
                                                        <div className="text-2xl font-bold text-orange-600">
                                                            {analysisResults.report.variant_analysis.significant_variants}
                                                        </div>
                                                        <div className="text-sm text-muted-foreground">Significant Variants</div>
                                                    </div>
                                                </div>

                                                {analysisResults.report.variant_analysis.top_variants && (
                                                    <div>
                                                        <h4 className="font-semibold mb-2">Top Variants</h4>
                                                        <div className="space-y-2">
                                                            {analysisResults.report.variant_analysis.top_variants.map((variant: any, index: number) => (
                                                                <div key={index} className="p-3 border rounded-lg text-sm">
                                                                    <div className="flex justify-between items-center">
                                                                        <span className="font-mono">{variant.position}</span>
                                                                        <Badge variant="outline">{variant.relevance_score}</Badge>
                                                                    </div>
                                                                    <div className="text-muted-foreground mt-1">
                                                                        {variant.change} • {variant.significance} • {variant.impact}
                                                                    </div>
                                                                </div>
                                                            ))}
                                                        </div>
                                                    </div>
                                                )}
                                            </div>
                                        )}
                                    </TabsContent>

                                    <TabsContent value="technical" className="space-y-4">
                                        {analysisResults.report.technical_details && (
                                            <div className="space-y-4">
                                                <div className="grid grid-cols-2 gap-4">
                                                    <div className="text-center p-4 bg-muted rounded-lg">
                                                        <div className="text-2xl font-bold">
                                                            {analysisResults.report.technical_details.analysis_parameters?.processing_time_seconds}s
                                                        </div>
                                                        <div className="text-sm text-muted-foreground">Processing Time</div>
                                                    </div>
                                                    <div className="text-center p-4 bg-muted rounded-lg">
                                                        <div className="text-2xl font-bold text-blue-600">
                                                            {analysisResults.report.technical_details.analysis_parameters?.variant_count}
                                                        </div>
                                                        <div className="text-sm text-muted-foreground">Variants Processed</div>
                                                    </div>
                                                </div>

                                                <div>
                                                    <h4 className="font-semibold mb-2">Limitations</h4>
                                                    <ul className="space-y-1 text-sm text-muted-foreground">
                                                        {analysisResults.report.technical_details.limitations?.map((limitation: string, index: number) => (
                                                            <li key={index} className="flex items-start gap-2">
                                                                <span className="text-orange-500 mt-1">•</span>
                                                                {limitation}
                                                            </li>
                                                        ))}
                                                    </ul>
                                                </div>
                                            </div>
                                        )}
                                    </TabsContent>
                                </Tabs>
                            </CardContent>
                        </Card>
                    )}
                </div>
            </div>
        </div>
    );
}
