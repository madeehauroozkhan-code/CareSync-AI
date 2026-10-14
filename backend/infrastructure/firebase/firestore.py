"""
backend/infrastructure/firebase/firestore.py
----------------------------------------------
Firestore client helpers and CRUD utilities.

Provides a thin abstraction over the Firestore Python SDK to enable:
  - Centralized connection management
  - Consistent error handling
  - Easy mocking in tests
  - Graceful demo-mode fallback

Collection naming follows the BACKEND_BLUEPRINT.md conventions.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from backend.core.config import settings
from backend.core.exceptions import FirebaseError, ServiceUnavailableError
from backend.core.logging import get_logger

logger = get_logger(__name__)

# Firestore collection names (centralised to avoid magic strings)
COLLECTIONS = {
    "users": "users",
    "sessions": "sessions",
    "cases": "cases",
    "appointments": "appointments",
    "audit_logs": "audit_logs",
    "agent_states": "agent_states",
    "medical_knowledge": "medical_knowledge",
    "hospitals": "hospitals",
}

# Module-level Firestore client reference
_firestore_client = None


def get_firestore_client():
    """
    Return the Firestore client, initializing it if necessary.

    Returns:
        google.cloud.firestore.Client or None in demo mode.
    """
    global _firestore_client

    if _firestore_client is not None:
        return _firestore_client

    if not settings.firebase_configured:
        logger.debug("Firestore unavailable – running in demo mode")
        return None

    try:
        from firebase_admin import firestore as firebase_firestore

        from backend.infrastructure.firebase.client import get_firebase_app

        app = get_firebase_app()
        if app is None:
            return None

        _firestore_client = firebase_firestore.client(app=app)
        logger.info("Firestore client initialized")
        return _firestore_client

    except Exception as exc:
        logger.error("Failed to initialize Firestore client", exc_info=exc)
        return None


# ──────────────────────────────────────────────────────────────────
# CRUD Helpers
# ──────────────────────────────────────────────────────────────────


def _get_db():
    """Internal: return DB or raise ServiceUnavailableError."""
    db = get_firestore_client()
    if db is None:
        raise ServiceUnavailableError("Firestore", "Firestore is not available in demo mode.")
    return db


async def create_document(
    collection: str,
    document_id: str,
    data: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Create a new Firestore document.

    Args:
        collection: Target Firestore collection name.
        document_id: Document ID to create.
        data: Document data as a Python dict.

    Returns:
        The created document with an added 'id' field.

    Raises:
        FirebaseError: If the Firestore write fails.
    """
    try:
        from google.cloud import firestore

        db = _get_db()
        doc_ref = db.collection(collection).document(document_id)
        data_with_meta = {
            **data,
            "created_at": firestore.SERVER_TIMESTAMP,
            "updated_at": firestore.SERVER_TIMESTAMP,
        }
        doc_ref.set(data_with_meta)
        logger.debug("Firestore document created", collection=collection, document_id=document_id)
        return {"id": document_id, **data}

    except (ServiceUnavailableError, FirebaseError):
        raise
    except Exception as exc:
        logger.error("Firestore create failed", collection=collection, document_id=document_id, exc_info=exc)
        raise FirebaseError(f"Failed to create document in {collection}.") from exc


async def get_document(
    collection: str,
    document_id: str,
) -> Optional[Dict[str, Any]]:
    """
    Retrieve a single Firestore document by ID.

    Returns:
        Document data dict with 'id' field, or None if not found.
    """
    try:
        db = _get_db()
        doc_ref = db.collection(collection).document(document_id)
        snapshot = doc_ref.get()

        if not snapshot.exists:
            logger.debug("Firestore document not found", collection=collection, document_id=document_id)
            return None

        return {"id": snapshot.id, **snapshot.to_dict()}

    except (ServiceUnavailableError, FirebaseError):
        raise
    except Exception as exc:
        logger.error("Firestore get failed", collection=collection, document_id=document_id, exc_info=exc)
        raise FirebaseError(f"Failed to retrieve document from {collection}.") from exc


async def update_document(
    collection: str,
    document_id: str,
    data: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Update fields in an existing Firestore document.
    Only the fields provided in *data* are modified (merge update).
    """
    try:
        from google.cloud import firestore

        db = _get_db()
        doc_ref = db.collection(collection).document(document_id)
        update_data = {**data, "updated_at": firestore.SERVER_TIMESTAMP}
        doc_ref.update(update_data)
        logger.debug("Firestore document updated", collection=collection, document_id=document_id)
        return {"id": document_id, **data}

    except (ServiceUnavailableError, FirebaseError):
        raise
    except Exception as exc:
        logger.error("Firestore update failed", collection=collection, document_id=document_id, exc_info=exc)
        raise FirebaseError(f"Failed to update document in {collection}.") from exc


async def delete_document(collection: str, document_id: str) -> bool:
    """Delete a Firestore document. Returns True if deletion succeeded."""
    try:
        db = _get_db()
        db.collection(collection).document(document_id).delete()
        logger.debug("Firestore document deleted", collection=collection, document_id=document_id)
        return True

    except (ServiceUnavailableError, FirebaseError):
        raise
    except Exception as exc:
        logger.error("Firestore delete failed", collection=collection, document_id=document_id, exc_info=exc)
        raise FirebaseError(f"Failed to delete document from {collection}.") from exc


async def query_collection(
    collection: str,
    filters: Optional[List[tuple]] = None,
    order_by: Optional[str] = None,
    limit: int = 100,
) -> List[Dict[str, Any]]:
    """
    Query a Firestore collection with optional filters.

    Args:
        collection: Collection name to query.
        filters: List of (field, operator, value) tuples, e.g. [("status", "==", "active")].
        order_by: Field to order results by.
        limit: Maximum number of results (default 100).

    Returns:
        List of document dicts.
    """
    try:
        db = _get_db()
        query = db.collection(collection)

        if filters:
            for field, operator, value in filters:
                query = query.where(field, operator, value)

        if order_by:
            query = query.order_by(order_by)

        query = query.limit(limit)
        docs = query.stream()
        return [{"id": doc.id, **doc.to_dict()} for doc in docs]

    except (ServiceUnavailableError, FirebaseError):
        raise
    except Exception as exc:
        logger.error("Firestore query failed", collection=collection, exc_info=exc)
        raise FirebaseError(f"Failed to query collection {collection}.") from exc
