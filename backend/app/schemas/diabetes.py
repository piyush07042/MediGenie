"""
Diabetes API Schemas
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class DiabetesPredictionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    age: int = Field(..., ge=1, le=120, description="Age in years", example=55)
    bmi: float = Field(..., ge=10, le=80, description="BMI", example=32.5)
    glucose: float = Field(..., ge=50, le=400, description="Glucose level", example=160)
    systolic_bp: float = Field(..., ge=50, le=250, description="Systolic blood pressure", example=140)
    insulin: float = Field(..., ge=0, le=1000, description="Insulin level", example=85)
    name: str | None = Field(default=None, description="Patient name")


class DiabetesPredictionResponse(BaseModel):
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
    "age": 55,
    "bmi": 32.5,
    "glucose": 160,
    "systolic_bp": 140,
    "insulin": 85,
}
