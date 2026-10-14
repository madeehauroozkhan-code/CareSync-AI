"""
backend/infrastructure/redis/client.py
----------------------------------------
Redis connection pool management for the AI Healthcare Coordination Platform.

A single connection pool is shared across all request handlers to minimise
connection overhead. The pool is initialised at application startup and closed
at shutdown via the FastAPI lifespan manager.

When REDIS_URL is empty or Redis is unreachable, operations return None so
that higher-level code can degrade gracefully.
"""

from __future__ import annotations

from typing import Optional

import redis
from redis import Redis
from redis.connection import ConnectionPool

from backend.core.config import settings
from backend.core.logging import get_logger

logger = get_logger(__name__)

# Module-level connection pool and client references
_redis_pool: Optional[ConnectionPool] = None
_redis_client: Optional[Redis] = None
_redis_init_attempted: bool = False


def initialize_redis() -> Optional[Redis]:
    """
    Create the Redis connection pool and return a client instance.
    Called once at application startup.
    """
    global _redis_pool, _redis_client, _redis_init_attempted

    if _redis_client is not None:
        return _redis_client

    if _redis_init_attempted:
        return None

    _redis_init_attempted = True

    if not settings.redis_configured:
        logger.warning("Redis URL not configured – caching disabled")
        return None

    try:
        _redis_pool = ConnectionPool.from_url(
            settings.redis_url,
            max_connections=settings.redis_max_connections,
            decode_responses=settings.redis_decode_responses,
            socket_timeout=5,
            socket_connect_timeout=5,
        )
        _redis_client = Redis(connection_pool=_redis_pool)

        # Verify connectivity with a PING
        _redis_client.ping()
        logger.info("Redis connected", url=_mask_url(settings.redis_url))
        return _redis_client

    except Exception as exc:
        logger.warning("Redis connection failed – caching disabled", exc_info=exc)
        _redis_pool = None
        _redis_client = None
        return None


def get_redis() -> Optional[Redis]:
    """
    Return the shared Redis client.
    Attempts lazy initialization if not yet connected.
    """
    global _redis_client
    if _redis_client is None:
        _redis_client = initialize_redis()
    return _redis_client


def close_redis() -> None:
    """
    Close the Redis connection pool. Called during application shutdown.
    """
    global _redis_pool, _redis_client
    if _redis_pool is not None:
        try:
            _redis_pool.disconnect()
            logger.info("Redis connection pool closed")
        except Exception as exc:
            logger.warning("Error closing Redis pool", exc_info=exc)
        finally:
            _redis_pool = None
            _redis_client = None


async def health_check() -> dict:
    """
    Perform a Redis health check.

    Returns:
        Dict with 'status' ("healthy" | "degraded") and optional 'latency_ms'.
    """
    client = get_redis()
    if client is None:
        return {"status": "degraded", "reason": "Not connected"}

    try:
        import time

        start = time.perf_counter()
        client.ping()
        latency_ms = round((time.perf_counter() - start) * 1000, 2)
        return {"status": "healthy", "latency_ms": latency_ms}

    except Exception as exc:
        logger.warning("Redis health check failed", exc_info=exc)
        return {"status": "degraded", "reason": str(exc)}


def _mask_url(url: str) -> str:
    """Mask credentials in Redis URL for safe logging."""
    try:
        import re

        return re.sub(r"(:)[^@]+(@)", r"\1****\2", url)
    except Exception:
        return "redis://****"
