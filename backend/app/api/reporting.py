from __future__ import annotations

import os

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.pdf_generator import generate_clinical_pdf_report

from app.models.models import (
    Patient,
    ClinicalSummary,
)

router = APIRouter(
    prefix="/reports",
    tags=["Clinical Reports"],
)

TEMP_DIR = "temp_reports"
os.makedirs(TEMP_DIR, exist_ok=True)


@router.get("/{patient_id}/pdf")
def generate_pdf(
    patient_id: int,
    db: Session = Depends(get_db),
):
    """
    Generate a clinical PDF report for a patient.
    """

    patient = (
        db.query(Patient)
        .filter(Patient.id == patient_id)
        .first()
    )

    if patient is None:
        raise HTTPException(
            status_code=404,
            detail="Patient not found",
        )

    summary = (
        db.query(ClinicalSummary)
        .filter(
            ClinicalSummary.patient_id == patient.id
        )
        .first()
    )

    report = {
        "patient": patient,
        "summary": summary,
    }

    pdf_bytes = generate_clinical_pdf_report(report)

    filename = (
        f"MediGenie_Report_{patient.id}.pdf"
    )

    output_path = os.path.join(
        TEMP_DIR,
        filename,
    )

    with open(output_path, "wb") as fp:
        fp.write(pdf_bytes)

    return FileResponse(
        output_path,
        media_type="application/pdf",
        filename=filename,
    )