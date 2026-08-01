import pytest

from app.agents.base.agent_state import AgentState
from app.agents.intake import PatientIntakeAgent


@pytest.mark.asyncio
async def test_patient_intake():

    state = AgentState(
        patient={
            "name": "John",
            "age": 45,
            "gender": "male",
        }
    )

    agent = PatientIntakeAgent()

    result = await agent.execute(state)

    assert result.success
    assert result.confidence == 1.0