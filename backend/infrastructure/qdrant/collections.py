"""
backend/infrastructure/qdrant/collections.py
---------------------------------------------
Qdrant collection management helpers.

Handles creation and validation of the vector collections defined
in settings. Collections are idempotent — creating an already-existing
collection is a no-op.
"""

from __future__ import annotations

from backend.core.config import settings
from backend.core.logging import get_logger

logger = get_logger(__name__)

# Collection definitions: name → vector config
COLLECTION_CONFIGS = {
    settings.qdrant_collection_medical_knowledge: {
        "description": "Medical knowledge base for RAG retrieval",
        "vector_size": settings.qdrant_vector_size,
    },
    settings.qdrant_collection_patient_memory: {
        "description": "Long-term patient interaction memory",
        "vector_size": settings.qdrant_vector_size,
    },
}


async def ensure_collections() -> bool:
    """
    Ensure all required Qdrant collections exist.
    Creates missing collections; skips existing ones.

    Returns:
        True if all collections are available, False otherwise.
    """
    from backend.infrastructure.qdrant.client import get_qdrant

    client = get_qdrant()
    if client is None:
        logger.warning("Qdrant unavailable; skipping collection setup")
        return False

    try:
        from qdrant_client.http.models import Distance, VectorParams

        existing_names = {c.name for c in client.get_collections().collections}

        for collection_name, config in COLLECTION_CONFIGS.items():
            if collection_name in existing_names:
                logger.debug("Qdrant collection already exists", collection=collection_name)
                continue

            client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=config["vector_size"],
                    distance=Distance.COSINE,
                ),
            )
            logger.info(
                "Qdrant collection created",
                collection=collection_name,
                vector_size=config["vector_size"],
            )

        return True

    except Exception as exc:
        logger.error("Failed to ensure Qdrant collections", exc_info=exc)
        return False


async def get_collection_info(collection_name: str) -> dict:
    """Return metadata for a specific Qdrant collection."""
    from backend.infrastructure.qdrant.client import get_qdrant

    client = get_qdrant()
    if client is None:
        return {"status": "unavailable"}

    try:
        info = client.get_collection(collection_name)
        return {
            "name": collection_name,
            "status": info.status,
            "vectors_count": info.vectors_count,
            "points_count": info.points_count,
        }
    except Exception as exc:
        logger.warning("Failed to get Qdrant collection info", collection=collection_name, exc_info=exc)
        return {"name": collection_name, "status": "error", "reason": str(exc)}
