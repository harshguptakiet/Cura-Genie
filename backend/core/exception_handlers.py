"""
Global Exception Handlers for CuraGenie FastAPI Application
Provides centralized exception handling for all unhandled errors
"""

import logging
from typing import Dict, Any
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

from .errors import error_handler, CuraGenieError, ErrorCode
from .middleware import get_request_id

logger = logging.getLogger(__name__)


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors"""
    context = {
        "request_id": get_request_id(request),
        "endpoint": f"{request.method} {request.url.path}",
        "user_id": getattr(request.state, "user_id", None),
        "validation_errors": exc.errors()
    }
    
    error_response = error_handler.handle_api_error(
        CuraGenieError(
            message="Validation error in request data",
            error_code=ErrorCode.VALIDATION_ERROR,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details={"validation_errors": exc.errors()}
        ),
        context
    )
    
    return JSONResponse(
        status_code=error_response["status_code"],
        content=error_response
    )


async def pydantic_validation_exception_handler(request: Request, exc: ValidationError):
    """Handle Pydantic model validation errors"""
    context = {
        "request_id": get_request_id(request),
        "endpoint": f"{request.method} {request.url.path}",
        "user_id": getattr(request.state, "user_id", None),
        "validation_errors": exc.errors()
    }
    
    error_response = error_handler.handle_api_error(
        CuraGenieError(
            message="Data validation failed",
            error_code=ErrorCode.VALIDATION_ERROR,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details={"validation_errors": exc.errors()}
        ),
        context
    )
    
    return JSONResponse(
        status_code=error_response["status_code"],
        content=error_response
    )


async def curagenie_exception_handler(request: Request, exc: CuraGenieError):
    """Handle CuraGenie-specific exceptions"""
    context = {
        "request_id": get_request_id(request),
        "endpoint": f"{request.method} {request.url.path}",
        "user_id": getattr(request.state, "user_id", None)
    }
    
    error_response = error_handler.handle_api_error(exc, context)
    
    return JSONResponse(
        status_code=error_response["status_code"],
        content=error_response
    )


async def general_exception_handler(request: Request, exc: Exception):
    """Handle all other unhandled exceptions"""
    context = {
        "request_id": get_request_id(request),
        "endpoint": f"{request.method} {request.url.path}",
        "user_id": getattr(request.state, "user_id", None)
    }
    
    error_response = error_handler.handle_api_error(exc, context)
    
    return JSONResponse(
        status_code=error_response["status_code"],
        content=error_response
    )


def setup_exception_handlers(app):
    """Setup all exception handlers for the FastAPI application"""
    
    # Add exception handlers
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(ValidationError, pydantic_validation_exception_handler)
    app.add_exception_handler(CuraGenieError, curagenie_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
    
    logger.info("Exception handlers configured successfully")


def create_error_response(
    message: str,
    error_code: ErrorCode,
    status_code: int = 500,
    details: Dict[str, Any] = None,
    request: Request = None
) -> JSONResponse:
    """Create a standardized error response"""
    
    context = {}
    if request:
        context = {
            "request_id": get_request_id(request),
            "endpoint": f"{request.method} {request.url.path}",
            "user_id": getattr(request.state, "user_id", None)
        }
    
    error_response = error_handler.handle_api_error(
        CuraGenieError(
            message=message,
            error_code=error_code,
            status_code=status_code,
            details=details or {}
        ),
        context
    )
    
    return JSONResponse(
        status_code=error_response["status_code"],
        content=error_response
    )
