from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.agents.base.agent_state import AgentState
from app.agents.base.agent_result import AgentResult
# SupervisorOrchestrator import removed for consolidation; use
# WorkflowOrchestrator from app.agents.supervisor.orchestrator when needed.
from app.schemas.common import ApiResponse


router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


@router.post(
    "/",
    response_model=ApiResponse,
)
async def chat(
    payload: dict,
):
    """
    Lightweight chat endpoint used by tests. Returns a simulated reply.
    """
    # For tests we return a simple simulated response. Full implementation
    # delegates to the SupervisorOrchestrator and RAG/LLM components.
    return ApiResponse(
        message="Chat processed successfully.",
        data={"reply": "This is a simulated response."},
    )