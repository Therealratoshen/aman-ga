"""
Rate Limiting Module for API Protection
Prevents abuse and brute force attacks
"""

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request
from typing import Dict, List
from datetime import datetime, timedelta
import threading
import re


class RateLimitConfig:
    """Rate limit configurations"""
    
    # Authentication limits
    LOGIN_PER_MINUTE = 5
    LOGIN_PER_HOUR = 20
    REGISTER_PER_HOUR = 10
    
    # Payment upload limits
    UPLOAD_PER_MINUTE = 3
    UPLOAD_PER_HOUR = 20
    UPLOAD_PER_DAY = 50
    
    # API general limits
    API_PER_MINUTE = 30
    API_PER_HOUR = 500
    
    # Admin limits
    ADMIN_ACTION_PER_MINUTE = 10


# Global limiter instance
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[f"{RateLimitConfig.API_PER_HOUR}/hour"]
)


def _rate_limit_exceeded_handler(request, exc):
    """Default rate limit exceeded handler"""
    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded"}
    )


def setup_app(app):
    """Setup rate limiter on FastAPI app"""
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# Decorator functions for specific endpoints - now using the global limiter
def login_limit():
    """Rate limit for login endpoint"""
    return [
        limiter.limit(f"{RateLimitConfig.LOGIN_PER_MINUTE}/minute"),
        limiter.limit(f"{RateLimitConfig.LOGIN_PER_HOUR}/hour")
    ]


def register_limit():
    """Rate limit for registration endpoint"""
    return [
        limiter.limit(f"{RateLimitConfig.REGISTER_PER_HOUR}/hour")
    ]


def upload_limit():
    """Rate limit for payment upload endpoint"""
    return [
        limiter.limit(f"{RateLimitConfig.UPLOAD_PER_MINUTE}/minute"),
        limiter.limit(f"{RateLimitConfig.UPLOAD_PER_HOUR}/hour"),
        limiter.limit(f"{RateLimitConfig.UPLOAD_PER_DAY}/day")
    ]


def admin_limit():
    """Rate limit for admin actions"""
    return [
        limiter.limit(f"{RateLimitConfig.ADMIN_ACTION_PER_MINUTE}/minute")
    ]


class RateLimitTracker:
    """Track rate limit violations for monitoring - thread-safe version"""
    
    def __init__(self):
        self.violations: Dict[str, List[datetime]] = {}
        self.blocked_ips: Dict[str, datetime] = {}
        self.BLOCK_THRESHOLD = 10  # Block after 10 violations
        self.BLOCK_DURATION = timedelta(hours=1)
        self.lock = threading.Lock()  # Add thread safety
    
    def record_violation(self, ip: str) -> bool:
        """Record a rate limit violation. Returns True if IP should be blocked."""
        with self.lock:  # Thread safety
            now = datetime.now()
            
            if ip not in self.violations:
                self.violations[ip] = []
            
            # Clean old violations (older than 1 hour) - periodic cleanup
            self.violations[ip] = [
                v for v in self.violations[ip] 
                if now - v < timedelta(hours=1)
            ]
            
            self.violations[ip].append(now)
            
            # Check if should be blocked
            if len(self.violations[ip]) >= self.BLOCK_THRESHOLD:
                self.blocked_ips[ip] = now + self.BLOCK_DURATION
                return True
            
            return False
    
    def is_blocked(self, ip: str) -> bool:
        """Check if IP is currently blocked - thread-safe"""
        with self.lock:  # Thread safety
            if ip not in self.blocked_ips:
                return False
            
            now = datetime.now()
            if now > self.blocked_ips[ip]:
                # Block expired - cleanup
                del self.blocked_ips[ip]
                return False
            
            return True
    
    def get_violation_count(self, ip: str) -> int:
        """Get current violation count for IP - thread-safe"""
        with self.lock:  # Thread safety
            if ip not in self.violations:
                return 0
            
            now = datetime.now()
            return len([
                v for v in self.violations[ip] 
                if now - v < timedelta(hours=1)
            ])
    
    def cleanup_expired_blocks(self):
        """Periodically cleanup expired blocks - thread-safe"""
        with self.lock:  # Thread safety
            now = datetime.now()
            expired_ips = [ip for ip, expiry in self.blocked_ips.items() if now > expiry]
            for ip in expired_ips:
                del self.blocked_ips[ip]


# Global tracker instance
rate_limit_tracker = RateLimitTracker()


def check_ip_blocked(ip: str) -> bool:
    """Check if IP is blocked"""
    return rate_limit_tracker.is_blocked(ip)


def get_client_ip(request: Request) -> str:
    """Get client IP from request, handling proxies"""
    # Check for forwarded headers
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        # Take the first IP in the chain and validate it
        first_ip = forwarded.split(",")[0].strip()
        # Basic validation to prevent IP spoofing
        ip_pattern = re.compile(r'^(\d{1,3}\.){3}\d{1,3}$|^([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$')
        if ip_pattern.match(first_ip):
            return first_ip
    
    # Check for real IP header
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        ip_pattern = re.compile(r'^(\d{1,3}\.){3}\d{1,3}$|^([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$')
        if ip_pattern.match(real_ip.strip()):
            return real_ip.strip()
    
    # Fall back to direct connection IP
    return request.client.host if request.client else "unknown"
