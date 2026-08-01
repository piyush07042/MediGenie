"""
Health check endpoints.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.core.config import settings
from app.core.startup import app_state

router = APIRouter(
    prefix="/health",
    tags=["Health"],
)


@router.get("")
async def health_check():
    """
    Returns application health status.
    """

    return {
        "status": "healthy",
        "application": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "services": {
            "supervisor": app_state.supervisor is not None,
            "ml_model": app_state.ml_model is not None,
            "vector_store": app_state.vector_store is not None,
            "ocr": app_state.ocr_engine is not None,
        },
    }