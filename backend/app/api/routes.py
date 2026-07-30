from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from app.agents.cdss_engine import run_multi_agent_pipeline
from app.core.risk_assessment import evaluate_disease_risk

router = APIRouter()

class ClinicalAnalysisRequest(BaseModel):
    patient_name: str
    age: int
    gender: str
    medical_history: Optional[str] = "None"
    glucose: Optional[float] = 100.0
    bmi: Optional[float] = 24.0
    systolic_bp: Optional[float] = 120.0
    raw_report_text: str

@router.post("/clinical/analyze")
def analyze_clinical_case(request: ClinicalAnalysisRequest):
    patient_context = {
        "name": request.patient_name,
        "age": request.age,
        "gender": request.gender,
        "medical_history": request.medical_history
    }
    
    # 1. Run Machine Learning & Explainable AI (Phase 9)
    metrics = {
        "glucose": request.glucose,
        "bmi": request.bmi,
        "age": request.age,
        "systolic_bp": request.systolic_bp
    }
    ml_risk_output = evaluate_disease_risk(metrics)
    
    # 2. Run CDSS Pipeline with RAG Evidence (Phase 10 & Multi-Agent)
    llm_analysis = run_multi_agent_pipeline(patient_context, request.raw_report_text)
    
    # Merge outputs
    return {
        "status": "success",
        "disease_risk_module": ml_risk_output,
        "cdss_agent_output": llm_analysis
    }