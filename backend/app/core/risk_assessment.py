"""
Risk assessment utilities.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


def evaluate_disease_risk(patient_metrics: dict[str, Any]) -> dict[str, Any]:
    """
    Evaluate disease risk from structured patient metrics.

    Returns:
        Dictionary containing risk score, category,
        contributing factors, and recommendations.
    """

    score = 0.0
    factors: list[str] = []

    # -------------------------------
    # Age
    # -------------------------------
    age = patient_metrics.get("age")
    if isinstance(age, (int, float)) and age >= 60:
        score += 0.20
        factors.append("age")

    # -------------------------------
    # Blood Pressure
    # -------------------------------
    systolic_bp = patient_metrics.get("systolic_bp")
    if isinstance(systolic_bp, (int, float)) and systolic_bp >= 140:
        score += 0.25
        factors.append("blood_pressure")

    # -------------------------------
    # Cholesterol
    # -------------------------------
    cholesterol = patient_metrics.get("cholesterol")
    if isinstance(cholesterol, (int, float)) and cholesterol >= 240:
        score += 0.25
        factors.append("cholesterol")

    # -------------------------------
    # Blood Sugar
    # -------------------------------
    glucose = (
        patient_metrics.get("fasting_blood_sugar")
        or patient_metrics.get("glucose")
    )

    if isinstance(glucose, (int, float)) and glucose >= 126:
        score += 0.15
        factors.append("blood_glucose")

    # -------------------------------
    # BMI
    # -------------------------------
    bmi = patient_metrics.get("bmi")
    if isinstance(bmi, (int, float)) and bmi >= 30:
        score += 0.15
        factors.append("bmi")

    # -------------------------------
    # Final Risk
    # -------------------------------
    score = min(score, 1.0)

    if score >= 0.70:
        risk_level = "high"
    elif score >= 0.40:
        risk_level = "moderate"
    else:
        risk_level = "low"

    return {
        "evaluated_condition": "Metabolic & Cardiovascular Risk Profile",
        "risk_score": round(score, 3),
        "estimated_risk_score_percent": round(score * 100, 1),
        "risk_level": risk_level,
        "risk_category": risk_level,
        "drivers": factors,
        "explainable_ai_factors": factors,
        "recommendations": [
            "Review modifiable cardiovascular risk factors.",
            "Maintain a healthy diet and regular physical activity.",
            "Monitor blood pressure, cholesterol, and blood glucose regularly.",
            "Consult a clinician if symptoms are present.",
        ],
    }


@dataclass
class RiskAssessmentEngine:
    """
    Compatibility wrapper for the DiseaseRiskAgent.
    """

    def predict(
        self,
        patient: dict[str, Any] | None = None,
        metrics: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Predict disease risk from patient information.
        """

        assessment_input: dict[str, Any] = {}

        if patient:
            assessment_input.update(patient)

        if metrics:
            assessment_input.update(metrics)

        return evaluate_disease_risk(assessment_input)