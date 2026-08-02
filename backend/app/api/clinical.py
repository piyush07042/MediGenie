"""
Clinical Analysis API
"""

from __future__ import annotations

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from app.agents.base.agent_state import AgentState
from app.core.deps import get_supervisor
from app.schemas.cdss import (
    AnalysisRequestSchema,
)
from app.schemas.common import ApiResponse

router = APIRouter(
    prefix="/clinical",
    tags=["Clinical Decision Support"],
)


@router.post(
    "/analyze",
    response_model=ApiResponse,
    status_code=status.HTTP_200_OK,
)
async def analyze_clinical_case(
    request: AnalysisRequestSchema,
    supervisor=Depends(get_supervisor),
):
    """
    Execute the complete MediGenie Supervisor workflow.
    """

    try:

        state = AgentState()

        state.patient_context = (
            request.patient_context.model_dump()
        )

        state.raw_report_text = (
            request.raw_report_text
        )

        final_state, results, metrics = (
            await supervisor.run(state)
        )

        return ApiResponse(
            message="Clinical analysis completed successfully.",
            data={
                "workflow_state": final_state,
                "agent_results": results,
                "metrics": metrics,
            },
        )

    except Exception as exc:

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Clinical workflow failed: {exc}",
        )