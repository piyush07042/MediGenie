"""
Report generation service: centralize final report composition.
"""
from __future__ import annotations

import copy
from typing import Any
from datetime import datetime

from app.agents.base.agent_state import AgentState


def build_final_report(state: AgentState) -> dict[str, Any]:
    metadata = copy.deepcopy(state.metadata)
    metadata.pop("last_agent_output", None)
    metadata.pop("agent_outputs", None)
    metadata.pop("last_agent_confidence", None)
    metadata.pop("last_agent_execution_time", None)

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
        "drug_safety": state.drug_analysis,
        "recommendations": state.recommendations,
        "warnings": state.warnings,
        "errors": state.errors,
        "execution_trace": state.execution_trace,
        "metadata": metadata,
    }

    report["clinical_summary"] = _build_clinical_summary(report)

    return report


def _build_clinical_summary(report: dict[str, Any]) -> str:
    patient = report.get("patient", {}) or {}
    if not patient:
        patient = report.get("patient_context", {}) or {}
    risk = report.get("disease_risk", {}) or {}
    drug_analysis = report.get("drug_analysis", {}) or {}
    knowledge = report.get("knowledge_results", []) or []
    recommendations = report.get("recommendations", []) or []

    lines: list[str] = []

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
        score = (
            risk.get("risk_score")
            or risk.get("estimated_risk_score_percent")
            or risk.get("confidence")
            or "N/A"
        )
        lines.append(
            f"Disease risk assessment indicates {category} risk (score: {score})."
        )
        drivers = risk.get("top_factors") or risk.get("drivers") or []
        if isinstance(drivers, dict):
            drivers = [drivers]
        if drivers:
            formatted = []
            for d in drivers:
                if isinstance(d, dict):
                    formatted.append(f"{d.get('feature', 'Factor')}: {d.get('value', '')}")
                else:
                    formatted.append(str(d))
            if formatted:
                lines.append("Primary contributing factors: " + ", ".join(formatted))

    if drug_analysis:
        status = drug_analysis.get("status", "PASS")
        overall_risk = drug_analysis.get("overall_risk", "Low")
        lines.append(f"Medication safety check status: {status} (overall risk: {overall_risk}).")
        if status == "FLAGGED":
            issues = []
            for interaction in drug_analysis.get("interactions", []):
                issues.append(interaction.get("explanation", "Potential interaction"))
            for allergy in drug_analysis.get("allergies", []):
                issues.append(allergy.get("explanation", "Allergy conflict."))
            for contraindication in drug_analysis.get("contraindications", []):
                issues.append(contraindication.get("explanation", "Contraindication."))
            if issues:
                lines.append("Safety issues identified: " + " ".join(issues))
        if drug_analysis.get("pregnancy", {}).get("category") and drug_analysis.get("pregnancy", {}).get("category") != "Not Applicable":
            lines.append(
                f"Pregnancy safety: {drug_analysis['pregnancy'].get('category')} - {drug_analysis['pregnancy'].get('explanation')}"
            )
        if drug_analysis.get("renal_adjustment", {}).get("recommendations"):
            lines.append("Renal dosing considerations present; review recommendations and monitor kidney function.")
        if drug_analysis.get("liver_adjustment", {}).get("recommendations"):
            lines.append("Liver dosing considerations present; review recommendations and monitor hepatic function.")

    if knowledge:
        lines.append("Relevant clinical evidence was retrieved to support patient management.")
        lines.append("Retrieved evidence snippets may inform treatment planning and monitoring.")

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
