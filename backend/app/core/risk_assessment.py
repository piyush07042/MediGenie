import numpy as np
import pandas as pd
import xgboost as xgb

def evaluate_disease_risk(patient_metrics: dict) -> dict:
    """
    Evaluates patient disease risk scores using tabular ML criteria
    and outputs feature contribution (Explainable AI - XAI).
    """
    # Sample extractable numerical metrics
    glucose = patient_metrics.get("glucose", 100)
    bmi = patient_metrics.get("bmi", 24.0)
    age = patient_metrics.get("age", 40)
    systolic_bp = patient_metrics.get("systolic_bp", 120)

    # Simplified rule-weighted feature scoring representing trained model behavior
    risk_score = 0.0
    xai_factors = []

    # Glucose Evaluation
    if glucose >= 126:
        risk_score += 0.4
        xai_factors.append({"feature": "Fasting Glucose", "value": f"{glucose} mg/dL", "impact": "High Risk", "reasoning": "Elevated glucose above 126 mg/dL indicates potential hyperglycemia/diabetes."})
    elif glucose >= 100:
        risk_score += 0.2
        xai_factors.append({"feature": "Fasting Glucose", "value": f"{glucose} mg/dL", "impact": "Moderate Risk", "reasoning": "Glucose between 100-125 mg/dL indicates impaired fasting glucose."})

    # BMI Evaluation
    if bmi >= 30:
        risk_score += 0.25
        xai_factors.append({"feature": "BMI", "value": f"{bmi}", "impact": "High Risk", "reasoning": "BMI >= 30 increases metabolic and cardiovascular risk factors."})

    # Systolic BP Evaluation
    if systolic_bp >= 140:
        risk_score += 0.25
        xai_factors.append({"feature": "Systolic BP", "value": f"{systolic_bp} mmHg", "impact": "High Risk", "reasoning": "Systolic blood pressure >= 140 mmHg indicates Stage 2 Hypertension."})

    # Age Factor
    if age >= 50:
        risk_score += 0.1
        xai_factors.append({"feature": "Age", "value": f"{age}", "impact": "Low-Moderate Risk", "reasoning": "Age >= 50 is a non-modifiable risk contributing factor."})

    # Calculate final risk percentage bounded between 0% and 99%
    final_percentage = min(round(risk_score * 100, 1), 99.0)
    
    risk_category = "Low"
    if final_percentage >= 70:
        risk_category = "High"
    elif final_percentage >= 40:
        risk_category = "Moderate"

    return {
        "disease_risk_assessment": {
            "evaluated_condition": "Metabolic & Cardiovascular Risk Profile",
            "estimated_risk_score_percent": final_percentage,
            "risk_category": risk_category,
            "explainable_ai_factors": xai_factors
        }
    }