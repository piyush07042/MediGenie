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

from ml.inference.predictor import Predictor
from ml.inference.predictor import PredictorConfig
from ml.registry import resolve_model_directory


def _resolve_model_directory(model_directory: str | Path) -> Path:
    """Resolve the best available heart-disease model directory."""
    candidate = Path(model_directory).expanduser()
    if candidate.exists() and candidate.is_dir():
        return candidate

    fallback = resolve_model_directory("heart_disease")
    if fallback.exists() and fallback.is_dir():
        return fallback

    return candidate

logger = logging.getLogger(__name__)


class HeartDiseaseService:
    """Thin service wrapper around the shared predictor."""

    def __init__(self, model_directory: str | Path) -> None:

        self.model_directory = _resolve_model_directory(model_directory)
        self.predictor = Predictor(
            PredictorConfig(model_directory=self.model_directory)
        )
        self._initialized = False
        try:
            self.predictor.initialize()
            self._initialized = True
        except Exception as exc:  # pragma: no cover - defensive fallback
            logger.warning("Heart disease predictor initialization failed: %s", exc)
            self._initialized = False

    def predict(self, patient_data: dict[str, Any]) -> dict[str, Any]:
        """Execute disease prediction."""

        if self.predictor is None or not self._initialized:
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
            "status": "healthy" if self._initialized else "degraded",
            "service": "heart_disease",
            "model_loaded": self._initialized,
            "model_directory": str(self.model_directory),
        }


_service: HeartDiseaseService | None = None


def get_heart_disease_service(model_directory: str | Path) -> HeartDiseaseService:
    """Return singleton service instance."""

    global _service

    if _service is None:
        _service = HeartDiseaseService(model_directory)

    return _service
