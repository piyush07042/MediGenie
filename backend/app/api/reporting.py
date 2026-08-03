from __future__ import annotations

import os

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from sqlalchemy.orm import Session, DeclarativeMeta

from app.db.session import get_db
from app.core.pdf_generator import generate_clinical_pdf_report
from app.core.report_renderer import (
    list_report_templates,
    render_report_html,
)

from app.models.models import (
    AIReport,
    Patient,
)

router = APIRouter(
    prefix="/reports",
    tags=["Clinical Reports"],
)

TEMP_DIR = "temp_reports"
os.makedirs(TEMP_DIR, exist_ok=True)


def _serialize_model(model: object) -> dict[str, object]:
    """Serialize a SQLAlchemy ORM model to a plain dict for template rendering."""
    if model is None:
        return {}
    if isinstance(model, dict):
        return model
    if isinstance(model.__class__, DeclarativeMeta):
        return {
            column.key: getattr(model, column.key)
            for column in model.__table__.columns
        }
    return {
        key: getattr(model, key)
        for key in dir(model)
        if not key.startswith("_") and not callable(getattr(model, key, None))
    }


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
        db.query(AIReport)
        .filter(
            AIReport.patient_id == patient.id
        )
        .order_by(AIReport.id.desc())
        .first()
    )

    if summary is None:
        raise HTTPException(
            status_code=404,
            detail="Clinical report not found for this patient.",
        )

    report = {
        "patient": _serialize_model(patient),
        "summary": _serialize_model(summary),
        "generated_at": summary.created_at.isoformat() if getattr(summary, 'created_at', None) else None,
        "clinical_summary": getattr(summary, 'clinical_summary', None) or getattr(summary, 'summary_text', None) or getattr(summary, 'summary', None) or "No clinical summary available.",
        "disease_risk": getattr(summary, 'risk_assessment', None) or {},
        "medications": getattr(patient, 'current_medications', None) or [],
        "allergies": getattr(patient, 'allergies', None) or [],
        "recommendations": [],
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


@router.get("/{patient_id}/html")
def generate_html(
    patient_id: int,
    template: str = "report_template.html",
    db: Session = Depends(get_db),
):
    """Return an HTML-rendered clinical report for a patient."""
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
        db.query(AIReport)
        .filter(
            AIReport.patient_id == patient.id
        )
        .order_by(AIReport.id.desc())
        .first()
    )

    if summary is None:
        raise HTTPException(
            status_code=404,
            detail="Clinical report not found for this patient.",
        )

    report = {
        "patient": _serialize_model(patient),
        "summary": _serialize_model(summary),
        "generated_at": summary.created_at.isoformat() if getattr(summary, 'created_at', None) else None,
        "clinical_summary": getattr(summary, 'clinical_summary', None) or getattr(summary, 'summary_text', None) or getattr(summary, 'summary', None) or "",
        "disease_risk": getattr(summary, 'risk_assessment', None) or {},
        "medications": getattr(patient, 'current_medications', None) or [],
        "allergies": getattr(patient, 'allergies', None) or [],
        "recommendations": [],
    }

    html = render_report_html(report, template_name=template)

    return HTMLResponse(content=html, media_type="text/html")


@router.get("/templates")
def available_templates():
    """Return a list of available report HTML templates."""
    return {"templates": list_report_templates()}
