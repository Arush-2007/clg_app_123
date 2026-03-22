from __future__ import annotations

import logging
import time
import uuid
from collections import defaultdict, deque
from collections.abc import Callable
from threading import Lock

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse, Response

from src.core.telemetry import metrics_store

logger = logging.getLogger("college_app")


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id
        started = time.perf_counter()

        response = await call_next(request)
        elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
        response.headers["X-Request-ID"] = request_id

        logger.info(
            "request_complete",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": elapsed_ms,
                "request_id": request_id,
            },
        )
        metrics_store.record(response.status_code, elapsed_ms)
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, requests_per_minute: int):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self._hits: dict[str, deque[float]] = defaultdict(deque)
        self._lock = Lock()

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        window_start = now - 60

        with self._lock:
            queue = self._hits[client_ip]
            while queue and queue[0] < window_start:
                queue.popleft()
            if len(queue) >= self.requests_per_minute:
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Rate limit exceeded. Try again in a minute."},
                )
            queue.append(now)

        return await call_next(request)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "same-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        return response
