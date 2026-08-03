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
        "age": 45,
        "gender": "Female",
    }

    state.recommendations = [
        {
            "title": "Lifestyle",
            "recommendation": "Exercise regularly.",
        },
    ]

    agent = ReportGenerationAgent()

    result = await agent.run(state)

    assert result.success
    assert "Clinical Summary for John Doe" in state.final_report["clinical_summary"]
