from __future__ import annotations

import time

from app.agents.base.base_agent import BaseAgent
from app.agents.base.agent_result import AgentResult
from app.agents.base.agent_state import AgentState

from app.core.risk_assessment import predict_disease_risk


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

        prediction = predict_disease_risk(assessment_input)

        state.disease_risk = prediction
        state.metadata["risk_source"] = prediction.get("risk_source", "model" if "model_used" in prediction else "heuristic")
        state.metadata["risk_model"] = prediction.get("model_used")

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