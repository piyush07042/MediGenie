import io
from typing import Dict, Any
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable

def generate_clinical_pdf_report(clinical_data: Dict[str, Any]) -> bytes:
    """
    Phase 13: Generates a professional Explainable CDSS PDF Report.
    Returns the PDF as raw bytes for API streaming / downloading.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    
    # Custom Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        textColor=colors.HexColor('#1E3A8A'),
        spaceAfter=10
    )
    
    heading_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        textColor=colors.HexColor('#1E3A8A'),
        spaceBefore=12,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#333333')
    )

    alert_style = ParagraphStyle(
        'AlertBody',
        parent=body_style,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor('#B91C1C')
    )

    elements = []

    # 1. Header Title
    elements.append(Paragraph("MediGenie — Clinical Decision Support Report", title_style))
    elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#1E3A8A'), spaceAfter=15))

    # Extract Data
    cdss_summary = clinical_data.get("unified_cdss_summary", {})
    patient_name = cdss_summary.get("patient_name", "Unknown")
    urgency = cdss_summary.get("overall_urgency", "Routine")
    priority_directives = cdss_summary.get("priority_directives", [])
    
    risk_info = clinical_data.get("disease_risk_module", {}).get("disease_risk_assessment", {})
    safety_info = clinical_data.get("drug_safety_module", {}).get("drug_safety_assessment", {})
    cdss_output = clinical_data.get("cdss_agent_output", {})

    # 2. Patient Demographics Summary Table
    meta_data = [
        [
            Paragraph("<b>Patient Name:</b> " + patient_name, body_style),
            Paragraph("<b>Overall Urgency:</b> " + f"<font color='{'red' if urgency == 'High' else 'green'}'><b>{urgency}</b></font>", body_style)
        ],
        [
            Paragraph("<b>Report Generated:</b> Auto-generated CDSS System", body_style),
            Paragraph("<b>Status:</b> Evaluated", body_style)
        ]
    ]
    meta_table = Table(meta_data, colWidths=[270, 270])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F3F4F6')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#D1D5DB')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E5E7EB')),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(meta_table)
    elements.append(Spacer(1, 10))

    # 3. Priority Directives (Alerts)
    if priority_directives:
        elements.append(Paragraph("Priority Directives & High-Risk Alerts", heading_style))
        for directive in priority_directives:
            elements.append(Paragraph("• " + directive, alert_style))
        elements.append(Spacer(1, 10))

    # 4. Disease Risk Assessment & Explainable AI (XAI)
    elements.append(Paragraph("Disease Risk Assessment & XAI Factors", heading_style))
    risk_score = risk_info.get("estimated_risk_score_percent", "N/A")
    risk_category = risk_info.get("risk_category", "N/A")
    elements.append(Paragraph(f"<b>Condition Evaluated:</b> {risk_info.get('evaluated_condition', 'Metabolic Risk')}", body_style))
    elements.append(Paragraph(f"<b>Estimated Risk Score:</b> {risk_score}% ({risk_category} Risk)", body_style))
    elements.append(Spacer(1, 6))

    # XAI Table
    xai_factors = risk_info.get("explainable_ai_factors", [])
    if xai_factors:
        xai_data = [["Feature", "Value", "Impact", "Clinical Reasoning"]]
        for factor in xai_factors:
            xai_data.append([
                Paragraph(str(factor.get("feature")), body_style),
                Paragraph(str(factor.get("value")), body_style),
                Paragraph(str(factor.get("impact")), body_style),
                Paragraph(str(factor.get("reasoning")), body_style)
            ])
        xai_table = Table(xai_data, colWidths=[100, 70, 80, 290])
        xai_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E0E7FF')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1E3A8A')),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        elements.append(xai_table)
        elements.append(Spacer(1, 10))

    # 5. Drug Safety Analysis
    elements.append(Paragraph("Drug Safety & Allergy Verification", heading_style))
    safety_status = safety_info.get("status", "PASS")
    elements.append(Paragraph(f"<b>Status:</b> <font color='{'red' if safety_status == 'FLAGGED' else 'green'}'><b>{safety_status}</b></font>", body_style))
    
    allergy_conflicts = safety_info.get("allergy_conflicts", [])
    if allergy_conflicts:
        for item in allergy_conflicts:
            elements.append(Paragraph(f"• <b>Allergy Conflict:</b> {item.get('medication')} — {item.get('reasoning')}", alert_style))
            
    interaction_warnings = safety_info.get("interaction_warnings", [])
    if interaction_warnings:
        for item in interaction_warnings:
            elements.append(Paragraph(f"• <b>Drug Interaction:</b> {' + '.join(item.get('drugs_involved', []))} — {item.get('warning')}", alert_style))

    elements.append(Spacer(1, 10))

    # 6. Clinical Decision Support & Recommendations
    cds_details = cdss_output.get("clinical_decision_support", {})
    if cds_details:
        elements.append(Paragraph("Clinical Decision Support Considerations", heading_style))
        for idea in cds_details.get("suggested_clinical_considerations", []):
            elements.append(Paragraph("• " + idea, body_style))

        elements.append(Spacer(1, 6))
        elements.append(Paragraph("Recommended Further Diagnostics", heading_style))
        for diag in cds_details.get("further_diagnostics", []):
            elements.append(Paragraph("• " + diag, body_style))

    elements.append(Spacer(1, 15))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#94A3B8'), spaceAfter=10))
    elements.append(Paragraph("<b>Disclaimer:</b> <i>This report is generated by MediGenie AI Clinical Support System for physician review. Clinical decisions remain the sole responsibility of the attending healthcare provider.</i>", body_style))

    # Build PDF Document
    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()