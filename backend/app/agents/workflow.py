"""
Workflow Entry Point
====================
"""

from __future__ import annotations

from app.agents.base.agent_state import AgentState

from app.agents.supervisor.orchestrator import WorkflowOrchestrator as _InnerWorkflowOrchestrator


class WorkflowOrchestratorWrapper:
    """Backward-compatible wrapper exposing the orchestrator expected by tests.

    This wrapper mirrors the older `WorkflowOrchestrator()` API with
    `execute()` and `get_pipeline()` methods.
    """

    def __init__(self) -> None:
        self._inner = _InnerWorkflowOrchestrator()

    async def execute(self, state: AgentState):
        return await self._inner.execute(state)

    def get_pipeline(self):
        return self._inner.get_pipeline()

    @property
    def agents(self):
        return getattr(self._inner, 'agents', [])


# Expose the compatible name the tests import
WorkflowOrchestrator = WorkflowOrchestratorWrapper