"""
Workflow Entry Point
====================
"""

from __future__ import annotations

from app.agents.agent_state import AgentState
from app.agents.supervisor.supervisor import Supervisor


async def run_workflow(state: AgentState):

    supervisor = Supervisor()

    return await supervisor.run(state)