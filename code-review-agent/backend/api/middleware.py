import time
import uuid
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from backend.utils.logger import get_logger
logger = get_logger(__name__)

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log every request with timing and status code"""
    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = str(uuid.uuid4())[:8]
        start = time.time()
        logger.info(f"[{request_id}] {request.method} {request.url.path} — started")
        try:
            response = await call_next(request)
            duration = round((time.time() - start) * 1000)
            logger.info(
                f"[{request_id}] {request.method} {request.url.path} "
                f"— {response.status_code} ({duration}ms)"
            )
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Response-Time"] = f"{duration}ms"
            return response
        except Exception as e:
            duration = round((time.time() - start) * 1000)
            logger.error(f"[{request_id}] {request.method} {request.url.path} — FAILED ({duration}ms): {e}")
            raise