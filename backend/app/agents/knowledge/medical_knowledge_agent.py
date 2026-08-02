"""
Medical Knowledge Agent

Responsibilities
----------------
1. Build a medical search query from the patient context.
2. Retrieve evidence from the ChromaDB knowledge base.
3. Store retrieved evidence into AgentState.
4. Return standardized AgentResult.
"""

from __future__ import annotations

from app.agents.base.base_agent import BaseAgent
from app.agents.base.agent_result import AgentResult
from app.agents.base.agent_state import AgentState

from app.core.rag import (
    seed_sample_guidelines,
    query_knowledge_base,
)


class MedicalKnowledgeAgent(BaseAgent):
    """
    Retrieves evidence from the medical knowledge base (RAG).
    """

    agent_name = "MedicalKnowledgeAgent"

    async def run(
        self,
        state: AgentState,
    ) -> AgentResult:

        # -----------------------------------------------------
        # Ensure knowledge base is initialized
        # -----------------------------------------------------

        seed_sample_guidelines()

        # -----------------------------------------------------
        # Build query from available patient context
        # -----------------------------------------------------

        query_parts = []

        if state.symptoms:
            query_parts.extend(state.symptoms)

        if state.disease_risk:
            risk = state.disease_risk.get(
                "condition",
                ""
            )

            if risk:
                query_parts.append(risk)

        if state.extracted_metrics:

            glucose = state.extracted_metrics.get("glucose")

            if glucose is not None and glucose >= 126:
                query_parts.append("Diabetes")

            systolic = state.extracted_metrics.get("systolic_bp")

            if systolic is not None and systolic >= 140:
                query_parts.append("Hypertension")

        if not query_parts:
            query_parts.append("General Clinical Guidelines")

        query = " ".join(query_parts)

        # -----------------------------------------------------
        # Query RAG
        # -----------------------------------------------------

        documents = query_knowledge_base(
            query_text=query,
            n_results=3,
        )

        knowledge = []

        evidence = []

        for document in documents:

            knowledge.append(
                {
                    "document": document
                }
            )

            evidence.append(document[:120])

        # -----------------------------------------------------
        # Store into AgentState
        # -----------------------------------------------------

        state.knowledge_results = knowledge

        state.set_agent_output(
            self.agent_name,
            knowledge,
            confidence=0.92,
        )

        # -----------------------------------------------------
        # Return Result
        # -----------------------------------------------------

        return AgentResult(
            agent=self.agent_name,
            status="SUCCESS",
            confidence=0.92,
            result=knowledge,
            evidence=evidence,
            metadata={
                "query": query,
                "documents_found": len(knowledge),
            },
        )

    def validate(
        self,
        state: AgentState,
    ) -> None:
        """
        Optional validation.
        """

        return