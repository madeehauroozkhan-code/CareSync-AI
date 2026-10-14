"""
backend/infrastructure/qdrant/client.py
----------------------------------------
Qdrant vector database client initialization.

A single QdrantClient instance is shared across the application.
Initialized at startup; gracefully degrades when Qdrant is unavailable.
"""

from __future__ import annotations

from typing import Optional

from backend.core.config import settings
from backend.core.logging import get_logger

logger = get_logger(__name__)

_qdrant_client = None
_qdrant_init_attempted = False


def initialize_qdrant():
    """
    Initialize the Qdrant client and return it.
    Called once at application startup.
    """
    global _qdrant_client, _qdrant_init_attempted

    if _qdrant_client is not None:
        return _qdrant_client
        
    if _qdrant_init_attempted:
        return None
        
    _qdrant_init_attempted = True

    if not settings.qdrant_configured:
        logger.warning("Qdrant URL not configured – vector search disabled")
        return None

    try:
        from qdrant_client import QdrantClient

        kwargs = {"url": settings.qdrant_url, "timeout": 10}
        if settings.qdrant_api_key:
            kwargs["api_key"] = settings.qdrant_api_key

        _qdrant_client = QdrantClient(**kwargs)

        # Verify connection by listing collections
        _qdrant_client.get_collections()
        logger.info("Qdrant connected", url=settings.qdrant_url)
        return _qdrant_client

    except Exception as exc:
        logger.warning("Qdrant connection failed - vector search disabled", exc_info=exc)
        _qdrant_client = None
        return None


def get_qdrant():
    """Return the Qdrant client, attempting lazy initialization."""
    global _qdrant_client
    if _qdrant_client is None:
        _qdrant_client = initialize_qdrant()
    return _qdrant_client


def close_qdrant() -> None:
    """Close the Qdrant client connection."""
    global _qdrant_client
    if _qdrant_client is not None:
        try:
            _qdrant_client.close()
            logger.info("Qdrant client closed")
        except Exception as exc:
            logger.warning("Error closing Qdrant client", exc_info=exc)
        finally:
            _qdrant_client = None


async def health_check() -> dict:
    """Perform a Qdrant health check."""
    client = get_qdrant()
    if client is None:
        return {"status": "degraded", "reason": "Not connected"}

    try:
        import time

        start = time.perf_counter()
        client.get_collections()
        latency_ms = round((time.perf_counter() - start) * 1000, 2)
        return {"status": "healthy", "latency_ms": latency_ms}
    except Exception as exc:
        return {"status": "degraded", "reason": str(exc)}
