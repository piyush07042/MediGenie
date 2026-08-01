from __future__ import annotations

import time

from app.agents.base.base_agent import BaseAgent
from app.agents.base.agent_result import AgentResult
from app.agents.base.agent_state import AgentState

from app.core.risk_assessment import RiskAssessmentEngine


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

        if not state.extracted_metrics:

            return AgentResult(
                agent=self.agent_name,
                status="FAILED",
                confidence=0.0,
                result={},
                warnings=[
                    "No extracted metrics available."
                ],
            )

        engine = RiskAssessmentEngine()

        prediction = engine.predict(
            patient=state.patient,
            metrics=state.extracted_metrics,
        )

        state.disease_risk = prediction

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