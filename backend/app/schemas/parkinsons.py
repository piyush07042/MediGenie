"""
Parkinson's Disease API Schemas
"""

from __future__ import annotations

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field


class ParkinsonsPredictionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    age: int = Field(..., ge=1, le=120, description="Age in years", json_schema_extra={"example": 60})
    motor_UPDRS: float = Field(..., ge=0.0, le=100.0, description="Motor Unified Parkinson's Disease Rating Scale", json_schema_extra={"example": 20.0})
    total_UPDRS: float = Field(..., ge=0.0, le=200.0, description="Total Unified Parkinson's Disease Rating Scale", json_schema_extra={"example": 35.0})
    Jitter_local: float = Field(..., ge=0.0, le=0.1, description="Local jitter in voice signal", json_schema_extra={"example": 0.005})
    Shimmer_local: float = Field(..., ge=0.0, le=0.2, description="Local shimmer in voice signal", json_schema_extra={"example": 0.02})
    name: str | None = Field(default=None, description="Patient name")


class ParkinsonsPredictionResponse(BaseModel):
    success: bool = True
    disease: str
    prediction: int
    probability: float
    confidence: float
    confidence_label: str | None = None
    explanations: list[dict] | None = None
    recommendations: list[dict] | None = None
    structured_recommendation: dict | None = None
    final_report: dict | None = None
    evidence: list[dict] | None = None
    citations: list[dict] | None = None
    similarity_scores: list[float] | None = None
    evidence_summary: str | None = None
    class_probabilities: dict[str, float]
    drug_safety: dict | None = None


REQUEST_EXAMPLE = {
    "age": 60,
    "motor_UPDRS": 20.0,
    "total_UPDRS": 35.0,
    "Jitter_local": 0.005,
    "Shimmer_local": 0.02,
    "name": "Test Parkinson's Patient",
}
