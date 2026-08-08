from io import BytesIO
from typing import Any, Dict, List, Optional
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
    KeepTogether,
)


def _format_datetime(ts: Optional[str]) -> str:
    if not ts:
        return datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    try:
        return datetime.fromisoformat(ts).strftime("%Y-%m-%d %H:%M")
    except Exception:
        return str(ts)


def _safe_get(d: Dict[str, Any], key: str, default: Any = "") -> Any:
    return d.get(key) if d and key in d else default


def generate_medigenie_report(report: Dict[str, Any]) -> bytes:
    """
    Generate a professional clinical PDF report for MediGenie.

    report: a dictionary with structured keys (patient, inputs, result, summary, recommendations,
            medication_safety, evidence, followup, explainability, meta)

    Returns PDF bytes.
    """
    buffer = BytesIO()

    styles = getSampleStyleSheet()
    normal = styles["Normal"]
    normal.spaceAfter = 6
    normal.fontName = "Helvetica"
    heading = ParagraphStyle("Heading", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=12, textColor=colors.HexColor("#0B68D8"))
    section_title = ParagraphStyle("SectionTitle", parent=styles["Heading3"], fontName="Helvetica-Bold", fontSize=10, textColor=colors.HexColor("#0B68D8"))
    small = ParagraphStyle("Small", parent=normal, fontSize=9, textColor=colors.grey)

    doc = BaseDocTemplate(buffer, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm, topMargin=24 * mm, bottomMargin=18 * mm)

    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height - 12 * mm, id="normal")

    def _header_footer(canvas, doc_obj):
        canvas.saveState()
        # Header
        logo_path = report.get("meta", {}).get("logo_path")
        if logo_path:
            try:
                img = Image(logo_path, width=32, height=32)
                img.drawOn(canvas, doc.leftMargin, A4[1] - 40)
            except Exception:
                pass

        canvas.setFont("Helvetica-Bold", 14)
        canvas.drawString(doc.leftMargin + (36 if logo_path else 0), A4[1] - 30, "MEDIGENIE")
        canvas.setFont("Helvetica", 8)
        canvas.drawString(doc.leftMargin + (36 if logo_path else 0), A4[1] - 42, "AI Clinical Decision Support System")
        canvas.setFont("Helvetica-Bold", 9)
        canvas.drawRightString(A4[0] - doc.rightMargin, A4[1] - 30, "AI Generated Clinical Report")

        # Report metadata line
        report_id = report.get("meta", {}).get("report_id", "-")
        gen_ts = _format_datetime(report.get("meta", {}).get("generated_at"))
        version = report.get("meta", {}).get("version", "1.0")
        canvas.setFont("Helvetica", 8)
        canvas.drawRightString(A4[0] - doc.rightMargin, A4[1] - 42, f"Report ID: {report_id}    Generated: {gen_ts}    Version: {version}")

        # Footer
        footer_text = "MediGenie AI CDSS"
        canvas.setFont("Helvetica", 8)
        canvas.drawString(doc.leftMargin, 18 * mm, footer_text)
        timestamp = _format_datetime(report.get("meta", {}).get("generated_at"))
        canvas.drawCentredString(A4[0] / 2, 18 * mm, timestamp)
        canvas.drawRightString(A4[0] - doc.rightMargin, 18 * mm, f"Page {doc_obj.page}")

        canvas.restoreState()

    doc.addPageTemplates([PageTemplate(id="Report", frames=[frame], onPage=_header_footer)])

    elements: List[Any] = []

    # Title
    elements.append(Paragraph("AI Clinical Report", heading))
    elements.append(Spacer(1, 6))

    # PATIENT INFORMATION table
    patient = report.get("patient", {}) or {}
    pat_rows = []
    def add_row(label, value):
        if value is None or (isinstance(value, str) and not value.strip()):
            return
        pat_rows.append([Paragraph(f"<b>{label}</b>", normal), Paragraph(str(value), normal)])

    add_row("Patient Name", f"{patient.get('first_name','') } {patient.get('last_name','') }".strip())
    add_row("Age", patient.get("age"))
    add_row("Gender", patient.get("gender"))
    add_row("Disease", report.get("meta", {}).get("disease"))
    add_row("Report Date", _format_datetime(report.get("meta", {}).get("generated_at")))
    add_row("Patient ID", patient.get("id") or patient.get("patient_id"))

    if pat_rows:
        t = Table(pat_rows, colWidths=[50 * mm, doc.width - 50 * mm])
        t.setStyle(
            TableStyle(
                [
                    ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#d1e4ff")),
                    ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.whitesmoke),
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f8fbff")),
                ]
            )
        )
        elements.append(Paragraph("Patient Information", section_title))
        elements.append(Spacer(1, 4))
        elements.append(t)
        elements.append(Spacer(1, 8))

    # Clinical input summary - only non-null
    inputs = report.get("inputs", {}) or {}
    input_rows = []
    for key, val in inputs.items():
        if val is None or (isinstance(val, str) and not str(val).strip()):
            continue
        input_rows.append([Paragraph(f"{key.replace('_',' ').title()}", normal), Paragraph(str(val), normal)])

    if input_rows:
        t = Table(input_rows, colWidths=[60 * mm, doc.width - 60 * mm])
        t.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), colors.white),
                    ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, colors.HexColor("#fbfbfe")]),
                    ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#eef3ff")),
                    ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.whitesmoke),
                ]
            )
        )
        elements.append(Paragraph("Clinical Input Summary", section_title))
        elements.append(Spacer(1, 4))
        elements.append(t)
        elements.append(Spacer(1, 8))

    # Prediction Result large colored box
    result = report.get("result", {}) or {}
    pred = result.get("prediction") or result.get("label") or "Pending ML Screening"
    if str(pred) == "N/A":
        pred = "Pending ML Screening"

    raw_risk = result.get("risk") or result.get("risk_level") or result.get("confidence_label") or "Pending ML Evaluation"
    if str(raw_risk).upper() in ("UNKNOWN", "N/A"):
        risk = "PENDING ML EVALUATION"
    else:
        risk = str(raw_risk).upper()

    prob = result.get("probability")
    try:
        prob_text = f"{float(prob) * 100:.1f}%" if prob is not None else "Pending Screening"
    except Exception:
        prob_text = str(prob) if prob is not None else "Pending Screening"

    conf = result.get("confidence")
    try:
        conf_text = f"{float(conf) * 100:.0f}%" if conf is not None and isinstance(conf, (int, float)) and float(conf) <= 1 else (f"{float(conf):.0f}%" if isinstance(conf, (int, float)) else str(conf or "Baseline"))
    except Exception:
        conf_text = str(conf) if conf is not None else "Baseline"
    if conf_text in ("None", "N/A"):
        conf_text = "Baseline Intake"

    # color by risk
    if "HIGH" in risk:
        box_color = colors.HexColor("#ffe6e6")
        border = colors.HexColor("#e04d4d")
    elif "MED" in risk or "MOD" in risk:
        box_color = colors.HexColor("#fff6e6")
        border = colors.HexColor("#e08b1f")
    else:
        box_color = colors.HexColor("#e8fff0")
        border = colors.HexColor("#1f9b4a")

    pred_table = Table(
        [
            [Paragraph(f"<b>Prediction</b>", normal), Paragraph(str(pred), heading)],
            [Paragraph(f"<b>Risk Level</b>", normal), Paragraph(str(risk), normal)],
            [Paragraph(f"<b>Probability</b>", normal), Paragraph(prob_text, normal)],
            [Paragraph(f"<b>Confidence</b>", normal), Paragraph(conf_text, normal)],
        ],
        colWidths=[50 * mm, doc.width - 50 * mm],
    )
    pred_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), box_color),
                ("BOX", (0, 0), (-1, -1), 1.0, border),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )

    elements.append(Paragraph("Prediction Result", section_title))
    elements.append(Spacer(1, 4))
    elements.append(pred_table)
    elements.append(Spacer(1, 8))

    # Clinical summary
    clinical_summary = report.get("clinical_summary") or report.get("summary")
    if clinical_summary:
        elements.append(Paragraph("Clinical Summary", section_title))
        elements.append(Spacer(1, 4))
        elements.append(Paragraph(clinical_summary, normal))
        elements.append(Spacer(1, 8))

    # Key risk factors bullets
    factors = report.get("key_risk_factors") or report.get("risk_factors") or []
    if factors:
        bullets = [Paragraph(f"• {str(x)}", normal) for x in factors]
        elements.append(Paragraph("Key Risk Factors", section_title))
        elements.append(Spacer(1, 4))
        elements.extend(bullets)
        elements.append(Spacer(1, 8))

    # Recommendations numbered
    recs = report.get("recommendations") or []
    if recs:
        elements.append(Paragraph("AI Recommendations", section_title))
        elements.append(Spacer(1, 4))
        for i, r in enumerate(recs[:20], start=1):
            elements.append(Paragraph(f"{i}. {str(r)}", normal))
        elements.append(Spacer(1, 8))

    # Clinical Intelligence / Guideline-derived summary
    clinical = report.get("clinical_intelligence") or {}
    if clinical:
        elements.append(Paragraph("Clinical Intelligence", section_title))
        elements.append(Spacer(1, 4))
        for key, value in clinical.items():
            if isinstance(value, list):
                elements.append(Paragraph(f"<b>{key}:</b>", normal))
                for item in value:
                    elements.append(Paragraph(f"• {item}", normal))
            else:
                elements.append(Paragraph(f"<b>{key}:</b> {value}", normal))
            elements.append(Spacer(1, 4))
        elements.append(Spacer(1, 8))

    # Medication safety
    med = report.get("medication_safety") or {}
    if med:
        rows = []
        rows.append([Paragraph("Risk Level", normal), Paragraph(str(med.get("risk_level") or "None"), normal)])
        rows.append([Paragraph("Warnings", normal), Paragraph(", ".join(med.get("warnings") or []) or "None", normal)])
        rows.append([Paragraph("Drug interactions", normal), Paragraph(", ".join(med.get("interactions") or []) or "None", normal)])
        rows.append([Paragraph("Contraindications", normal), Paragraph(", ".join(med.get("contraindications") or []) or "None", normal)])
        rows.append([Paragraph("Renal adjustment", normal), Paragraph(str(med.get("renal_adjustment") or "None"), normal)])
        rows.append([Paragraph("Liver adjustment", normal), Paragraph(str(med.get("liver_adjustment") or "None"), normal)])
        rows.append([Paragraph("Pregnancy safety", normal), Paragraph(str(med.get("pregnancy_safety") or "None"), normal)])
        t = Table(rows, colWidths=[60 * mm, doc.width - 60 * mm])
        t.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#eef3ff")), ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, colors.HexColor("#fbfbfe")])]))
        elements.append(Paragraph("Medication Safety", section_title))
        elements.append(Spacer(1, 4))
        elements.append(t)
        elements.append(Spacer(1, 8))

    # Medical evidence - top 3
    evidence = report.get("evidence") or []
    if evidence:
        elements.append(Paragraph("Medical Evidence", section_title))
        elements.append(Spacer(1, 4))
        for ev in evidence[:3]:
            src = ev.get("source") or ev.get("source_name") or ev.get("title") or "Unknown"
            cat = ev.get("category") or ev.get("type") or ""
            excerpt = ev.get("excerpt") or ev.get("snippet") or ev.get("summary") or ""
            if isinstance(excerpt, str) and len(excerpt) > 300:
                excerpt = excerpt[:300].rsplit(" ", 1)[0] + "..."
            score = ev.get("score") or ev.get("similarity") or ""
            elements.append(Paragraph(f"Source: <b>{src}</b>", normal))
            if cat:
                elements.append(Paragraph(f"Category: {cat}", small))
            if excerpt:
                elements.append(Paragraph(excerpt, normal))
            if score:
                elements.append(Paragraph(f"Similarity: {score}", small))
            elements.append(Spacer(1, 6))

    # Follow-up plan
    follow = report.get("follow_up") or report.get("followup") or []
    if follow:
        elements.append(Paragraph("Follow-up Plan", section_title))
        elements.append(Spacer(1, 4))
        for item in follow:
            elements.append(Paragraph(f"• {item}", normal))
        elements.append(Spacer(1, 8))

    # Explainability
    explain = report.get("explainability") or report.get("explain") or {}
    elements.append(Paragraph("AI Explainability", section_title))
    elements.append(Spacer(1, 4))
    if explain and (explain.get("top_factors") or explain.get("feature_importance") or explain.get("shap")):
        if explain.get("top_factors"):
            elements.append(Paragraph("Top factors:", small))
            for f in explain.get("top_factors")[:10]:
                elements.append(Paragraph(f"• {f}", normal))
        if explain.get("feature_importance"):
            elements.append(Paragraph("Feature importance:", small))
            elements.append(Paragraph(str(explain.get("feature_importance")), normal))
        if explain.get("shap"):
            elements.append(Paragraph("SHAP summary available.", small))
    else:
        elements.append(Paragraph("Explainability not available.", normal))

    # Disclaimer box
    disclaimer = (
        "This report is AI-assisted and is intended to support qualified healthcare professionals. "
        "It should not replace clinical judgement. Use in conjunction with clinical assessment and local protocols."
    )
    disc_table = Table([[Paragraph(disclaimer, small)]], colWidths=[doc.width])
    disc_table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#fff7e6")), ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#f1c27d"))]))
    elements.append(Spacer(1, 8))
    elements.append(disc_table)

    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf
