"""
backend/infrastructure/redis/cache.py
---------------------------------------
High-level Redis cache helpers for the AI Healthcare Coordination Platform.

Provides a RedisCache class with typed get/set/delete/expire helpers and
automatic JSON serialization/deserialization of complex values.

When the Redis client is unavailable, all operations return None/False
so that callers can decide how to handle cache misses gracefully.
"""

from __future__ import annotations

import json
from typing import Any, Optional

from backend.core.config import settings
from backend.core.logging import get_logger

logger = get_logger(__name__)


class RedisCache:
    """
    Thin wrapper around a Redis client that adds:
      - Automatic JSON serialisation for non-string values
      - Per-key TTL support with a global default fallback
      - Safe no-op behaviour when the client is None (demo/offline mode)
    """

    def __init__(self, client=None) -> None:
        self._client = client

    @property
    def _available(self) -> bool:
        return self._client is not None

    # ── Core Operations ──────────────────────────────────────────

    def get(self, key: str) -> Optional[Any]:
        """
        Retrieve a cached value by key.

        Returns:
            Deserialized value, or None if the key does not exist or cache is unavailable.
        """
        if not self._available:
            return None
        try:
            raw = self._client.get(key)
            if raw is None:
                return None
            # Attempt JSON decode; fall back to returning raw string
            try:
                return json.loads(raw)
            except (json.JSONDecodeError, TypeError):
                return raw
        except Exception as exc:
            logger.warning("Redis GET failed", key=key, exc_info=exc)
            return None

    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
    ) -> bool:
        """
        Store a value in the cache.

        Args:
            key: Cache key.
            value: Value to store (serialised to JSON if not a plain string).
            ttl: Expiry in seconds. Defaults to settings.redis_default_ttl.

        Returns:
            True if stored successfully, False otherwise.
        """
        if not self._available:
            return False
        try:
            serialized = json.dumps(value) if not isinstance(value, (str, bytes)) else value
            effective_ttl = ttl if ttl is not None else settings.redis_default_ttl
            self._client.setex(key, effective_ttl, serialized)
            return True
        except Exception as exc:
            logger.warning("Redis SET failed", key=key, exc_info=exc)
            return False

    def delete(self, key: str) -> bool:
        """Remove a key from the cache. Returns True if the key was deleted."""
        if not self._available:
            return False
        try:
            result = self._client.delete(key)
            return bool(result)
        except Exception as exc:
            logger.warning("Redis DELETE failed", key=key, exc_info=exc)
            return False

    def delete_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching a glob pattern (e.g., "session:*").

        Returns:
            Number of keys deleted.

        Warning: Use with caution on large key spaces.
        """
        if not self._available:
            return 0
        try:
            keys = self._client.keys(pattern)
            if not keys:
                return 0
            return self._client.delete(*keys)
        except Exception as exc:
            logger.warning("Redis DELETE PATTERN failed", pattern=pattern, exc_info=exc)
            return 0

    def expire(self, key: str, ttl: int) -> bool:
        """Set or update the TTL of an existing key."""
        if not self._available:
            return False
        try:
            return bool(self._client.expire(key, ttl))
        except Exception as exc:
            logger.warning("Redis EXPIRE failed", key=key, exc_info=exc)
            return False

    def exists(self, key: str) -> bool:
        """Return True if the key exists in the cache."""
        if not self._available:
            return False
        try:
            return bool(self._client.exists(key))
        except Exception as exc:
            logger.warning("Redis EXISTS failed", key=key, exc_info=exc)
            return False

    def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """Atomically increment an integer counter. Returns the new value."""
        if not self._available:
            return None
        try:
            return self._client.incrby(key, amount)
        except Exception as exc:
            logger.warning("Redis INCRBY failed", key=key, exc_info=exc)
            return None

    # ── Convenience Namespaced Helpers ──────────────────────────

    def session_key(self, session_id: str) -> str:
        return f"session:{session_id}"

    def user_key(self, user_id: str) -> str:
        return f"user:{user_id}"

    def workflow_key(self, workflow_id: str) -> str:
        return f"workflow:{workflow_id}"

    def rate_limit_key(self, user_id: str, endpoint: str) -> str:
        return f"rate:{user_id}:{endpoint}"
