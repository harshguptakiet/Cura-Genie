"""
Enhanced Genomic Analysis API for CuraGenie
Provides comprehensive VCF analysis with real-time ML predictions
"""

import logging
import time
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, Any
import json

from db.database import get_db
from db.models import GenomicData
from schemas.schemas import UploadResponse
from core.config import settings
from services.enhanced_genomic_processor import EnhancedGenomicProcessor

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/enhanced-genomic", tags=["enhanced-genomic"])

# Initialize enhanced processor
enhanced_processor = EnhancedGenomicProcessor()

@router.post("/analyze", response_model=UploadResponse, status_code=202)
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
            file_url=f"memory_upload_{int(time.time())}",
            status="processing",
            metadata_json=json.dumps({
                "file_size_bytes": file_size,
                "analysis_type": "comprehensive",
                "uploaded_at": time.time()
            })
        )
        
        db.add(genomic_data)
        db.commit()
        db.refresh(genomic_data)
        
        # Run comprehensive analysis in background
        if background_tasks:
            background_tasks.add_task(
                run_comprehensive_analysis,
                genomic_data.id,
                file_content,
                file.filename,
                user_id
            )
        else:
            # Run synchronously if no background tasks
            result = await run_comprehensive_analysis(
                genomic_data.id,
                file_content,
                file.filename,
                user_id
            )
            
            if result.get("status") == "success":
                genomic_data.status = "completed"
                genomic_data.results_json = json.dumps(result)
            else:
                genomic_data.status = "failed"
                genomic_data.error_message = result.get("error", "Unknown error")
            
            db.commit()
        
        logger.info(f"Comprehensive analysis started for genomic_data_id: {genomic_data.id}")
        
        return UploadResponse(
            id=genomic_data.id,
            message="Comprehensive VCF analysis started. Results will be available shortly.",
            status="processing"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during comprehensive analysis: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during analysis")

@router.get("/capabilities")
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

@router.get("/status/{analysis_id}")
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
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting analysis status: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving analysis status")

@router.get("/results/{analysis_id}")
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
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting analysis results: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving analysis results")

async def run_comprehensive_analysis(
    genomic_data_id: int,
    file_content: bytes,
    filename: str,
    user_id: str
) -> Dict[str, Any]:
    """Run comprehensive genomic analysis"""
    
    try:
        logger.info(f"Running comprehensive analysis for genomic_data_id: {genomic_data_id}")
        
        # Run enhanced genomic processing
        result = await enhanced_processor.process_vcf_comprehensive(
            vcf_content=file_content,
            filename=filename,
            user_id=user_id,
            target_time=60.0
        )
        
        if result.get("status") == "success":
            logger.info(f"✅ Comprehensive analysis completed for genomic_data_id: {genomic_data_id}")
            logger.info(f"   - Processing time: {result.get('processing_time_seconds', 0):.2f}s")
            logger.info(f"   - Target time met: {result.get('target_time_met', False)}")
            logger.info(f"   - Variants analyzed: {result.get('total_variants', 0)}")
            logger.info(f"   - Diseases predicted: {len(result.get('ml_predictions', {}))}")
        else:
            logger.error(f"❌ Comprehensive analysis failed for genomic_data_id: {genomic_data_id}")
            logger.error(f"   - Error: {result.get('error', 'Unknown error')}")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Error in comprehensive analysis for genomic_data_id {genomic_data_id}: {e}")
        return {"status": "error", "message": str(e)}
