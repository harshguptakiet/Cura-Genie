"""
Error Handling Utilities for CuraGenie API Endpoints
Provides common error handling patterns and helper functions
"""

import functools
import time
from typing import Callable, Any, Dict, Optional
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse

from .errors import (
    CuraGenieError, ValidationError, AuthenticationError,
    ProcessingError, DatabaseError, ExternalServiceError,
    log_operation_result, get_request_context
)
from .middleware import get_request_id


def handle_errors(func: Callable) -> Callable:
    """Decorator to handle errors in API endpoints with proper logging"""
    
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        request = None
        
        # Extract request object from args
        for arg in args:
            if hasattr(arg, 'url') and hasattr(arg, 'method'):
                request = arg
                break
        
        try:
            result = await func(*args, **kwargs)
            
            # Log successful operation
            if request:
                process_time = time.time() - start_time
                log_operation_result(
                    operation=f"api_{func.__name__}",
                    success=True,
                    context={
                        "request_id": get_request_id(request),
                        "endpoint": f"{request.method} {request.url.path}",
                        "process_time": process_time
                    }
                )
            
            return result
            
        except CuraGenieError as e:
            # Log CuraGenie-specific errors
            if request:
                process_time = time.time() - start_time
                log_operation_result(
                    operation=f"api_{func.__name__}",
                    success=False,
                    context={
                        "request_id": get_request_id(request),
                        "endpoint": f"{request.method} {request.url.path}",
                        "error_type": type(e).__name__,
                        "error_message": str(e),
                        "process_time": process_time
                    }
                )
            
            # Re-raise for the exception handler to catch
            raise
            
        except Exception as e:
            # Log unexpected errors
            if request:
                process_time = time.time() - start_time
                log_operation_result(
                    operation=f"api_{func.__name__}",
                    success=False,
                    context={
                        "request_id": get_request_id(request),
                        "endpoint": f"{request.method} {request.url.path}",
                        "error_type": type(e).__name__,
                        "error_message": str(e),
                        "process_time": process_time
                    }
                )
            
            # Re-raise for the exception handler to catch
            raise
    
    return wrapper


def validate_file_upload(
    file_size: int,
    max_size: int = 100 * 1024 * 1024,  # 100MB default
    allowed_types: list = None
) -> None:
    """Validate file upload parameters"""
    
    if file_size > max_size:
        raise ValidationError(
            f"File size {file_size} bytes exceeds maximum allowed size of {max_size} bytes",
            details={
                "file_size": file_size,
                "max_size": max_size,
                "allowed_types": allowed_types
            }
        )
    
    if allowed_types and not any(file_size > 0 for _ in allowed_types):
        raise ValidationError(
            "File type not allowed",
            details={
                "file_size": file_size,
                "allowed_types": allowed_types
            }
        )


def validate_user_permissions(
    user_id: int,
    required_role: str = None,
    resource_owner_id: int = None
) -> None:
    """Validate user permissions for accessing resources"""
    
    if user_id is None:
        raise AuthenticationError("User not authenticated")
    
    if required_role and user_id != 1:  # Assuming user 1 is admin for demo
        raise AuthenticationError(
            f"Insufficient permissions. Required role: {required_role}",
            details={
                "user_id": user_id,
                "required_role": required_role,
                "current_role": "patient"  # Demo assumption
            }
        )
    
    if resource_owner_id and user_id != resource_owner_id:
        raise AuthenticationError(
            "Access denied. You can only access your own resources.",
            details={
                "user_id": user_id,
                "resource_owner_id": resource_owner_id
            }
        )


def safe_database_operation(operation_name: str):
    """Decorator to safely handle database operations with retry logic"""
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            max_retries = 3
            retry_delay = 0.1
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        # Last attempt failed
                        raise DatabaseError(
                            f"Database operation '{operation_name}' failed after {max_retries} attempts: {e}",
                            details={
                                "operation": operation_name,
                                "attempts": max_retries,
                                "error": str(e)
                            }
                        )
                    
                    # Wait before retry
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
        
        return wrapper
    return decorator


def log_operation_with_context(
    operation: str,
    success: bool,
    request: Request,
    details: Dict[str, Any] = None
):
    """Log operation with request context"""
    
    context = {
        "request_id": get_request_id(request),
        "endpoint": f"{request.method} {request.url.path}",
        "user_agent": request.headers.get("user-agent"),
        "ip_address": request.client.host if request.client else None
    }
    
    log_operation_result(operation, success, context, details)


def create_success_response(
    data: Any,
    message: str = "Operation completed successfully",
    request: Request = None
) -> Dict[str, Any]:
    """Create a standardized success response"""
    
    response = {
        "success": True,
        "message": message,
        "data": data
    }
    
    if request:
        response["request_id"] = get_request_id(request)
    
    return response


def create_error_response(
    message: str,
    error_code: str = "UNKNOWN_ERROR",
    details: Dict[str, Any] = None,
    request: Request = None
) -> Dict[str, Any]:
    """Create a standardized error response"""
    
    response = {
        "success": False,
        "error": True,
        "message": message,
        "error_code": error_code
    }
    
    if details:
        response["details"] = details
    
    if request:
        response["request_id"] = get_request_id(request)
    
    return response


def handle_external_service_error(
    service_name: str,
    operation: str,
    error: Exception,
    request: Request = None
) -> None:
    """Handle external service errors with proper logging"""
    
    error_details = {
        "service": service_name,
        "operation": operation,
        "error_type": type(error).__name__,
        "error_message": str(error)
    }
    
    if request:
        error_details["request_id"] = get_request_id(request)
    
    log_operation_result(
        operation=f"external_service_{operation}",
        success=False,
        context=error_details
    )
    
    raise ExternalServiceError(
        f"{service_name} service error during {operation}: {str(error)}",
        details=error_details
    )


def validate_required_fields(data: Dict[str, Any], required_fields: list) -> None:
    """Validate that all required fields are present in the data"""
    
    missing_fields = []
    for field in required_fields:
        if field not in data or data[field] is None:
            missing_fields.append(field)
    
    if missing_fields:
        raise ValidationError(
            f"Missing required fields: {', '.join(missing_fields)}",
            details={
                "missing_fields": missing_fields,
                "required_fields": required_fields,
                "provided_fields": list(data.keys())
            }
        )


def sanitize_error_message(message: str, debug: bool = False) -> str:
    """Sanitize error messages for production vs debug environments"""
    
    if debug:
        return message
    
    # Remove sensitive information in production
    sensitive_patterns = [
        "password", "token", "secret", "key", "credential"
    ]
    
    for pattern in sensitive_patterns:
        if pattern.lower() in message.lower():
            return "An error occurred. Please check your input and try again."
    
    return message
