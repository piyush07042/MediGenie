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
from app.agents.base.agent_result import AgentResult
from app.agents.base.agent_state import AgentState


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

            category = str(risk.get("risk_category", "")).strip().title()

            score = risk.get("risk_score", 0)

            drivers = risk.get("top_factors") or risk.get("drivers") or []
            if isinstance(drivers, dict):
                drivers = [drivers]

            risk_recs = risk.get("recommendations", [])
            if isinstance(risk_recs, str):
                risk_recs = [risk_recs]

            if category == "High":
                recommendations.append({
                    "priority": "High",
                    "title": "Elevated Risk Profile",
                    "recommendation": (
                        "Patient is at high risk. Review the top risk drivers "
                        "and accelerate diagnostic evaluation and treatment planning."
                    ),
                })
            elif risk_recs:
                for rec in risk_recs:
                    recommendations.append({
                        "priority": "High" if category == "High" else "Medium",
                        "title": "Risk-Based Recommendation",
                        "recommendation": str(rec),
                    })
            elif category == "Moderate":
                recommendations.append({
                    "priority": "Medium",
                    "title": "Moderate Risk Management",
                    "recommendation": (
                        "Patient is at moderate risk. Continue monitoring trends "
                        "and implement guideline-supported preventive measures."
                    ),
                })
            else:
                recommendations.append({
                    "priority": "Low",
                    "title": "Routine Monitoring",
                    "recommendation": (
                        "Patient has low risk. Maintain regular follow-up and lifestyle optimization."
                    ),
                })

            evidence.append(
                f"Disease Risk Score: {score}"
            )

            if drivers:
                formatted_drivers = []
                for driver in drivers:
                    if isinstance(driver, dict):
                        formatted_drivers.append(
                            f"{driver.get('feature')}={driver.get('value')}"
                        )
                    else:
                        formatted_drivers.append(str(driver))
                evidence.append(
                    "Top factors: " + ", ".join(formatted_drivers)
                )

            if risk_recs:
                evidence.extend([f"Risk recommendation: {str(rec)}" for rec in risk_recs])

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

            for interaction in drug.get("interaction_warnings", []):
                evidence.append(
                    f"Interaction: {interaction.get('severity', 'Unknown')} - "
                    f"{interaction.get('warning', 'No description')}"
                )

            for allergy in drug.get("allergy_conflicts", []):
                evidence.append(
                    f"Allergy conflict: {allergy.get('medication', 'Unknown')} "
                    f"({allergy.get('allergen_match', 'Unknown')})"
                )

        # ----------------------------------------------------
        # Medical Knowledge
        # ----------------------------------------------------

        knowledge = state.knowledge_results

        if knowledge:

            recommendation_text = (
                "Consult the retrieved clinical guidance and align the care plan "
                "with the most relevant evidence-based recommendations."
            )

            if len(knowledge) > 1:
                recommendation_text = (
                    "Consult the retrieved clinical guidance snippets and align "
                    "the care plan with the most relevant evidence-based recommendations."
                )

            recommendations.append({
                "priority": "Information",
                "title": "Evidence-Based Guidance",
                "recommendation": recommendation_text,
            })

            for item in knowledge:
                document = item.get("document", "")
                metadata = item.get("metadata", {})
                if metadata:
                    evidence.append(
                        f"[{metadata.get('category', 'Guideline')}] "
                        f"{document[:160]}"
                    )
                else:
                    evidence.append(document[:160])

            if len(knowledge) == 1 and document:
                recommendations.append({
                    "priority": "Information",
                    "title": "Specific Guideline Insight",
                    "recommendation": document[:280],
                })

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