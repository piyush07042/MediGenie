"""
Startup validation and shared application state.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.core.config import settings


@dataclass
class AppState:
    """Shared runtime state for the backend application."""

    supervisor: Any = None
    ml_model: Any = None
    vector_store: Any = None
    ocr_engine: Any = None


app_state = AppState()


def validate_environment() -> None:
    """
    Validate required configuration at startup.
    """

    required = [
        settings.SECRET_KEY,
        settings.DATABASE_URL,
    ]

    if not all(required):
        raise RuntimeError(
            "Required environment variables are missing."
        )