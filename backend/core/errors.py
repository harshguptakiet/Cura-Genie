"""
CuraGenie Error Handling and Logging Framework
Provides centralized error handling, structured logging, and consistent error responses
"""

import uuid
import traceback
import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional, Union
from enum import Enum
from functools import wraps
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
import sys

from .config import settings


class ErrorCode(Enum):
    """Standardized error codes for the CuraGenie platform"""
    # Validation Errors (1000-1999)
    VALIDATION_ERROR = 1000
    MISSING_REQUIRED_FIELD = 1001
    INVALID_FILE_FORMAT = 1002
    FILE_TOO_LARGE = 1003
    INVALID_EMAIL = 1004
    
    # Authentication Errors (2000-2999)
    AUTHENTICATION_FAILED = 2000
    INVALID_TOKEN = 2001
    TOKEN_EXPIRED = 2002
    INSUFFICIENT_PERMISSIONS = 2003
    SESSION_EXPIRED = 2004
    
    # Processing Errors (3000-3999)
    FILE_PROCESSING_FAILED = 3000
    GENOMIC_ANALYSIS_ERROR = 3001
    ML_MODEL_ERROR = 3002
    UPLOAD_FAILED = 3003
    ANALYSIS_TIMEOUT = 3004
    
    # Database Errors (4000-4999)
    DATABASE_CONNECTION_ERROR = 4000
    DATABASE_QUERY_ERROR = 4001
    TRANSACTION_FAILED = 4002
    CONSTRAINT_VIOLATION = 4003
    
    # External Service Errors (5000-5999)
    S3_UPLOAD_ERROR = 5000
    OPENAI_API_ERROR = 5001
    CELERY_TASK_ERROR = 5002
    EXTERNAL_API_ERROR = 5003
    
    # System Errors (9000-9999)
    INTERNAL_SERVER_ERROR = 9000
    SERVICE_UNAVAILABLE = 9001
    RATE_LIMIT_EXCEEDED = 9002


class CuraGenieError(Exception):
    """Base exception class for CuraGenie platform"""
    
    def __init__(
        self,
        message: str,
        error_code: ErrorCode,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        self.context = context or {}
        super().__init__(self.message)


class ValidationError(CuraGenieError):
    """Raised when input validation fails"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, ErrorCode.VALIDATION_ERROR, 400, details)


class AuthenticationError(CuraGenieError):
    """Raised when authentication fails"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, ErrorCode.AUTHENTICATION_FAILED, 401, details)


class ProcessingError(CuraGenieError):
    """Raised when file processing or analysis fails"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, ErrorCode.FILE_PROCESSING_FAILED, 422, details)


class DatabaseError(CuraGenieError):
    """Raised when database operations fail"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, ErrorCode.DATABASE_QUERY_ERROR, 500, details)


class ExternalServiceError(CuraGenieError):
    """Raised when external service calls fail"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, ErrorCode.EXTERNAL_API_ERROR, 502, details)


class CuraGenieErrorHandler:
    """Centralized error handler for the CuraGenie platform"""
    
    def __init__(self):
        self.logger = self._setup_structured_logging()
        self._setup_error_mapping()
    
    def _setup_structured_logging(self) -> logging.Logger:
        """Setup structured logging with JSON format"""
        logger = logging.getLogger("curagenie_errors")
        logger.setLevel(logging.ERROR)
        
        # Create console handler with JSON formatter
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.ERROR)
        
        # Create JSON formatter
        formatter = logging.Formatter(
            '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": %(message)s}'
        )
        console_handler.setFormatter(formatter)
        
        # Add file handler for production
        if not settings.debug:
            file_handler = logging.FileHandler("logs/errors.log")
            file_handler.setLevel(logging.ERROR)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        
        logger.addHandler(console_handler)
        return logger
    
    def _setup_error_mapping(self):
        """Setup user-friendly error message mapping"""
        self.user_messages = {
            ErrorCode.VALIDATION_ERROR: "The provided data is invalid. Please check your input and try again.",
            ErrorCode.MISSING_REQUIRED_FIELD: "Required information is missing. Please fill in all required fields.",
            ErrorCode.INVALID_FILE_FORMAT: "The file format is not supported. Please upload a valid file.",
            ErrorCode.FILE_TOO_LARGE: "The file is too large. Please upload a smaller file.",
            ErrorCode.AUTHENTICATION_FAILED: "Authentication failed. Please log in again.",
            ErrorCode.INSUFFICIENT_PERMISSIONS: "You don't have permission to perform this action.",
            ErrorCode.FILE_PROCESSING_FAILED: "Failed to process your file. Please try again or contact support.",
            ErrorCode.GENOMIC_ANALYSIS_ERROR: "Genomic analysis failed. Please check your file and try again.",
            ErrorCode.DATABASE_CONNECTION_ERROR: "Service temporarily unavailable. Please try again later.",
            ErrorCode.EXTERNAL_API_ERROR: "External service error. Please try again later.",
            ErrorCode.INTERNAL_SERVER_ERROR: "An unexpected error occurred. Please try again later."
        }
    
    def handle_api_error(
        self, 
        error: Exception, 
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Handle API errors and return structured error response"""
        error_id = str(uuid.uuid4())
        context = context or {}
        
        # Determine error type and status code
        if isinstance(error, CuraGenieError):
            error_type = type(error).__name__
            status_code = error.status_code
            error_code = error.error_code
            details = error.details
        elif isinstance(error, HTTPException):
            error_type = "HTTPException"
            status_code = error.status_code
            error_code = ErrorCode.INTERNAL_SERVER_ERROR
            details = {"detail": error.detail}
        else:
            error_type = type(error).__name__
            status_code = 500
            error_code = ErrorCode.INTERNAL_SERVER_ERROR
            details = {"detail": str(error)}
        
        # Create structured log entry
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": "ERROR",
            "service": "curagenie-backend",
            "error_id": error_id,
            "user_id": context.get("user_id"),
            "endpoint": context.get("endpoint"),
            "error_type": error_type,
            "error_code": error_code.value,
            "message": str(error),
            "status_code": status_code,
            "context": context,
            "stack_trace": traceback.format_exc(),
            "request_id": context.get("request_id")
        }
        
        # Log the error
        self.logger.error(json.dumps(log_entry, default=str))
        
        # Return user-friendly error response
        return {
            "error": True,
            "error_id": error_id,
            "message": self._get_user_friendly_message(error_code),
            "status_code": status_code,
            "details": details if settings.debug else None
        }
    
    def _get_user_friendly_message(self, error_code: ErrorCode) -> str:
        """Get user-friendly error message"""
        return self.user_messages.get(error_code, "An unexpected error occurred. Please try again.")
    
    def _get_error_details(self, error: Exception) -> Dict[str, Any]:
        """Get detailed error information for debugging"""
        return {
            "type": type(error).__name__,
            "message": str(error),
            "traceback": traceback.format_exc()
        }


# Global error handler instance
error_handler = CuraGenieErrorHandler()


def error_handler_decorator(func):
    """Decorator to automatically handle errors in API endpoints"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            # Extract context from request if available
            context = {}
            for arg in args:
                if hasattr(arg, 'url') and hasattr(arg, 'method'):
                    context["endpoint"] = f"{arg.method} {arg.url.path}"
                    break
            
            error_response = error_handler.handle_api_error(e, context)
            return JSONResponse(
                status_code=error_response["status_code"],
                content=error_response
            )
    return wrapper


def get_request_context(request: Request) -> Dict[str, Any]:
    """Extract context information from FastAPI request"""
    return {
        "endpoint": f"{request.method} {request.url.path}",
        "request_id": str(uuid.uuid4()),
        "user_agent": request.headers.get("user-agent"),
        "ip_address": request.client.host if request.client else None,
        "query_params": dict(request.query_params),
        "path_params": dict(request.path_params)
    }


def log_request_info(request: Request, user_id: Optional[str] = None):
    """Log request information for debugging"""
    context = get_request_context(request)
    if user_id:
        context["user_id"] = user_id
    
    logger = logging.getLogger("curagenie_requests")
    logger.info(json.dumps({
        "timestamp": datetime.utcnow().isoformat(),
        "level": "INFO",
        "service": "curagenie-backend",
        "request_id": context["request_id"],
        "user_id": context.get("user_id"),
        "endpoint": context["endpoint"],
        "ip_address": context["ip_address"],
        "user_agent": context["user_agent"]
    }, default=str))


def log_operation_result(
    operation: str,
    success: bool,
    context: Dict[str, Any],
    details: Optional[Dict[str, Any]] = None
):
    """Log operation results for monitoring"""
    logger = logging.getLogger("curagenie_operations")
    
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "level": "INFO" if success else "ERROR",
        "service": "curagenie-backend",
        "operation": operation,
        "success": success,
        "context": context,
        "details": details or {}
    }
    
    if success:
        logger.info(json.dumps(log_entry, default=str))
    else:
        logger.error(json.dumps(log_entry, default=str))
