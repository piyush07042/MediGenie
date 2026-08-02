"""
heart_disease_service.py

Heart Disease prediction service.

Responsibilities
----------------
✓ Load predictor once
✓ Validate requests
✓ Execute prediction
✓ Return API-friendly response
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from backend.ml.inference.predictor import Predictor
from backend.ml.inference.predictor import PredictorConfig

logger = logging.getLogger(__name__)


class HeartDiseaseService:
    """Thin service wrapper around the shared predictor."""

    def __init__(self, model_directory: str | Path) -> None:

        self.model_directory = Path(model_directory)
        self.predictor = Predictor(
            PredictorConfig(model_directory=self.model_directory)
        )
        self.predictor.initialize()

    def predict(self, patient_data: dict[str, Any]) -> dict[str, Any]:
        """Execute disease prediction."""

        if self.predictor is None:
            raise RuntimeError("Predictor not initialized.")

        result = self.predictor.predict(patient_data)

        return {
            "success": True,
            "disease": "heart_disease",
            "prediction": result.prediction,
            "probability": result.probability,
            "confidence": result.confidence,
            "class_probabilities": result.class_probabilities,
        }

    def health(self) -> dict[str, Any]:
        """Service health status."""

        return {
            "status": "healthy",
            "service": "heart_disease",
            "model_loaded": self.predictor is not None,
        }


_service: HeartDiseaseService | None = None


def get_heart_disease_service(model_directory: str | Path) -> HeartDiseaseService:
    """Return singleton service instance."""

    global _service

    if _service is None:
        _service = HeartDiseaseService(model_directory)

    return _service
