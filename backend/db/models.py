from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.database import Base
import json

class GenomicData(Base):
    __tablename__ = 'genomic_data'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    filename = Column(String, index=True)
    file_url = Column(String, index=True)
    status = Column(String, default='processing')
    metadata_json = Column(Text, default='{}')
    uploaded_at = Column(DateTime, default=None)
    
    # Relationships
    prs_scores = relationship("PrsScore", back_populates="genomic_data")
    # reports relationship removed to avoid circular imports

class PrsScore(Base):
    __tablename__ = 'prs_scores'

    id = Column(Integer, primary_key=True, index=True)
    genomic_data_id = Column(Integer, ForeignKey('genomic_data.id'))
    disease_type = Column(String, index=True)
    score = Column(Float)
    calculated_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    genomic_data = relationship("GenomicData", back_populates="prs_scores")

class MlPrediction(Base):
    __tablename__ = 'ml_predictions'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    prediction = Column(String)
    confidence = Column(Float)

class MRIAnalysis(Base):
    __tablename__ = 'mri_analyses'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    filename = Column(String)
    file_path = Column(String)
    status = Column(String, default='processing')  # processing, analyzing, completed, failed
    metadata_json = Column(Text, default='{}')
    results_json = Column(Text, default='{}')
    overall_risk_level = Column(String)  # low, moderate, high
    confidence_score = Column(Float)
    error_message = Column(Text)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    analysis_started_at = Column(DateTime(timezone=True), default=None)
    analysis_completed_at = Column(DateTime(timezone=True), default=None)
