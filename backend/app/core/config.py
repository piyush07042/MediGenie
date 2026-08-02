"""
Application configuration.
"""

from __future__ import annotations

from pydantic import Field
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


settings = Settings()