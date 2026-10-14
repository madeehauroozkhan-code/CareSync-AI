"""
backend/core/config.py
-----------------------
Centralized, type-safe configuration management using Pydantic BaseSettings.

All settings are read from environment variables or a .env file at project root.
Sensitive values are never hardcoded. Defaults are safe for local development.

Usage:
    from backend.core.config import settings
    print(settings.app_name)
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import List, Literal, Optional

from pydantic import AnyHttpUrl, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    """
    Application-wide settings loaded from environment variables.
    All fields map 1-to-1 with variables in .env.example.
    """

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[1] / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # Ignore unrecognised env vars gracefully
    )

    # ── Application ─────────────────────────────────────────────
    app_name: str = Field(
        default="AI Healthcare Coordination Platform",
        description="Human-readable application name",
    )
    app_version: str = Field(default="1.0.0")
    app_env: Literal["development", "staging", "production"] = Field(
        default="development"
    )
    debug: bool = Field(default=True)
    secret_key: str = Field(
        default="change-me-to-a-strong-random-secret-key",
        description="Used for token signing and session security",
    )
    cors_allowed_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173", "http://localhost:5174"],
        description="Comma-separated list of allowed CORS origins",
    )

    # ── Logging ──────────────────────────────────────────────────
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO"
    )
    log_format: Literal["json", "text"] = Field(default="json")

    # ── API ──────────────────────────────────────────────────────
    api_host: str = Field(default="0.0.0.0")
    api_port: int = Field(default=8000)
    api_workers: int = Field(default=1)
    api_reload: bool = Field(default=True)

    # ── Firebase ─────────────────────────────────────────────────
    firebase_project_id: str = Field(default="")
    firebase_credentials_path: str = Field(default="")
    firebase_storage_bucket: str = Field(default="")
    firebase_database_url: str = Field(default="")

    # ── Redis ─────────────────────────────────────────────────────
    redis_url: str = Field(default="redis://localhost:6379/0")
    redis_max_connections: int = Field(default=20)
    redis_decode_responses: bool = Field(default=True)
    redis_default_ttl: int = Field(default=3600, description="Default TTL in seconds")

    # ── RabbitMQ ──────────────────────────────────────────────────
    rabbitmq_url: str = Field(default="")
    rabbitmq_exchange: str = Field(default="sahayak.events")
    rabbitmq_exchange_type: str = Field(default="topic")
    rabbitmq_prefetch_count: int = Field(default=10)

    # ── Qdrant ────────────────────────────────────────────────────
    qdrant_url: str = Field(default="http://localhost:6333")
    qdrant_api_key: Optional[str] = Field(default=None)
    qdrant_collection_medical_knowledge: str = Field(default="medical_knowledge")
    qdrant_collection_patient_memory: str = Field(default="patient_memory")
    qdrant_vector_size: int = Field(default=1024, description="BAAI BGE-M3 embedding dimension")

    # ── LLM Providers ────────────────────────────────────────────
    llm_primary_provider: Literal["gemini", "openai", "none"] = Field(default="gemini")
    llm_fallback_provider: Literal["gemini", "openai", "none"] = Field(default="openai")
    gemini_api_key: str = Field(default="")
    gemini_model: str = Field(default="gemini-2.5-flash")
    openai_api_key: str = Field(default="")
    openai_model: str = Field(default="gpt-4.1-mini")
    groq_api_key: str = Field(default="")
    groq_whisper_model: str = Field(default="whisper-large-v3")

    # ── Embedding Model ───────────────────────────────────────────
    embedding_model: str = Field(default="BAAI/bge-m3")
    embedding_device: str = Field(default="cpu")

    # ── Celery ────────────────────────────────────────────────────
    celery_broker_url: str = Field(default="redis://localhost:6379/1")
    celery_result_backend: str = Field(default="redis://localhost:6379/2")

    # ── External Services ─────────────────────────────────────────
    google_maps_api_key: str = Field(default="")
    twilio_account_sid: str = Field(default="")
    twilio_auth_token: str = Field(default="")
    twilio_whatsapp_from: str = Field(default="")
    twilio_sms_from: str = Field(default="")

    # ── Observability ─────────────────────────────────────────────
    otel_enabled: bool = Field(default=False)
    otel_service_name: str = Field(default="ai-sahayak-backend")
    otel_exporter_otlp_endpoint: str = Field(default="http://localhost:4317")

    # ── Feature Flags ─────────────────────────────────────────────
    demo_mode: bool = Field(default=True)
    enable_auth: bool = Field(default=False)
    enable_rate_limiting: bool = Field(default=False)
    max_requests_per_minute: int = Field(default=60)

    # ── Computed Properties ───────────────────────────────────────
    @property
    def is_production(self) -> bool:
        """True when running in production environment."""
        return self.app_env == "production"

    @property
    def is_development(self) -> bool:
        """True when running in development environment."""
        return self.app_env == "development"

    @property
    def firebase_configured(self) -> bool:
        """True when Firebase credentials are provided."""
        return bool(self.firebase_project_id and self.firebase_credentials_path)

    @property
    def redis_configured(self) -> bool:
        """True when a Redis URL is configured."""
        return bool(self.redis_url)

    @property
    def rabbitmq_configured(self) -> bool:
        """True when a RabbitMQ URL is configured."""
        return bool(self.rabbitmq_url)

    @property
    def qdrant_configured(self) -> bool:
        """True when Qdrant URL is configured."""
        return bool(self.qdrant_url)

    @property
    def llm_configured(self) -> bool:
        """True when at least one LLM provider key is present."""
        return bool(self.gemini_api_key or self.openai_api_key)

    @field_validator("cors_allowed_origins", mode="before")
    @classmethod
    def _parse_cors_origins(cls, value: object) -> List[str]:
        """Accept either a list or a comma-separated string for CORS origins."""
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return list(value)


@lru_cache(maxsize=1)
def get_settings() -> AppSettings:
    """
    Return a cached singleton of AppSettings.
    The cache ensures the .env file is only parsed once per process.
    """
    return AppSettings()


# Module-level convenience alias used throughout the codebase:
#   from backend.core.config import settings
settings: AppSettings = get_settings()
