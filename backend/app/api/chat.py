"""
AI Clinical Chat API
"""

from __future__ import annotations

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from pydantic import BaseModel

from app.agents.agent_state import AgentState
from app.agents.supervisor.supervisor import Supervisor
from app.core.deps import get_supervisor
from app.schemas.common import ApiResponse

router = APIRouter(
    prefix="/chat",
    tags=["AI Clinical Chat"],
)


class ChatRequest(BaseModel):
    """
    Clinical chat request.
    """

    message: str

    patient_context: dict | None = None


@router.post(
    "/",
    response_model=ApiResponse,
    status_code=status.HTTP_200_OK,
)
async def clinical_chat(
    request: ChatRequest,
    supervisor: Supervisor = Depends(get_supervisor),
):
    """
    Clinical AI chat endpoint.
    """

    try:

        state = AgentState()

        state.patient_context = (
            request.patient_context or {}
        )

        state.chat_message = request.message

        final_state, results, metrics = await supervisor.run(
            state
        )

        return ApiResponse(
            message="Chat response generated successfully.",
            data={
                "workflow_state": final_state,
                "agent_results": results,
                "workflow_metrics": metrics,
            },
        )

    except Exception as exc:

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat processing failed: {exc}",
        )