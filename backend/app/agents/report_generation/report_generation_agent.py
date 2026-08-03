"""
Report Generation Agent

Collects outputs from every previous agent
and prepares the final structured report.

This agent DOES NOT generate new medical claims.
It only summarizes validated outputs.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from app.agents.base.base_agent import BaseAgent
from app.agents.base.agent_result import AgentResult
from app.agents.base.agent_state import AgentState

from app.services.report.report_service import build_final_report


class ReportGenerationAgent(BaseAgent):

    agent_name = "ReportGenerationAgent"

    async def run(
        self,
        state: AgentState,
    ) -> AgentResult:

        report = build_final_report(state)

        state.final_report = report

        state.set_agent_output(self.agent_name, report, confidence=1.0)

        return AgentResult(agent=self.agent_name, status="SUCCESS", confidence=1.0, result=report, metadata={"sections": len(report)})

    def _build_clinical_summary(self, report: dict[str, Any]) -> str:
        """Build a human-readable clinical summary for the final report."""

        patient = report.get("patient", {}) or {}
        if not patient:
            patient = report.get("patient_context", {}) or {}
        risk = report.get("disease_risk", {}) or {}
        drug_analysis = report.get("drug_analysis", {}) or {}
        knowledge = report.get("knowledge_results", []) or []
        recommendations = report.get("recommendations", []) or []

        lines = []

        name = (
            patient.get("name")
            or patient.get("first_name")
            or patient.get("patient_name")
            or "Patient"
        )
        age = patient.get("age")
        gender = patient.get("gender")

        lines.append(f"Clinical Summary for {name}.")
        if age is not None:
            lines.append(f"Age: {age}.")
        if gender:
            lines.append(f"Gender: {gender}.")

        if risk:
            category = risk.get("risk_category") or risk.get("risk_level") or "Unknown"
            score = risk.get("risk_score") or risk.get("estimated_risk_score_percent") or risk.get("confidence") or "N/A"
            lines.append(
                f"Disease risk assessment indicates {category} risk "
                f"(score: {score})."
            )
            drivers = risk.get("top_factors") or risk.get("drivers") or []
            if isinstance(drivers, dict):
                drivers = [drivers]
            if drivers:
                formatted = []
                for d in drivers:
                    if isinstance(d, dict):
                        formatted.append(
                            f"{d.get('feature', 'Factor')}: {d.get('value', '')}"
                        )
                    else:
                        formatted.append(str(d))
                if formatted:
                    lines.append(
                        "Primary contributing factors: " + ", ".join(formatted)
                    )

        if drug_analysis:
            status = drug_analysis.get("status", "PASS")
            lines.append(f"Medication safety check status: {status}.")
            if status == "FLAGGED":
                issues = []
                for interaction in drug_analysis.get("interactions", []):
                    issues.append(interaction.get("explanation", "Potential interaction"))
                for allergy in drug_analysis.get("allergies", []):
                    issues.append(allergy.get("explanation", "Allergy conflict."))
                for contraindication in drug_analysis.get("contraindications", []):
                    issues.append(contraindication.get("explanation", "Contraindication."))
                if issues:
                    lines.append(
                        "Safety issues identified: " + " ".join(issues)
                    )

        if knowledge:
            lines.append(
                "Relevant clinical evidence was retrieved to support patient management."
            )
            lines.append(
                "Retrieved evidence snippets may inform treatment planning and monitoring."
            )

        if recommendations:
            lines.append("Recommended next steps:")
            for rec in recommendations:
                title = rec.get("title") if isinstance(rec, dict) else None
                rec_text = rec.get("recommendation") if isinstance(rec, dict) else str(rec)
                if title:
                    lines.append(f"- {title}: {rec_text}")
                else:
                    lines.append(f"- {rec_text}")

        return "\n".join(lines)
