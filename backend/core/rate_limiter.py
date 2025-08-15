"""
Rate Limiting Middleware for CuraGenie Platform
Protects authentication endpoints from brute force attacks and abuse
"""

import time
import asyncio
from typing import Dict, Tuple, Optional
from fastapi import HTTPException, status, Request
from fastapi.responses import JSONResponse
import logging
from collections import defaultdict
import threading

logger = logging.getLogger(__name__)

class RateLimiter:
    """Rate limiter implementation with sliding window"""
    
    def __init__(self):
        self.requests: Dict[str, list] = defaultdict(list)
        self.lock = threading.Lock()
        self.cleanup_interval = 3600  # 1 hour
        self.last_cleanup = time.time()
    
    def _cleanup_old_requests(self):
        """Remove old requests outside the cleanup interval"""
        current_time = time.time()
        if current_time - self.last_cleanup > self.cleanup_interval:
            with self.lock:
                cutoff_time = current_time - max(
                    self.cleanup_interval * 2,  # Keep some history
                    3600  # At least 1 hour
                )
                
                for key in list(self.requests.keys()):
                    self.requests[key] = [
                        req_time for req_time in self.requests[key]
                        if req_time > cutoff_time
                    ]
                    
                    # Remove empty entries
                    if not self.requests[key]:
                        del self.requests[key]
                
                self.last_cleanup = current_time
    
    def is_allowed(self, key: str, max_requests: int, window_seconds: int) -> bool:
        """
        Check if request is allowed based on rate limiting rules
        
        Args:
            key: Unique identifier for the rate limiting (e.g., IP address, user ID)
            max_requests: Maximum number of requests allowed
            window_seconds: Time window in seconds
            
        Returns:
            bool: True if request is allowed, False otherwise
        """
        current_time = time.time()
        cutoff_time = current_time - window_seconds
        
        with self.lock:
            # Clean up old requests
            self.requests[key] = [
                req_time for req_time in self.requests[key]
                if req_time > cutoff_time
            ]
            
            # Check if request is allowed
            if len(self.requests[key]) >= max_requests:
                return False
            
            # Add current request
            self.requests[key].append(current_time)
            return True
    
    def get_remaining_requests(self, key: str, max_requests: int, window_seconds: int) -> int:
        """Get remaining requests allowed for the key"""
        current_time = time.time()
        cutoff_time = current_time - window_seconds
        
        with self.lock:
            valid_requests = [
                req_time for req_time in self.requests[key]
                if req_time > cutoff_time
            ]
            return max(0, max_requests - len(valid_requests))
    
    def get_reset_time(self, key: str, window_seconds: int) -> Optional[float]:
        """Get time when rate limit resets for the key"""
        if not self.requests[key]:
            return None
        
        with self.lock:
            oldest_request = min(self.requests[key])
            return oldest_request + window_seconds

# Global rate limiter instance
rate_limiter = RateLimiter()

def get_client_identifier(request: Request) -> str:
    """
    Get unique identifier for rate limiting based on request
    
    Priority order:
    1. X-Forwarded-For header (for proxied requests)
    2. X-Real-IP header (for nginx proxy)
    3. Client host
    4. Fallback to user agent + timestamp
    """
    # Check for forwarded IP headers
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # Take the first IP in the chain
        client_ip = forwarded_for.split(",")[0].strip()
        return f"ip:{client_ip}"
    
    # Check for real IP header
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return f"ip:{real_ip}"
    
    # Use client host
    if request.client:
        return f"ip:{request.client.host}"
    
    # Fallback to user agent + timestamp
    user_agent = request.headers.get("User-Agent", "unknown")
    timestamp = int(time.time() / 60)  # Round to minute
    return f"ua:{user_agent}:{timestamp}"

def rate_limit(max_requests: int, window_seconds: int):
    """
    Decorator to apply rate limiting to API endpoints
    
    Args:
        max_requests: Maximum number of requests allowed
        window_seconds: Time window in seconds
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Find the request object in arguments
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            
            if not request:
                # Try to find in kwargs
                request = kwargs.get('request')
            
            if not request:
                logger.warning("Rate limiting applied but no request object found")
                return await func(*args, **kwargs)
            
            # Get client identifier
            client_id = get_client_identifier(request)
            
            # Check rate limit
            if not rate_limiter.is_allowed(client_id, max_requests, window_seconds):
                remaining_time = rate_limiter.get_reset_time(client_id, window_seconds)
                reset_time = int(remaining_time) if remaining_time else 0
                
                logger.warning(f"Rate limit exceeded for {client_id}")
                
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "detail": "Rate limit exceeded",
                        "retry_after": reset_time,
                        "limit": max_requests,
                        "window": window_seconds
                    },
                    headers={
                        "Retry-After": str(reset_time),
                        "X-RateLimit-Limit": str(max_requests),
                        "X-RateLimit-Window": str(window_seconds),
                        "X-RateLimit-Reset": str(reset_time)
                    }
                )
            
            # Request allowed, proceed
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator

def rate_limit_by_user(max_requests: int, window_seconds: int):
    """
    Decorator to apply rate limiting based on authenticated user ID
    
    Args:
        max_requests: Maximum number of requests allowed
        window_seconds: Time window in seconds
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Find the current_user in arguments
            current_user = None
            for arg in args:
                if hasattr(arg, 'id') and hasattr(arg, 'email'):
                    current_user = arg
                    break
            
            if not current_user:
                # Try to find in kwargs
                current_user = kwargs.get('current_user')
            
            if not current_user:
                logger.warning("User-based rate limiting applied but no user found")
                return await func(*args, **kwargs)
            
            # Use user ID for rate limiting
            user_id = f"user:{current_user.id}"
            
            # Check rate limit
            if not rate_limiter.is_allowed(user_id, max_requests, window_seconds):
                remaining_time = rate_limiter.get_reset_time(user_id, window_seconds)
                reset_time = int(remaining_time) if remaining_time else 0
                
                logger.warning(f"User rate limit exceeded for user {current_user.email}")
                
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "detail": "Rate limit exceeded for user",
                        "retry_after": reset_time,
                        "limit": max_requests,
                        "window": window_seconds
                    },
                    headers={
                        "Retry-After": str(reset_time),
                        "X-RateLimit-Limit": str(max_requests),
                        "X-RateLimit-Window": str(window_seconds),
                        "X-RateLimit-Reset": str(reset_time)
                    }
                )
            
            # Request allowed, proceed
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator

# Predefined rate limiting configurations
AUTH_RATE_LIMITS = {
    "login": (5, 300),      # 5 attempts per 5 minutes
    "register": (3, 600),   # 3 attempts per 10 minutes
    "password_reset": (3, 3600),  # 3 attempts per hour
    "verify_email": (5, 300),     # 5 attempts per 5 minutes
}

def apply_auth_rate_limits():
    """Apply standard rate limiting to authentication endpoints"""
    return {
        "login": rate_limit(*AUTH_RATE_LIMITS["login"]),
        "register": rate_limit(*AUTH_RATE_LIMITS["register"]),
        "password_reset": rate_limit(*AUTH_RATE_LIMITS["password_reset"]),
        "verify_email": rate_limit(*AUTH_RATE_LIMITS["verify_email"]),
    }

# Utility functions for monitoring
def get_rate_limit_stats() -> Dict[str, Dict]:
    """Get current rate limiting statistics"""
    stats = {}
    
    for key, requests in rate_limiter.requests.items():
        current_time = time.time()
        
        # Calculate stats for different time windows
        windows = {
            "1min": 60,
            "5min": 300,
            "1hour": 3600
        }
        
        window_stats = {}
        for window_name, window_seconds in windows.items():
            cutoff_time = current_time - window_seconds
            valid_requests = [req for req in requests if req > cutoff_time]
            window_stats[window_name] = len(valid_requests)
        
        stats[key] = {
            "total_requests": len(requests),
            "windows": window_stats,
            "last_request": max(requests) if requests else None
        }
    
    return stats

def clear_rate_limits():
    """Clear all rate limiting data (useful for testing)"""
    with rate_limiter.lock:
        rate_limiter.requests.clear()
        rate_limiter.last_cleanup = time.time()
    logger.info("Rate limiting data cleared")
