import logging
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import numpy as np
from PIL import Image
import io

from db.database import get_db
from db.models import MlPrediction
from schemas.schemas import MlPredictionResponse, MlInferenceRequest
from cg_worker.tasks import run_ml_inference, run_brain_tumor_inference

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/ml", tags=["ml"])

@router.post("/predict-brain-tumor", status_code=202)
async def predict_brain_tumor(file: UploadFile = File(...)):
    """
    Trigger brain tumor prediction from an uploaded MRI scan.
    """
    contents = await file.read()
    
    # Basic validation for image file
    if not contents:
        raise HTTPException(status_code=400, detail="Empty file uploaded")
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File is not an image")

    # Queue the inference task
    run_brain_tumor_inference.delay(list(contents))
    
    return {
        "message": "Brain tumor prediction started",
        "status": "processing"
    }

@router.post("/trigger-prediction", status_code=202)
async def trigger_ml_prediction(
    request: MlInferenceRequest,
    db: Session = Depends(get_db)
):
    """
    Trigger ML model inference
    Returns immediately and processes in background
    """
    try:
        # Validate clinical data
        required_fields = ["age", "bmi", "glucose_level", "blood_pressure"]
        missing_fields = [field for field in required_fields if field not in request.clinical_data]
        
        if missing_fields:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required clinical data fields: {', '.join(missing_fields)}"
            )
        
        # Validate data types and ranges
        try:
            age = float(request.clinical_data["age"])
            bmi = float(request.clinical_data["bmi"])
            glucose = float(request.clinical_data["glucose_level"])
            bp = float(request.clinical_data["blood_pressure"])
            
            if not (0 < age < 150):
                raise ValueError("Age must be between 0 and 150")
            if not (10 < bmi < 60):
                raise ValueError("BMI must be between 10 and 60")
            if not (50 < glucose < 500):
                raise ValueError("Glucose level must be between 50 and 500")
            if not (60 < bp < 250):
                raise ValueError("Blood pressure must be between 60 and 250")
                
        except (ValueError, TypeError) as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid clinical data: {str(e)}"
            )
        
        # Queue ML inference task
        run_ml_inference.delay(request.user_id, request.clinical_data)
        
        logger.info(f"Queued ML inference for user: {request.user_id}")
        
        return {
            "message": "ML prediction started",
            "status": "processing",
            "user_id": request.user_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error triggering ML prediction: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/predictions/user/{user_id}", response_model=List[MlPredictionResponse])
def get_user_predictions(user_id: str, db: Session = Depends(get_db)):
    """Get all ML predictions for a user"""
    predictions = db.query(MlPrediction).filter(MlPrediction.user_id == user_id).all()
    return predictions

@router.get("/predictions/{prediction_id}", response_model=MlPredictionResponse)
def get_prediction(prediction_id: int, db: Session = Depends(get_db)):
    """Get a specific ML prediction"""
    prediction = db.query(MlPrediction).filter(MlPrediction.id == prediction_id).first()
    if not prediction:
        raise HTTPException(status_code=404, detail="Prediction not found")
    return prediction

@router.delete("/predictions/{prediction_id}")
def delete_prediction(prediction_id: int, db: Session = Depends(get_db)):
    """Delete a specific ML prediction"""
    prediction = db.query(MlPrediction).filter(MlPrediction.id == prediction_id).first()
    if not prediction:
        raise HTTPException(status_code=404, detail="Prediction not found")
    
    db.delete(prediction)
    db.commit()
    
    return {"message": "Prediction deleted successfully"}
