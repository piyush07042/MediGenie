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
            risk = state.disease_risk.get("condition") or state.disease_risk.get("evaluated_condition")
            category = state.disease_risk.get("risk_category")

            if risk:
                query_parts.append(risk)

            if category:
                query_parts.append(category)

        if state.extracted_metrics:

            glucose = state.extracted_metrics.get("glucose")

            if glucose is not None and glucose >= 126:
                query_parts.append("Diabetes")

            systolic = state.extracted_metrics.get("systolic_bp")

            if systolic is not None and systolic >= 140:
                query_parts.append("Hypertension")

        if not query_parts:
            query_parts.append("General Clinical Guidelines")

        diagnosis = getattr(state, "diagnosis", None) or state.patient.get("diagnosis")
        if diagnosis:
            query_parts.append(str(diagnosis))

        query = " ".join(query_parts)

        # -----------------------------------------------------
        # Query RAG
        # -----------------------------------------------------

        documents = query_knowledge_base(
            query_text=query,
            n_results=3,
        )

        knowledge = []
        citations = []
        evidence = []

        for document in documents:
            if isinstance(document, dict):
                doc_text = str(document.get("document", ""))
                metadata = document.get("metadata", {}) or {}
                raw_id = document.get("id")
                similarity_score = document.get("similarity_score")
            else:
                doc_text = str(document)
                metadata = {}
                raw_id = None
                similarity_score = None

            entry = {
                "id": raw_id,
                "document": doc_text,
                "metadata": metadata,
                "similarity_score": similarity_score,
            }
            knowledge.append(entry)

            if doc_text:
                evidence.append(doc_text[:200])

            citations.append({
                "source": metadata.get("source") or metadata.get("title") or "Clinical guideline",
                "identifier": metadata.get("id") or metadata.get("source") or "",
                "text": doc_text,
                "similarity_score": similarity_score,
            })

        unique_knowledge = []
        seen_docs: set[tuple[str, str]] = set()
        for entry in knowledge:
            doc_text = str(entry.get("document", "") or "").strip()
            identifier = entry.get("metadata", {}).get("id") or entry.get("metadata", {}).get("source") or ""
            key = (str(identifier), doc_text)
            if key not in seen_docs and doc_text:
                seen_docs.add(key)
                unique_knowledge.append(entry)

        if not unique_knowledge:
            state.add_warning("No knowledge evidence was retrieved for the current query.")

        state.knowledge_results = unique_knowledge

        state.set_agent_output(
            self.agent_name,
            unique_knowledge,
            confidence=0.92,
        )

        # -----------------------------------------------------
        # Return Result
        # -----------------------------------------------------

        return AgentResult(
            agent=self.agent_name,
            status="SUCCESS",
            confidence=0.92,
            result=unique_knowledge,
            evidence=evidence,
            metadata={
                "query": query,
                "documents_found": len(unique_knowledge),
                "citations": citations,
                "similarity_scores": [entry.get("similarity_score") for entry in unique_knowledge],
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