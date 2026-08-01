"""
Medical Report Analysis Agent tests.
"""

from __future__ import annotations

import pytest

from app.agents.agent_state import AgentState
from app.agents.report_analysis.report_analysis_agent import (
    MedicalReportAnalysisAgent,
)


@pytest.mark.asyncio
async def test_report_analysis():

    agent = MedicalReportAnalysisAgent()

    state = AgentState()

    state.raw_report_text = (
        "HbA1c 8.1%. Glucose elevated."
    )

    result = await agent.run(state)

    assert result.success is True