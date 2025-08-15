"""
CuraGenie Middleware for Request Tracking and Error Handling
Provides request ID tracking, logging, and error handling middleware
"""

import uuid
import time
import logging
from typing import Callable
from fastapi import Request, Response
from fastapi.middleware.base import BaseHTTPMiddleware
from starlette.middleware.base import RequestResponseEndpoint
from starlette.types import ASGIApp

from .errors import get_request_context, log_request_info, log_operation_result
from .config import settings


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware to add request ID to all requests"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Add request ID to response headers
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        
        return response


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for request/response logging"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.logger = logging.getLogger("curagenie_middleware")
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start_time = time.time()
        
        # Log request start
        if settings.enable_request_logging:
            context = get_request_context(request)
            context["request_id"] = request.state.request_id
            log_request_info(request, context.get("user_id"))
        
        # Process request
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # Log successful request
            if settings.enable_request_logging:
                log_operation_result(
                    operation="http_request",
                    success=True,
                    context={
                        "request_id": request.state.request_id,
                        "method": request.method,
                        "path": request.url.path,
                        "status_code": response.status_code,
                        "process_time": process_time
                    }
                )
            
            # Add process time to response headers
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            
            # Log failed request
            if settings.enable_request_logging:
                log_operation_result(
                    operation="http_request",
                    success=False,
                    context={
                        "request_id": request.state.request_id,
                        "method": request.method,
                        "path": request.url.path,
                        "error": str(e),
                        "process_time": process_time
                    }
                )
            
            # Re-raise the exception for the error handler to catch
            raise


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Middleware for centralized error handling"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        try:
            return await call_next(request)
        except Exception as e:
            # Let the global exception handler deal with it
            # This middleware ensures all errors are caught
            raise


def setup_middleware(app: ASGIApp) -> None:
    """Setup all middleware for the FastAPI application"""
    app.add_middleware(ErrorHandlingMiddleware)
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(RequestIDMiddleware)


def get_request_id(request: Request) -> str:
    """Get the request ID from the request state"""
    return getattr(request.state, "request_id", str(uuid.uuid4()))


def log_api_call(
    request: Request,
    operation: str,
    success: bool,
    details: dict = None
):
    """Log API call results for monitoring"""
    if not settings.enable_operation_logging:
        return
    
    context = {
        "request_id": get_request_id(request),
        "endpoint": f"{request.method} {request.url.path}",
        "user_agent": request.headers.get("user-agent"),
        "ip_address": request.client.host if request.client else None
    }
    
    log_operation_result(operation, success, context, details)
