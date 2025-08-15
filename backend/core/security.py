"""
Security Middleware and Rate Limiting for CuraGenie

This module provides:
- Rate limiting to all public endpoints
- Request throttling for heavy operations
- CSRF protection for state-changing operations
- IP-based blocking for malicious activity
- Security headers and protection
"""

import time
import hashlib
import secrets
from typing import Dict, List, Optional, Tuple, Any
from collections import defaultdict, deque
from datetime import datetime, timedelta
from fastapi import Request, HTTPException, Response
from fastapi.responses import JSONResponse
import logging
import re
import ipaddress

logger = logging.getLogger(__name__)

class RateLimiter:
    """Advanced rate limiter with sliding window algorithm"""
    
    def __init__(self):
        self.requests: Dict[str, deque] = defaultdict(deque)
        self.blocked_ips: Dict[str, float] = {}
        self.suspicious_ips: Dict[str, int] = defaultdict(int)
        
        # Rate limit configurations
        self.rate_limits = {
            "default": {"requests": 100, "window": 60},  # 100 requests per minute
            "auth": {"requests": 5, "window": 60},       # 5 auth attempts per minute
            "upload": {"requests": 10, "window": 3600},  # 10 uploads per hour
            "api": {"requests": 1000, "window": 3600},   # 1000 API calls per hour
            "strict": {"requests": 20, "window": 60},    # 20 requests per minute
        }
        
        # IP blocking thresholds
        self.max_suspicious_attempts = 10
        self.block_duration = 3600  # 1 hour
    
    def _get_client_identifier(self, request: Request) -> str:
        """Get unique client identifier (IP + User-Agent hash)"""
        client_ip = self._get_client_ip(request)
        user_agent = request.headers.get("user-agent", "")
        
        # Create hash of IP + User-Agent for more accurate identification
        identifier = f"{client_ip}:{hashlib.md5(user_agent.encode()).hexdigest()[:8]}"
        return identifier
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address considering proxies"""
        # Check for forwarded headers
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            # Take the first IP in the chain
            client_ip = forwarded_for.split(",")[0].strip()
        else:
            client_ip = request.client.host
        
        return client_ip
    
    def _is_ip_blocked(self, client_ip: str) -> bool:
        """Check if IP is currently blocked"""
        if client_ip in self.blocked_ips:
            block_until = self.blocked_ips[client_ip]
            if time.time() < block_until:
                return True
            else:
                # Remove expired block
                del self.blocked_ips[client_ip]
        return False
    
    def _block_ip(self, client_ip: str, duration: int = None):
        """Block an IP address"""
        block_duration = duration or self.block_duration
        self.blocked_ips[client_ip] = time.time() + block_duration
        logger.warning(f"IP {client_ip} blocked for {block_duration} seconds")
    
    def _increment_suspicious_counter(self, client_ip: str):
        """Increment suspicious activity counter for an IP"""
        self.suspicious_ips[client_ip] += 1
        
        if self.suspicious_ips[client_ip] >= self.max_suspicious_attempts:
            self._block_ip(client_ip)
            logger.warning(f"IP {client_ip} blocked due to suspicious activity")
    
    def _detect_suspicious_activity(self, request: Request) -> bool:
        """Detect suspicious activity patterns"""
        client_ip = self._get_client_ip(request)
        
        # Check for suspicious patterns
        suspicious_patterns = [
            # SQL injection attempts
            r'(\b(union|select|insert|update|delete|drop|create|alter|exec|execute)\b)',
            r'(\b(and|or)\s+\d+\s*=\s*\d+)',
            r'(\b(and|or)\s+\d+\s*=\s*\d+\s*--)',
            r'(\b(and|or)\s+\d+\s*=\s*\d+\s*#)',
            r'(\b(and|or)\s+\d+\s*=\s*\d+\s*/\*)',
            r'(\b(and|or)\s+\d+\s*=\s*\d+\s*\*/)',
            
            # XSS attempts
            r'<script[^>]*>',
            r'javascript:',
            r'on\w+\s*=',
            
            # Path traversal
            r'\.\./',
            r'\.\.\\',
            
            # Command injection
            r'[;&|`]',
            r'\$\{.*\}',
            r'\{.*\}',
        ]
        
        # Check URL path and query parameters
        path = request.url.path
        query = str(request.query_params)
        headers = str(request.headers)
        
        all_text = f"{path} {query} {headers}".lower()
        
        for pattern in suspicious_patterns:
            if re.search(pattern, all_text, re.IGNORECASE):
                self._increment_suspicious_counter(client_ip)
                logger.warning(f"Suspicious activity detected from {client_ip}: {pattern}")
                return True
        
        return False
    
    def check_rate_limit(self, request: Request, limit_type: str = "default") -> bool:
        """Check if request is within rate limits"""
        client_ip = self._get_client_ip(request)
        
        # Check if IP is blocked
        if self._is_ip_blocked(client_ip):
            raise HTTPException(
                status_code=429,
                detail="IP address is temporarily blocked due to suspicious activity"
            )
        
        # Detect suspicious activity
        if self._detect_suspicious_activity(request):
            # Don't block immediately, just log and continue
            pass
        
        # Get rate limit configuration
        limit_config = self.rate_limits.get(limit_type, self.rate_limits["default"])
        max_requests = limit_config["requests"]
        window = limit_config["window"]
        
        # Get client identifier
        client_id = self._get_client_identifier(request)
        current_time = time.time()
        
        # Clean old requests outside the window
        if client_id in self.requests:
            while self.requests[client_id] and current_time - self.requests[client_id][0] > window:
                self.requests[client_id].popleft()
        
        # Check if limit exceeded
        if len(self.requests[client_id]) >= max_requests:
            logger.warning(f"Rate limit exceeded for {client_id} ({limit_type})")
            return False
        
        # Add current request
        self.requests[client_id].append(current_time)
        return True
    
    def get_remaining_requests(self, request: Request, limit_type: str = "default") -> int:
        """Get remaining requests for current window"""
        client_id = self._get_client_identifier(request)
        limit_config = self.rate_limits.get(limit_type, self.rate_limits["default"])
        max_requests = limit_config["requests"]
        window = limit_config["window"]
        
        current_time = time.time()
        
        # Clean old requests
        if client_id in self.requests:
            while self.requests[client_id] and current_time - self.requests[client_id][0] > window:
                self.requests[client_id].popleft()
        
        remaining = max(0, max_requests - len(self.requests[client_id]))
        return remaining

# Global rate limiter instance
rate_limiter = RateLimiter()

class SecurityMiddleware:
    """Security middleware for CuraGenie"""
    
    def __init__(self):
        self.csrf_tokens: Dict[str, str] = {}
        self.session_tokens: Dict[str, Dict[str, Any]] = {}
        
    async def __call__(self, request: Request, call_next):
        """Process request through security middleware"""
        
        # Check rate limits
        try:
            # Determine rate limit type based on endpoint
            limit_type = self._get_rate_limit_type(request)
            
            if not rate_limiter.check_rate_limit(request, limit_type):
                return JSONResponse(
                    status_code=429,
                    content={
                        "error": "Rate limit exceeded",
                        "detail": "Too many requests. Please try again later.",
                        "retry_after": 60
                    },
                    headers={"Retry-After": "60"}
                )
        except HTTPException as e:
            return JSONResponse(
                status_code=e.status_code,
                content={"error": e.detail}
            )
        
        # Add security headers
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
        
        # Add rate limit headers
        remaining = rate_limiter.get_remaining_requests(request, limit_type)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(time.time() + 60))
        
        return response
    
    def _get_rate_limit_type(self, request: Request) -> str:
        """Determine rate limit type based on endpoint"""
        path = request.url.path.lower()
        
        if any(auth_endpoint in path for auth_endpoint in ["/auth", "/login", "/register"]):
            return "auth"
        elif any(upload_endpoint in path for upload_endpoint in ["/upload", "/file"]):
            return "upload"
        elif any(api_endpoint in path for api_endpoint in ["/api", "/genomic", "/mri"]):
            return "api"
        elif any(strict_endpoint in path for strict_endpoint in ["/admin", "/settings"]):
            return "strict"
        else:
            return "default"
    
    def generate_csrf_token(self, session_id: str) -> str:
        """Generate CSRF token for a session"""
        token = secrets.token_urlsafe(32)
        self.csrf_tokens[session_id] = token
        return token
    
    def validate_csrf_token(self, session_id: str, token: str) -> bool:
        """Validate CSRF token"""
        if session_id not in self.csrf_tokens:
            return False
        
        valid_token = self.csrf_tokens[session_id]
        return secrets.compare_digest(token, valid_token)
    
    def cleanup_expired_tokens(self):
        """Clean up expired CSRF tokens"""
        # In a real implementation, you'd want to store tokens with expiration times
        # and clean them up periodically
        pass

# Global security middleware instance
security_middleware = SecurityMiddleware()

class RequestThrottler:
    """Request throttling for heavy operations"""
    
    def __init__(self):
        self.operation_timestamps: Dict[str, Dict[str, float]] = defaultdict(dict)
        self.throttle_configs = {
            "file_upload": {"min_interval": 1.0},      # 1 second between uploads
            "genomic_analysis": {"min_interval": 5.0},  # 5 seconds between analyses
            "mri_analysis": {"min_interval": 10.0},     # 10 seconds between MRI analyses
            "prs_calculation": {"min_interval": 2.0},   # 2 seconds between PRS calculations
        }
    
    def check_throttle(self, operation: str, user_id: str) -> bool:
        """Check if operation is throttled for user"""
        if operation not in self.throttle_configs:
            return True  # No throttling for unknown operations
        
        config = self.throttle_configs[operation]
        min_interval = config["min_interval"]
        
        current_time = time.time()
        last_operation = self.operation_timestamps[operation].get(user_id, 0)
        
        if current_time - last_operation < min_interval:
            return False  # Throttled
        
        # Update timestamp
        self.operation_timestamps[operation][user_id] = current_time
        return True
    
    def get_wait_time(self, operation: str, user_id: str) -> float:
        """Get wait time until next operation is allowed"""
        if operation not in self.throttle_configs:
            return 0.0
        
        config = self.throttle_configs[operation]
        min_interval = config["min_interval"]
        
        current_time = time.time()
        last_operation = self.operation_timestamps[operation].get(user_id, 0)
        
        wait_time = max(0.0, min_interval - (current_time - last_operation))
        return wait_time

# Global request throttler instance
request_throttler = RequestThrottler()

class IPBlocklist:
    """IP address blocklist management"""
    
    def __init__(self):
        self.blocked_ips: Dict[str, Dict[str, Any]] = {}
        self.whitelist: set = set()
        self.blacklist: set = set()
        
        # Load initial blocklists (in production, these would come from database/config)
        self._load_initial_lists()
    
    def _load_initial_lists(self):
        """Load initial IP blocklists"""
        # Whitelist - trusted IPs (e.g., internal networks)
        trusted_networks = [
            "127.0.0.0/8",      # Localhost
            "10.0.0.0/8",       # Private network
            "172.16.0.0/12",    # Private network
            "192.168.0.0/16",   # Private network
        ]
        
        for network in trusted_networks:
            try:
                net = ipaddress.ip_network(network)
                for ip in net:
                    self.whitelist.add(str(ip))
            except ValueError:
                logger.warning(f"Invalid network range: {network}")
        
        # Blacklist - known malicious IPs (in production, this would be dynamic)
        # This is just an example - real blacklists would be much more comprehensive
        pass
    
    def is_ip_blocked(self, ip: str) -> bool:
        """Check if IP is blocked"""
        # Check whitelist first
        if ip in self.whitelist:
            return False
        
        # Check blacklist
        if ip in self.blacklist:
            return True
        
        # Check dynamic blocklist
        if ip in self.blocked_ips:
            block_info = self.blocked_ips[ip]
            if block_info["expires_at"] > time.time():
                return True
            else:
                # Remove expired block
                del self.blocked_ips[ip]
        
        return False
    
    def block_ip(self, ip: str, reason: str, duration: int = 3600):
        """Block an IP address"""
        if ip in self.whitelist:
            logger.warning(f"Attempted to block whitelisted IP: {ip}")
            return False
        
        self.blocked_ips[ip] = {
            "reason": reason,
            "blocked_at": time.time(),
            "expires_at": time.time() + duration,
            "duration": duration
        }
        
        logger.warning(f"IP {ip} blocked for {duration} seconds. Reason: {reason}")
        return True
    
    def unblock_ip(self, ip: str) -> bool:
        """Unblock an IP address"""
        if ip in self.blocked_ips:
            del self.blocked_ips[ip]
            logger.info(f"IP {ip} unblocked")
            return True
        return False
    
    def get_block_info(self, ip: str) -> Optional[Dict[str, Any]]:
        """Get information about a blocked IP"""
        return self.blocked_ips.get(ip)
    
    def cleanup_expired_blocks(self):
        """Clean up expired IP blocks"""
        current_time = time.time()
        expired_ips = [
            ip for ip, info in self.blocked_ips.items()
            if info["expires_at"] <= current_time
        ]
        
        for ip in expired_ips:
            del self.blocked_ips[ip]
        
        if expired_ips:
            logger.info(f"Cleaned up {len(expired_ips)} expired IP blocks")

# Global IP blocklist instance
ip_blocklist = IPBlocklist()

# Decorators for easy use
def rate_limit(limit_type: str = "default"):
    """Decorator to apply rate limiting to endpoints"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Extract request from args or kwargs
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            
            if not request:
                for value in kwargs.values():
                    if isinstance(value, Request):
                        request = value
                        break
            
            if request:
                if not rate_limiter.check_rate_limit(request, limit_type):
                    return JSONResponse(
                        status_code=429,
                        content={
                            "error": "Rate limit exceeded",
                            "detail": "Too many requests. Please try again later.",
                            "retry_after": 60
                        },
                        headers={"Retry-After": "60"}
                    )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def throttle_operation(operation: str):
    """Decorator to throttle operations"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Extract user_id from args or kwargs
            user_id = None
            for arg in args:
                if isinstance(arg, (int, str)):
                    user_id = str(arg)
                    break
            
            if not user_id:
                for key, value in kwargs.items():
                    if key in ["user_id", "user"]:
                        user_id = str(value)
                        break
            
            if user_id:
                if not request_throttler.check_throttle(operation, user_id):
                    wait_time = request_throttler.get_wait_time(operation, user_id)
                    return JSONResponse(
                        status_code=429,
                        content={
                            "error": "Operation throttled",
                            "detail": f"Please wait {wait_time:.1f} seconds before next {operation}",
                            "retry_after": int(wait_time)
                        },
                        headers={"Retry-After": str(int(wait_time))}
                    )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def require_csrf_token():
    """Decorator to require CSRF token for state-changing operations"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Extract request and token from args or kwargs
            request = None
            csrf_token = None
            
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            
            if not request:
                for value in kwargs.values():
                    if isinstance(value, Request):
                        request = value
                        break
            
            if request:
                # Get CSRF token from headers or form data
                csrf_token = request.headers.get("x-csrf-token") or request.form().get("csrf_token")
                
                if not csrf_token:
                    return JSONResponse(
                        status_code=400,
                        content={"error": "CSRF token required", "detail": "CSRF token is missing"}
                    )
                
                # Validate token (you'd need to implement session management)
                # For now, we'll just check if it exists
                if not csrf_token or len(csrf_token) < 32:
                    return JSONResponse(
                        status_code=400,
                        content={"error": "Invalid CSRF token", "detail": "CSRF token is invalid"}
                    )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

