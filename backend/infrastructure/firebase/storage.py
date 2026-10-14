"""
backend/infrastructure/firebase/storage.py
-------------------------------------------
Firebase Cloud Storage helpers for the AI Healthcare Coordination Platform.

Handles:
  - File uploads (medical documents, audio, images)
  - File downloads (generating signed URLs)
  - File deletion

Bucket is initialised from Firebase Admin SDK once at startup.
In demo mode, all operations return mock responses.
"""

from __future__ import annotations

import mimetypes
import os
from pathlib import Path
from typing import BinaryIO, Optional

from backend.core.config import settings
from backend.core.exceptions import FirebaseError, ServiceUnavailableError
from backend.core.logging import get_logger

logger = get_logger(__name__)

_bucket = None


def get_storage_bucket():
    """Return the Firebase Storage bucket, initializing if necessary."""
    global _bucket

    if _bucket is not None:
        return _bucket

    if not settings.firebase_configured:
        logger.debug("Firebase Storage unavailable – demo mode")
        return None

    try:
        from firebase_admin import storage as firebase_storage

        from backend.infrastructure.firebase.client import get_firebase_app

        app = get_firebase_app()
        if app is None:
            return None

        _bucket = firebase_storage.bucket(app=app)
        logger.info("Firebase Storage bucket initialized", bucket=settings.firebase_storage_bucket)
        return _bucket

    except Exception as exc:
        logger.error("Firebase Storage initialization failed", exc_info=exc)
        return None


async def upload_file(
    file_data: BinaryIO,
    destination_path: str,
    content_type: Optional[str] = None,
) -> str:
    """
    Upload a file to Firebase Cloud Storage.

    Args:
        file_data: File-like object to upload.
        destination_path: Path within the bucket (e.g., "users/uid/documents/report.pdf").
        content_type: MIME type. Auto-detected from destination_path if not provided.

    Returns:
        Public URL or signed URL of the uploaded file.

    Raises:
        ServiceUnavailableError: If Firebase Storage is not configured.
        FirebaseError: If the upload fails.
    """
    bucket = get_storage_bucket()
    if bucket is None:
        raise ServiceUnavailableError("Firebase Storage", "Storage is not available in demo mode.")

    if content_type is None:
        content_type, _ = mimetypes.guess_type(destination_path)
        content_type = content_type or "application/octet-stream"

    try:
        blob = bucket.blob(destination_path)
        blob.upload_from_file(file_data, content_type=content_type)
        blob.make_public()
        url = blob.public_url
        logger.info("File uploaded to Firebase Storage", path=destination_path, url=url)
        return url

    except Exception as exc:
        logger.error("Firebase Storage upload failed", path=destination_path, exc_info=exc)
        raise FirebaseError(f"Failed to upload file to {destination_path}.") from exc


async def get_signed_url(destination_path: str, expiration_minutes: int = 60) -> str:
    """
    Generate a signed URL for temporary private access to a stored file.

    Args:
        destination_path: Path within the bucket.
        expiration_minutes: How long the URL remains valid (default 60 minutes).

    Returns:
        Signed URL string.
    """
    bucket = get_storage_bucket()
    if bucket is None:
        raise ServiceUnavailableError("Firebase Storage")

    try:
        import datetime

        blob = bucket.blob(destination_path)
        url = blob.generate_signed_url(
            expiration=datetime.timedelta(minutes=expiration_minutes),
            method="GET",
        )
        logger.debug("Signed URL generated", path=destination_path, expiration_minutes=expiration_minutes)
        return url

    except Exception as exc:
        logger.error("Failed to generate signed URL", path=destination_path, exc_info=exc)
        raise FirebaseError(f"Failed to generate signed URL for {destination_path}.") from exc


async def delete_file(destination_path: str) -> bool:
    """Delete a file from Firebase Storage. Returns True on success."""
    bucket = get_storage_bucket()
    if bucket is None:
        return False

    try:
        blob = bucket.blob(destination_path)
        blob.delete()
        logger.info("File deleted from Firebase Storage", path=destination_path)
        return True

    except Exception as exc:
        logger.warning("Firebase Storage delete failed", path=destination_path, exc_info=exc)
        return False
