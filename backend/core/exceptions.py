"""
backend/core/exceptions.py
---------------------------
Custom exception hierarchy for the AI Healthcare Coordination Platform.

All domain exceptions descend from AppException and carry:
  - status_code  → HTTP status code for API responses
  - error_code   → Machine-readable code for client error handling
  - detail       → Human-readable description
  - metadata     → Optional structured context (never contains PII)

These exceptions are caught by the global exception handlers registered
in backend/core/middleware.py and converted to consistent JSON responses.
"""

from __future__ import annotations

from typing import Any, Dict, Optional


# ──────────────────────────────────────────────────────────────────
# Base Exception
# ──────────────────────────────────────────────────────────────────


class AppException(Exception):
    """
    Base class for all application-specific exceptions.
    Provides structured attributes that map cleanly to HTTP error responses.
    """

    status_code: int = 500
    error_code: str = "INTERNAL_ERROR"

    def __init__(
        self,
        detail: str = "An unexpected error occurred.",
        *,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(detail)
        self.detail = detail
        self.metadata: Dict[str, Any] = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the exception to a JSON-safe dict for API responses."""
        payload: Dict[str, Any] = {
            "error": True,
            "error_code": self.error_code,
            "detail": self.detail,
        }
        if self.metadata:
            payload["metadata"] = self.metadata
        return payload

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"status_code={self.status_code}, "
            f"error_code={self.error_code!r}, "
            f"detail={self.detail!r})"
        )


# ──────────────────────────────────────────────────────────────────
# 4xx Client Errors
# ──────────────────────────────────────────────────────────────────


class ValidationError(AppException):
    """
    Raised when request input fails validation.
    Extends the base so Pydantic validation errors can be wrapped consistently.
    """

    status_code = 422
    error_code = "VALIDATION_ERROR"

    def __init__(
        self,
        detail: str = "Request validation failed.",
        *,
        fields: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        meta = metadata or {}
        if fields:
            meta["fields"] = fields
        super().__init__(detail, metadata=meta)


class AuthenticationError(AppException):
    """
    Raised when a request cannot be authenticated
    (missing, invalid, or expired credentials).
    """

    status_code = 401
    error_code = "AUTHENTICATION_REQUIRED"

    def __init__(
        self,
        detail: str = "Authentication is required to access this resource.",
        *,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(detail, metadata=metadata)


class AuthorizationError(AppException):
    """
    Raised when an authenticated user lacks permission to perform an operation.
    """

    status_code = 403
    error_code = "AUTHORIZATION_DENIED"

    def __init__(
        self,
        detail: str = "You do not have permission to perform this operation.",
        *,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(detail, metadata=metadata)


class NotFoundError(AppException):
    """
    Raised when a requested resource does not exist.
    """

    status_code = 404
    error_code = "NOT_FOUND"

    def __init__(
        self,
        resource: str = "Resource",
        resource_id: Optional[str] = None,
        *,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        if resource_id:
            detail = f"{resource} with ID '{resource_id}' was not found."
        else:
            detail = f"{resource} was not found."
        super().__init__(detail, metadata=metadata)
        self.resource = resource
        self.resource_id = resource_id


class ConflictError(AppException):
    """
    Raised when an operation conflicts with existing state
    (e.g., duplicate record, concurrent modification).
    """

    status_code = 409
    error_code = "CONFLICT"

    def __init__(
        self,
        detail: str = "The request conflicts with the current state of the resource.",
        *,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(detail, metadata=metadata)


class RateLimitError(AppException):
    """
    Raised when a client exceeds its allowed request rate.
    """

    status_code = 429
    error_code = "RATE_LIMIT_EXCEEDED"

    def __init__(
        self,
        detail: str = "Too many requests. Please slow down.",
        *,
        retry_after: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        meta = metadata or {}
        if retry_after is not None:
            meta["retry_after_seconds"] = retry_after
        super().__init__(detail, metadata=meta)
        self.retry_after = retry_after


# ──────────────────────────────────────────────────────────────────
# 5xx Server / Infrastructure Errors
# ──────────────────────────────────────────────────────────────────


class ExternalServiceError(AppException):
    """
    Raised when an external service (Firebase, Redis, RabbitMQ, Qdrant,
    LLM provider, Twilio, etc.) returns an error or is unreachable.
    """

    status_code = 502
    error_code = "EXTERNAL_SERVICE_ERROR"

    def __init__(
        self,
        service: str,
        detail: str = "An external service returned an unexpected error.",
        *,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        meta = metadata or {}
        meta["service"] = service
        super().__init__(detail, metadata=meta)
        self.service = service


class ServiceUnavailableError(AppException):
    """
    Raised when a required infrastructure dependency is temporarily unavailable
    (e.g., Redis connection refused, RabbitMQ disconnected).
    """

    status_code = 503
    error_code = "SERVICE_UNAVAILABLE"

    def __init__(
        self,
        service: str = "Dependency",
        detail: Optional[str] = None,
        *,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        resolved_detail = detail or f"{service} is currently unavailable. Please try again later."
        meta = metadata or {}
        meta["service"] = service
        super().__init__(resolved_detail, metadata=meta)
        self.service = service


class OrchestrationError(AppException):
    """
    Raised when the LangGraph Planner encounters a workflow coordination failure.
    This is distinct from agent-level errors, which are handled within agent nodes.
    """

    status_code = 500
    error_code = "ORCHESTRATION_ERROR"

    def __init__(
        self,
        detail: str = "Workflow orchestration encountered an unrecoverable error.",
        *,
        workflow_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        meta = metadata or {}
        if workflow_id:
            meta["workflow_id"] = workflow_id
        super().__init__(detail, metadata=meta)
        self.workflow_id = workflow_id


class SharedMemoryError(AppException):
    """
    Raised when shared memory operations fail (read, write, or consistency violation).
    """

    status_code = 500
    error_code = "SHARED_MEMORY_ERROR"

    def __init__(
        self,
        detail: str = "Shared memory operation failed.",
        *,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(detail, metadata=metadata)


class FirebaseError(ExternalServiceError):
    """
    Specialization for Firebase-specific failures.
    """

    error_code = "FIREBASE_ERROR"

    def __init__(
        self,
        detail: str = "Firebase operation failed.",
        *,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__("Firebase", detail, metadata=metadata)


class VectorDatabaseError(ExternalServiceError):
    """
    Specialization for Qdrant or other vector database failures.
    """

    error_code = "VECTOR_DB_ERROR"

    def __init__(
        self,
        detail: str = "Vector database operation failed.",
        *,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__("Qdrant", detail, metadata=metadata)


class LLMProviderError(ExternalServiceError):
    """
    Raised when an LLM provider (Gemini, OpenAI, Groq) returns an error
    or the response cannot be parsed.
    """

    error_code = "LLM_PROVIDER_ERROR"

    def __init__(
        self,
        provider: str = "LLM",
        detail: str = "LLM provider returned an error.",
        *,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(provider, detail, metadata=metadata)
        self.provider = provider
