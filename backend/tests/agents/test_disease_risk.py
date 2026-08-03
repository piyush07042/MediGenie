"""
Disease Risk Agent tests.
"""

from __future__ import annotations

import pytest

from app.agents.base.agent_state import AgentState
from app.agents.risk.disease_risk_agent import DiseaseRiskAgent


@pytest.mark.asyncio
async def test_disease_risk():

    state = AgentState()

    state.patient_context = {
        "age": 58,
        "glucose": 175,
        "bmi": 31,
    }

    agent = DiseaseRiskAgent()

    result = await agent.run(state)

    assert result.success
    assert state.disease_risk.get("risk_level") in {"low", "moderate", "high"}
    assert "risk_score" in state.disease_risk


@pytest.mark.asyncio
async def test_disease_risk_uses_diabetes_model_when_diagnosis_is_diabetes():

    state = AgentState()

    state.patient_context = {
        "age": 55,
        "bmi": 32,
        "glucose": 150,
        "systolic_bp": 140,
        "cholesterol": 220,
        "diagnosis": "Type 2 Diabetes",
    }

    agent = DiseaseRiskAgent()

    result = await agent.run(state)

    assert result.success
    assert state.disease_risk.get("model_used") == "diabetes_model"
    assert state.disease_risk.get("condition") == "Diabetes Risk"
    assert state.disease_risk.get("risk_category") == "high"
