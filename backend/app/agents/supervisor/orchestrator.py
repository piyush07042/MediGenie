"""
Workflow Orchestrator
=====================
"""

from __future__ import annotations

from app.agents.base.agent_result import AgentResult
from app.agents.base.agent_state import AgentState
from app.agents.registry import get_workflow_agents
from app.agents.supervisor.executor import WorkflowExecutor
from app.agents.supervisor.metrics import WorkflowMetrics


class WorkflowOrchestrator:
    """
    Main orchestrator responsible for executing the
    complete MediGenie multi-agent workflow.
    """

    def __init__(self) -> None:
        self.executor = WorkflowExecutor()
        self.agents = get_workflow_agents()

    async def execute(
        self,
        state: AgentState,
    ) -> tuple[
        AgentState,
        list[AgentResult],
        WorkflowMetrics,
    ]:
        """
        Execute the complete workflow.
        """
        return await self.executor.execute(
            self.agents,
            state,
        )

    def get_pipeline(self) -> list[str]:
        """
        Return the ordered workflow pipeline.
        """
        return [
            agent.agent_name
            for agent in self.agents
        ]


# ----------------------------------------------------------------------
# Backward compatibility
# ----------------------------------------------------------------------

SupervisorOrchestrator = WorkflowOrchestrator