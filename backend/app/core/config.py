"""
Application configuration.
"""

from __future__ import annotations

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )

    # ==========================================================
    # Application
    # ==========================================================

    APP_NAME: str = "MediGenie"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # ==========================================================
    # API
    # ==========================================================

    API_V1_PREFIX: str = "/api/v1"

    # ==========================================================
    # Security
    # ==========================================================

    SECRET_KEY: str = "dev-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # ==========================================================
    # Database
    # ==========================================================

    DATABASE_URL: str = "sqlite:///./medigenie_cdss.db"

    # ==========================================================
    # CORS
    # ==========================================================

    BACKEND_CORS_ORIGINS: list[str] = Field(
        default_factory=lambda: [
            "http://localhost:3000",
        ]
    )

    ALLOW_CREDENTIALS: bool = True

    ALLOW_METHODS: list[str] = Field(
        default_factory=lambda: [
            "*",
        ]
    )

    ALLOW_HEADERS: list[str] = Field(
        default_factory=lambda: [
            "*",
        ]
    )

    # ==========================================================
    # Uploads
    # ==========================================================

    UPLOAD_DIRECTORY: str = "uploads"
    MAX_UPLOAD_SIZE: int = 20 * 1024 * 1024

    # ==========================================================
    # Logging
    # ==========================================================

    LOG_LEVEL: str = "INFO"
    LOG_DIRECTORY: str = "logs"

    # ==========================================================
    # AI Providers
    # ==========================================================

    OPENAI_API_KEY: str | None = None
    GOOGLE_API_KEY: str | None = None
    LANGCHAIN_API_KEY: str | None = None
    HUGGINGFACE_API_KEY: str | None = None

    # ==========================================================
    # OCR
    # ==========================================================

    TESSERACT_CMD: str | None = None
    POPPLER_PATH: str | None = None

    # ==========================================================
    # Redis
    # ==========================================================

    REDIS_URL: str | None = None

    # ==========================================================
    # Notifications
    # ==========================================================

    DRUG_SAFETY_WEBHOOK_URL: str | None = None

    # ==========================================================
    # Scheduler
    # ==========================================================

    SCHEDULER_ENABLED: bool = False
    SCHEDULER_INTERVAL_SECONDS: int = 0
    SCHEDULER_PATIENT_ID: int | None = None
    SCHEDULER_OUT_DIR: str = "temp_reports"
    SCHEDULER_DRY_RUN: bool = True

    AGENT_FALLBACK_MAPPINGS: dict[str, str] = Field(default_factory=dict)

    @field_validator("DEBUG", "ALLOW_CREDENTIALS", mode="before")
    @classmethod
    def parse_bool_fields(cls, value):
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            lowered = value.strip().lower()
            if lowered in {"1", "true", "yes", "on", "debug", "release"}:
                return lowered in {"1", "true", "yes", "on", "debug"}
            if lowered in {"0", "false", "no", "off", "none", "null", ""}:
                return False
        return value

    @field_validator("AGENT_FALLBACK_MAPPINGS", mode="before")
    @classmethod
    def parse_fallback_mappings(cls, value):
        if isinstance(value, str) and value.strip():
            try:
                import json

                return json.loads(value)
            except ValueError:
                return {}
        return value or {}


settings = Settings()