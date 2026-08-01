"""
Startup validation.
"""

from __future__ import annotations

from app.core.config import settings


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