"""
backend/core/middleware.py
---------------------------
FastAPI middleware stack for the AI Healthcare Coordination Platform.

Provides:
  1. RequestIDMiddleware   – Injects a unique correlation ID into every request
  2. LoggingMiddleware     – Structured request/response logging
  3. ErrorHandlerMiddleware – Converts AppException subclasses to JSON responses

Order of registration matters: middlewares execute in reverse registration order.
The recommended registration order in main.py is:
    app.add_middleware(ErrorHandlerMiddleware)  # outermost — catches everything
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(RequestIDMiddleware)     # innermost — runs first
"""

from __future__ import annotations

import time
import uuid
from typing import Awaitable, Callable

import structlog
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from pydantic import ValidationError as PydanticValidationError
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from backend.core.exceptions import AppException
from backend.core.logging import bind_request_context, clear_request_context, get_logger

logger = get_logger(__name__)

# Header names
REQUEST_ID_HEADER = "X-Request-ID"
RESPONSE_TIME_HEADER = "X-Response-Time-Ms"


# ──────────────────────────────────────────────────────────────────
# 1. Request ID Middleware
# ──────────────────────────────────────────────────────────────────


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Injects a unique request ID into every request.

    - If the incoming request already carries an X-Request-ID header,
      that value is reused (useful for distributed tracing).
    - Otherwise, a new UUID4 is generated.
    - The request ID is added to the response headers and bound to
      the structlog context so every log within the request carries it.
    """

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        request_id = request.headers.get(REQUEST_ID_HEADER) or str(uuid.uuid4())

        # Store on the request state so downstream code can read it
        request.state.request_id = request_id

        # Bind to structlog context for this request lifecycle
        bind_request_context(request_id=request_id)

        try:
            response = await call_next(request)
        finally:
            clear_request_context()

        response.headers[REQUEST_ID_HEADER] = request_id
        return response


# ──────────────────────────────────────────────────────────────────
# 2. Logging Middleware
# ──────────────────────────────────────────────────────────────────


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Emits a structured log entry for every request/response cycle.

    Logs include:
      - HTTP method and path
      - Response status code
      - Response time in milliseconds
      - Request ID (from RequestIDMiddleware)
      - Client host

    Health-check endpoints are logged at DEBUG level to reduce noise.
    """

    _HEALTH_PATHS = frozenset({
        "/health", "/health/live", "/health/ready", "/health/services",
        "/api/v1/dashboard/cases", "/api/v1/dashboard/outbreaks",
        "/api/v1/dashboard/hospitals", "/api/v1/dashboard/volunteers",
    })

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        start_time = time.perf_counter()
        request_id = getattr(request.state, "request_id", "unknown")

        response: Response | None = None
        exc_info = None

        try:
            response = await call_next(request)
            return response
        except Exception as exc:
            exc_info = exc
            raise
        finally:
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            status_code = getattr(response, "status_code", 500) if response else 500

            log_payload = {
                "http_method": request.method,
                "http_path": request.url.path,
                "http_status": status_code,
                "response_time_ms": round(elapsed_ms, 2),
                "client_host": request.client.host if request.client else "unknown",
                "request_id": request_id,
            }

            if request.url.path in self._HEALTH_PATHS:
                logger.debug("Health check", **log_payload)
            elif status_code >= 500:
                logger.error("Request completed with server error", **log_payload, exc_info=exc_info)
            elif status_code >= 400:
                logger.warning("Request completed with client error", **log_payload)
            else:
                logger.info("Request completed", **log_payload)

            if response is not None:
                response.headers[RESPONSE_TIME_HEADER] = f"{elapsed_ms:.2f}"


# ──────────────────────────────────────────────────────────────────
# 3. Error Handler Middleware
# ──────────────────────────────────────────────────────────────────


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """
    Global exception handler that converts all unhandled exceptions into
    structured JSON error responses.

    Hierarchy:
      - AppException subclasses → use their own status_code and error_code
      - Pydantic ValidationError → 422 VALIDATION_ERROR
      - Any other Exception      → 500 INTERNAL_ERROR

    Sensitive information is never surfaced in production error responses.
    """

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        try:
            return await call_next(request)

        except AppException as exc:
            logger.warning(
                "Application error",
                error_code=exc.error_code,
                status_code=exc.status_code,
                detail=exc.detail,
                metadata=exc.metadata,
            )
            return JSONResponse(
                status_code=exc.status_code,
                content=exc.to_dict(),
            )

        except PydanticValidationError as exc:
            logger.warning("Pydantic validation error", errors=exc.errors())
            return JSONResponse(
                status_code=422,
                content={
                    "error": True,
                    "error_code": "VALIDATION_ERROR",
                    "detail": "Request validation failed.",
                    "metadata": {"errors": exc.errors()},
                },
            )

        except Exception as exc:  # noqa: BLE001
            logger.exception("Unhandled exception", exc_info=exc)
            return JSONResponse(
                status_code=500,
                content={
                    "error": True,
                    "error_code": "INTERNAL_ERROR",
                    "detail": "An unexpected error occurred. Our team has been notified.",
                },
            )
