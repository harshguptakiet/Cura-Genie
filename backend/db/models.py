"""
Comprehensive Database Models for CuraGenie

This module defines all database models with:
- Proper relationships and foreign keys
- Unique constraints to prevent duplicates
- Data validation constraints
- Proper indexing for performance
- Enum types for data consistency
"""

import enum
from datetime import datetime
from typing import List, Optional
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, Text, 
    ForeignKey, UniqueConstraint, CheckConstraint, Index,
    Enum as SQLEnum, JSON, BigInteger, text
)
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

# Enum definitions
class UserRole(enum.Enum):
    PATIENT = "patient"
    DOCTOR = "doctor"
    ADMIN = "admin"
    RESEARCHER = "researcher"

class ProcessingStatus(enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class FileType(enum.Enum):
    VCF = "vcf"
    FASTQ = "fastq"
    BAM = "bam"
    SAM = "sam"
    GFF = "gff"
    GTF = "gtf"

class RiskLevel(enum.Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"

class EventType(enum.Enum):
    UPLOAD = "upload"
    ANALYSIS = "analysis"
    LOGIN = "login"
    REGISTRATION = "registration"
    PASSWORD_CHANGE = "password_change"
    PROFILE_UPDATE = "profile_update"

# User Management Models
class User(Base):
    """Enhanced user model with proper relationships and constraints"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.PATIENT, index=True)
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    is_verified = Column(Boolean, nullable=False, default=False)
    is_email_verified = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    last_login = Column(DateTime)
    
    # Profile information
    first_name = Column(String(100))
    last_name = Column(String(100))
    date_of_birth = Column(DateTime)
    gender = Column(String(20))
    phone = Column(String(20))
    
    # Relationships
    genomic_data = relationship("GenomicData", back_populates="user", cascade="all, delete-orphan")
    prs_scores = relationship("PRSScore", back_populates="user", cascade="all, delete-orphan")
    timeline_events = relationship("TimelineEvent", back_populates="user", cascade="all, delete-orphan")
    patient_profiles = relationship("PatientProfile", back_populates="user", cascade="all, delete-orphan")
    medical_reports = relationship("MedicalReport", back_populates="user", cascade="all, delete-orphan")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("length(email) >= 5", name="email_length_check"),
        CheckConstraint("length(username) >= 3", name="username_length_check"),
        CheckConstraint("length(hashed_password) >= 32", name="password_length_check"),
        Index("idx_users_active_verified", "is_active", "is_verified"),
        Index("idx_users_role_active", "role", "is_active"),
    )

class PatientProfile(Base):
    """Patient-specific profile information"""
    __tablename__ = "patient_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    
    # Medical information
    height_cm = Column(Float)
    weight_kg = Column(Float)
    blood_type = Column(String(10))
    allergies = Column(JSON)
    medications = Column(JSON)
    medical_history = Column(JSON)
    
    # Emergency contact
    emergency_contact_name = Column(String(100))
    emergency_contact_phone = Column(String(20))
    emergency_contact_relationship = Column(String(50))
    
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="patient_profiles")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("height_cm > 0", name="positive_height_check"),
        CheckConstraint("weight_kg > 0", name="positive_weight_check"),
    )

# Genomic Data Models
class GenomicData(Base):
    """Enhanced genomic data model with proper relationships"""
    __tablename__ = "genomic_data"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # File information
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_type = Column(SQLEnum(FileType), nullable=False, index=True)
    file_url = Column(Text, nullable=False)
    file_size_bytes = Column(BigInteger)
    
    # Processing information
    status = Column(SQLEnum(ProcessingStatus), nullable=False, default=ProcessingStatus.PENDING, index=True)
    uploaded_at = Column(DateTime, nullable=False, default=func.now(), index=True)
    processed_at = Column(DateTime)
    
    # Analysis results
    metadata_json = Column(JSON)
    total_variants = Column(Integer)
    quality_score = Column(Float)
    processing_errors = Column(Text)
    
    # Relationships
    user = relationship("User", back_populates="genomic_data")
    prs_scores = relationship("PRSScore", back_populates="genomic_data", cascade="all, delete-orphan")
    genomic_variants = relationship("GenomicVariant", back_populates="genomic_data", cascade="all, delete-orphan")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("file_size_bytes > 0", name="positive_file_size_check"),
        CheckConstraint("quality_score >= 0 AND quality_score <= 1", name="quality_score_range_check"),
        Index("idx_genomic_data_user_status", "user_id", "status"),
        Index("idx_genomic_data_type_status", "file_type", "status"),
        Index("idx_genomic_data_uploaded", "uploaded_at"),
    )

class GenomicVariant(Base):
    """Genomic variant model with duplicate prevention"""
    __tablename__ = "genomic_variants"
    
    id = Column(Integer, primary_key=True, index=True)
    genomic_data_id = Column(Integer, ForeignKey("genomic_data.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Variant information
    chromosome = Column(String(10), nullable=False, index=True)
    position = Column(BigInteger, nullable=False, index=True)
    reference = Column(String(100), nullable=False)
    alternative = Column(String(100), nullable=False)
    variant_type = Column(String(50), nullable=False, index=True)
    
    # Quality metrics
    quality = Column(Float)
    filter_status = Column(String(50))
    variant_id = Column(String(100), index=True)
    
    # Additional information
    gene = Column(String(100), index=True)
    transcript = Column(String(100))
    protein_change = Column(String(100))
    clinical_significance = Column(String(50))
    
    # Relationships
    genomic_data = relationship("GenomicData", back_populates="genomic_variants")
    
    # Constraints - Prevent duplicate variants within the same file
    __table_args__ = (
        UniqueConstraint('genomic_data_id', 'chromosome', 'position', 'reference', 'alternative', 
                        name='unique_variant_per_file'),
        CheckConstraint("position > 0", name="positive_position_check"),
        CheckConstraint("quality >= 0", name="non_negative_quality_check"),
        Index("idx_variants_chromosome_position", "chromosome", "position"),
        Index("idx_variants_gene", "gene"),
        Index("idx_variants_type", "variant_type"),
    )

# PRS Scores Models
class PRSScore(Base):
    """PRS score model with duplicate prevention and proper constraints"""
    __tablename__ = "prs_scores"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    genomic_data_id = Column(Integer, ForeignKey("genomic_data.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Score information
    disease_type = Column(String(100), nullable=False, index=True)
    score = Column(Float, nullable=False)
    risk_level = Column(SQLEnum(RiskLevel), nullable=False, index=True)
    percentile = Column(Float)
    variants_used = Column(Integer)
    confidence = Column(Float)
    
    # Calculation metadata
    algorithm_version = Column(String(50))
    reference_population = Column(String(100))
    calculated_at = Column(DateTime, nullable=False, default=func.now(), index=True)
    
    # Relationships
    user = relationship("User", back_populates="prs_scores")
    genomic_data = relationship("GenomicData", back_populates="prs_scores")
    
    # Constraints - Prevent duplicate scores for same user/disease/file combination
    __table_args__ = (
        UniqueConstraint('user_id', 'disease_type', 'genomic_data_id', 
                        name='unique_prs_per_user_disease_file'),
        CheckConstraint("score >= 0.0 AND score <= 1.0", name="score_range_check"),
        CheckConstraint("percentile >= 0.0 AND percentile <= 100.0", name="percentile_range_check"),
        CheckConstraint("confidence >= 0.0 AND confidence <= 1.0", name="confidence_range_check"),
        CheckConstraint("variants_used > 0", name="positive_variants_check"),
        Index("idx_prs_user_disease", "user_id", "disease_type"),
        Index("idx_prs_risk_level", "risk_level"),
        Index("idx_prs_calculated", "calculated_at"),
    )

# Timeline and Events Models
class TimelineEvent(Base):
    """Timeline event model with proper categorization"""
    __tablename__ = "timeline_events"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Event information
    event_type = Column(SQLEnum(EventType), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String(50), default="completed", index=True)
    
    # Metadata
    metadata_json = Column(JSON)
    related_file_id = Column(Integer)
    related_analysis_id = Column(Integer)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=func.now(), index=True)
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="timeline_events")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("length(title) >= 1", name="title_length_check"),
        CheckConstraint("length(description) >= 1", name="description_length_check"),
        Index("idx_timeline_user_type", "user_id", "event_type"),
        Index("idx_timeline_created", "created_at"),
        Index("idx_timeline_status", "status"),
    )

# Medical Reports Models
class MedicalReport(Base):
    """Medical report model for comprehensive health tracking"""
    __tablename__ = "medical_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Report information
    report_type = Column(String(100), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    summary = Column(Text)
    
    # Medical data
    findings = Column(JSON)
    recommendations = Column(JSON)
    risk_factors = Column(JSON)
    
    # Metadata
    doctor_name = Column(String(100))
    hospital_name = Column(String(100))
    report_date = Column(DateTime, nullable=False, default=func.now())
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="medical_reports")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("length(title) >= 1", name="report_title_length_check"),
        CheckConstraint("length(content) >= 1", name="report_content_length_check"),
        Index("idx_reports_user_type", "user_id", "report_type"),
        Index("idx_reports_date", "report_date"),
    )

# Authentication and Security Models
class UserSession(Base):
    """User session tracking for security"""
    __tablename__ = "user_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Session information
    session_token = Column(String(255), nullable=False, unique=True, index=True)
    refresh_token = Column(String(255), unique=True, index=True)
    device_info = Column(JSON)
    ip_address = Column(String(45))
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=func.now())
    expires_at = Column(DateTime, nullable=False, index=True)
    last_used = Column(DateTime, onupdate=func.now())
    
    # Constraints
    __table_args__ = (
        CheckConstraint("expires_at > created_at", name="valid_expiry_check"),
        Index("idx_sessions_user_expires", "user_id", "expires_at"),
        Index("idx_sessions_expires", "expires_at"),
    )

class PasswordResetToken(Base):
    """Password reset token model"""
    __tablename__ = "password_reset_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Token information
    token = Column(String(255), nullable=False, unique=True, index=True)
    is_used = Column(Boolean, nullable=False, default=False)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=func.now())
    expires_at = Column(DateTime, nullable=False, index=True)
    used_at = Column(DateTime)
    
    # Constraints
    __table_args__ = (
        CheckConstraint("expires_at > created_at", name="reset_token_expiry_check"),
        Index("idx_reset_tokens_user", "user_id"),
        Index("idx_reset_tokens_expires", "expires_at"),
    )

# Database initialization function
def init_database():
    """Initialize database with all models"""
    from db.database_manager import db_manager
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        # Create all tables
        Base.metadata.create_all(bind=db_manager.engine)
        
        # Create additional indexes for performance
        with db_manager.get_session_context() as session:
            # Create composite indexes for common query patterns
            session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_prs_user_disease_file 
                ON prs_scores (user_id, disease_type, genomic_data_id)
            """))
            
            session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_variants_file_chrom_pos 
                ON genomic_variants (genomic_data_id, chromosome, position)
            """))
            
            session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_timeline_user_created 
                ON timeline_events (user_id, created_at DESC)
            """))
        
        logger.info("✅ Database initialized successfully with all models and indexes")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize database: {e}")
        raise
