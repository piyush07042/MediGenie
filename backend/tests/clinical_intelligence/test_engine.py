import pytest
from app.clinical_intelligence.engine import generate_clinical_intelligence

def test_engine_routes_to_diabetes():
    prediction = {"risk_level": "high"}
    patient = {}
    result = generate_clinical_intelligence("diabetes", prediction, patient)
    assert result["Guideline"] == "ADA 2025"

def test_engine_routes_to_heart():
    prediction = {"risk_level": "high"}
    patient = {}
    result = generate_clinical_intelligence("heart_disease", prediction, patient)
    assert result["Guideline"] == "AHA/ACC"

def test_engine_fallback():
    prediction = {"risk_level": "low"}
    patient = {}
    result = generate_clinical_intelligence("unknown_disease", prediction, patient)
    assert result["Guideline"] == "General Medical Guidelines"
