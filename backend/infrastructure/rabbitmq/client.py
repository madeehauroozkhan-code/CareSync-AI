"""
backend/infrastructure/rabbitmq/client.py
------------------------------------------
RabbitMQ (AMQP) connection management using aio-pika.

A single RobustConnection is used so that aio-pika automatically
reconnects on network failures. Channels are obtained per-use from
a ChannelPool to avoid blocking.

The connection is established at startup and closed at shutdown by
the FastAPI lifespan manager.

When RABBITMQ_URL is empty, all operations silently no-op so the platform
can run without RabbitMQ in demo/test environments.
"""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from backend.core.config import settings
from backend.core.logging import get_logger

logger = get_logger(__name__)

# Module-level connection and channel pool references
_connection = None
_channel_pool = None


async def initialize_rabbitmq() -> bool:
    """
    Establish a RabbitMQ connection and create a channel pool.
    Called once at application startup.

    Returns:
        True if the connection was established, False otherwise.
    """
    global _connection, _channel_pool

    if not settings.rabbitmq_configured:
        logger.warning("RabbitMQ URL not configured – messaging disabled")
        return False

    try:
        import aio_pika

        _connection = await aio_pika.connect_robust(
            settings.rabbitmq_url,
            heartbeat=30,
            connection_timeout=10,
        )
        _channel_pool = aio_pika.pool.Pool(
            _create_channel,
            max_size=settings.rabbitmq_prefetch_count,
        )
        logger.info("RabbitMQ connected", url=_mask_url(settings.rabbitmq_url))

        # Declare the main exchange
        async with get_channel() as channel:
            await channel.declare_exchange(
                settings.rabbitmq_exchange,
                type=settings.rabbitmq_exchange_type,
                durable=True,
            )
            logger.info(
                "RabbitMQ exchange declared",
                exchange=settings.rabbitmq_exchange,
                type=settings.rabbitmq_exchange_type,
            )
        return True

    except Exception as exc:
        logger.warning("RabbitMQ connection failed - messaging disabled", exc_info=exc)
        _connection = None
        _channel_pool = None
        return False


async def _create_channel():
    """Create a new AMQP channel from the connection."""
    if _connection is None:
        raise RuntimeError("RabbitMQ connection is not established")
    return await _connection.channel()


@asynccontextmanager
async def get_channel() -> AsyncGenerator:
    """
    Context manager that yields an AMQP channel from the pool.

    Usage:
        async with get_channel() as channel:
            await channel.declare_queue(...)
    """
    if _channel_pool is None:
        raise RuntimeError("RabbitMQ channel pool is not initialized")

    async with _channel_pool.acquire() as channel:
        yield channel


async def close_rabbitmq() -> None:
    """Close the RabbitMQ connection pool and connection. Called at shutdown."""
    global _connection, _channel_pool

    if _channel_pool is not None:
        try:
            await _channel_pool.close()
        except Exception as exc:
            logger.warning("Error closing RabbitMQ channel pool", exc_info=exc)
        finally:
            _channel_pool = None

    if _connection is not None:
        try:
            await _connection.close()
            logger.info("RabbitMQ connection closed")
        except Exception as exc:
            logger.warning("Error closing RabbitMQ connection", exc_info=exc)
        finally:
            _connection = None


def is_connected() -> bool:
    """Return True if the RabbitMQ connection is established and open."""
    return _connection is not None and not _connection.is_closed


async def health_check() -> dict:
    """
    Perform a RabbitMQ health check.

    Returns:
        Dict with 'status' ("healthy" | "degraded") and optional details.
    """
    if not is_connected():
        return {"status": "degraded", "reason": "Not connected"}

    try:
        async with get_channel() as channel:
            # A successful channel acquisition means the broker is reachable
            return {"status": "healthy", "exchange": settings.rabbitmq_exchange}
    except Exception as exc:
        return {"status": "degraded", "reason": str(exc)}


def _mask_url(url: str) -> str:
    """Mask credentials in AMQP URL for safe logging."""
    try:
        import re

        return re.sub(r"(:)[^@]+(@)", r"\1****\2", url)
    except Exception:
        return "amqp://****"
