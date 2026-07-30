import os
import shutil
import json
from typing import Optional  # <--- Added missing import here
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, status
from app.schemas.cdss import AnalysisRequestSchema, AnalysisResponseSchema
from app.agents.workflow import medigenie_graph

router = APIRouter()

TEMP_UPLOAD_DIR = "temp_uploads"
os.makedirs(TEMP_UPLOAD_DIR, exist_ok=True)

@router.post("/analyze", response_model=AnalysisResponseSchema, status_code=status.HTTP_200_OK)
async def analyze_patient_data(payload: AnalysisRequestSchema):
    """
    Full Clinical Multi-Agent Workflow Execution API
    """
    try:
        initial_state = {
            "patient_context": payload.patient_context.model_dump(),
            "report_file_path": None,
            "raw_report_text": payload.raw_report_text
        }
        
        pipeline_result = medigenie_graph.invoke(initial_state)
        
        return AnalysisResponseSchema(
            status="success",
            message="Clinical Evaluation Completed",
            data=pipeline_result
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline Error: {str(e)}")

@router.post("/upload-report", response_model=AnalysisResponseSchema)
async def upload_and_analyze_report(
    file: UploadFile = File(...),
    patient_context_json: Optional[str] = Form(default="{}")
):
    """
    OCR Medical PDF/Image Processing & Agent Pipeline API
    """
    try:
        file_path = os.path.join(TEMP_UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        try:
            patient_context_dict = json.loads(patient_context_json)
        except Exception:
            patient_context_dict = {}

        initial_state = {
            "patient_context": patient_context_dict,
            "report_file_path": file_path,
            "raw_report_text": ""
        }

        pipeline_result = medigenie_graph.invoke(initial_state)

        # Cleanup uploaded file after execution
        if os.path.exists(file_path):
            os.remove(file_path)

        return AnalysisResponseSchema(
            status="success",
            message="Report Parsed & CDSS Analysis Completed",
            data=pipeline_result
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report Pipeline Error: {str(e)}")