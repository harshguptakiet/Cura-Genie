/**
 * Enhanced Genomic Analysis API Service
 * Connects frontend to the enhanced backend endpoints
 */

export interface VCFAnalysisRequest {
    vcf_content: string;
    analysis_type: string;
}

export interface AnalysisResponse {
    success: boolean;
    message: string;
    analysis_id?: string;
    estimated_time?: number;
}

export interface ReportResponse {
    success: boolean;
    report?: any;
    error_message?: string;
}

export interface AnalysisStatus {
    analysis_id: string;
    status: 'processing' | 'completed' | 'failed';
    progress: number;
    start_time: number;
    elapsed_time: number;
}

export interface SystemCapabilities {
    supported_diseases: string[];
    variant_annotation: {
        sources: string[];
        functional_impact: string[];
    };
    ml_models: {
        diabetes: string;
        alzheimer: string;
        brain_tumor: string;
    };
    performance_target: string;
    report_features: string[];
}

export interface MLModelInfo {
    diabetes: {
        type: string;
        status: string;
        features: number;
    };
    alzheimer: {
        type: string;
        status: string;
        features: number;
    };
    brain_tumor: {
        type: string;
        status: string;
        features: number;
    };
}

export interface PerformanceStats {
    total_analyses: number;
    successful_analyses: number;
    average_processing_time: number;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class EnhancedGenomicService {
    private baseUrl: string;

    constructor() {
        this.baseUrl = API_BASE_URL;
    }

    /**
     * Start comprehensive VCF analysis
     */
    async analyzeVCF(vcfContent: string): Promise<AnalysisResponse> {
        try {
            const response = await fetch(`${this.baseUrl}/api/enhanced-genomic/analyze`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    vcf_content: vcfContent,
                    analysis_type: 'comprehensive'
                }),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Error starting VCF analysis:', error);
            throw error;
        }
    }

    /**
     * Get analysis status
     */
    async getAnalysisStatus(analysisId: string): Promise<AnalysisStatus> {
        try {
            const response = await fetch(`${this.baseUrl}/api/enhanced-genomic/status/${analysisId}`);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Error getting analysis status:', error);
            throw error;
        }
    }

    /**
     * Get analysis results
     */
    async getAnalysisResults(analysisId: string): Promise<ReportResponse> {
        try {
            const response = await fetch(`${this.baseUrl}/api/enhanced-genomic/results/${analysisId}`);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Error getting analysis results:', error);
            throw error;
        }
    }

    /**
     * Get system capabilities
     */
    async getCapabilities(): Promise<SystemCapabilities> {
        try {
            const response = await fetch(`${this.baseUrl}/api/enhanced-genomic/capabilities`);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Error getting capabilities:', error);
            throw error;
        }
    }

    /**
     * Get ML model information
     */
    async getMLModelInfo(): Promise<{ success: boolean; models: MLModelInfo; total_models: number }> {
        try {
            const response = await fetch(`${this.baseUrl}/api/ml/models`);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Error getting ML model info:', error);
            throw error;
        }
    }

    /**
     * Test variant annotation service
     */
    async testVariantAnnotation(): Promise<any> {
        try {
            const response = await fetch(`${this.baseUrl}/api/variant-annotation/test`);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Error testing variant annotation:', error);
            throw error;
        }
    }

    /**
     * Test report generation service
     */
    async testReportGeneration(): Promise<any> {
        try {
            const response = await fetch(`${this.baseUrl}/api/report-generation/test`);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Error testing report generation:', error);
            throw error;
        }
    }

    /**
     * Get performance statistics
     */
    async getPerformanceStats(): Promise<{ success: boolean; statistics: PerformanceStats; capabilities: SystemCapabilities }> {
        try {
            const response = await fetch(`${this.baseUrl}/api/performance/stats`);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Error getting performance stats:', error);
            throw error;
        }
    }

    /**
     * Quick test of all services
     */
    async quickTest(): Promise<any> {
        try {
            const response = await fetch(`${this.baseUrl}/api/test/quick`);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Error running quick test:', error);
            throw error;
        }
    }

    /**
     * Health check
     */
    async healthCheck(): Promise<any> {
        try {
            const response = await fetch(`${this.baseUrl}/health`);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Error checking health:', error);
            throw error;
        }
    }

    /**
     * Poll analysis status until completion
     */
    async pollAnalysisStatus(analysisId: string, onProgress?: (status: AnalysisStatus) => void): Promise<AnalysisStatus> {
        return new Promise((resolve, reject) => {
            const pollInterval = setInterval(async () => {
                try {
                    const status = await this.getAnalysisStatus(analysisId);

                    if (onProgress) {
                        onProgress(status);
                    }

                    if (status.status === 'completed' || status.status === 'failed') {
                        clearInterval(pollInterval);
                        resolve(status);
                    }
                } catch (error) {
                    clearInterval(pollInterval);
                    reject(error);
                }
            }, 2000); // Poll every 2 seconds

            // Timeout after 5 minutes
            setTimeout(() => {
                clearInterval(pollInterval);
                reject(new Error('Analysis timeout after 5 minutes'));
            }, 5 * 60 * 1000);
        });
    }
}

// Export singleton instance
export const enhancedGenomicService = new EnhancedGenomicService();

// Export the class for testing
export { EnhancedGenomicService };
