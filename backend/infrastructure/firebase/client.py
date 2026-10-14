"""
backend/infrastructure/firebase/client.py
------------------------------------------
Firebase Admin SDK singleton initialization.

The SDK is initialized once at application startup using credentials
from the environment. All Firebase services (Firestore, Auth, Storage)
share this single initialized app instance.

When FIREBASE_CREDENTIALS_PATH is empty or the credentials file does not
exist, initialization is skipped and the system operates in demo mode.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

import firebase_admin
from firebase_admin import credentials

from backend.core.config import settings
from backend.core.logging import get_logger

logger = get_logger(__name__)

# Module-level reference to the initialized Firebase app
_firebase_app: Optional[firebase_admin.App] = None


def initialize_firebase() -> Optional[firebase_admin.App]:
    """
    Initialize Firebase Admin SDK if not already initialized.

    Returns:
        The initialized Firebase app, or None if credentials are unavailable.
    """
    global _firebase_app

    if _firebase_app is not None:
        return _firebase_app

    # Check if Firebase is already initialized by another module
    if firebase_admin._apps:
        _firebase_app = firebase_admin.get_app()
        logger.info("Firebase already initialized; reusing existing app")
        return _firebase_app

    if not settings.firebase_configured:
        logger.warning(
            "Firebase credentials not configured – running in demo mode.",
            hint="Set FIREBASE_PROJECT_ID and FIREBASE_CREDENTIALS_PATH in .env",
        )
        return None

    creds_path = Path(settings.firebase_credentials_path)
    if not creds_path.exists():
        logger.warning(
            "Firebase credentials file not found",
            path=str(creds_path),
            hint="Ensure the service account JSON file exists at the configured path",
        )
        return None

    try:
        cred = credentials.Certificate(str(creds_path))
        options: dict = {"projectId": settings.firebase_project_id}

        if settings.firebase_storage_bucket:
            options["storageBucket"] = settings.firebase_storage_bucket

        if settings.firebase_database_url:
            options["databaseURL"] = settings.firebase_database_url

        _firebase_app = firebase_admin.initialize_app(cred, options)
        logger.info(
            "Firebase Admin SDK initialized",
            project_id=settings.firebase_project_id,
            storage_bucket=settings.firebase_storage_bucket,
        )
        return _firebase_app

    except Exception as exc:
        logger.error("Firebase initialization failed", exc_info=exc)
        return None


def get_firebase_app() -> Optional[firebase_admin.App]:
    """
    Return the initialized Firebase app.
    Attempts initialization if not already done.
    """
    global _firebase_app
    if _firebase_app is None:
        _firebase_app = initialize_firebase()
    return _firebase_app


def shutdown_firebase() -> None:
    """
    Delete the Firebase app. Called during application shutdown.
    """
    global _firebase_app
    if _firebase_app is not None:
        try:
            firebase_admin.delete_app(_firebase_app)
            logger.info("Firebase Admin SDK shut down")
        except Exception as exc:
            logger.warning("Error shutting down Firebase", exc_info=exc)
        finally:
            _firebase_app = None
