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