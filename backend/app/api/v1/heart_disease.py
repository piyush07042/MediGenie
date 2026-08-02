"""
Heart Disease Prediction API
"""

from __future__ import annotations

import logging

from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import status

from backend.app.schemas.heart_disease import HeartDiseasePredictionRequest
from backend.app.schemas.heart_disease import HeartDiseasePredictionResponse
from backend.app.services.heart_disease_service import get_heart_disease_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/heart-disease", tags=["Heart Disease"])

MODEL_DIRECTORY = "backend/models/heart_disease"
service = get_heart_disease_service(MODEL_DIRECTORY)


@router.get("/health", status_code=status.HTTP_200_OK)
async def health():
    return service.health()


@router.post(
    "/predict",
    response_model=HeartDiseasePredictionResponse,
    status_code=status.HTTP_200_OK,
)
async def predict(request: HeartDiseasePredictionRequest):

    try:
        result = service.predict(request.model_dump())
        return HeartDiseasePredictionResponse(**result)
    except Exception as exc:
        logger.exception(exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )


@router.get("/", status_code=status.HTTP_200_OK)
async def info():
    return {
        "model": "Heart Disease",
        "version": "1.0.0",
        "status": "ready",
    }
