"""
Clinical Intelligence Engine
"""
from typing import Any
from app.clinical_intelligence import (
    diabetes,
    heart,
    stroke,
    kidney,
    liver,
    breast,
    parkinsons,
    hepatitis,
    thyroid
)

def generate_clinical_intelligence(disease_key: str, prediction: dict[str, Any], patient: dict[str, Any]) -> dict[str, Any]:
    if not disease_key:
        return {}
    
    key = disease_key.lower()
    
    if "diabet" in key:
        return diabetes.generate_guidance(prediction, patient)
    elif "heart" in key or "cardio" in key:
        return heart.generate_guidance(prediction, patient)
    elif "stroke" in key:
        return stroke.generate_guidance(prediction, patient)
    elif "kidney" in key or "renal" in key:
        return kidney.generate_guidance(prediction, patient)
    elif "liver" in key or "hepatic" in key:
        return liver.generate_guidance(prediction, patient)
    elif "breast" in key:
        return breast.generate_guidance(prediction, patient)
    elif "parkinson" in key:
        return parkinsons.generate_guidance(prediction, patient)
    elif "hepatitis" in key:
        return hepatitis.generate_guidance(prediction, patient)
    elif "thyroid" in key:
        return thyroid.generate_guidance(prediction, patient)
        
    # Default fallback
    return {
        "Guideline": "General Medical Guidelines",
        "Evidence Level": "Level C",
        "Risk Interpretation": "Requires further evaluation.",
        "Clinical Summary": "Undetermined disease specific state.",
        "Recommended Next Steps": ["Comprehensive clinical evaluation"],
        "Lifestyle Advice": ["Healthy diet and regular exercise"],
        "Monitoring Schedule": ["As determined by primary care provider"],
        "Recommended Laboratory Tests": ["CBC", "CMP"],
        "Recommended Imaging (if applicable)": ["As clinically indicated"],
        "Specialist Referral": ["Consider referral based on findings"],
        "Medication Considerations": ["Review current medications"],
        "Possible Complications": ["Unknown"],
        "Preventive Measures": ["Routine health maintenance"],
        "Emergency Warning Signs": ["Standard emergency symptoms (e.g. chest pain, shortness of breath)"],
        "Patient Education": ["General health counseling"],
        "References": ["Standard Clinical Guidelines"]
    }
