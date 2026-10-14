"""
backend/infrastructure/qdrant/operations.py
--------------------------------------------
High-level vector operations: upsert, search, and delete.

All operations use the shared Qdrant client and degrade gracefully
when the client is unavailable.
"""

from __future__ import annotations

import uuid
from typing import Any, Dict, List, Optional

from backend.core.exceptions import VectorDatabaseError
from backend.core.logging import get_logger

logger = get_logger(__name__)


async def upsert_vectors(
    collection_name: str,
    vectors: List[List[float]],
    payloads: List[Dict[str, Any]],
    ids: Optional[List[str]] = None,
) -> bool:
    """
    Upsert (insert or update) vectors into a Qdrant collection.

    Args:
        collection_name: Target collection.
        vectors: List of embedding vectors.
        payloads: Metadata dicts aligned with vectors.
        ids: Optional list of point IDs. Auto-generated if not provided.

    Returns:
        True on success.

    Raises:
        VectorDatabaseError: If the upsert fails.
    """
    from qdrant_client.http.models import PointStruct

    from backend.infrastructure.qdrant.client import get_qdrant

    client = get_qdrant()
    if client is None:
        logger.warning("Qdrant unavailable; skipping vector upsert", collection=collection_name)
        return False

    if ids is None:
        ids = [str(uuid.uuid4()) for _ in vectors]

    try:
        points = [
            PointStruct(id=point_id, vector=vector, payload=payload)
            for point_id, vector, payload in zip(ids, vectors, payloads)
        ]
        client.upsert(collection_name=collection_name, points=points)
        logger.debug("Vectors upserted", collection=collection_name, count=len(points))
        return True

    except Exception as exc:
        logger.error("Qdrant upsert failed", collection=collection_name, exc_info=exc)
        raise VectorDatabaseError(f"Failed to upsert vectors into {collection_name}.") from exc


async def search_vectors(
    collection_name: str,
    query_vector: List[float],
    *,
    limit: int = 10,
    score_threshold: float = 0.7,
    filter_payload: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """
    Search for similar vectors in a Qdrant collection.

    Args:
        collection_name: Collection to search.
        query_vector: Query embedding vector.
        limit: Maximum number of results.
        score_threshold: Minimum similarity score (0.0 – 1.0).
        filter_payload: Optional Qdrant payload filter dict.

    Returns:
        List of result dicts with 'id', 'score', and 'payload' fields.
    """
    from backend.infrastructure.qdrant.client import get_qdrant

    client = get_qdrant()
    if client is None:
        logger.warning("Qdrant unavailable; returning empty search results")
        return []

    try:
        query_filter = None
        if filter_payload:
            from qdrant_client.http.models import Filter, FieldCondition, MatchValue

            conditions = [
                FieldCondition(key=k, match=MatchValue(value=v))
                for k, v in filter_payload.items()
            ]
            query_filter = Filter(must=conditions)

        results = client.search(
            collection_name=collection_name,
            query_vector=query_vector,
            limit=limit,
            score_threshold=score_threshold,
            query_filter=query_filter,
        )

        return [
            {"id": str(hit.id), "score": hit.score, "payload": hit.payload or {}}
            for hit in results
        ]

    except Exception as exc:
        logger.error("Qdrant search failed", collection=collection_name, exc_info=exc)
        raise VectorDatabaseError(f"Vector search failed in {collection_name}.") from exc


async def delete_vectors(collection_name: str, ids: List[str]) -> bool:
    """
    Delete points from a Qdrant collection by ID.

    Returns:
        True on success, False if Qdrant is unavailable.
    """
    from qdrant_client.http.models import PointIdsList

    from backend.infrastructure.qdrant.client import get_qdrant

    client = get_qdrant()
    if client is None:
        return False

    try:
        client.delete(
            collection_name=collection_name,
            points_selector=PointIdsList(points=ids),
        )
        logger.debug("Vectors deleted", collection=collection_name, count=len(ids))
        return True

    except Exception as exc:
        logger.error("Qdrant delete failed", collection=collection_name, exc_info=exc)
        return False
