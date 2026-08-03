"""
Health check endpoints.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request, status

from app.core.config import settings
from app.core.startup import app_state
from app.schemas.common import ApiResponse

router = APIRouter(
    prefix="/health",
    tags=["Health"],
)


@router.get("", response_model=ApiResponse, status_code=status.HTTP_200_OK)
async def health_check():
    """
    Returns application health status.
    """

    return ApiResponse(
        message="Application health status retrieved successfully.",
        data={
            "status": "healthy",
            "application": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "services": {
                "supervisor": app_state.supervisor is not None,
                "ml_model": app_state.ml_model is not None,
                "vector_store": app_state.vector_store is not None,
                "ocr": app_state.ocr_engine is not None,
            },
            "model_registry_size": len(app_state.model_registry or {}),
        },
    )


@router.get("/ready", response_model=ApiResponse)
async def readiness_probe(request: Request):
    """
    Returns application readiness status.
    """

    startup_error = getattr(request.app.state, "startup_error", False)
    if startup_error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "success": False,
                "message": "Application startup failed.",
                "data": {
                    "ready": False,
                    "error": getattr(request.app.state, "startup_error_details", "Unknown startup error."),
                },
            },
        )

    return ApiResponse(
        message="Application is ready.",
        data={"ready": True},
    )


@router.get("/live", response_model=ApiResponse, status_code=status.HTTP_200_OK)
async def liveness_probe():
    """
    Returns application liveness status.
    """

    return ApiResponse(
        message="Application is live.",
        data={"live": True},
    )
