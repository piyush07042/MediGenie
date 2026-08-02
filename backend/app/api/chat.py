from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.agents.base.agent_state import AgentState
from app.agents.base.agent_result import AgentResult
from app.agents.supervisor.orchestrator import SupervisorOrchestrator

router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)