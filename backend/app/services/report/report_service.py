"""
Report generation service: centralize final report composition.
"""
from __future__ import annotations

import copy
from datetime import datetime
from typing import Any

from app.agents.base.agent_state import AgentState


def build_final_report(state: AgentState) -> dict[str, Any]:
    metadata = copy.deepcopy(state.metadata)
    metadata.pop("last_agent_output", None)
    metadata.pop("agent_outputs", None)
    metadata.pop("last_agent_confidence", None)
    metadata.pop("last_agent_execution_time", None)

    recommendation_output = state.recommendations[0] if state.recommendations and isinstance(state.recommendations[0], dict) else {}

    report = {
        "generated_at": datetime.utcnow().isoformat(),
        "patient": state.patient,
        "patient_summary": _build_patient_summary(
            state.patient,
            state.patient_history,
            state.symptoms,
            state.medications,
            state.allergies,
        ),
        "patient_history": state.patient_history,
        "symptoms": state.symptoms,
        "medications": state.medications,
        "allergies": state.allergies,
        "ocr_findings": _build_ocr_findings(state),
        "prediction": _build_prediction(state.disease_risk),
        "probability": _safe_float(state.disease_risk.get("probability") or state.disease_risk.get("risk_score") or state.disease_risk.get("confidence")),
        "confidence": _safe_float(state.disease_risk.get("confidence") or state.disease_risk.get("probability") or state.disease_risk.get("risk_score")),
        "explainability": _build_explainability(state.disease_risk),
        "retrieved_evidence": _build_retrieved_evidence(state.knowledge_results),
        "drug_safety": state.drug_analysis,
        "recommendations": state.recommendations,
        "follow_up": _build_follow_up(recommendation_output),
        "clinical_summary": _build_clinical_summary(state),
        "warnings": state.warnings,
        "errors": state.errors,
        "execution_trace": state.execution_trace,
        "metadata": metadata,
    }

    report["structured_recommendation"] = recommendation_output
    report["recommendation_summary"] = recommendation_output.get("recommendation_summary") if isinstance(recommendation_output, dict) else None
    report["drug_safety_summary"] = recommendation_output.get("drug_safety_summary") if isinstance(recommendation_output, dict) else {}
    report["medical_evidence"] = recommendation_output.get("medical_evidence") if isinstance(recommendation_output, dict) else []
    report["supporting_evidence"] = recommendation_output.get("supporting_evidence") if isinstance(recommendation_output, dict) else []
    report["patient_specific_recommendations"] = recommendation_output.get("patient_specific_recommendations") if isinstance(recommendation_output, dict) else []
    report["confidence_label"] = state.disease_risk.get("confidence_label") or state.disease_risk.get("risk_level")
    report["recommendation_priority"] = recommendation_output.get("recommendation_priority") if isinstance(recommendation_output, dict) else None

    return report


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _build_patient_summary(
    patient: dict[str, Any],
    patient_history: dict[str, Any],
    symptoms: list[str],
    medications: list[str],
    allergies: list[str],
) -> dict[str, Any]:
    name = patient.get("name") or f"{patient.get('first_name', '')} {patient.get('last_name', '')}".strip() or "Patient"
    age = patient.get("age")
    gender = patient.get("gender")
    summary_text = [f"{name}"]
    if age is not None:
        summary_text.append(f"Age {age}")
    if gender:
        summary_text.append(f"Gender {gender}")

    if symptoms:
        summary_text.append("presenting symptoms include " + ", ".join(symptoms))
    if medications:
        summary_text.append("current medications include " + ", ".join(medications))
    if allergies:
        summary_text.append("documented allergies include " + ", ".join(allergies))

    return {
        "name": name,
        "age": age,
        "gender": gender,
        "summary_text": ". ".join(summary_text) + "." if summary_text else "Patient information not available.",
        "history": patient_history,
        "symptoms": symptoms,
        "medications": medications,
        "allergies": allergies,
    }


def _build_ocr_findings(state: AgentState) -> dict[str, Any]:
    return {
        "raw_report_text": state.report_text or "",
        "ocr_result": state.ocr_result,
        "extracted_metrics": state.extracted_metrics,
    }


def _build_prediction(disease_risk: dict[str, Any]) -> dict[str, Any]:
    return {
        "risk_category": disease_risk.get("risk_category") or disease_risk.get("risk_level") or "Unknown",
        "risk_score": _safe_float(disease_risk.get("risk_score") or disease_risk.get("estimated_risk_score_percent") or disease_risk.get("probability") or disease_risk.get("confidence")),
        "probability": _safe_float(disease_risk.get("probability") or disease_risk.get("risk_score") or disease_risk.get("confidence")),
        "confidence": _safe_float(disease_risk.get("confidence") or disease_risk.get("probability") or disease_risk.get("risk_score")),
        "confidence_label": disease_risk.get("confidence_label") or disease_risk.get("risk_level") or None,
        "prediction": disease_risk.get("prediction") if disease_risk.get("prediction") is not None else int(_safe_float(disease_risk.get("probability", disease_risk.get("risk_score", 0.0))) >= 0.5),
        "class_probabilities": disease_risk.get("class_probabilities") or {
            "0": round(max(0.0, 1.0 - _safe_float(disease_risk.get("probability", disease_risk.get("risk_score", 0.0)))), 3),
            "1": round(min(1.0, _safe_float(disease_risk.get("probability", disease_risk.get("risk_score", 0.0)))), 3),
        },
    }


def _build_explainability(disease_risk: dict[str, Any]) -> dict[str, Any]:
    explanations = disease_risk.get("explanations") or disease_risk.get("drivers") or disease_risk.get("top_factors") or []
    if isinstance(explanations, dict):
        explanations = [explanations]
    return {
        "top_factors": disease_risk.get("top_factors") or disease_risk.get("drivers") or [],
        "explanations": explanations,
        "notes": disease_risk.get("explainability") or disease_risk.get("explanations") or [],
    }


def _build_retrieved_evidence(knowledge_results: list[dict[str, Any]] | None) -> dict[str, Any]:
    knowledge_results = knowledge_results or []
    evidence_summary = "".join(
        f"{item.get('source', 'Source')}: {item.get('text', '')}. "
        for item in knowledge_results
        if item
    )
    return {
        "knowledge_results": knowledge_results,
        "evidence_summary": evidence_summary.strip(),
    }


def _build_follow_up(recommendation_output: dict[str, Any]) -> list[Any]:
    follow_up = []
    if isinstance(recommendation_output, dict):
        follow_up = recommendation_output.get("follow_up_plan") or recommendation_output.get("follow_up") or []
    return follow_up if isinstance(follow_up, list) else [follow_up]


def _build_clinical_summary(state: AgentState) -> str:
    patient = state.patient or {}
    patient_name = patient.get("name") or patient.get("first_name") or "Patient"
    age = patient.get("age")
    gender = patient.get("gender")
    lines: list[str] = [f"Clinical Summary for {patient_name}."]

    if age is not None:
        lines.append(f"Age: {age}.")
    if gender:
        lines.append(f"Gender: {gender}.")

    prediction = state.disease_risk or {}
    if prediction:
        category = prediction.get("risk_category") or prediction.get("risk_level") or "Unknown"
        probability = prediction.get("probability") or prediction.get("risk_score") or prediction.get("confidence")
        lines.append(f"Predicted risk category: {category}.")
        if probability is not None:
            lines.append(f"Estimated probability: {round(_safe_float(probability) * 100, 1)}%.")

        if prediction.get("explanations"):
            lines.append("Key explainability factors:")
            for entry in prediction.get("explanations"):
                if isinstance(entry, dict):
                    lines.append(f"- {entry.get('feature', entry.get('label', 'Factor'))}: {entry.get('value', entry.get('description', entry))}")
                else:
                    lines.append(f"- {entry}")

    if state.ocr_result or state.report_text:
        lines.append("OCR findings and extracted report information were reviewed.")

    if state.knowledge_results:
        lines.append("Retrieved evidence from clinical knowledge sources was incorporated into the recommendation plan.")

    if state.drug_analysis:
        status = state.drug_analysis.get("status", "PASS")
        lines.append(f"Drug safety review status: {status}.")

    if state.recommendations:
        lines.append("Recommended next steps:")
        for rec in state.recommendations:
            if isinstance(rec, dict):
                lines.append(f"- {rec.get('title', 'Recommendation')}: {rec.get('recommendation', rec.get('summary', str(rec)))}")
            else:
                lines.append(f"- {rec}")

    return "\n".join(lines)
