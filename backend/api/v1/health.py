"""
backend/api/v1/health.py
--------------------------
Health check endpoints for the AI Healthcare Coordination Platform.

Provides:
  - GET /health            → Quick liveness probe
  - GET /health/live       → Kubernetes liveness probe
  - GET /health/ready      → Kubernetes readiness probe (checks dependencies)
  - GET /health/services   → Detailed health of all infrastructure services

These endpoints are used by:
  - Cloud Run / Kubernetes health checks
  - Load balancers
  - Monitoring dashboards
  - CI/CD deployment verification
"""

from __future__ import annotations

import asyncio
import platform
import time
from typing import Any, Dict

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from backend.core.config import settings
from backend.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/health", tags=["Health"])

# Application start time (used to compute uptime)
_START_TIME = time.time()


def _uptime_seconds() -> float:
    """Return seconds since application startup."""
    return round(time.time() - _START_TIME, 2)


# ──────────────────────────────────────────────────────────────────
# Liveness Probe
# ──────────────────────────────────────────────────────────────────


@router.get(
    "",
    summary="Quick health check",
    description="Returns 200 OK if the application is running.",
    response_description="Application status",
)
@router.get(
    "/live",
    summary="Liveness probe",
    description="Kubernetes/Cloud Run liveness probe. Returns 200 if the process is alive.",
)
async def liveness() -> Dict[str, Any]:
    """
    Lightweight liveness probe.
    Returns immediately without checking any dependencies.
    """
    return {
        "status": "alive",
        "service": settings.app_name,
        "version": settings.app_version,
        "environment": settings.app_env,
        "uptime_seconds": _uptime_seconds(),
    }


# ──────────────────────────────────────────────────────────────────
# Readiness Probe
# ──────────────────────────────────────────────────────────────────


@router.get(
    "/ready",
    summary="Readiness probe",
    description="Returns 200 if the application is ready to serve traffic (critical deps available).",
)
async def readiness() -> JSONResponse:
    """
    Readiness probe that checks critical infrastructure dependencies.
    Returns 503 if any critical dependency is unavailable.
    """
    checks: Dict[str, Any] = {}
    all_ready = True

    # Firebase (critical if auth is enabled)
    try:
        from backend.infrastructure.firebase.client import get_firebase_app

        fb_app = get_firebase_app()
        checks["firebase"] = "available" if fb_app is not None else "demo_mode"
    except Exception as exc:
        checks["firebase"] = f"error: {exc}"

    # Redis (critical for session management)
    try:
        from backend.infrastructure.redis.client import health_check as redis_health

        redis_result = await redis_health()
        checks["redis"] = redis_result.get("status", "unknown")
        if redis_result.get("status") != "healthy":
            all_ready = False
    except Exception as exc:
        checks["redis"] = f"error: {exc}"
        all_ready = False

    status_code = 200 if all_ready else 503
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "ready" if all_ready else "not_ready",
            "checks": checks,
            "uptime_seconds": _uptime_seconds(),
        },
    )


# ──────────────────────────────────────────────────────────────────
# Full Service Health
# ──────────────────────────────────────────────────────────────────


@router.get(
    "/services",
    summary="Detailed service health",
    description="Returns health status of all infrastructure dependencies.",
)
async def service_health() -> JSONResponse:
    """
    Comprehensive health report for all infrastructure services.
    Checks are run concurrently for speed.
    """
    start = time.perf_counter()

    results = await asyncio.gather(
        _check_firebase(),
        _check_redis(),
        _check_rabbitmq(),
        _check_qdrant(),
        return_exceptions=True,
    )

    service_labels = ["firebase", "redis", "rabbitmq", "qdrant"]
    services: Dict[str, Any] = {}

    overall_healthy = True
    for label, result in zip(service_labels, results):
        if isinstance(result, Exception):
            services[label] = {"status": "error", "reason": str(result)}
            overall_healthy = False
        else:
            services[label] = result
            if result.get("status") not in ("healthy", "demo_mode", "disabled"):
                overall_healthy = False

    elapsed_ms = round((time.perf_counter() - start) * 1000, 2)

    return JSONResponse(
        status_code=200 if overall_healthy else 207,
        content={
            "status": "healthy" if overall_healthy else "degraded",
            "service": settings.app_name,
            "version": settings.app_version,
            "environment": settings.app_env,
            "uptime_seconds": _uptime_seconds(),
            "check_duration_ms": elapsed_ms,
            "services": services,
            "system": {
                "python_version": platform.python_version(),
                "platform": platform.system(),
            },
        },
    )


# ──────────────────────────────────────────────────────────────────
# Individual Service Checkers
# ──────────────────────────────────────────────────────────────────


async def _check_firebase() -> Dict[str, Any]:
    """Check Firebase Admin SDK availability."""
    try:
        from backend.infrastructure.firebase.client import get_firebase_app

        app = get_firebase_app()
        if app is None:
            return {"status": "demo_mode", "reason": "Firebase credentials not configured"}
        return {"status": "healthy", "project_id": settings.firebase_project_id}
    except Exception as exc:
        return {"status": "error", "reason": str(exc)}


async def _check_redis() -> Dict[str, Any]:
    """Check Redis connectivity."""
    try:
        from backend.infrastructure.redis.client import health_check

        return await health_check()
    except Exception as exc:
        return {"status": "error", "reason": str(exc)}


async def _check_rabbitmq() -> Dict[str, Any]:
    """Check RabbitMQ connectivity."""
    try:
        from backend.infrastructure.rabbitmq.client import health_check

        return await health_check()
    except Exception as exc:
        return {"status": "error", "reason": str(exc)}


async def _check_qdrant() -> Dict[str, Any]:
    """Check Qdrant connectivity."""
    try:
        from backend.infrastructure.qdrant.client import health_check

        return await health_check()
    except Exception as exc:
        return {"status": "error", "reason": str(exc)}
