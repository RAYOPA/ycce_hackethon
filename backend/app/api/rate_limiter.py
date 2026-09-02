import time
from typing import Dict, Tuple
from fastapi import HTTPException, status
from app.core.config import settings

class RateLimiter:
    """
    A simple in-memory rate limiter for development/single-instance use.
    In a distributed production environment, this should be replaced with Redis.
    """
    def __init__(self, requests_per_minute: int):
        self.requests_per_minute = requests_per_minute
        self.clients: Dict[str, Tuple[int, float]] = {}

    def check_rate_limit(self, client_id: str):
        now = time.time()
        
        # Clean up old entries to prevent memory leak
        if len(self.clients) > 10000:
            self.clients = {k: v for k, v in self.clients.items() if now - v[1] < 60}
            
        count, window_start = self.clients.get(client_id, (0, now))

        if now - window_start > 60:
            count = 0
            window_start = now

        if count >= self.requests_per_minute:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later."
            )

        self.clients[client_id] = (count + 1, window_start)

# Global instances for rate limiting
login_rate_limiter = RateLimiter(requests_per_minute=settings.RATE_LIMIT_LOGIN)

def get_login_rate_limiter():
    """Dependency to check rate limit based on client IP or fallback"""
    from fastapi import Request
    def _rate_limit(request: Request):
        client_ip = request.client.host if request.client else "unknown"
        login_rate_limiter.check_rate_limit(client_ip)
    return _rate_limit
