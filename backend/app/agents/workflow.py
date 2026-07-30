from typing import TypedDict, Dict, Any, List, Optional
from langgraph.graph import StateGraph, END
from app.services.ocr_service import process_medical_report

# 1. Define the Shared State Schema
class MediGenieState(TypedDict):
    patient_context: Dict[str, Any]
    report_file_path: Optional[str]        # Added for OCR Input
    extracted_report_data: Optional[str]   # Added for OCR Output
    raw_report_text: str
    disease_risk_output: Dict[str, Any]
    drug_safety_output: Dict[str, Any]
    rag_output: Dict[str, Any]
    cdss_summary: Dict[str, Any]
    final_output: Dict[str, Any]


# 2. Define Node Execution Functions

def patient_intake_node(state: MediGenieState) -> Dict[str, Any]:
    """Node 1: Validates and structures patient context."""
    return {"patient_context": state.get("patient_context", {})}


def report_analysis_node(state: MediGenieState) -> Dict[str, Any]:
    """Node 2: Runs OCR extraction pipeline on uploaded reports/images."""
    report_file_path = state.get("report_file_path")
    
    if report_file_path:
        try:
            extracted_text = process_medical_report(report_file_path)
            print(f"OCR Successful: {len(extracted_text)} characters extracted.")
            return {
                "extracted_report_data": extracted_text,
                "raw_report_text": extracted_text  # Keeps raw_report_text in sync
            }
        except Exception as e:
            print(f"[OCR Error]: {e}")
            return {
                "extracted_report_data": "Error processing report.",
                "raw_report_text": ""
            }
    else:
        print("No report file provided. Skipping OCR.")
        return {
            "extracted_report_data": "No report uploaded.",
            "raw_report_text": state.get("raw_report_text", "")
        }


def disease_risk_node(state: MediGenieState) -> Dict[str, Any]:
    """Node 3: Executes Phase 9 ML Disease Risk Scoring."""
    from app.core.risk_assessment import evaluate_disease_risk
    ctx = state.get("patient_context", {})
    metrics = {
        "glucose": ctx.get("glucose", 100.0),
        "bmi": ctx.get("bmi", 24.0),
        "age": ctx.get("age", 40),
        "systolic_bp": ctx.get("systolic_bp", 120.0)
    }
    risk_res = evaluate_disease_risk(metrics)
    return {"disease_risk_output": risk_res}


def drug_safety_node(state: MediGenieState) -> Dict[str, Any]:
    """Node 4: Executes Phase 11 Rule-Based DDI & Allergy Check."""
    from app.core.drug_safety import analyze_drug_safety
    ctx = state.get("patient_context", {})
    safety_res = analyze_drug_safety(
        medications=ctx.get("current_medications", []),
        patient_allergies=ctx.get("allergies", [])
    )
    return {"drug_safety_output": safety_res}


def rag_knowledge_node(state: MediGenieState) -> Dict[str, Any]:
    """Node 5: Executes Phase 10 Guidelines Search safely."""
    text = state.get("raw_report_text", "")
    rag_res = []
    
    try:
        import app.core.rag as rag_module
        if hasattr(rag_module, "query_guidelines"):
            rag_res = rag_module.query_guidelines(text)
        elif hasattr(rag_module, "query_rag"):
            rag_res = rag_module.query_rag(text)
        elif hasattr(rag_module, "search_medical_guidelines"):
            rag_res = rag_module.search_medical_guidelines(text)
        elif hasattr(rag_module, "retrieve_guidelines"):
            rag_res = rag_module.retrieve_guidelines(text)
    except Exception as e:
        print(f"[RAG Node Warning] Knowledge retrieval skipped: {e}")
        rag_res = []

    return {"rag_output": {"retrieved_evidence_used": rag_res}}


def cdss_synthesis_node(state: MediGenieState) -> Dict[str, Any]:
    """Node 6: Consolidates outputs into the CDSS Unified Context."""
    from app.core.cdss_aggregator import consolidate_clinical_context
    from app.agents.cdss_engine import run_multi_agent_pipeline
    
    patient_ctx = state.get("patient_context", {})
    raw_text = state.get("raw_report_text", "")
    
    # Run agent LLM reasoning
    agent_llm_res = run_multi_agent_pipeline(patient_ctx, raw_text)
    
    # Consolidate state
    cdss_res = consolidate_clinical_context(
        patient_context=patient_ctx,
        ml_risk_data=state.get("disease_risk_output", {}),
        drug_safety_data=state.get("drug_safety_output", {}),
        rag_data=state.get("rag_output", {})
    )
    
    final_combined = {
        "status": "success",
        "unified_cdss_summary": cdss_res.get("unified_cdss_summary", {}),
        "disease_risk_module": state.get("disease_risk_output"),
        "drug_safety_module": state.get("drug_safety_output"),
        "cdss_agent_output": agent_llm_res
    }
    return {"cdss_summary": cdss_res, "final_output": final_combined}


# 3. Build the LangGraph StateGraph Execution Pipeline
workflow = StateGraph(MediGenieState)

# Add Nodes
workflow.add_node("intake", patient_intake_node)
workflow.add_node("report_analysis", report_analysis_node)  # Added OCR node
workflow.add_node("disease_risk", disease_risk_node)
workflow.add_node("drug_safety", drug_safety_node)
workflow.add_node("rag_knowledge", rag_knowledge_node)
workflow.add_node("cdss_synthesis", cdss_synthesis_node)

# Set Entry Point & Graph Transitions
workflow.set_entry_point("intake")
workflow.add_edge("intake", "report_analysis")
workflow.add_edge("report_analysis", "disease_risk")
workflow.add_edge("disease_risk", "drug_safety")
workflow.add_edge("drug_safety", "rag_knowledge")
workflow.add_edge("rag_knowledge", "cdss_synthesis")
workflow.add_edge("cdss_synthesis", END)

# Compile Executable Graph
medigenie_graph = workflow.compile()