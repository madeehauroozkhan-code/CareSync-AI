"""
backend/shared/memory/shared_memory.py
----------------------------------------
Shared Memory implementation for the AI Healthcare Coordination Platform.

Shared Memory is the persistent contextual foundation of backend intelligence.
As defined in the BACKEND_BLUEPRINT.md and AGENT_BIBLE.md, it represents the
continuously evolving understanding of an active healthcare case — not a
simple key-value store.

Architecture:
  - Short-term memory: Redis (fast, session-scoped, TTL-based)
  - Long-term memory:  Firestore (durable, case-scoped, auditable)
  - Semantic memory:   Qdrant (vector search for relevant context retrieval)

This class provides a unified interface over all three layers.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from backend.core.config import settings
from backend.core.logging import get_logger

logger = get_logger(__name__)

# Key prefixes for namespacing
_REDIS_PREFIX = "smem"
_CONTEXT_TTL = 7200  # 2 hours for active session context

_local_cache: Dict[str, Any] = {}

class SharedMemory:
    """
    Unified shared memory interface for agent collaboration.

    Provides:
      - Session context (Redis): Fast R/W for active workflow state
      - Case context (Firestore): Durable storage for medical case data
      - Semantic search (Qdrant): Vector similarity retrieval

    All methods degrade gracefully when individual backends are unavailable.
    """

    # ── Session Context (Redis) ──────────────────────────────────

    def set_context(
        self,
        session_id: str,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
    ) -> bool:
        """
        Store a value in the session context (Redis).

        Args:
            session_id: Unique session identifier.
            key: Context key within the session namespace.
            value: Value to store (auto-serialised to JSON).
            ttl: TTL in seconds. Defaults to _CONTEXT_TTL.

        Returns:
            True if stored, False if Redis is unavailable.
        """
        from backend.infrastructure.redis.client import get_redis

        redis_key = self._session_key(session_id, key)
        client = get_redis()
        if client is None:
            logger.debug("SharedMemory: Redis unavailable, using local cache", session_id=session_id, key=key)
            _local_cache[redis_key] = value
            return True

        redis_key = self._session_key(session_id, key)
        try:
            serialized = json.dumps(value, default=str)
            effective_ttl = ttl if ttl is not None else _CONTEXT_TTL
            client.setex(redis_key, effective_ttl, serialized)
            logger.debug("SharedMemory: context set", session_id=session_id, key=key)
            return True
        except Exception as exc:
            logger.warning("SharedMemory: context set failed", session_id=session_id, key=key, exc_info=exc)
            return False

    def get_context(self, session_id: str, key: str) -> Optional[Any]:
        """
        Retrieve a value from the session context (Redis).

        Returns:
            Deserialized value, or None if not found.
        """
        from backend.infrastructure.redis.client import get_redis

        redis_key = self._session_key(session_id, key)
        client = get_redis()
        if client is None:
            return _local_cache.get(redis_key)
        try:
            raw = client.get(redis_key)
            if raw is None:
                return None
            return json.loads(raw)
        except Exception as exc:
            logger.warning("SharedMemory: context get failed", session_id=session_id, key=key, exc_info=exc)
            return None

    def delete_context(self, session_id: str, key: str) -> bool:
        """Remove a specific key from the session context."""
        from backend.infrastructure.redis.client import get_redis

        redis_key = self._session_key(session_id, key)
        client = get_redis()
        if client is None:
            if redis_key in _local_cache:
                del _local_cache[redis_key]
                return True
            return False
        try:
            result = client.delete(redis_key)
            return bool(result)
        except Exception as exc:
            logger.warning("SharedMemory: context delete failed", session_id=session_id, key=key, exc_info=exc)
            return False

    def clear_session(self, session_id: str) -> int:
        """
        Remove all context keys for a given session.

        Returns:
            Number of keys deleted.
        """
        from backend.infrastructure.redis.client import get_redis

        pattern = self._session_key(session_id, "")
        client = get_redis()
        if client is None:
            keys_to_delete = [k for k in _local_cache.keys() if k.startswith(pattern)]
            for k in keys_to_delete:
                del _local_cache[k]
            return len(keys_to_delete)
        
        pattern = pattern + "*"
        try:
            keys = client.keys(pattern)
            if not keys:
                return 0
            count = client.delete(*keys)
            logger.info("SharedMemory: session cleared", session_id=session_id, keys_deleted=count)
            return count
        except Exception as exc:
            logger.warning("SharedMemory: session clear failed", session_id=session_id, exc_info=exc)
            return 0

    def get_full_session_context(self, session_id: str) -> Dict[str, Any]:
        """
        Retrieve all context keys for a session as a single dict.

        Returns:
            Dict of {key: value} for all session context keys.
        """
        from backend.infrastructure.redis.client import get_redis

        pattern = self._session_key(session_id, "")
        prefix = f"{_REDIS_PREFIX}:{session_id}:"
        
        client = get_redis()
        if client is None:
            result = {}
            for k, v in _local_cache.items():
                if k.startswith(pattern):
                    field_key = k[len(prefix):]
                    result[field_key] = v
            return result
            
        pattern = pattern + "*"
        try:
            keys = client.keys(pattern)
            if not keys:
                return {}

            prefix = f"{_REDIS_PREFIX}:{session_id}:"
            result: Dict[str, Any] = {}
            for redis_key in keys:
                field_key = redis_key[len(prefix):]
                raw = client.get(redis_key)
                if raw:
                    try:
                        result[field_key] = json.loads(raw)
                    except json.JSONDecodeError:
                        result[field_key] = raw
            return result
        except Exception as exc:
            logger.warning("SharedMemory: full context retrieval failed", session_id=session_id, exc_info=exc)
            return {}

    # ── Workflow State Helpers ────────────────────────────────────

    def set_workflow_state(self, workflow_id: str, state: Dict[str, Any]) -> bool:
        """Persist complete workflow state to Redis."""
        return self.set_context("workflow", workflow_id, state, ttl=_CONTEXT_TTL)

    def get_workflow_state(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve complete workflow state from Redis."""
        return self.get_context("workflow", workflow_id)

    # ── Internal Helpers ──────────────────────────────────────────

    @staticmethod
    def _session_key(session_id: str, key: str) -> str:
        """Build a namespaced Redis key for session context."""
        return f"{_REDIS_PREFIX}:{session_id}:{key}"
