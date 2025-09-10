"""
Feedback API endpoints for CuraGenie
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/feedback", tags=["feedback"])

class FeedbackSubmission(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    feedback_type: str  # "bug_report", "feature_request", "general_feedback"
    message: str
    rating: Optional[int] = None  # 1-5 stars

class FeedbackResponse(BaseModel):
    success: bool
    message: str
    feedback_id: Optional[str] = None

@router.post("/submit", response_model=FeedbackResponse)
async def submit_feedback(feedback: FeedbackSubmission):
    """
    Submit user feedback for CuraGenie platform
    """
    try:
        # Validate feedback type
        valid_types = ["bug_report", "feature_request", "general_feedback"]
        if feedback.feedback_type not in valid_types:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid feedback type. Must be one of: {', '.join(valid_types)}"
            )
        
        # Validate rating if provided
        if feedback.rating is not None and (feedback.rating < 1 or feedback.rating > 5):
            raise HTTPException(
                status_code=400,
                detail="Rating must be between 1 and 5"
            )
        
        # Validate message length
        if len(feedback.message.strip()) < 10:
            raise HTTPException(
                status_code=400,
                detail="Message must be at least 10 characters long"
            )
        
        # Generate a simple feedback ID (in production, you'd use a proper ID generator)
        feedback_id = f"FB_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Log the feedback (in production, you'd save to database)
        logger.info(f"Feedback received - ID: {feedback_id}, Type: {feedback.feedback_type}, Rating: {feedback.rating}")
        logger.info(f"Message: {feedback.message[:100]}...")
        
        # Here you would typically:
        # 1. Save to database
        # 2. Send email notification to support team
        # 3. Store in analytics system
        
        return FeedbackResponse(
            success=True,
            message="Thank you for your feedback! We'll review it and get back to you if needed.",
            feedback_id=feedback_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing feedback: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing your feedback. Please try again."
        )

@router.get("/health")
async def feedback_health():
    """
    Health check for feedback service
    """
    return {"status": "healthy", "service": "feedback"}
