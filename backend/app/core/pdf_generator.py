"""PDF report generator used by the reporting API."""

from __future__ import annotations

from io import BytesIO
from typing import Any

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors


def _safe_value(source: Any, keys: list[str], default: str = "N/A") -> str:
    if source is None:
        return default
    if isinstance(source, dict):
        for key in keys:
            if key in source and source[key] is not None:
                return str(source[key])
    else:
        for key in keys:
            value = getattr(source, key, None)
            if value is not None:
                return str(value)
    return default


def generate_clinical_pdf_report(report: dict[str, Any]) -> bytes:
    """Generate a clinical PDF report and return the raw bytes."""

    patient = report.get("patient", {}) or {}
    patient_name = _safe_value(patient, ["name", "first_name", "last_name"], "Patient")
    if patient_name == "Patient":
        first_name = _safe_value(patient, ["first_name"], "")
        last_name = _safe_value(patient, ["last_name"], "")
        patient_name = f"{first_name} {last_name}".strip() or "Patient"

    patient_id = _safe_value(patient, ["id", "patient_id"], "PT-UNKNOWN")
    age = _safe_value(patient, ["age"], "N/A")
    gender = _safe_value(patient, ["gender"], "N/A")

    disease_risk = report.get("disease_risk", {}) or {}
    risk_category = _safe_value(disease_risk, ["risk_category", "risk_level"], "Unknown")
    risk_score = _safe_value(disease_risk, ["risk_score", "estimated_risk_score_percent"], "N/A")

    medications = report.get("medications") or []
    if isinstance(medications, str):
        medications = [medications]
    allergies = report.get("allergies") or []
    if isinstance(allergies, str):
        allergies = [allergies]

    clinical_summary = (
        report.get("clinical_summary")
        or report.get("summary")
        or "No clinical summary available."
    )

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Heading1"],
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#1A365D"),
        spaceAfter=12,
    )
    heading_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#2B6CB0"),
        spaceBefore=10,
        spaceAfter=6,
    )
    body_style = ParagraphStyle(
        "BodyTextCustom",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#2D3748"),
    )

    story = []
    story.append(Paragraph("MediGenie CDSS Clinical Report", title_style))
    story.append(Spacer(1, 8))

    meta_table_data = [
        [Paragraph("<b>Patient ID:</b>", body_style), Paragraph(patient_id, body_style),
         Paragraph("<b>Risk Level:</b>", body_style), Paragraph(f"<b>{risk_category} ({risk_score})</b>", body_style)],
        [Paragraph("<b>Patient:</b>", body_style), Paragraph(patient_name, body_style),
         Paragraph("<b>Age / Gender:</b>", body_style), Paragraph(f"{age} / {gender}", body_style)],
        [Paragraph("<b>Medications:</b>", body_style), Paragraph(", ".join(medications) or "None", body_style),
         Paragraph("<b>Allergies:</b>", body_style), Paragraph(", ".join(allergies) or "None", body_style)],
    ]

    table = Table(meta_table_data, colWidths=[90, 180, 90, 150])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F7FAFC")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#E2E8F0")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))

    story.append(table)
    story.append(Spacer(1, 14))
    story.append(Paragraph("Clinical Summary", heading_style))

    for line in str(clinical_summary).split("\n"):
        if line.strip():
            story.append(Paragraph(line.strip(), body_style))
            story.append(Spacer(1, 4))

    doc.build(story)
    buffer.seek(0)
    return buffer.read()
