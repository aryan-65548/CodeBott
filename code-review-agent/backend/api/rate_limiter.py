import time
from collections import defaultdict
from fastapi import Request, HTTPException
from backend.utils.logger import get_logger

logger = get_logger(__name__)
_request_counts: dict[str, list[float]] = defaultdict(list)
RATE_LIMIT_REQUESTS = 20       
RATE_LIMIT_WINDOW = 60         

def get_client_ip(request: Request) -> str:
    """Extract real client IP, handles proxies"""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def check_rate_limit(request: Request):
    """
    Dependency — inject into any route to rate limit it.
    Raises 429 if client exceeds RATE_LIMIT_REQUESTS per RATE_LIMIT_WINDOW seconds.
    """
    ip = get_client_ip(request)
    now = time.time()
    window_start = now - RATE_LIMIT_WINDOW
    _request_counts[ip] = [
        ts for ts in _request_counts[ip] if ts > window_start
    ]

    if len(_request_counts[ip]) >= RATE_LIMIT_REQUESTS:
        logger.warning(f"Rate limit hit for IP: {ip}")
        raise HTTPException(
            status_code=429,
            detail=f"Too many requests. Max {RATE_LIMIT_REQUESTS} requests per {RATE_LIMIT_WINDOW} seconds."
        )
    _request_counts[ip].append(now)
    logger.debug(f"IP {ip} — {len(_request_counts[ip])}/{RATE_LIMIT_REQUESTS} requests in window")