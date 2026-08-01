"""
Recommendation Agent

Combines outputs from:

- Disease Risk Agent
- Medical Knowledge Agent
- Drug Safety Agent

Generates evidence-based clinical considerations.
"""

from __future__ import annotations

from app.agents.base.base_agent import BaseAgent
from app.agents.agent_result import AgentResult
from app.agents.agent_state import AgentState


class RecommendationAgent(BaseAgent):

    agent_name = "RecommendationAgent"

    async def run(
        self,
        state: AgentState,
    ) -> AgentResult:

        recommendations = []

        evidence = []

        warnings = []

        # ----------------------------------------------------
        # Disease Risk
        # ----------------------------------------------------

        risk = state.disease_risk

        if risk:

            category = risk.get("risk_category", "")

            score = risk.get("risk_score", 0)

            if category == "High":

                recommendations.append({
                    "priority": "High",
                    "title": "Urgent Clinical Review",
                    "recommendation":
                        "Patient demonstrates high disease risk. "
                        "Further clinical evaluation is recommended."
                })

            elif category == "Moderate":

                recommendations.append({
                    "priority": "Medium",
                    "title": "Follow-up Assessment",
                    "recommendation":
                        "Schedule follow-up investigations and monitor."
                })

            evidence.append(
                f"Disease Risk Score: {score}"
            )

        # ----------------------------------------------------
        # Drug Safety
        # ----------------------------------------------------

        drug = state.drug_analysis

        if drug:

            if drug.get("status") == "FLAGGED":

                recommendations.append({
                    "priority": "Critical",
                    "title": "Medication Safety Alert",
                    "recommendation":
                        "Review medication interactions and allergy conflicts "
                        "before prescribing."
                })

                warnings.append(
                    "Medication safety issues detected."
                )

        # ----------------------------------------------------
        # Medical Knowledge
        # ----------------------------------------------------

        knowledge = state.knowledge_results

        if knowledge:

            recommendations.append({
                "priority": "Information",
                "title": "Relevant Clinical Guidelines",
                "recommendation":
                    "Consult retrieved evidence before final decision."
            })

            evidence.extend([
                item.get("document", "")[:150]
                for item in knowledge
            ])

        # ----------------------------------------------------
        # Default
        # ----------------------------------------------------

        if not recommendations:

            recommendations.append({

                "priority": "Low",

                "title": "No Significant Findings",

                "recommendation":
                    "No evidence requiring immediate intervention."
            })

        state.recommendations = recommendations

        state.set_agent_output(

            self.agent_name,

            recommendations,

            confidence=0.95,
        )

        return AgentResult(

            agent=self.agent_name,

            status="SUCCESS",

            confidence=0.95,

            result=recommendations,

            evidence=evidence,

            warnings=warnings,

            metadata={

                "recommendation_count": len(recommendations)

            },
        )