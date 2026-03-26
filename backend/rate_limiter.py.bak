"""
Rate Limiting Module for API Protection
Prevents abuse and brute force attacks
"""

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request
from typing import Dict, List
from datetime import datetime, timedelta


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


class RateLimiter:
    """Rate limiting service"""
    
    def __init__(self):
        self.limiter = Limiter(
            key_func=get_remote_address,
            default_limits=[f"{RateLimitConfig.API_PER_HOUR}/hour"]
        )
        
    def get_limiter(self) -> Limiter:
        return self.limiter
    
    def setup_app(self, app):
        """Setup rate limiter on FastAPI app"""
        app.state.limiter = self.limiter
        app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# Decorator functions for specific endpoints
def login_limit():
    """Rate limit for login endpoint"""
    from slowapi import Limiter
    from slowapi.util import get_remote_address
    limiter = Limiter(key_func=get_remote_address)
    return [
        limiter.limit(f"{RateLimitConfig.LOGIN_PER_MINUTE}/minute"),
        limiter.limit(f"{RateLimitConfig.LOGIN_PER_HOUR}/hour")
    ]


def register_limit():
    """Rate limit for registration endpoint"""
    from slowapi import Limiter
    from slowapi.util import get_remote_address
    limiter = Limiter(key_func=get_remote_address)
    return [
        limiter.limit(f"{RateLimitConfig.REGISTER_PER_HOUR}/hour")
    ]


def upload_limit():
    """Rate limit for payment upload endpoint"""
    from slowapi import Limiter
    from slowapi.util import get_remote_address
    limiter = Limiter(key_func=get_remote_address)
    return [
        limiter.limit(f"{RateLimitConfig.UPLOAD_PER_MINUTE}/minute"),
        limiter.limit(f"{RateLimitConfig.UPLOAD_PER_HOUR}/hour"),
        limiter.limit(f"{RateLimitConfig.UPLOAD_PER_DAY}/day")
    ]


def admin_limit():
    """Rate limit for admin actions"""
    from slowapi import Limiter
    from slowapi.util import get_remote_address
    limiter = Limiter(key_func=get_remote_address)
    return [
        limiter.limit(f"{RateLimitConfig.ADMIN_ACTION_PER_MINUTE}/minute")
    ]


class RateLimitTracker:
    """Track rate limit violations for monitoring"""
    
    def __init__(self):
        self.violations: Dict[str, List[datetime]] = {}
        self.blocked_ips: Dict[str, datetime] = {}
        self.BLOCK_THRESHOLD = 10  # Block after 10 violations
        self.BLOCK_DURATION = timedelta(hours=1)
    
    def record_violation(self, ip: str) -> bool:
        """Record a rate limit violation. Returns True if IP should be blocked."""
        now = datetime.now()
        
        if ip not in self.violations:
            self.violations[ip] = []
        
        # Clean old violations (older than 1 hour)
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
        """Check if IP is currently blocked"""
        if ip not in self.blocked_ips:
            return False
        
        if datetime.now() > self.blocked_ips[ip]:
            # Block expired
            del self.blocked_ips[ip]
            return False
        
        return True
    
    def get_violation_count(self, ip: str) -> int:
        """Get current violation count for IP"""
        if ip not in self.violations:
            return 0
        
        now = datetime.now()
        return len([
            v for v in self.violations[ip] 
            if now - v < timedelta(hours=1)
        ])


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
        # Take the first IP in the chain
        return forwarded.split(",")[0].strip()
    
    # Check for real IP header
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip.strip()
    
    # Fall back to direct connection IP
    return request.client.host if request.client else "unknown"
