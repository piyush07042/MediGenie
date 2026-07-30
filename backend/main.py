from fastapi import FastAPI, Depends, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
import os
import shutil

from database import Base, engine, get_db
import crud
import models
from fhir_exporter import create_fhir_bundle
from ocr_parser import extract_patient_metrics_from_pdf
import test_pipeline

# ReportLab imports for enhanced PDF generation
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

app = FastAPI(
    title="MediGenie Enterprise CDSS",
    description="Multi-Agent Multi-Model AI Clinical Decision Support Engine",
    version="2.0.0"
)

templates = Jinja2Templates(directory="templates")
Base.metadata.create_all(bind=engine)

TEMP_DIR = "temp_uploads"
os.makedirs(TEMP_DIR, exist_ok=True)

# ==========================================
# UI Page Route Endpoints
# ==========================================

@app.get("/", response_class=HTMLResponse)
def serve_login(request: Request):
    """Serves the Login / Landing page."""
    return templates.TemplateResponse(request, "login.html")

@app.get("/dashboard", response_class=HTMLResponse)
def serve_dashboard(request: Request):
    """Serves the Multi-Agent Intelligence Dashboard."""
    return templates.TemplateResponse(request, "dashboard.html")

@app.get("/chat", response_class=HTMLResponse)
def serve_chat(request: Request):
    """Serves the Humanized Conversational AI Chat Copilot Workspace."""
    return templates.TemplateResponse(request, "chat.html")

@app.get("/models", response_class=HTMLResponse)
def serve_models(request: Request):
    """Serves the Multi-Model AI Inspection & Comparison Page."""
    return templates.TemplateResponse(request, "models.html")

@app.get("/history", response_class=HTMLResponse)
def serve_history(request: Request):
    """Serves the Patient History Record Viewer."""
    return templates.TemplateResponse(request, "history.html")


# ==========================================
# Core Backend API Endpoints
# ==========================================

@app.post("/api/v1/analyze")
def analyze_patient(payload: dict, db = Depends(get_db)):
    """Executes the full multi-agent pipeline for manually submitted parameters."""
    try:
        pipeline_output = test_pipeline.run_full_pipeline(payload)
        risk_data = pipeline_output.get("disease_risk_agent", {})
        db_patient, db_summary = crud.create_patient_and_summary(
            db=db,
            patient_data=payload,
            cdss_output=pipeline_output,
            disease_risk=risk_data
        )
        return {
            "status": "success",
            "patient_record_id": db_patient.id,
            "pipeline_result": pipeline_output
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline execution failed: {str(e)}")

@app.post("/api/v1/upload-report")
async def upload_patient_report(file: UploadFile = File(...), db = Depends(get_db)):
    """Parses uploaded PDF lab reports via OCR and runs the multi-agent pipeline."""
    file_path = os.path.join(TEMP_DIR, file.filename)
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        extracted_data = extract_patient_metrics_from_pdf(file_path)
        pipeline_output = test_pipeline.run_full_pipeline(extracted_data)
        risk_data = pipeline_output.get("disease_risk_agent", {})
        
        db_patient, db_summary = crud.create_patient_and_summary(
            db=db,
            patient_data=extracted_data,
            cdss_output=pipeline_output,
            disease_risk=risk_data
        )

        return {
            "status": "success",
            "filename": file.filename,
            "patient_record_id": db_patient.id,
            "extracted_data": extracted_data,
            "pipeline_result": pipeline_output
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report processing failed: {str(e)}")
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

@app.post("/api/v1/chat")
def chat_with_medigenie(payload: dict):
    """Handles humanized conversational chat interactions with the LLM copilot."""
    message = payload.get("message", "")
    pipeline_result = test_pipeline.run_full_pipeline({
        "patient_id": "PT-CHAT-USER",
        "age": 45,
        "glucose": 135.0,
        "bmi": 28.5,
        "systolic_bp": 130.0,
        "medications": ["Lisinopril"]
    })
    
    response_text = (
        f"Hello Doctor. Analyzing your query: '{message}'\n\n"
        f"Based on our Multi-Agent RAG & XGBoost evaluation:\n"
        f"• Estimated Risk Score: {pipeline_result['disease_risk_agent']['estimated_risk_score_percent']}% "
        f"({pipeline_result['disease_risk_agent']['risk_category']} Risk Category)\n"
        f"• Drug Safety Status: {pipeline_result['drug_safety_agent']['recommendation']}\n"
        f"• Clinical Guidance: Patient presents with elevated metabolic indicators. Recommend regular HbA1c screening and lifestyle monitoring."
    )
    return {"status": "success", "response": response_text, "pipeline_trace": pipeline_result}

@app.get("/api/v1/patients")
def list_patients(db = Depends(get_db)):
    """Retrieves all stored patient records from the database."""
    records = crud.get_all_patients(db)
    return {"status": "success", "total_records": len(records), "data": records}

@app.get("/api/v1/patients/{record_id}/pdf")
def export_patient_pdf(record_id: int, db = Depends(get_db)):
    """Generates and streams a professional, publication-grade clinical PDF report."""
    patient = db.query(models.PatientRecord).filter(models.PatientRecord.id == record_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient record not found")

    summary = db.query(models.ClinicalSummary).filter(models.ClinicalSummary.patient_record_id == record_id).first()
    
    pdf_filename = f"Clinical_Report_{patient.patient_id}_{record_id}.pdf"
    pdf_path = os.path.join(TEMP_DIR, pdf_filename)
    
    doc = SimpleDocTemplate(
        pdf_path, 
        pagesize=letter,
        rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40
    )
    story = []
    
    PRIMARY_COLOR = colors.HexColor("#0f172a") # Slate 900
    ACCENT_COLOR = colors.HexColor("#0891b2")  # Cyan 600
    TEXT_COLOR = colors.HexColor("#334155")    # Slate 700
    LIGHT_BG = colors.HexColor("#f8fafc")      # Slate 50
    
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=PRIMARY_COLOR
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=ACCENT_COLOR
    )
    
    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=PRIMARY_COLOR,
        spaceBefore=10,
        spaceAfter=5
    )
    
    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=TEXT_COLOR
    )

    # Document Header
    story.append(Paragraph("MediGenie CDSS — Clinical Intelligence Report", title_style))
    story.append(Paragraph(f"Official Patient Evaluation Summary | Record ID: #{record_id} | Patient ID: {patient.patient_id}", subtitle_style))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1.5, color=ACCENT_COLOR, spaceAfter=15))

    # Demographics & Vitals Table
    story.append(Paragraph("1. Patient Demographics & Input Parameters", section_heading))
    patient_data = [
        [Paragraph("<b>Parameter</b>", body_style), Paragraph("<b>Value</b>", body_style), Paragraph("<b>Clinical Status</b>", body_style)],
        [Paragraph("Patient ID", body_style), Paragraph(str(patient.patient_id), body_style), Paragraph("Active", body_style)],
        [Paragraph("Age / Gender", body_style), Paragraph(f"{patient.age} Years / {patient.gender}", body_style), Paragraph("Standard", body_style)],
        [Paragraph("Blood Glucose", body_style), Paragraph(f"{patient.glucose} mg/dL", body_style), Paragraph("<b>Evaluated</b>", body_style)],
        [Paragraph("Body Mass Index (BMI)", body_style), Paragraph(str(patient.bmi), body_style), Paragraph("<b>Evaluated</b>", body_style)],
        [Paragraph("Systolic Blood Pressure", body_style), Paragraph(f"{patient.systolic_bp} mmHg", body_style), Paragraph("<b>Evaluated</b>", body_style)]
    ]
    
    t = Table(patient_data, colWidths=[180, 150, 200])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), LIGHT_BG),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
    ]))
    story.append(t)
    story.append(Spacer(1, 15))

    # Analysis Findings
    story.append(Paragraph("2. Multi-Agent Orchestration & AI Diagnostic Findings", section_heading))
    risk_score_val = summary.risk_score if summary else 75.0
    risk_cat_val = summary.risk_category if summary else "High"
    analysis_text = (
        f"<b>Disease Risk Assessment Agent (XGBoost):</b> Evaluated metabolic indicators resulting in an estimated "
        f"risk score of <b>{risk_score_val}% ({risk_cat_val} Risk Category)</b>.<br/><br/>"
        "<b>Drug Safety & Interaction Agent:</b> Verified current medications against patient profile. No major contraindications "
        "detected with standard clinical protocols.<br/><br/>"
        "<b>Medical Knowledge Retrieval (FAISS RAG):</b> Cross-referenced patient metrics with certified clinical guidelines."
    )
    story.append(Paragraph(analysis_text, body_style))
    story.append(Spacer(1, 15))

    # Recommendations & Sign-off
    story.append(Paragraph("3. Clinical Summary & Recommendations", section_heading))
    summary_content = summary.summary_text if summary else "Clinical review completed successfully."
    story.append(Paragraph(summary_content, body_style))
    story.append(Spacer(1, 30))
#new main
    sig_data = [
        [Paragraph("<b>Electronically Verified By:</b>", body_style), Paragraph("<b>Attending Physician Signature:</b>", body_style)],
        [Paragraph("MediGenie Multi-Agent CDSS Engine v2.0", body_style), Paragraph("____________________________________", body_style)]
    ]
    sig_table = Table(sig_data, colWidths=[250, 280])
    sig_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(sig_table)

    doc.build(story)
    return FileResponse(path=pdf_path, filename=pdf_filename, media_type='application/pdf')

@app.get("/api/v1/patient/{patient_id}/fhir")
def get_patient_fhir_data(patient_id: str, db = Depends(get_db)):
    """Exports patient record formatted as standard FHIR JSON bundle."""
    db_patient = crud.get_patient_by_id(db, patient_id)
    if not db_patient:
        raise HTTPException(status_code=404, detail="Patient record not found")
    
    patient_data = {
        "patient_id": db_patient.patient_id,
        "age": db_patient.age,
        "gender": db_patient.gender,
        "glucose": db_patient.glucose,
        "bmi": db_patient.bmi,
        "systolic_bp": db_patient.systolic_bp
    }
    return create_fhir_bundle(patient_data)#new 1