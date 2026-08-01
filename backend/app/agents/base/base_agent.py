"""
Base Agent for MediGenie

Every AI agent in the system must inherit from BaseAgent.

Responsibilities
----------------
- Standard execution lifecycle
- Logging
- Error handling
- Timing
- Validation
- Standard AgentResult generation
"""

from __future__ import annotations

import logging
import time

from abc import ABC, abstractmethod

from .agent_result import AgentResult
from .agent_state import AgentState


logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """
    Abstract base class for all MediGenie agents.
    """

    agent_name: str = "BaseAgent"

    def __init__(self):
        self.logger = logging.getLogger(self.agent_name)

    async def execute(self, state: AgentState) -> AgentResult:
        """
        Main execution wrapper.

        Handles:

        • timing
        • logging
        • exception handling
        • standard response
        """

        start = time.perf_counter()

        self.logger.info("%s started.", self.agent_name)

        try:

            self.validate(state)

            result = await self.run(state)

            elapsed = time.perf_counter() - start

            result.processing_time = round(elapsed, 4)

            state.add_trace(
                f"{self.agent_name} completed in {elapsed:.3f}s"
            )

            self.logger.info(
                "%s completed in %.3fs",
                self.agent_name,
                elapsed,
            )

            return result

        except Exception as exc:

            elapsed = time.perf_counter() - start

            state.add_error(str(exc))

            self.logger.exception(
                "%s failed: %s",
                self.agent_name,
                exc,
            )

            return AgentResult(
                agent=self.agent_name,
                status="FAILED",
                confidence=0.0,
                result=None,
                error=str(exc),
                processing_time=round(elapsed, 4),
            )

    @abstractmethod
    async def run(
        self,
        state: AgentState,
    ) -> AgentResult:
        """
        Business logic.

        Every child agent must implement this.
        """
        raise NotImplementedError

    def validate(self, state: AgentState):
        """
        Optional validation hook.

        Child agents may override.
        """
        return

    def info(self, message: str):
        self.logger.info(message)

    def warning(self, message: str):
        self.logger.warning(message)

    def error(self, message: str):
        self.logger.error(message)