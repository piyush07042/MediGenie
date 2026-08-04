from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status

from app.agents.base.agent_state import AgentState
from app.core.deps import get_supervisor
from app.schemas.common import ApiResponse


router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


def _as_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [str(item) for item in value if item is not None]
    return [str(value)]


def _build_chat_reply(final_state: AgentState) -> str:
    if final_state.final_report:
        clinical_summary = final_state.final_report.get("clinical_summary")
        if clinical_summary:
            return str(clinical_summary)

    if final_state.recommendations:
        first_rec = final_state.recommendations[0]
        if isinstance(first_rec, dict):
            title = first_rec.get("title") or first_rec.get("priority") or "Recommendation"
            recommendation = first_rec.get("recommendation") or first_rec.get("summary") or "Please review the recommended next steps."
            return f"{title}: {recommendation}"
        return str(first_rec)

    if final_state.disease_risk:
        risk_category = final_state.disease_risk.get("risk_category") or final_state.disease_risk.get("risk_level") or "Unknown"
        probability = final_state.disease_risk.get("probability") or final_state.disease_risk.get("risk_score") or final_state.disease_risk.get("confidence")
        if probability is not None:
            return f"Risk assessment indicates {risk_category} with estimated probability {probability}."
        return f"Risk assessment indicates {risk_category}."

    return "I reviewed the context and prepared a clinical workflow summary for you."


@router.post(
    "/",
    response_model=ApiResponse,
    status_code=status.HTTP_200_OK,
)
async def chat(
    payload: dict,
    supervisor=Depends(get_supervisor),
):
    """
    Execute the clinical workflow for chat-style requests and return a
    structured reply derived from the workflow state.
    """
    try:
        payload = payload or {}
        patient_context = payload.get("patient_context") or payload.get("patient") or {}
        message = payload.get("message") or payload.get("query") or payload.get("text") or ""
        raw_report_text = payload.get("raw_report_text") or payload.get("report_text") or payload.get("report") or ""

        state = AgentState()
        if isinstance(patient_context, dict):
            state.patient = dict(patient_context)
            state.patient.setdefault("name", state.patient.get("name", ""))
            state.patient.setdefault("age", state.patient.get("age", 0))
            state.patient.setdefault("gender", state.patient.get("gender", ""))

        if message:
            state.symptoms = _as_list(payload.get("symptoms") or message)

        medications = payload.get("medications") or state.patient.get("current_medications") or []
        allergies = payload.get("allergies") or state.patient.get("allergies") or []
        state.medications = _as_list(medications)
        state.allergies = _as_list(allergies)

        if raw_report_text:
            state.raw_report_text = raw_report_text
            state.report_text = raw_report_text

        final_state, results, metrics = await supervisor.run(state)

        return ApiResponse(
            message="Chat processed successfully.",
            data={
                "reply": _build_chat_reply(final_state),
                "workflow_state": final_state,
                "agent_results": results,
                "metrics": metrics,
                "clinical_summary": (final_state.final_report or {}).get("clinical_summary") if final_state.final_report else None,
            },
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat workflow failed: {exc}",
        )