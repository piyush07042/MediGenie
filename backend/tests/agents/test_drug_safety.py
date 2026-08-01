"""
Drug Safety Agent tests.
"""

from __future__ import annotations

import pytest

from app.agents.agent_state import AgentState
from app.agents.drug_safety.drug_safety_agent import (
    DrugSafetyAgent,
)


@pytest.mark.asyncio
async def test_drug_safety():

    state = AgentState()

    state.patient_context = {
        "current_medications": [
            "Metformin",
            "Lisinopril",
        ]
    }

    agent = DrugSafetyAgent()

    result = await agent.run(state)

    assert result.success