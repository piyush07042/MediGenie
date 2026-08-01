"""
Supervisor tests.
"""

from __future__ import annotations

import pytest

from app.agents.agent_result import AgentResult
from app.agents.agent_state import AgentState
from app.agents.supervisor.supervisor import Supervisor


@pytest.mark.asyncio
async def test_supervisor_initialization():

    supervisor = Supervisor()

    assert supervisor is not None


@pytest.mark.asyncio
async def test_supervisor_runs_workflow():

    supervisor = Supervisor()

    state = AgentState()

    state.patient_context = {
        "name": "John Doe",
        "age": 52,
        "gender": "Male",
    }

    state.raw_report_text = (
        "HbA1c 7.8%. Blood glucose elevated."
    )

    final_state, results, metrics = await supervisor.run(
        state
    )

    assert final_state is not None

    assert isinstance(results, list)

    assert metrics is not None


@pytest.mark.asyncio
async def test_supervisor_returns_agent_results():

    supervisor = Supervisor()

    state = AgentState()

    state.patient_context = {
        "name": "Jane",
    }

    state.raw_report_text = "Normal CBC"

    _, results, _ = await supervisor.run(state)

    assert all(
        isinstance(result, AgentResult)
        for result in results
    )