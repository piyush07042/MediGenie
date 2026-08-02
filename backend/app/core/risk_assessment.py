"""
Risk assessment utilities.
"""

from __future__ import annotations

import pickle
from dataclasses import dataclass
from pathlib import Path
from typing import Any

MODEL_PATHS = [
    Path(__file__).resolve().parents[2] / "app" / "ml" / "models" / "disease_risk_model.pkl",
    Path(__file__).resolve().parents[1] / "ml" / "models" / "disease_risk_model.pkl",
]


def _load_model_artifact(path: str | Path | None = None) -> dict[str, Any] | None:
    """Load the persisted risk model artifact if it exists."""
    candidate_paths = [Path(path)] if path is not None else MODEL_PATHS

    for candidate in candidate_paths:
        if not candidate.exists():
            continue
        with candidate.open("rb") as handle:
            return pickle.load(handle)

    return None


def _build_feature_vector(patient_metrics: dict[str, Any]) -> list[float]:
    """Normalize the patient metrics into the model feature order."""
    return [
        float(patient_metrics.get("age", 0) or 0),
        float(patient_metrics.get("glucose", patient_metrics.get("fasting_blood_sugar", 0)) or 0),
        float(patient_metrics.get("bmi", 0) or 0),
        float(patient_metrics.get("systolic_bp", patient_metrics.get("blood_pressure", 0)) or 0),
        float(patient_metrics.get("cholesterol", 0) or 0),
    ]


def predict_disease_risk(patient_metrics: dict[str, Any]) -> dict[str, Any]:
    """Evaluate disease risk using the trained model when available."""
    artifact = _load_model_artifact()
    if artifact is not None:
        model = artifact.get("model")
        if model is not None:
            feature_vector = _build_feature_vector(patient_metrics)
            probabilities = model.predict_proba([feature_vector])[0]
            positive_probability = float(probabilities[-1])
            score = min(max(positive_probability, 0.0), 1.0)
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
                "drivers": [name for name, value in {
                    "age": patient_metrics.get("age", 0),
                    "glucose": patient_metrics.get("glucose", patient_metrics.get("fasting_blood_sugar", 0)),
                    "bmi": patient_metrics.get("bmi", 0),
                    "systolic_bp": patient_metrics.get("systolic_bp", patient_metrics.get("blood_pressure", 0)),
                    "cholesterol": patient_metrics.get("cholesterol", 0),
                }.items() if value is not None and value != 0],
                "explainable_ai_factors": [
                    "age",
                    "glucose",
                    "bmi",
                    "systolic_bp",
                    "cholesterol",
                ],
                "recommendations": [
                    "Review modifiable cardiovascular risk factors.",
                    "Maintain a healthy diet and regular physical activity.",
                    "Monitor blood pressure, cholesterol, and blood glucose regularly.",
                    "Consult a clinician if symptoms are present.",
                ],
                "confidence": round(score, 3),
            }

    return evaluate_disease_risk_heuristic(patient_metrics)


def evaluate_disease_risk_heuristic(patient_metrics: dict[str, Any]) -> dict[str, Any]:
    """Fallback heuristic evaluation used when no trained model is available."""
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


def evaluate_disease_risk(patient_metrics: dict[str, Any]) -> dict[str, Any]:
    """Backward-compatible alias to the model-aware risk predictor."""
    return predict_disease_risk(patient_metrics)


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

        return predict_disease_risk(assessment_input)