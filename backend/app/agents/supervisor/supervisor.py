"""
Supervisor Agent

Coordinates the execution of all registered AI agents.

Responsibilities
----------------
- Executes agents in workflow order
- Maintains shared AgentState
- Aggregates AgentResults
- Records execution metrics
- Handles failures
"""

from __future__ import annotations

import logging
import time

from app.agents.base import (
    AgentRegistry,
    AgentResult,
    AgentState,
    BaseAgent,
)

logger = logging.getLogger(__name__)


class SupervisorAgent(BaseAgent):
    """
    Main orchestrator of MediGenie.
    """

    agent_name = "SupervisorAgent"

    def __init__(self, registry: AgentRegistry):
        super().__init__()

        self.registry = registry

        # Default workflow
        self.workflow = [
            "PatientIntakeAgent",
            "MedicalReportAnalysisAgent",
            "DiseaseRiskAgent",
            "MedicalKnowledgeAgent",
            "DrugSafetyAgent",
            "RecommendationAgent",
            "ReportGenerationAgent",
        ]

    async def run(self, state: AgentState) -> AgentResult:
        """
        Execute all registered agents.
        """

        start = time.perf_counter()

        results: dict[str, dict] = {}
        completed = []
        failed = []

        total_confidence = 0.0
        confidence_count = 0

        all_warnings = []
        all_evidence = []

        logger.info("Supervisor started.")

        for agent_name in self.workflow:

            if not self.registry.exists(agent_name):
                logger.warning(
                    "Agent '%s' not registered.",
                    agent_name,
                )
                continue

            agent = self.registry.get(agent_name)

            logger.info("Executing %s", agent_name)

            result = await agent.execute(state)

            results[agent_name] = result.to_dict()

            if result.success:
                completed.append(agent_name)
            else:
                failed.append(agent_name)

            if result.confidence > 0:
                confidence_count += 1
                total_confidence += result.confidence

            all_warnings.extend(result.warnings)
            all_evidence.extend(result.evidence)

        overall_confidence = (
            round(total_confidence / confidence_count, 3)
            if confidence_count > 0
            else 0.0
        )

        elapsed = round(
            time.perf_counter() - start,
            3,
        )

        summary = {
            "completed_agents": completed,
            "failed_agents": failed,
            "overall_confidence": overall_confidence,
            "execution_time": elapsed,
            "warnings": all_warnings,
            "evidence": all_evidence,
            "results": results,
        }

        state.metadata["supervisor"] = summary

        logger.info("Supervisor finished.")

        return AgentResult(
            agent=self.agent_name,
            status="SUCCESS"
            if not failed
            else "PARTIAL_SUCCESS",
            confidence=overall_confidence,
            result=summary,
            evidence=all_evidence,
            warnings=all_warnings,
            metadata={
                "completed": len(completed),
                "failed": len(failed),
                "execution_time": elapsed,
            },
        )