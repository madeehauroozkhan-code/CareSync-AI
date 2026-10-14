"""
backend/core/dependencies.py
------------------------------
FastAPI dependency injection definitions for the AI Healthcare Coordination Platform.

All infrastructure clients (Firebase, Redis, RabbitMQ, Qdrant) are exposed
as FastAPI dependencies so they can be injected into route handlers and tested
via dependency overrides.

Usage in a route:
    from backend.core.dependencies import get_firestore, get_redis_cache

    @router.get("/example")
    async def example(db=Depends(get_firestore), cache=Depends(get_redis_cache)):
        ...
"""

from __future__ import annotations

from typing import AsyncGenerator

from fastapi import Depends, HTTPException, Request, status

from backend.core.config import settings
from backend.core.exceptions import AuthenticationError
from backend.core.logging import get_logger

logger = get_logger(__name__)


# ──────────────────────────────────────────────────────────────────
# Firebase Dependencies
# ──────────────────────────────────────────────────────────────────


def get_firebase_client():
    """
    Dependency that returns the Firebase Admin app client.
    The client is initialized once at startup by the lifespan manager.
    """
    from backend.infrastructure.firebase.client import get_firebase_app

    app = get_firebase_app()
    if app is None:
        logger.warning("Firebase client requested but not initialized")
    return app


def get_firestore():
    """
    Dependency that returns the Firestore client (db).
    """
    from backend.infrastructure.firebase.firestore import get_firestore_client

    return get_firestore_client()


def get_firebase_auth():
    """
    Dependency that returns the Firebase Auth module reference.
    """
    from backend.infrastructure.firebase import auth as firebase_auth

    return firebase_auth


def get_firebase_storage():
    """
    Dependency that returns the Firebase Storage bucket.
    """
    from backend.infrastructure.firebase.storage import get_storage_bucket

    return get_storage_bucket()


# ──────────────────────────────────────────────────────────────────
# Redis Dependencies
# ──────────────────────────────────────────────────────────────────


def get_redis_client():
    """
    Dependency that returns the raw Redis client from the connection pool.
    """
    from backend.infrastructure.redis.client import get_redis

    return get_redis()


def get_redis_cache():
    """
    Dependency that returns the RedisCache helper for get/set/delete operations.
    """
    from backend.infrastructure.redis.cache import RedisCache
    from backend.infrastructure.redis.client import get_redis

    return RedisCache(client=get_redis())


# ──────────────────────────────────────────────────────────────────
# RabbitMQ Dependencies
# ──────────────────────────────────────────────────────────────────


async def get_rabbitmq_channel() -> AsyncGenerator:
    """
    Dependency that yields an AMQP channel for publishing/consuming.
    Uses aio-pika connection pool managed by the lifespan manager.
    """
    from backend.infrastructure.rabbitmq.client import get_channel

    async with get_channel() as channel:
        yield channel


def get_event_publisher():
    """
    Dependency that returns the EventPublisher for broadcasting events.
    """
    from backend.infrastructure.rabbitmq.publisher import EventPublisher

    return EventPublisher()


# ──────────────────────────────────────────────────────────────────
# Qdrant Dependencies
# ──────────────────────────────────────────────────────────────────


def get_qdrant_client():
    """
    Dependency that returns the Qdrant client for vector operations.
    """
    from backend.infrastructure.qdrant.client import get_qdrant

    return get_qdrant()


# ──────────────────────────────────────────────────────────────────
# Shared Memory / Orchestration Dependencies
# ──────────────────────────────────────────────────────────────────


def get_shared_memory():
    """
    Dependency that returns the SharedMemory instance.
    """
    from backend.shared.memory.shared_memory import SharedMemory

    return SharedMemory()


def get_context_manager():
    """
    Dependency that returns the ContextManager for session-level context lifecycle.
    """
    from backend.shared.memory.context_manager import ContextManager

    return ContextManager()


def get_state_manager():
    """
    Dependency that returns the StateManager for workflow state transitions.
    """
    from backend.shared.memory.state_manager import StateManager

    return StateManager()


def get_event_bus():
    """
    Dependency that returns the EventBus for in-process event pub/sub.
    """
    from backend.shared.events.event_bus import EventBus

    return EventBus.get_instance()


def get_planner():
    """
    Dependency that returns the PlannerOrchestrator (LangGraph entrypoint).
    """
    from backend.orchestration.planner import PlannerOrchestrator

    return PlannerOrchestrator()


# ──────────────────────────────────────────────────────────────────
# Authentication Dependencies
# ──────────────────────────────────────────────────────────────────


async def verify_firebase_token(request: Request) -> dict:
    """
    Dependency that extracts and verifies a Firebase ID token from the
    Authorization header (Bearer scheme).

    When settings.enable_auth is False (development mode), authentication
    is bypassed and a mock user dict is returned instead.

    Raises:
        AuthenticationError: If the token is missing or invalid.
    """
    if not settings.enable_auth:
        # Development / demo mode: return a mock user
        return {
            "uid": "dev-user-001",
            "email": "dev@ai-sahayak.local",
            "name": "Dev User",
            "role": "patient",
        }

    authorization = request.headers.get("Authorization", "")
    if not authorization.startswith("Bearer "):
        raise AuthenticationError(
            "Missing or malformed Authorization header. Expected 'Bearer <token>'."
        )

    token = authorization.removeprefix("Bearer ").strip()
    if not token:
        raise AuthenticationError("Bearer token is empty.")

    try:
        from backend.infrastructure.firebase.auth import verify_token

        return await verify_token(token)
    except Exception as exc:  # noqa: BLE001
        logger.warning("Firebase token verification failed", exc_info=exc)
        raise AuthenticationError("Invalid or expired authentication token.") from exc


# Convenience alias for routes that require authentication
RequireAuth = Depends(verify_firebase_token)
