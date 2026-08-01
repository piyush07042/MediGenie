"""
Application Version API
"""

from __future__ import annotations

from fastapi import APIRouter, status

from app.schemas.common import ApiResponse

router = APIRouter(
    prefix="/version",
    tags=["Version"],
)

APP_NAME = "MediGenie"
APP_VERSION = "2.0.0"
API_VERSION = "v1"


@router.get(
    "/",
    response_model=ApiResponse,
    status_code=status.HTTP_200_OK,
)
async def get_version():
    """
    Return application version information.
    """

    return ApiResponse(
        message="Version information retrieved successfully.",
        data={
            "application": APP_NAME,
            "version": APP_VERSION,
            "api_version": API_VERSION,
        },
    )