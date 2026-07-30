from typing import List, Dict, Any

# Knowledge Base: Common dangerous drug interactions
KNOWN_INTERACTIONS = [
    {
        "pair": {"aspirin", "warfarin"},
        "severity": "High",
        "description": "Concomitant use significantly increases the risk of major bleeding."
    },
    {
        "pair": {"metformin", "contrast_media"},
        "severity": "High",
        "description": "Iodinated contrast media may cause acute renal failure leading to metformin accumulation and lactic acidosis."
    },
    {
        "pair": {"lisinopril", "spironolactone"},
        "severity": "Moderate",
        "description": "Combination increases the risk of severe hyperkalemia (high serum potassium)."
    },
    {
        "pair": {"ciprofloxacin", "theophylline"},
        "severity": "Moderate",
        "description": "Ciprofloxacin can increase serum theophylline levels, raising the risk of toxicity."
    }
]

# Knowledge Base: Drug class allergy mappings
DRUG_ALLERGY_MAP = {
    "penicillin": ["amoxicillin", "ampicillin", "piperacillin", "penicillin_v"],
    "sulfa": ["sulfamethoxazole", "trimethoprim-sulfamethoxazole", "sulfasalazine"],
    "nsaid": ["ibuprofen", "naproxen", "aspirin", "ketorolac"]
}

def analyze_drug_safety(medications: List[str], patient_allergies: List[str]) -> Dict[str, Any]:
    """
    Performs deterministic rule-based checks for drug interactions,
    patient allergy conflicts, and safety cautions.
    """
    meds_clean = [m.strip().lower() for m in medications if m.strip()]
    allergies_clean = [a.strip().lower() for a in patient_allergies if a.strip()]

    safety_alerts = []
    allergy_conflicts = []
    interaction_warnings = []

    # 1. Check Drug-Drug Interactions
    for i in range(len(meds_clean)):
        for j in range(i + 1, len(meds_clean)):
            drug1, drug2 = meds_clean[i], meds_clean[j]
            for interaction in KNOWN_INTERACTIONS:
                if {drug1, drug2} == interaction["pair"]:
                    interaction_warnings.append({
                        "drugs_involved": [drug1.capitalize(), drug2.capitalize()],
                        "severity": interaction["severity"],
                        "warning": interaction["description"]
                    })

    # 2. Check Patient Allergies
    for drug in meds_clean:
        for allergy in allergies_clean:
            # Direct match
            if allergy in drug:
                allergy_conflicts.append({
                    "medication": drug.capitalize(),
                    "allergen_match": allergy.capitalize(),
                    "severity": "Critical",
                    "reasoning": f"Patient has a documented allergy to '{allergy}'."
                })
            # Class match
            elif allergy in DRUG_ALLERGY_MAP:
                if drug in DRUG_ALLERGY_MAP[allergy]:
                    allergy_conflicts.append({
                        "medication": drug.capitalize(),
                        "allergen_match": f"Class: {allergy.capitalize()}",
                        "severity": "Critical",
                        "reasoning": f"Medication belongs to the '{allergy.capitalize()}' family, to which the patient is allergic."
                    })

    # Determine Safety Status
    is_safe = len(allergy_conflicts) == 0 and len(interaction_warnings) == 0

    return {
        "drug_safety_assessment": {
            "status": "PASS" if is_safe else "FLAGGED",
            "medications_checked": [m.capitalize() for m in meds_clean],
            "allergy_conflicts": allergy_conflicts,
            "interaction_warnings": interaction_warnings,
            "recommendation": "Proceed as planned." if is_safe else "Review flagged safety issues before prescribing."
        }
    }