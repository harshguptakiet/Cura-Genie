"""
Comprehensive Input Validation Framework for CuraGenie

This module provides:
- Custom validators for domain-specific data (emails, genomic files, etc.)
- Input sanitization utilities (HTML, SQL, file names)
- Validation error handling middleware
- Request size limits and security checks
"""

import re
import html
import os
import mimetypes
from typing import Any, Optional, List, Dict, Union
from pathlib import Path
from datetime import datetime, date
from pydantic import BaseModel, validator, Field, ValidationError
from fastapi import HTTPException, Request
import logging

logger = logging.getLogger(__name__)

# Constants for validation
MAX_REQUEST_SIZE = 100 * 1024 * 1024  # 100MB
MAX_FILENAME_LENGTH = 255
MAX_DESCRIPTION_LENGTH = 1000
MAX_EMAIL_LENGTH = 255
MAX_USERNAME_LENGTH = 50
MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_LENGTH = 128

# Allowed file extensions and MIME types
ALLOWED_GENOMIC_EXTENSIONS = {
    '.vcf', '.vcf.gz', '.fastq', '.fastq.gz', '.fq', '.fq.gz',
    '.bam', '.sam', '.fa', '.fasta', '.txt', '.csv'
}

ALLOWED_MRI_EXTENSIONS = {
    '.dcm', '.nii', '.nii.gz', '.jpg', '.jpeg', '.png', '.tiff', '.tif'
}

ALLOWED_GENOMIC_MIME_TYPES = {
    'text/plain', 'application/gzip', 'application/x-gzip',
    'application/octet-stream', 'text/csv'
}

ALLOWED_MRI_MIME_TYPES = {
    'application/dicom', 'image/jpeg', 'image/png', 'image/tiff',
    'application/octet-stream'
}

# File size limits
MAX_GENOMIC_FILE_SIZE = 500 * 1024 * 1024  # 500MB
MAX_MRI_FILE_SIZE = 100 * 1024 * 1024  # 100MB

class InputSanitizer:
    """Utility class for sanitizing user input"""
    
    @staticmethod
    def sanitize_html(text: str) -> str:
        """Remove HTML tags and escape special characters"""
        if not text:
            return text
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        # Escape HTML entities
        return html.escape(text)
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Create safe filename for storage"""
        if not filename:
            return filename
        # Remove path traversal attempts
        filename = os.path.basename(filename)
        # Remove dangerous characters
        filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
        # Limit length
        return filename[:MAX_FILENAME_LENGTH]
    
    @staticmethod
    def sanitize_sql_input(text: str) -> str:
        """Basic SQL injection prevention (use parameterized queries instead)"""
        if not text:
            return text
        # Remove common SQL injection patterns
        dangerous_patterns = [
            r'(\b(union|select|insert|update|delete|drop|create|alter|exec|execute)\b)',
            r'(\b(and|or)\s+\d+\s*=\s*\d+)',
            r'(\b(and|or)\s+\d+\s*=\s*\d+\s*--)',
            r'(\b(and|or)\s+\d+\s*=\s*\d+\s*#)',
            r'(\b(and|or)\s+\d+\s*=\s*\d+\s*/\*)',
            r'(\b(and|or)\s+\d+\s*=\s*\d+\s*\*/)',
        ]
        
        for pattern in dangerous_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        return text
    
    @staticmethod
    def validate_genomic_coordinates(chrom: str, pos: int) -> bool:
        """Validate genomic coordinates are within reasonable ranges"""
        valid_chroms = [str(i) for i in range(1, 23)] + ['X', 'Y', 'MT']
        return chrom in valid_chroms and 1 <= pos <= 300_000_000
    
    @staticmethod
    def validate_email_format(email: str) -> bool:
        """Validate email format using regex"""
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(email_regex, email))
    
    @staticmethod
    def validate_password_strength(password: str) -> Dict[str, bool]:
        """Validate password strength requirements"""
        if not password:
            return {"valid": False, "errors": ["Password cannot be empty"]}
        
        errors = []
        
        if len(password) < MIN_PASSWORD_LENGTH:
            errors.append(f"Password must be at least {MIN_PASSWORD_LENGTH} characters")
        
        if len(password) > MAX_PASSWORD_LENGTH:
            errors.append(f"Password cannot exceed {MAX_PASSWORD_LENGTH} characters")
        
        if not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter")
        
        if not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter")
        
        if not re.search(r'\d', password):
            errors.append("Password must contain at least one number")
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("Password must contain at least one special character")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    @staticmethod
    def validate_username_format(username: str) -> bool:
        """Validate username format"""
        if not username:
            return False
        
        if len(username) < 3:
            return False
        
        if len(username) > MAX_USERNAME_LENGTH:
            return False
        
        # Username can only contain letters, numbers, hyphens, and underscores
        username_regex = r'^[a-zA-Z0-9_-]+$'
        return bool(re.match(username_regex, username))

class FileUploadValidator:
    """Validator for file uploads with comprehensive security checks"""
    
    @staticmethod
    def validate_genomic_file(file: Any, filename: str, content_type: str, file_size: int) -> Dict[str, Any]:
        """Validate genomic file upload with comprehensive checks"""
        errors = []
        
        # Validate file extension
        file_ext = Path(filename).suffixes
        ext = ''.join(file_ext).lower()
        if ext not in ALLOWED_GENOMIC_EXTENSIONS:
            errors.append(f"Invalid file type. Allowed: {', '.join(ALLOWED_GENOMIC_EXTENSIONS)}")
        
        # Validate file size
        if file_size > MAX_GENOMIC_FILE_SIZE:
            errors.append(f"File too large. Maximum size: {MAX_GENOMIC_FILE_SIZE // (1024*1024)}MB")
        
        # Validate MIME type
        if content_type not in ALLOWED_GENOMIC_MIME_TYPES:
            errors.append(f"Invalid MIME type: {content_type}")
        
        # Validate filename
        if len(filename) > MAX_FILENAME_LENGTH:
            errors.append(f"Filename too long. Maximum length: {MAX_FILENAME_LENGTH}")
        
        # Check for suspicious filename patterns
        suspicious_patterns = [
            r'\.\./',  # Path traversal
            r'\.\.\\',  # Windows path traversal
            r'\.exe$',  # Executable files
            r'\.bat$',  # Batch files
            r'\.sh$',   # Shell scripts
            r'\.php$',  # PHP files
            r'\.asp$',  # ASP files
            r'\.jsp$',  # JSP files
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, filename, re.IGNORECASE):
                errors.append("Suspicious filename detected")
                break
        
        if errors:
            raise ValidationError(f"File validation failed: {'; '.join(errors)}")
        
        return {
            "filename": InputSanitizer.sanitize_filename(filename),
            "size": file_size,
            "type": ext,
            "mime_type": content_type,
            "valid": True
        }
    
    @staticmethod
    def validate_mri_file(file: Any, filename: str, content_type: str, file_size: int) -> Dict[str, Any]:
        """Validate MRI file upload with comprehensive checks"""
        errors = []
        
        # Validate file extension
        file_ext = Path(filename).suffixes
        ext = ''.join(file_ext).lower()
        if ext not in ALLOWED_MRI_EXTENSIONS:
            errors.append(f"Invalid file type. Allowed: {', '.join(ALLOWED_MRI_EXTENSIONS)}")
        
        # Validate file size
        if file_size > MAX_MRI_FILE_SIZE:
            errors.append(f"File too large. Maximum size: {MAX_MRI_FILE_SIZE // (1024*1024)}MB")
        
        # Validate MIME type
        if content_type not in ALLOWED_MRI_MIME_TYPES:
            errors.append(f"Invalid MIME type: {content_type}")
        
        # Validate filename
        if len(filename) > MAX_FILENAME_LENGTH:
            errors.append(f"Filename too long. Maximum length: {MAX_FILENAME_LENGTH}")
        
        # Check for suspicious filename patterns
        suspicious_patterns = [
            r'\.\./',  # Path traversal
            r'\.\.\\',  # Windows path traversal
            r'\.exe$',  # Executable files
            r'\.bat$',  # Batch files
            r'\.sh$',   # Shell scripts
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, filename, re.IGNORECASE):
                errors.append("Suspicious filename detected")
                break
        
        if errors:
            raise ValidationError(f"File validation failed: {'; '.join(errors)}")
        
        return {
            "filename": InputSanitizer.sanitize_filename(filename),
            "size": file_size,
            "type": ext,
            "mime_type": content_type,
            "valid": True
        }
    
    @staticmethod
    def validate_file_content(file_content: bytes, file_type: str) -> bool:
        """Basic file content validation"""
        try:
            if file_type.startswith('.vcf'):
                # Check if VCF file starts with expected header
                content_str = file_content[:1024].decode('utf-8', errors='ignore')
                if not content_str.startswith('##fileformat=VCF'):
                    return False
            elif file_type.startswith('.fastq') or file_type.startswith('.fq'):
                # Check if FASTQ file starts with @
                content_str = file_content[:1024].decode('utf-8', errors='ignore')
                if not content_str.startswith('@'):
                    return False
            elif file_type.startswith('.dcm'):
                # Check if DICOM file starts with expected signature
                if not file_content.startswith(b'\x00\x00\x00\x00'):
                    return False
            
            return True
        except Exception:
            return False

class ValidationError(Exception):
    """Custom validation error"""
    def __init__(self, message: str, field: str = None, value: Any = None):
        self.message = message
        self.field = field
        self.value = value
        super().__init__(self.message)

class RequestValidationMiddleware:
    """Middleware to validate all incoming requests"""
    
    @staticmethod
    async def validate_request(request: Request) -> None:
        """Validate incoming request for security and size"""
        
        # Check request size
        content_length = request.headers.get('content-length')
        if content_length and int(content_length) > MAX_REQUEST_SIZE:
            raise HTTPException(
                status_code=413, 
                detail=f"Request too large. Maximum size: {MAX_REQUEST_SIZE // (1024*1024)}MB"
            )
        
        # Check for suspicious patterns in headers
        user_agent = request.headers.get('user-agent', '')
        suspicious_agents = ['sqlmap', 'nikto', 'nmap', 'burp', 'zap']
        
        for agent in suspicious_agents:
            if agent.lower() in user_agent.lower():
                logger.warning(f"Suspicious user agent detected: {user_agent}")
                # Don't block, just log for monitoring
        
        # Check for path traversal attempts
        path = request.url.path
        if '..' in path or '//' in path:
            raise HTTPException(status_code=400, detail="Invalid path")
        
        # Check for suspicious query parameters
        query_params = str(request.query_params)
        suspicious_query_patterns = [
            r'(\b(union|select|insert|update|delete|drop|create|alter|exec|execute)\b)',
            r'(\b(and|or)\s+\d+\s*=\s*\d+)',
            r'(\b(and|or)\s+\d+\s*=\s*\d+\s*--)',
        ]
        
        for pattern in suspicious_query_patterns:
            if re.search(pattern, query_params, re.IGNORECASE):
                logger.warning(f"Suspicious query parameter detected: {query_params}")
                # Don't block, just log for monitoring

# Enhanced Pydantic models with validation
class UserRegistrationRequest(BaseModel):
    """Enhanced user registration request with comprehensive validation"""
    email: str = Field(..., max_length=MAX_EMAIL_LENGTH, description="User email address")
    username: str = Field(..., min_length=3, max_length=MAX_USERNAME_LENGTH, description="Username")
    password: str = Field(..., min_length=MIN_PASSWORD_LENGTH, max_length=MAX_PASSWORD_LENGTH, description="Password")
    role: str = Field(default="patient", description="User role")
    
    @validator('email')
    def validate_email(cls, v):
        if not InputSanitizer.validate_email_format(v):
            raise ValueError('Invalid email format')
        return v.lower().strip()
    
    @validator('password')
    def validate_password(cls, v):
        validation_result = InputSanitizer.validate_password_strength(v)
        if not validation_result["valid"]:
            raise ValueError('; '.join(validation_result["errors"]))
        return v
    
    @validator('username')
    def validate_username(cls, v):
        if not InputSanitizer.validate_username_format(v):
            raise ValueError('Username can only contain letters, numbers, hyphens, and underscores (3-50 characters)')
        return v.strip()
    
    @validator('role')
    def validate_role(cls, v):
        valid_roles = ['patient', 'doctor', 'admin']
        if v not in valid_roles:
            raise ValueError(f'Invalid role. Must be one of: {", ".join(valid_roles)}')
        return v

class UserLoginRequest(BaseModel):
    """Enhanced user login request with validation"""
    email: str = Field(..., max_length=MAX_EMAIL_LENGTH, description="User email address")
    password: str = Field(..., description="User password")
    
    @validator('email')
    def validate_email(cls, v):
        if not InputSanitizer.validate_email_format(v):
            raise ValueError('Invalid email format')
        return v.lower().strip()

class GenomicDataUploadRequest(BaseModel):
    """Enhanced genomic data upload request with validation"""
    user_id: int = Field(..., gt=0, description="User ID")
    file_type: str = Field(..., description="File type (vcf, fastq, etc.)")
    description: Optional[str] = Field(None, max_length=MAX_DESCRIPTION_LENGTH, description="File description")
    
    @validator('file_type')
    def validate_file_type(cls, v):
        valid_types = ['vcf', 'fastq', 'bam', 'fasta', 'txt', 'csv']
        if v.lower() not in valid_types:
            raise ValueError(f'Invalid file type. Must be one of: {", ".join(valid_types)}')
        return v.lower()
    
    @validator('description')
    def validate_description(cls, v):
        if v:
            return InputSanitizer.sanitize_html(v.strip())
        return v

class MRIAnalysisUploadRequest(BaseModel):
    """Enhanced MRI analysis upload request with validation"""
    user_id: int = Field(..., gt=0, description="User ID")
    analysis_type: str = Field(..., description="Type of MRI analysis")
    description: Optional[str] = Field(None, max_length=MAX_DESCRIPTION_LENGTH, description="Analysis description")
    
    @validator('analysis_type')
    def validate_analysis_type(cls, v):
        valid_types = ['brain_tumor', 'alzheimer', 'stroke', 'general']
        if v.lower() not in valid_types:
            raise ValueError(f'Invalid analysis type. Must be one of: {", ".join(valid_types)}')
        return v.lower()
    
    @validator('description')
    def validate_description(cls, v):
        if v:
            return InputSanitizer.sanitize_html(v.strip())
        return v

class ValidationResponse(BaseModel):
    """Standard validation response format"""
    valid: bool
    errors: List[str] = []
    warnings: List[str] = []
    sanitized_data: Optional[Dict[str, Any]] = None

def validate_and_sanitize_input(data: Dict[str, Any], validation_rules: Dict[str, Any]) -> ValidationResponse:
    """Generic input validation and sanitization function"""
    errors = []
    warnings = []
    sanitized_data = {}
    
    try:
        for field, rules in validation_rules.items():
            value = data.get(field)
            
            if field not in data and rules.get('required', False):
                errors.append(f"Field '{field}' is required")
                continue
            
            if value is not None:
                # Type validation
                expected_type = rules.get('type')
                if expected_type and not isinstance(value, expected_type):
                    errors.append(f"Field '{field}' must be of type {expected_type.__name__}")
                    continue
                
                # Length validation
                if isinstance(value, str):
                    min_length = rules.get('min_length')
                    max_length = rules.get('max_length')
                    
                    if min_length and len(value) < min_length:
                        errors.append(f"Field '{field}' must be at least {min_length} characters")
                    
                    if max_length and len(value) > max_length:
                        errors.append(f"Field '{field}' must not exceed {max_length} characters")
                    
                    # Sanitization
                    if rules.get('sanitize_html', False):
                        value = InputSanitizer.sanitize_html(value)
                    
                    if rules.get('sanitize_sql', False):
                        value = InputSanitizer.sanitize_sql_input(value)
                
                # Range validation for numbers
                if isinstance(value, (int, float)):
                    min_val = rules.get('min')
                    max_val = rules.get('max')
                    
                    if min_val is not None and value < min_val:
                        errors.append(f"Field '{field}' must be at least {min_val}")
                    
                    if max_val is not None and value > max_val:
                        errors.append(f"Field '{field}' must not exceed {max_val}")
                
                # Custom validation
                custom_validator = rules.get('custom_validator')
                if custom_validator:
                    try:
                        value = custom_validator(value)
                    except Exception as e:
                        errors.append(f"Field '{field}' validation failed: {str(e)}")
                        continue
                
                sanitized_data[field] = value
        
        return ValidationResponse(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            sanitized_data=sanitized_data
        )
        
    except Exception as e:
        return ValidationResponse(
            valid=False,
            errors=[f"Validation error: {str(e)}"]
        )

