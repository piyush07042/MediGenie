"""
Workflow Orchestrator
=====================
"""

from __future__ import annotations

from app.agents.agent_result import AgentResult
from app.agents.agent_state import AgentState

from app.agents.registry import get_workflow_agents

from app.agents.supervisor.executor import WorkflowExecutor
from app.agents.supervisor.metrics import WorkflowMetrics


class WorkflowOrchestrator:

    def __init__(self):

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

        return await self.executor.execute(
            self.agents,
            state,
        )

    def get_pipeline(self) -> list[str]:

        return [
            agent.agent_name
            for agent in self.agents
        ]