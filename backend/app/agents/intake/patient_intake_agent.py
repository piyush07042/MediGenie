"""
Patient Intake Agent

Responsible for:
- validating incoming patient data
- preparing AgentState
- checking required fields
- normalizing input
"""

from __future__ import annotations

from typing import Any

from app.agents.base.base_agent import BaseAgent
from app.agents.base.agent_result import AgentResult
from app.agents.base.agent_state import AgentState


class PatientIntakeAgent(BaseAgent):

    agent_name = "PatientIntakeAgent"

    REQUIRED_FIELDS = [
        "name",
        "age",
        "gender",
    ]

    async def run(
        self,
        state: AgentState,
    ) -> AgentResult:

        patient = state.patient or {}

        missing = []

        for field in self.REQUIRED_FIELDS:

            if field not in patient or patient[field] in (None, ""):
                missing.append(field)

        if missing:

            return AgentResult(
                agent=self.agent_name,
                status="FAILED",
                confidence=0.0,
                result={},
                warnings=[
                    f"Missing required fields: {', '.join(missing)}"
                ],
            )

        patient["gender"] = str(
            patient["gender"]
        ).strip().title()

        patient["name"] = str(
            patient["name"]
        ).strip()

        patient["age"] = int(patient["age"])

        state.patient = patient

        state.metadata["patient_validated"] = True

        return AgentResult(
            agent=self.agent_name,
            status="SUCCESS",
            confidence=1.0,
            result=patient,
            metadata={
                "validated": True,
            },
        )