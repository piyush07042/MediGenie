"""
Medical Report Upload API
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Optional

import logging

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from app.agents.base.agent_state import AgentState
from app.agents.supervisor.supervisor import Supervisor
from app.core.deps import get_supervisor
from app.core.file_validation import validate_upload
from app.schemas.common import ApiResponse
from app.core.rag import ingest_documents
from app.core.config import settings
from app.core.deps import get_db
from app.services.report.report_service import get_patient_id_from_context, save_ai_report

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/upload",
    tags=["Medical Report Upload"],
)

UPLOAD_DIRECTORY = Path(settings.UPLOAD_DIRECTORY)
UPLOAD_DIRECTORY.mkdir(
    parents=True,
    exist_ok=True,
)


@router.post(
    "/report",
    response_model=ApiResponse,
    status_code=status.HTTP_200_OK,
)
async def upload_report(
    file: UploadFile = File(...),
    patient_context_json: Optional[str] = Form("{}"),
    supervisor: Supervisor = Depends(get_supervisor),
    db: Session = Depends(get_db),
):
    """
    Upload a medical report and execute the Supervisor workflow.
    """

    await validate_upload(file)

    destination = UPLOAD_DIRECTORY / file.filename

    try:

        with destination.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        try:
            patient_context = json.loads(
                patient_context_json
            )
        except json.JSONDecodeError:
            patient_context = {}

        state = AgentState()

        state.patient = patient_context
        state.uploaded_reports = [str(destination)]
        state.report_text = str(destination)
        state.raw_report_text = str(destination)

        final_state, results, metrics = await supervisor.run(
            state
        )

        patient_id = get_patient_id_from_context(state.patient)
        if patient_id is not None:
            logger.info("Saving report...")
            logger.info("Patient ID: %s", patient_id)
            save_ai_report(db, patient_id, final_state)
        else:
            logger.info("Skipping report persistence: no patient_id found in uploaded report context.")

        # Optional: index the extracted report text into the knowledge store.
        try:
            text = ""
            if state.report_text and isinstance(state.report_text, str):
                report_path = Path(state.report_text)
                if report_path.exists() and report_path.is_file():
                    if report_path.suffix.lower() == ".txt":
                        text = report_path.read_text(encoding="utf-8")
                    else:
                        from app.services.ocr.ocr_service import extract_text as ocr_extract_text

                        text = ocr_extract_text(str(report_path))
                else:
                    text = state.report_text

            if text and text.strip():
                ingest_documents([text], metadatas=[{"source": "uploaded_report"}])
        except Exception:
            # non-fatal
            pass

        return ApiResponse(
            message="Medical report processed successfully.",
            data={
                "workflow_state": final_state,
                "agent_results": results,
                "workflow_metrics": metrics,
            },
        )

    except Exception as exc:

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Report processing failed: {exc}",
        )

    finally:

        if destination.exists():
            destination.unlink()