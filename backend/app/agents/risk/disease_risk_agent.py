from __future__ import annotations

import time
from typing import Any

from app.agents.base.base_agent import BaseAgent
from app.agents.base.agent_result import AgentResult
from app.agents.base.agent_state import AgentState

from app.services.risk.risk_service import get_risk_service
from app.services.heart_disease_service import get_heart_disease_service
from pathlib import Path
from app.core.config import settings


class DiseaseRiskAgent(BaseAgent):
    """
    Disease Risk Agent

    Responsibilities
    ----------------
    - Receives extracted metrics
    - Calls the ML risk engine
    - Stores risk prediction
    """

    agent_name = "DiseaseRiskAgent"

    def _normalize_prediction(self, prediction: dict[str, Any]) -> dict[str, Any]:
        normalized = dict(prediction or {})
        score = float(normalized.get("probability", normalized.get("confidence", normalized.get("risk_score", 0.0))))
        confidence = float(normalized.get("confidence", score))
        normalized.setdefault("probability", round(score, 3))
        normalized.setdefault("confidence", round(confidence, 3))
        normalized.setdefault("class_probabilities", {
            "0": round(max(0.0, 1.0 - score), 3),
            "1": round(min(1.0, score), 3),
        })
        normalized.setdefault("confidence_label", normalized.get("confidence_label") or normalized.get("risk_level") or "Unknown")
        if "explanations" not in normalized:
            drivers = normalized.get("drivers") or normalized.get("top_factors") or []
            if isinstance(drivers, dict):
                drivers = [drivers]
            explanations = []
            for driver in drivers[:4]:
                if isinstance(driver, dict) and driver.get("feature"):
                    explanations.append({
                        "feature": driver.get("feature"),
                        "importance": float(driver.get("importance", 1.0)),
                    })
                elif isinstance(driver, str):
                    explanations.append({
                        "feature": driver,
                        "importance": 1.0,
                    })
            normalized["explanations"] = explanations
        return normalized

    async def run(
        self,
        state: AgentState,
    ) -> AgentResult:

        start = time.perf_counter()

        # Accept either pre-extracted metrics or fall back to patient_context
        metrics = state.extracted_metrics or state.patient_context or state.patient

        if not metrics:
            return AgentResult(
                agent=self.agent_name,
                status="FAILED",
                confidence=0.0,
                result={},
                warnings=[
                    "No extracted metrics or patient context available."
                ],
            )

        # Merge patient and metrics into a single input dict and call
        # the centralized prediction function directly.
        assessment_input: dict = {}

        if state.patient:
            assessment_input.update(state.patient)

        if state.patient_context:
            assessment_input.update(state.patient_context)

        if metrics:
            assessment_input.update(metrics)

        # Prefer specialized Heart Disease service when heart-related features are present.
        # If the model rejects partial/unsupported input, fall back to the general risk engine.
        heart_keys = {"cholesterol", "chol", "systolic_bp", "trestbps", "thalach", "oldpeak"}
        has_heart_features = any(k in assessment_input for k in heart_keys)

        prediction = None

        if has_heart_features:
            model_dir = Path(settings.HEART_DISEASE_MODEL_DIRECTORY)
            heart_service = get_heart_disease_service(model_dir)
            try:
                prediction = heart_service.predict(assessment_input)
            except Exception as exc:
                prediction = None
                assessment_input.setdefault("risk_fallback_reason", str(exc))

        if prediction is None:
            risk_service = get_risk_service()
            prediction = risk_service.predict(patient=None, metrics=assessment_input)

        normalized_prediction = self._normalize_prediction(prediction)
        state.disease_risk = normalized_prediction
        state.metadata["risk_source"] = normalized_prediction.get("risk_source", "model" if "model_used" in normalized_prediction else "heuristic")
        state.metadata["risk_model"] = normalized_prediction.get("model_used")

        elapsed = round(
            time.perf_counter() - start,
            3,
        )

        state.set_agent_output(
            self.agent_name,
            prediction,
            confidence=prediction.get(
                "confidence",
                0.0,
            ),
            execution_time=elapsed,
        )

        return AgentResult(
            agent=self.agent_name,
            status="SUCCESS",
            confidence=prediction.get(
                "confidence",
                0.0,
            ),
            result=prediction,
            metadata={
                "execution_time": elapsed,
            },
        )