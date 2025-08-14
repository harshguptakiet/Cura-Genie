#!/usr/bin/env python3
"""
Enhanced CuraGenie FastAPI Backend with Comprehensive Genomic Analysis
- Real-time VCF processing with variant annotation
- ML-powered disease risk prediction (Diabetes, Alzheimer's, Brain Tumors)
- Comprehensive reporting system
- Performance-optimized for 60-second processing
"""

import os
import logging
import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, UploadFile, File, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

# Import our enhanced services
from services.enhanced_genomic_processor import EnhancedGenomicProcessor
from services.variant_annotation import VariantAnnotator
from services.ml_prediction_service import MLPredictionService
from services.report_gen import ReportGenerator

# Import database models
from db.database import get_db, SessionLocal
from db.models import GenomicData

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="CuraGenie Enhanced API",
    description="Advanced AI-Powered Healthcare Platform with Real-Time Genomic Analysis",
    version="2.0.0-enhanced",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
enhanced_processor = EnhancedGenomicProcessor()
variant_annotator = VariantAnnotator()
ml_service = MLPredictionService()
report_generator = ReportGenerator()

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0-enhanced",
        "services": {
            "enhanced_processor": "initialized",
            "variant_annotator": "initialized",
            "ml_service": "initialized",
            "report_generator": "initialized"
        }
    }

# Enhanced Genomic Analysis Endpoints
@app.post("/api/enhanced-genomic/analyze")
async def analyze_vcf_comprehensive(
    user_id: str,
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
):
    """
    Comprehensive VCF analysis endpoint
    Provides real-time disease risk prediction and variant annotation
    """
    try:
        # Validate file type
        if not file.filename.lower().endswith(('.vcf', '.vcf.gz')):
            raise HTTPException(
                status_code=400,
                detail="Only VCF files are supported for comprehensive analysis"
            )
        
        logger.info(f"Starting comprehensive VCF analysis for user {user_id}, file: {file.filename}")
        
        # Read file content
        file_content = await file.read()
        file_size = len(file_content)
        
        # Create database record
        genomic_data = GenomicData(
            user_id=user_id,
            filename=file.filename,
            file_url=f"memory_upload_{int(datetime.now().timestamp())}",
            status="processing",
            metadata_json=json.dumps({
                "file_size_bytes": file_size,
                "analysis_type": "comprehensive",
                "uploaded_at": datetime.now().isoformat()
            })
        )
        
        db.add(genomic_data)
        db.commit()
        db.refresh(genomic_data)
        
        # Run comprehensive analysis
        result = await enhanced_processor.process_vcf_comprehensive(
            vcf_content=file_content,
            filename=file.filename,
            user_id=user_id,
            target_time=60.0
        )
        
        # Update database with results
        if result.get("status") == "success":
            genomic_data.status = "completed"
            genomic_data.results_json = json.dumps(result)
            genomic_data.analysis_completed_at = datetime.utcnow()
        else:
            genomic_data.status = "failed"
            genomic_data.error_message = result.get("error", "Unknown error")
        
        db.commit()
        
        logger.info(f"✅ Comprehensive analysis completed for genomic_data_id: {genomic_data.id}")
        
        return {
            "status": "success",
            "analysis_id": genomic_data.id,
            "message": "Comprehensive VCF analysis completed successfully",
            "processing_time": result.get("processing_time_seconds", 0),
            "target_time_met": result.get("target_time_met", False),
            "total_variants": result.get("total_variants", 0),
            "diseases_analyzed": list(result.get("ml_predictions", {}).keys())
        }
        
    except Exception as e:
        logger.error(f"❌ Error in comprehensive analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/api/enhanced-genomic/capabilities")
async def get_analysis_capabilities():
    """Get information about analysis capabilities"""
    try:
        capabilities = enhanced_processor.get_processing_capabilities()
        return {
            "status": "success",
            "capabilities": capabilities
        }
    except Exception as e:
        logger.error(f"Error getting capabilities: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving capabilities")

@app.get("/api/enhanced-genomic/status/{analysis_id}")
async def get_analysis_status(analysis_id: int, db: Session = Depends(get_db)):
    """Get status of comprehensive analysis"""
    try:
        genomic_data = db.query(GenomicData).filter(GenomicData.id == analysis_id).first()
        
        if not genomic_data:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        return {
            "analysis_id": analysis_id,
            "status": genomic_data.status,
            "filename": genomic_data.filename,
            "uploaded_at": genomic_data.uploaded_at.isoformat() if genomic_data.uploaded_at else None,
            "completed_at": genomic_data.analysis_completed_at.isoformat() if genomic_data.analysis_completed_at else None,
            "error_message": genomic_data.error_message,
            "has_results": genomic_data.results_json is not None
        }
        
    except Exception as e:
        logger.error(f"Error getting analysis status: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving analysis status")

@app.get("/api/enhanced-genomic/results/{analysis_id}")
async def get_analysis_results(analysis_id: int, db: Session = Depends(get_db)):
    """Get comprehensive analysis results"""
    try:
        genomic_data = db.query(GenomicData).filter(GenomicData.id == analysis_id).first()
        
        if not genomic_data:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        if genomic_data.status != "completed":
            raise HTTPException(
                status_code=400,
                detail=f"Analysis is not complete. Current status: {genomic_data.status}"
            )
        
        if not genomic_data.results_json:
            raise HTTPException(status_code=404, detail="Analysis results not found")
        
        # Parse results JSON
        try:
            results = json.loads(genomic_data.results_json)
            return {
                "status": "success",
                "analysis_id": analysis_id,
                "results": results
            }
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail="Error parsing analysis results")
        
    except Exception as e:
        logger.error(f"Error getting analysis results: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving analysis results")

# ML Model Information Endpoints
@app.get("/api/ml/models")
async def get_ml_models():
    """Get information about available ML models"""
    try:
        model_info = ml_service.get_model_info()
        return {
            "status": "success",
            "models": model_info
        }
    except Exception as e:
        logger.error(f"Error getting ML model info: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving ML model information")

# Variant Annotation Endpoints
@app.post("/api/variants/annotate")
async def annotate_variants_batch(variants: List[Dict]):
    """Annotate a batch of variants"""
    try:
        async with variant_annotator as annotator:
            annotated_variants = await annotator.annotate_variants_batch(variants)
            
            # Generate summary
            summary = annotator.get_annotation_summary(annotated_variants)
            
            return {
                "status": "success",
                "annotated_variants": len(annotated_variants),
                "summary": summary,
                "variants": annotated_variants
            }
            
    except Exception as e:
        logger.error(f"Error in variant annotation: {e}")
        raise HTTPException(status_code=500, detail=f"Variant annotation failed: {str(e)}")

# Report Generation Endpoints
@app.post("/api/reports/generate")
async def generate_comprehensive_report(
    user_id: str,
    genomic_data: Dict,
    variant_annotations: List[Dict],
    ml_predictions: Dict,
    processing_time: float
):
    """Generate comprehensive genomic analysis report"""
    try:
        report = report_generator.generate_report(
            user_id=user_id,
            genomic_data=genomic_data,
            variant_annotations=variant_annotations,
            ml_predictions=ml_predictions,
            processing_time=processing_time
        )
        
        return {
            "status": "success",
            "report": report
        }
        
    except Exception as e:
        logger.error(f"Error generating report: {e}")
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")

# Performance Testing Endpoints
@app.post("/api/test/performance")
async def test_processing_performance(
    file: UploadFile = File(...),
    target_time: float = 60.0
):
    """Test processing performance with a VCF file"""
    try:
        if not file.filename.lower().endswith(('.vcf', '.vcf.gz')):
            raise HTTPException(
                status_code=400,
                detail="Only VCF files are supported for performance testing"
            )
        
        file_content = await file.read()
        
        # Run performance test
        start_time = datetime.now()
        result = await enhanced_processor.process_vcf_comprehensive(
            vcf_content=file_content,
            filename=file.filename,
            user_id="test_user",
            target_time=target_time
        )
        end_time = datetime.now()
        
        actual_time = (end_time - start_time).total_seconds()
        
        return {
            "status": "success",
            "test_results": {
                "target_time_seconds": target_time,
                "actual_time_seconds": actual_time,
                "target_met": actual_time <= target_time,
                "performance_score": max(0, 100 - ((actual_time - target_time) / target_time) * 100),
                "analysis_result": result
            }
        }
        
    except Exception as e:
        logger.error(f"Error in performance testing: {e}")
        raise HTTPException(status_code=500, detail=f"Performance test failed: {str(e)}")

# API Information Endpoint
@app.get("/api/info")
async def get_api_information():
    """Get comprehensive API information"""
    return {
        "api_name": "CuraGenie Enhanced API",
        "version": "2.0.0-enhanced",
        "description": "Advanced AI-Powered Healthcare Platform with Real-Time Genomic Analysis",
        "features": {
            "real_time_vcf_processing": True,
            "variant_annotation": True,
            "ml_disease_prediction": True,
            "comprehensive_reporting": True,
            "performance_optimized": True,
            "target_processing_time": "60 seconds"
        },
        "supported_diseases": ["diabetes", "alzheimer", "brain_tumor"],
        "annotation_sources": ["ClinVar", "gnomAD", "SIFT", "PolyPhen-2"],
        "ml_models": ["GradientBoosting", "RandomForest", "Neural Networks"],
        "endpoints": [
            "/api/enhanced-genomic/analyze",
            "/api/enhanced-genomic/capabilities",
            "/api/enhanced-genomic/status/{id}",
            "/api/enhanced-genomic/results/{id}",
            "/api/ml/models",
            "/api/variants/annotate",
            "/api/reports/generate",
            "/api/test/performance"
        ]
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    logger.info(f"🚀 Starting Enhanced CuraGenie API on port {port}")
    logger.info(f"📊 Target processing time: 60 seconds")
    logger.info(f"🧬 Supported diseases: Diabetes, Alzheimer's, Brain Tumors")
    logger.info(f"🔬 Annotation sources: ClinVar, gnomAD, SIFT, PolyPhen-2")
    
    uvicorn.run(
        "main_enhanced:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )
