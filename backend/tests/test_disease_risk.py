import pytest

from app.agents.base.agent_state import AgentState
from app.agents.risk import DiseaseRiskAgent


@pytest.mark.asyncio
async def test_risk_agent():

    state = AgentState()

    state.patient = {
        "age": 50,
        "gender": "Male",
    }

    state.extracted_metrics = {
        "glucose": 165,
        "bmi": 31,
    }

    agent = DiseaseRiskAgent()

    result = await agent.execute(state)

    assert result.status in [
        "SUCCESS",
        "FAILED",
    ]