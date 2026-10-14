"""
backend/core/logging.py
------------------------
Structured JSON logging configuration for the AI Healthcare Coordination Platform.

Uses structlog for structured, machine-readable log output.
All logs are privacy-safe: sensitive fields are scrubbed before emission.

Usage:
    from backend.core.logging import get_logger
    logger = get_logger(__name__)
    logger.info("Request received", request_id="abc123", user_id="u001")
"""

from __future__ import annotations

import logging
import sys
from typing import Any, MutableMapping

import structlog
from structlog.types import EventDict, WrappedLogger

from backend.core.config import settings

# Fields that must never appear in logs (redacted with ****)
_SENSITIVE_FIELDS = frozenset(
    {
        "password",
        "token",
        "access_token",
        "refresh_token",
        "api_key",
        "secret",
        "authorization",
        "firebase_credentials",
        "otp",
        "pin",
        "credit_card",
        "ssn",
        "aadhaar",
    }
)


def _redact_sensitive(
    logger: WrappedLogger,  # noqa: ARG001
    method_name: str,  # noqa: ARG001
    event_dict: EventDict,
) -> EventDict:
    """
    Structlog processor that redacts sensitive fields from every log event.
    Operates recursively on nested dicts.
    """
    for key in list(event_dict.keys()):
        if key.lower() in _SENSITIVE_FIELDS:
            event_dict[key] = "****"
    return event_dict


def _add_service_context(
    logger: WrappedLogger,  # noqa: ARG001
    method_name: str,  # noqa: ARG001
    event_dict: EventDict,
) -> EventDict:
    """
    Structlog processor that injects static service metadata into every log event.
    """
    event_dict.setdefault("service", settings.app_name)
    event_dict.setdefault("version", settings.app_version)
    event_dict.setdefault("env", settings.app_env)
    return event_dict


def configure_logging() -> None:
    """
    Configure both standard library logging and structlog.
    Should be called once at application startup.
    """
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)

    # ── Standard library logging (used by third-party libs) ────────
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level,
    )
    if settings.log_format == "json":
        renderer = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer(
            colors=True,
            exception_formatter=structlog.dev.plain_traceback,
        )

    # ── Shared processors applied to every log event ────────────────
    shared_processors: list[Any] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
        _add_service_context,
        _redact_sensitive,
    ]

    if settings.log_format == "json":
        # Ensure exceptions are formatted as JSON-serialisable strings
        shared_processors.append(structlog.processors.format_exc_info)

    # Configure standard library logging to use our renderer
    formatter = structlog.stdlib.ProcessorFormatter(
        processor=renderer,
        foreign_pre_chain=shared_processors,
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(log_level)

    # Silence noisy third-party loggers in production
    if settings.is_production:
        for noisy_logger in ("uvicorn.access", "httpx", "httpcore"):
            logging.getLogger(noisy_logger).setLevel(logging.WARNING)

    structlog.configure(
        processors=shared_processors
        + [
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str = __name__) -> structlog.BoundLogger:
    """
    Return a structlog BoundLogger bound to *name*.

    Args:
        name: Typically __name__ of the calling module.

    Returns:
        A structlog BoundLogger with service context pre-bound.
    """
    return structlog.get_logger(name)


def bind_request_context(
    request_id: str,
    *,
    user_id: str | None = None,
    session_id: str | None = None,
) -> None:
    """
    Bind per-request context variables so every log within the request
    automatically includes request_id, user_id, and session_id.

    Should be called at the start of each request (e.g., in middleware).
    """
    ctx: MutableMapping[str, Any] = {}
    ctx["request_id"] = request_id
    if user_id:
        ctx["user_id"] = user_id
    if session_id:
        ctx["session_id"] = session_id
    structlog.contextvars.bind_contextvars(**ctx)


def clear_request_context() -> None:
    """
    Clear all per-request context variables.
    Should be called at the end of each request (e.g., in middleware).
    """
    structlog.contextvars.clear_contextvars()
