import uuid
import logging
import json
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import boto3
from botocore.exceptions import ClientError

from db.database import get_db
from db.models import GenomicData
from schemas.schemas import GenomicDataResponse, UploadResponse
from core.config import settings
from cg_worker.tasks import process_genomic_file

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/genomic-data", tags=["genomic-data"])

# Initialize S3 client
s3_client = boto3.client(
    's3',
    aws_access_key_id=settings.aws_access_key_id,
    aws_secret_access_key=settings.aws_secret_access_key,
    region_name=settings.aws_region
)

@router.post("/upload", response_model=UploadResponse, status_code=202)
async def upload_genomic_file(
    user_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Non-blocking genomic file upload endpoint
    Immediately uploads to S3 and queues background processing
    """
    try:
        # Validate file type
        allowed_extensions = ['.vcf', '.fastq', '.fq', '.vcf.gz', '.fastq.gz']
        file_extension = '.' + file.filename.lower().split('.')[-1]
        if not any(file.filename.lower().endswith(ext.lower()) for ext in allowed_extensions):
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Generate unique file key for S3
        file_uuid = str(uuid.uuid4())
        s3_key = f"users/{user_id}/uploads/{file_uuid}_{file.filename}"
        
        logger.info(f"Starting upload for user {user_id}, file: {file.filename}")
        
        # Read file content
        file_content = await file.read()
        file_size = len(file_content)
        
        # Upload to S3
        try:
            s3_client.put_object(
                Bucket=settings.s3_bucket_name,
                Key=s3_key,
                Body=file_content,
                ContentType=file.content_type or 'application/octet-stream'
            )
            logger.info(f"Successfully uploaded {file.filename} to S3: {s3_key}")
        except ClientError as e:
            logger.error(f"Failed to upload to S3: {e}")
            raise HTTPException(status_code=500, detail="Failed to upload file to storage")
        
        # Create database record
        genomic_data = GenomicData(
            user_id=user_id,
            filename=file.filename,
            file_url=s3_key,  # Store S3 key as file_url
            status="processing",
            metadata_json=json.dumps({"file_size_bytes": file_size, "uploaded_at": str(uuid.uuid4())})
        )
        
        db.add(genomic_data)
        db.commit()
        db.refresh(genomic_data)
        
        # Queue background processing task
        process_genomic_file.delay(genomic_data.id)
        
        logger.info(f"Queued processing for genomic_data_id: {genomic_data.id}")
        
        return UploadResponse(
            id=genomic_data.id,
            message="File uploaded successfully. Processing started.",
            status="processing"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during upload: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during upload")

@router.get("/user/{user_id}", response_model=List[GenomicDataResponse])
def get_user_genomic_data(user_id: str, db: Session = Depends(get_db)):
    """Get all genomic data records for a user"""
    genomic_data = db.query(GenomicData).filter(GenomicData.user_id == user_id).all()
    return genomic_data

@router.get("/{genomic_data_id}", response_model=GenomicDataResponse)
def get_genomic_data(genomic_data_id: int, db: Session = Depends(get_db)):
    """Get a specific genomic data record"""
    genomic_data = db.query(GenomicData).filter(GenomicData.id == genomic_data_id).first()
    if not genomic_data:
        raise HTTPException(status_code=404, detail="Genomic data not found")
    return genomic_data
