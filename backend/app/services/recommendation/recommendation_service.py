"""
Recommendation service: centralize recommendation generation logic
so agents can call a single API.
"""
from __future__ import annotations

from typing import Any

from app.agents.base.agent_state import AgentState
from app.services.recommendation.knowledge_evidence import (
    build_citations_from_knowledge,
    summarize_evidence,
)


def _build_evidence_payload(knowledge_results: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
    """Convert retrieved knowledge snippets into evidence entries for recommendations."""
    evidence: list[dict[str, Any]] = []
    for entry in knowledge_results or []:
        if not isinstance(entry, dict):
            continue

        document = entry.get("document") or entry.get("text") or ""
        metadata = entry.get("metadata") or {}
        source = metadata.get("source") or metadata.get("title") or "Clinical guideline"
        snippet = str(document).strip()
        if snippet:
            evidence.append({
                "source": source,
                "text": snippet,
            })

    return evidence


def _build_similarity_scores(knowledge_results: list[dict[str, Any]] | None) -> list[float]:
    scores: list[float] = []
    for entry in knowledge_results or []:
        score = entry.get("similarity_score")
        if isinstance(score, (int, float)):
            scores.append(float(score))
    return scores


def _build_recommendation_context(state: AgentState) -> dict[str, Any]:
    knowledge_results = state.knowledge_results or []
    evidence_payload = _build_evidence_payload(knowledge_results)
    citations = build_citations_from_knowledge(knowledge_results)
    similarity_scores = _build_similarity_scores(knowledge_results)
    evidence_summary = summarize_evidence(knowledge_results)

    return {
        "evidence": evidence_payload,
        "citations": citations,
        "similarity_scores": similarity_scores,
        "evidence_summary": evidence_summary,
    }


def generate_recommendations(state: AgentState) -> list[dict[str, Any]]:
    """Generate recommendations based on state outputs.

    This extracts the logic previously embedded in RecommendationAgent
    so other callers (CLI/tests) can reuse it.
    """
    recommendations: list[dict[str, Any]] = []
    context = _build_recommendation_context(state)

    # Disease risk
    risk = state.disease_risk or {}
    if risk:
        category = str(risk.get("risk_category", "")).strip().title()
        score = risk.get("risk_score", 0)
        drivers = risk.get("top_factors") or risk.get("drivers") or []
        if isinstance(drivers, dict):
            drivers = [drivers]

        risk_recs = risk.get("recommendations", [])
        if isinstance(risk_recs, str):
            risk_recs = [risk_recs]

        if category == "High":
            recommendations.append({
                "priority": "High",
                "title": "Elevated Risk Profile",
                "recommendation": (
                    "Patient is at high risk. Review the top risk drivers "
                    "and accelerate diagnostic evaluation and treatment planning."
                ),
                **context,
            })
        elif risk_recs:
            for rec in risk_recs:
                recommendations.append({
                    "priority": "High" if category == "High" else "Medium",
                    "title": "Risk-Based Recommendation",
                    "recommendation": str(rec),
                    **context,
                })
        elif category == "Moderate":
            recommendations.append({
                "priority": "Medium",
                "title": "Moderate Risk Management",
                "recommendation": (
                    "Patient is at moderate risk. Continue monitoring trends "
                    "and implement guideline-supported preventive measures."
                ),
                **context,
            })
        else:
            recommendations.append({
                "priority": "Low",
                "title": "Routine Monitoring",
                "recommendation": (
                    "Patient has low risk. Maintain regular follow-up and lifestyle optimization."
                ),
                **context,
            })

    # Drug safety
    drug = state.drug_analysis or {}
    if drug:
        details = []
        for item in drug.get("interactions", []):
            details.append(f"Interaction: {item.get('severity')} severity between {', '.join(item.get('drugs_involved', []))}.")
        for item in drug.get("allergies", []):
            details.append(f"Allergy: {item.get('medication')} ({item.get('allergy_type')}).")
        for item in drug.get("contraindications", []):
            details.append(f"Contraindication: {item.get('medication')} for {item.get('condition')}." )

        if drug.get("status") == "FLAGGED":
            recommendations.append({
                "priority": "Critical",
                "title": "Medication Safety Alert",
                "recommendation": (
                    "Review medication interactions, allergy conflicts, contraindications, and organ function adjustments before prescribing."
                ),
                "drug_safety_findings": details,
                **context,
            })
        else:
            recommendations.append({
                "priority": "Low",
                "title": "Medication Safety Review",
                "recommendation": (
                    "Drug safety review did not identify significant issues. Continue therapy with standard monitoring."
                ),
                "drug_safety_findings": details,
                **context,
            })

    # Knowledge-based suggestions
    knowledge = state.knowledge_results or []
    if knowledge:
        recommendations.append({
            "priority": "Information",
            "title": "Evidence-Based Guidance",
            "recommendation": (
                "Consult the retrieved clinical guidance and align the care plan with the most relevant evidence-based recommendations."
            ),
            **context,
        })

    if not recommendations:
        recommendations.append({
            "priority": "Low",
            "title": "No Significant Findings",
            "recommendation": "No evidence requiring immediate intervention.",
            **context,
        })

    return recommendations
