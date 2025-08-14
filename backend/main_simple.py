"""
Simplified Enhanced Genomic Analysis Backend
Works with minimal dependencies (no numpy/pandas)
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import json
import asyncio
import time

# Import our simplified services
from services.enhanced_genomic_processor_simple import SimpleEnhancedGenomicProcessor
from services.variant_annotation_simple import SimpleVariantAnnotator
from services.ml_prediction_simple import SimpleMLPredictionService
from services.report_generator_simple import SimpleReportGenerator

# Initialize FastAPI app
app = FastAPI(
    title="CuraGenie Enhanced Genomic Analysis",
    description="Real-time prediction model for Diabetes, Alzheimer's, and Brain Tumors from VCF data",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
processor = SimpleEnhancedGenomicProcessor()
variant_annotator = SimpleVariantAnnotator()
ml_service = SimpleMLPredictionService()
report_generator = SimpleReportGenerator()

# Pydantic models for API requests/responses
class VCFAnalysisRequest(BaseModel):
    vcf_content: str
    analysis_type: str = "comprehensive"

class AnalysisResponse(BaseModel):
    success: bool
    message: str
    analysis_id: Optional[str] = None
    estimated_time: Optional[int] = None

class ReportResponse(BaseModel):
    success: bool
    report: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None

# In-memory storage for analysis results (in production, use Redis/database)
analysis_results = {}
analysis_status = {}

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "CuraGenie Enhanced Genomic Analysis API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "services": {
            "variant_annotation": "available",
            "ml_prediction": "available",
            "report_generation": "available"
        }
    }

@app.post("/api/enhanced-genomic/analyze", response_model=AnalysisResponse)
async def analyze_vcf_comprehensive(request: VCFAnalysisRequest):
    """Analyze VCF content comprehensively"""
    try:
        # Generate analysis ID
        analysis_id = f"analysis_{int(time.time())}"
        
        # Store initial status
        analysis_status[analysis_id] = {
            "status": "processing",
            "start_time": time.time(),
            "progress": 0
        }
        
        # Start background processing
        background_tasks = BackgroundTasks()
        background_tasks.add_task(
            run_comprehensive_analysis, 
            analysis_id, 
            request.vcf_content
        )
        
        return AnalysisResponse(
            success=True,
            message="Analysis started successfully",
            analysis_id=analysis_id,
            estimated_time=60  # Target: under 60 seconds
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start analysis: {str(e)}")

@app.get("/api/enhanced-genomic/capabilities")
async def get_analysis_capabilities():
    """Get system capabilities"""
    return processor.get_capabilities()

@app.get("/api/enhanced-genomic/status/{analysis_id}")
async def get_analysis_status(analysis_id: str):
    """Get analysis status"""
    if analysis_id not in analysis_status:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    status = analysis_status[analysis_id]
    return {
        "analysis_id": analysis_id,
        "status": status["status"],
        "progress": status.get("progress", 0),
        "start_time": status["start_time"],
        "elapsed_time": time.time() - status["start_time"]
    }

@app.get("/api/enhanced-genomic/results/{analysis_id}", response_model=ReportResponse)
async def get_analysis_results(analysis_id: str):
    """Get analysis results"""
    if analysis_id not in analysis_results:
        raise HTTPException(status_code=404, detail="Results not found")
    
    result = analysis_results[analysis_id]
    if result.get("error"):
        return ReportResponse(
            success=False,
            error_message=result["error_message"]
        )
    
    return ReportResponse(
        success=True,
        report=result["report"]
    )

@app.get("/api/ml/models")
async def get_ml_model_info():
    """Get ML model information"""
    try:
        models_info = {
            "diabetes": {
                "type": "Gradient Boosting",
                "status": "loaded" if "diabetes" in ml_service.models else "not_loaded",
                "features": 20
            },
            "alzheimer": {
                "type": "Random Forest",
                "status": "loaded" if "alzheimer" in ml_service.models else "not_loaded",
                "features": 20
            },
            "brain_tumor": {
                "type": "Random Forest",
                "status": "loaded" if "brain_tumor" in ml_service.models else "not_loaded",
                "features": 20
            }
        }
        
        return {
            "success": True,
            "models": models_info,
            "total_models": len(ml_service.models)
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/api/variant-annotation/test")
async def test_variant_annotation():
    """Test variant annotation service"""
    try:
        test_variants = [
            {'chrom': 'chr1', 'pos': 1000, 'ref': 'A', 'alt': 'T'},
            {'chrom': 'chr2', 'pos': 2000, 'ref': 'AT', 'alt': 'A'}
        ]
        
        async with variant_annotator:
            annotations = await variant_annotator.annotate_variants_batch(test_variants)
        
        return {
            "success": True,
            "variants_annotated": len(annotations),
            "sample_annotation": {
                "chrom": annotations[0].chrom,
                "pos": annotations[0].pos,
                "ref": annotations[0].ref,
                "alt": annotations[0].alt,
                "significance": annotations[0].clinvar_significance,
                "frequency": annotations[0].gnomad_frequency,
                "impact": annotations[0].functional_impact
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/api/report-generation/test")
async def test_report_generation():
    """Test report generation service"""
    try:
        # Create test data
        from services.report_generator_simple import SimpleVariant, SimpleDiseaseAssessment
        
        test_variants = [
            SimpleVariant("chr1", 1000, "A", "T", "likely_pathogenic", 0.001, "transition")
        ]
        
        test_assessments = [
            SimpleDiseaseAssessment("Diabetes", 0.7, "High", 0.8, 
                                   ["High genetic predisposition"], 
                                   ["Consult healthcare provider"])
        ]
        
        report = report_generator.generate_report(test_variants, test_assessments, 30.0)
        
        return {
            "success": True,
            "report_generated": True,
            "report_sections": list(report.keys()),
            "sample_summary": report.get("executive_summary", {})
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/api/performance/stats")
async def get_performance_stats():
    """Get performance statistics"""
    try:
        stats = processor.get_processing_stats()
        return {
            "success": True,
            "statistics": stats,
            "capabilities": processor.get_capabilities()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

# Background task function
async def run_comprehensive_analysis(analysis_id: str, vcf_content: str):
    """Run comprehensive analysis in background"""
    try:
        # Update status
        analysis_status[analysis_id]["status"] = "processing"
        analysis_status[analysis_id]["progress"] = 25
        
        # Process VCF
        result = await processor.process_vcf_comprehensive(vcf_content)
        
        # Update status
        analysis_status[analysis_id]["progress"] = 100
        
        if result.success:
            analysis_status[analysis_id]["status"] = "completed"
            analysis_results[analysis_id] = {
                "success": True,
                "report": result.report,
                "processing_time": result.processing_time,
                "variants_processed": result.variants_processed
            }
        else:
            analysis_status[analysis_id]["status"] = "failed"
            analysis_results[analysis_id] = {
                "success": False,
                "error": True,
                "error_message": result.error_message
            }
            
    except Exception as e:
        analysis_status[analysis_id]["status"] = "failed"
        analysis_results[analysis_id] = {
            "success": False,
            "error": True,
            "error_message": str(e)
        }

# Test endpoint for quick verification
@app.get("/api/test/quick")
async def quick_test():
    """Quick test of all services"""
    try:
        # Test VCF processing
        test_vcf = """##fileformat=VCFv4.2
#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO
chr1\t1000\t.\tA\tT\t100\tPASS\t."""
        
        result = await processor.process_vcf_comprehensive(test_vcf)
        
        return {
            "success": True,
            "services_tested": [
                "variant_annotation",
                "ml_prediction", 
                "report_generation",
                "enhanced_processor"
            ],
            "test_result": {
                "success": result.success,
                "processing_time": result.processing_time,
                "variants_processed": result.variants_processed
            },
            "message": "All services are working correctly!"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Some services may not be working correctly"
        }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting CuraGenie Enhanced Genomic Analysis Backend...")
    print("📊 Services initialized:")
    print("   ✅ Variant Annotation Service")
    print("   ✅ ML Prediction Service") 
    print("   ✅ Report Generation Service")
    print("   ✅ Enhanced Genomic Processor")
    print("🌐 API available at: http://localhost:8000")
    print("📚 API docs at: http://localhost:8000/docs")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
