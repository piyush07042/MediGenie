"""
Drug Safety Agent

Responsibilities
----------------
1. Analyze patient medications.
2. Detect drug-drug interactions.
3. Detect allergy conflicts.
4. Store results into AgentState.
5. Return standardized AgentResult.
"""

from __future__ import annotations

from app.agents.base.base_agent import BaseAgent
from app.agents.agent_result import AgentResult
from app.agents.agent_state import AgentState

from app.core.drug_safety import analyze_drug_safety


class DrugSafetyAgent(BaseAgent):
    """
    Drug Safety Agent

    Uses the deterministic drug safety engine to detect:
    - Drug interactions
    - Allergy conflicts
    - Prescription warnings
    """

    agent_name = "DrugSafetyAgent"

    async def run(
        self,
        state: AgentState,
    ) -> AgentResult:

        medications = state.medications or []
        allergies = state.allergies or []

        result = analyze_drug_safety(
            medications=medications,
            patient_allergies=allergies,
        )

        assessment = result.get(
            "drug_safety_assessment",
            {},
        )

        warnings = []

        evidence = []

        # Interaction warnings
        for interaction in assessment.get(
            "interaction_warnings",
            [],
        ):

            warnings.append(interaction["warning"])

            evidence.append(
                f"{interaction['severity']} Interaction: "
                f"{', '.join(interaction['drugs_involved'])}"
            )

        # Allergy conflicts
        for allergy in assessment.get(
            "allergy_conflicts",
            [],
        ):

            warnings.append(allergy["reasoning"])

            evidence.append(
                f"Allergy Conflict: {allergy['medication']}"
            )

        confidence = 1.0

        state.drug_analysis = assessment

        state.set_agent_output(
            self.agent_name,
            assessment,
            confidence=confidence,
        )

        return AgentResult(
            agent=self.agent_name,
            status="SUCCESS",
            confidence=confidence,
            result=assessment,
            evidence=evidence,
            warnings=warnings,
            metadata={
                "medications_checked": len(medications),
                "allergies_checked": len(allergies),
                "status": assessment.get("status"),
            },
        )

    def validate(
        self,
        state: AgentState,
    ) -> None:
        """
        Validation hook.
        """
        return