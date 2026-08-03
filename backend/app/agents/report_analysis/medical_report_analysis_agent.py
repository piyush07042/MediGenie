from __future__ import annotations

import time

from app.agents.base.base_agent import BaseAgent
from app.agents.base.agent_result import AgentResult
from app.agents.base.agent_state import AgentState

from app.services.ocr.ocr_service import OCRService
from app.services.ocr.parser import Parser


class MedicalReportAnalysisAgent(BaseAgent):
    """
    Medical Report Analysis Agent

    Responsibilities
    ----------------
    1. Extract text from uploaded reports.
    2. Parse clinical values.
    3. Store results into AgentState.
    """

    agent_name = "MedicalReportAnalysisAgent"

    async def run(self, state: AgentState) -> AgentResult:

        start = time.perf_counter()

        # Accept either uploaded report files or raw report text for tests
        if not state.uploaded_reports and not state.raw_report_text:
            return AgentResult(
                agent=self.agent_name,
                status="FAILED",
                confidence=0.0,
                result={},
                warnings=["No medical reports uploaded or raw report text provided."],
            )

        extracted_reports = []
        parsed_metrics = {}

        if state.uploaded_reports:
            for report in state.uploaded_reports:

                text = OCRService.extract_text(report)

                metrics = Parser.parse(text)

                extracted_reports.append(
                    {
                        "report": report,
                        "text": text,
                        "metrics": metrics,
                    }
                )

                parsed_metrics.update(metrics)
        else:
            # Use raw_report_text (tests supply this)
            text = state.raw_report_text or ""
            metrics = Parser.parse(text)
            extracted_reports.append({"report": None, "text": text, "metrics": metrics})
            parsed_metrics.update(metrics)

        state.report_text = "\n\n".join(
            item["text"] for item in extracted_reports
        )

        state.ocr_result = extracted_reports

        state.extracted_metrics = parsed_metrics

        elapsed = round(time.perf_counter() - start, 3)

        state.set_agent_output(
            self.agent_name,
            parsed_metrics,
            confidence=0.95,
            execution_time=elapsed,
        )

        return AgentResult(
            agent=self.agent_name,
            status="SUCCESS",
            confidence=0.95,
            result=parsed_metrics,
            metadata={
                "reports_processed": len(extracted_reports),
                "execution_time": elapsed,
            },
        )