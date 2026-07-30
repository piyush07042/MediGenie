from fastapi import APIRouter, Response
from pydantic import BaseModel
from typing import Optional, Union, Dict, Any, List

from app.agents.workflow import medigenie_graph
from app.core.pdf_generator import generate_clinical_pdf_report

router = APIRouter()

class ClinicalAnalysisRequest(BaseModel):
    patient_id: Optional[int] = 1
    first_name: Optional[str] = "John"
    last_name: Optional[str] = "Doe"
    patient_name: Optional[str] = None
    age: int
    gender: str
    medical_history: Union[str, Dict[str, Any]] = "None"
    allergies: Optional[List[str]] = []
    current_medications: Optional[List[str]] = []
    glucose: Optional[float] = 100.0
    bmi: Optional[float] = 24.0
    systolic_bp: Optional[float] = 120.0
    raw_report_text: str

@router.post("/clinical/analyze")
def analyze_clinical_case(request: ClinicalAnalysisRequest):
    name = request.patient_name or f"{request.first_name} {request.last_name}".strip()
    history_str = request.medical_history if isinstance(request.medical_history, str) else str(request.medical_history)

    # Initial State Payload for LangGraph
    initial_state = {
        "patient_context": {
            "name": name,
            "age": request.age,
            "gender": request.gender,
            "medical_history": history_str,
            "allergies": request.allergies,
            "current_medications": request.current_medications,
            "glucose": request.glucose,
            "bmi": request.bmi,
            "systolic_bp": request.systolic_bp
        },
        "raw_report_text": request.raw_report_text
    }
    
    # Run StateGraph Workflow Execution (Phase 14 & 15 Orchestration)
    final_graph_state = medigenie_graph.invoke(initial_state)
    
    return final_graph_state["final_output"]

@router.post("/clinical/generate-pdf")
def generate_pdf_report(request: ClinicalAnalysisRequest):
    analysis_result = analyze_clinical_case(request)
    pdf_bytes = generate_clinical_pdf_report(analysis_result)
    
    patient_name = analysis_result["unified_cdss_summary"]["patient_name"].replace(" ", "_")
    filename = f"MediGenie_Report_{patient_name}.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )