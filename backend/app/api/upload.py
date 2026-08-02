"""
Medical Report Upload API
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Optional

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)

from app.agents.base.agent_state import AgentState
from app.agents.supervisor.supervisor import Supervisor
from app.core.deps import get_supervisor
from app.core.file_validation import validate_upload
from app.schemas.common import ApiResponse

router = APIRouter(
    prefix="/upload",
    tags=["Medical Report Upload"],
)

UPLOAD_DIRECTORY = Path("uploads")
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

        state.patient_context = patient_context
        state.report_file_path = str(destination)

        final_state, results, metrics = await supervisor.run(
            state
        )

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