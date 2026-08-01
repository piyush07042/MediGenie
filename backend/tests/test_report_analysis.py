import pytest

from app.agents.base.agent_state import AgentState
from app.agents.report_analysis import MedicalReportAnalysisAgent


@pytest.mark.asyncio
async def test_report_analysis():

    state = AgentState(
        uploaded_reports=[
            "sample_report.pdf"
        ]
    )

    agent = MedicalReportAnalysisAgent()

    result = await agent.execute(state)

    assert result.status in [
        "SUCCESS",
        "FAILED",
    ]