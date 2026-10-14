"""
backend/infrastructure/firebase/auth.py
----------------------------------------
Firebase Authentication helpers for the AI Healthcare Coordination Platform.

Provides:
  - Token verification (ID tokens issued by Firebase Auth)
  - User creation / retrieval / deletion via Admin SDK
  - Custom claims management for role-based access control

When Firebase is not configured (demo mode), all functions return
safe mock responses so development can proceed without credentials.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from backend.core.config import settings
from backend.core.exceptions import AuthenticationError, FirebaseError
from backend.core.logging import get_logger

logger = get_logger(__name__)


# ──────────────────────────────────────────────────────────────────
# Token Verification
# ──────────────────────────────────────────────────────────────────


async def verify_token(id_token: str) -> Dict[str, Any]:
    """
    Verify a Firebase ID token and return the decoded claims.

    Args:
        id_token: Raw Firebase ID token from the client.

    Returns:
        Decoded token payload (uid, email, name, custom claims, etc.)

    Raises:
        AuthenticationError: If the token is invalid or expired.
    """
    if not settings.firebase_configured:
        logger.debug("Firebase not configured; skipping token verification (demo mode)")
        return {
            "uid": "demo-user-001",
            "email": "demo@ai-sahayak.local",
            "name": "Demo User",
            "role": "patient",
        }

    try:
        from firebase_admin import auth as firebase_auth

        decoded = firebase_auth.verify_id_token(id_token, check_revoked=True)
        logger.debug("Firebase token verified", uid=decoded.get("uid"))
        return decoded

    except Exception as exc:
        logger.warning("Firebase token verification failed", exc_info=exc)
        raise AuthenticationError("Invalid or expired authentication token.") from exc


# ──────────────────────────────────────────────────────────────────
# User Management
# ──────────────────────────────────────────────────────────────────


async def get_user(uid: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve a Firebase Auth user record by UID.

    Returns:
        User record dict, or None if the user does not exist.
    """
    if not settings.firebase_configured:
        return {"uid": uid, "email": f"{uid}@demo.local", "display_name": "Demo User"}

    try:
        from firebase_admin import auth as firebase_auth

        user = firebase_auth.get_user(uid)
        return {
            "uid": user.uid,
            "email": user.email,
            "display_name": user.display_name,
            "photo_url": user.photo_url,
            "disabled": user.disabled,
            "custom_claims": user.custom_claims or {},
            "provider_data": [p.provider_id for p in user.provider_data],
        }

    except Exception as exc:
        logger.warning("Failed to retrieve Firebase user", uid=uid, exc_info=exc)
        return None


async def set_custom_claims(uid: str, claims: Dict[str, Any]) -> bool:
    """
    Set custom claims on a Firebase Auth user (used for RBAC roles).

    Args:
        uid: Firebase user UID.
        claims: Dict of custom claim key-value pairs (e.g. {"role": "doctor"}).

    Returns:
        True if successful, False otherwise.
    """
    if not settings.firebase_configured:
        logger.debug("Skipping custom claims (demo mode)", uid=uid, claims=claims)
        return True

    try:
        from firebase_admin import auth as firebase_auth

        firebase_auth.set_custom_user_claims(uid, claims)
        logger.info("Custom claims set", uid=uid, claims=claims)
        return True

    except Exception as exc:
        logger.error("Failed to set custom claims", uid=uid, exc_info=exc)
        return False


async def revoke_tokens(uid: str) -> bool:
    """
    Revoke all refresh tokens for a user (e.g., on logout or account suspension).
    """
    if not settings.firebase_configured:
        return True

    try:
        from firebase_admin import auth as firebase_auth

        firebase_auth.revoke_refresh_tokens(uid)
        logger.info("Firebase tokens revoked", uid=uid)
        return True

    except Exception as exc:
        logger.error("Failed to revoke Firebase tokens", uid=uid, exc_info=exc)
        return False
