from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum
import re

class UserRole(str, Enum):
    PATIENT = "patient"
    DOCTOR = "doctor"
    ADMIN = "admin"

# User Authentication Schemas
class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    role: UserRole = UserRole.PATIENT
    
    @validator('password')
    def validate_password(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one symbol')
        return v
    
    @validator('username')
    def validate_username(cls, v):
        """Validate username format"""
        if len(v) < 3:
            raise ValueError('Username must be at least 3 characters long')
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username can only contain letters, numbers, and underscores')
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str
    remember_me: bool = False

class SocialAuth(BaseModel):
    provider: str  # google, facebook, github
    token: str
    email: EmailStr
    name: str
    avatar_url: Optional[str] = None

class ForgotPassword(BaseModel):
    email: EmailStr

class ResetPassword(BaseModel):
    token: str
    new_password: str
    
    @validator('new_password')
    def validate_new_password(cls, v):
        """Validate new password strength"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one symbol')
        return v

class ChangePassword(BaseModel):
    current_password: str
    new_password: str
    
    @validator('new_password')
    def validate_new_password(cls, v):
        """Validate new password strength"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one symbol')
        return v

# Enhanced Token Schemas
class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds
    user_id: int
    role: str
    email: str

class TokenRefresh(BaseModel):
    refresh_token: str

class TokenData(BaseModel):
    email: Optional[str] = None
    user_id: Optional[int] = None
    role: Optional[str] = None

# Legacy Token Schema (for backward compatibility)
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    role: str

class User(BaseModel):
    id: int
    email: str
    username: str
    role: UserRole
    is_active: bool
    is_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Patient Profile Schemas
class PatientProfileCreate(BaseModel):
    first_name: str
    last_name: str
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    blood_type: Optional[str] = None
    allergies: Optional[str] = None
    current_medications: Optional[str] = None
    medical_history: Optional[str] = None
    emergency_contact: Optional[str] = None

class PatientProfileUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    blood_type: Optional[str] = None
    allergies: Optional[str] = None
    current_medications: Optional[str] = None
    medical_history: Optional[str] = None
    emergency_contact: Optional[str] = None

class PatientProfile(BaseModel):
    id: int
    user_id: int
    first_name: str
    last_name: str
    date_of_birth: Optional[datetime]
    gender: Optional[str]
    phone: Optional[str]
    address: Optional[str]
    blood_type: Optional[str]
    allergies: Optional[str]
    current_medications: Optional[str]
    medical_history: Optional[str]
    emergency_contact: Optional[str]
    avatar_url: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# Medical Report Schemas
class MedicalReportCreate(BaseModel):
    genomic_data_id: Optional[int] = None
    report_title: str
    report_type: str
    report_data: Optional[str] = None
    summary: Optional[str] = None
    recommendations: Optional[str] = None

class MedicalReport(BaseModel):
    id: int
    user_id: int
    genomic_data_id: Optional[int]
    report_title: str
    report_type: str
    report_data: Optional[str]
    summary: Optional[str]
    recommendations: Optional[str]
    status: str
    generated_at: datetime
    
    class Config:
        from_attributes = True

# Combined User with Profile
class UserWithProfile(BaseModel):
    id: int
    email: str
    username: str
    role: UserRole
    is_active: bool
    is_verified: bool
    created_at: datetime
    profile: Optional[PatientProfile] = None
    
    class Config:
        from_attributes = True

# Dashboard Data
class UserDashboard(BaseModel):
    user: UserWithProfile
    total_uploads: int
    total_reports: int
    recent_uploads: List[dict]
    recent_reports: List[MedicalReport]
    prs_scores: List[dict]

# Password Reset Schemas
class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    email: EmailStr
    reset_token: str
    new_password: str
    
    @validator('new_password')
    def validate_new_password(cls, v):
        """Validate new password strength"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one symbol')
        return v

# Authentication Response Schemas
class AuthResponse(BaseModel):
    user: User
    tokens: TokenResponse
    message: str = "Authentication successful"

class PasswordChangeResponse(BaseModel):
    message: str = "Password changed successfully"
    timestamp: datetime

class PasswordResetResponse(BaseModel):
    message: str = "Password reset email sent"
    timestamp: datetime
