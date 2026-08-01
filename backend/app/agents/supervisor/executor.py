"""
Workflow Executor
=================

Responsible for executing MediGenie agents sequentially.

Responsibilities
----------------
- Execute agents
- Share AgentState
- Collect AgentResult
- Record execution metrics
- Stop on fatal failures
"""

from __future__ import annotations

import logging

from app.agents.agent_result import AgentResult
from app.agents.agent_state import AgentState
from app.agents.base_agent import BaseAgent
from app.agents.supervisor.metrics import WorkflowMetrics

logger = logging.getLogger(__name__)


class WorkflowExecutor:
    """
    Executes the multi-agent workflow.
    """

    def __init__(
        self,
        stop_on_failure: bool = True,
    ):
        self.stop_on_failure = stop_on_failure

    async def execute(
        self,
        agents: list[BaseAgent],
        state: AgentState,
    ) -> tuple[AgentState, list[AgentResult], WorkflowMetrics]:
        """
        Execute all agents sequentially.

        Returns
        -------
        (
            updated_state,
            agent_results,
            workflow_metrics,
        )
        """

        metrics = WorkflowMetrics()
        results: list[AgentResult] = []

        logger.info("Starting workflow execution")

        for agent in agents:

            logger.info("Executing %s", agent.agent_name)

            result = await agent.execute(state)

            results.append(result)

            metrics.record(result)

            # Record execution trace
            state.add_trace(
                f"{agent.agent_name}: {result.status}"
            )

            # Collect warnings
            for warning in result.warnings:
                state.add_warning(
                    f"{agent.agent_name}: {warning}"
                )

            # Collect errors
            if result.error:
                state.add_error(
                    f"{agent.agent_name}: {result.error}"
                )

            # Stop workflow if configured
            if (
                self.stop_on_failure
                and not result.success
            ):
                logger.error(
                    "Workflow stopped because %s failed.",
                    agent.agent_name,
                )
                break

        metrics.finish()

        logger.info(
            "Workflow completed in %.3fs",
            metrics.total_execution_time,
        )

        return (
            state,
            results,
            metrics,
        )