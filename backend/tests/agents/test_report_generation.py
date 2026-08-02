"""
Report Generation Agent tests.
"""

from __future__ import annotations

import pytest

from app.agents.base.agent_state import AgentState
from app.agents.report_generation.report_generation_agent import (
    ReportGenerationAgent,
)


@pytest.mark.asyncio
async def test_report_generation():

    state = AgentState()

    state.patient_context = {
        "name": "John Doe",
    }

    state.recommendations = [
        "Exercise regularly",
    ]

    agent = ReportGenerationAgent()

    result = await agent.run(state)

    assert result.success