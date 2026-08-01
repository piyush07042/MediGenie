"""
Report Generation Agent

Collects outputs from every previous agent
and prepares the final structured report.

This agent DOES NOT generate new medical claims.
It only summarizes validated outputs.
"""

from __future__ import annotations

from datetime import datetime

from app.agents.base.base_agent import BaseAgent
from app.agents.agent_result import AgentResult
from app.agents.agent_state import AgentState


class ReportGenerationAgent(BaseAgent):

    agent_name = "ReportGenerationAgent"

    async def run(
        self,
        state: AgentState,
    ) -> AgentResult:

        report = {

            "generated_at": datetime.utcnow().isoformat(),

            "patient": state.patient,

            "patient_history": state.patient_history,

            "symptoms": state.symptoms,

            "medications": state.medications,

            "allergies": state.allergies,

            "uploaded_reports": state.uploaded_reports,

            "extracted_metrics": state.extracted_metrics,

            "disease_risk": state.disease_risk,

            "knowledge_results": state.knowledge_results,

            "drug_analysis": state.drug_analysis,

            "recommendations": state.recommendations,

            "warnings": state.warnings,

            "errors": state.errors,

            "execution_trace": state.execution_trace,

            "metadata": state.metadata,
        }

        state.final_report = report

        state.set_agent_output(

            self.agent_name,

            report,

            confidence=1.0,
        )

        return AgentResult(

            agent=self.agent_name,

            status="SUCCESS",

            confidence=1.0,

            result=report,

            metadata={
                "sections": len(report),
            },
        )