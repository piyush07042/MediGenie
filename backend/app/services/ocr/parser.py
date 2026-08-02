import re


def extract_patient_metrics(text: str) -> dict:
    metrics = {
        "patient_id": "PT-UNKNOWN",
        "age": 45,
        "gender": "Female",
        "glucose": 100.0,
        "bmi": 24.5,
        "systolic_bp": 120.0,
        "cholesterol": 190.0,
    }

    if not text:
        return metrics

    pid_match = re.search(
        r"(?:Patient\s*ID|PID|ID)[\s:-]*([A-Z0-9-]+)",
        text,
        re.IGNORECASE,
    )
    if pid_match:
        metrics["patient_id"] = pid_match.group(1).strip()

    age_match = re.search(
        r"(?:Age)[\s:-]*(\d{1,3})",
        text,
        re.IGNORECASE,
    )
    if age_match:
        metrics["age"] = int(age_match.group(1))

    gender_match = re.search(
        r"(?:Gender|Sex)[\s:-]*(Male|Female)",
        text,
        re.IGNORECASE,
    )
    if gender_match:
        metrics["gender"] = gender_match.group(1).capitalize()

    glucose_match = re.search(
        r"(?:Fasting\s*Glucose|Glucose|Blood\s*Sugar)[\s:-]*(\d+(?:\.\d+)?)",
        text,
        re.IGNORECASE,
    )
    if glucose_match:
        metrics["glucose"] = float(glucose_match.group(1))

    bmi_match = re.search(
        r"(?:BMI|Body\s*Mass\s*Index)[\s:-]*(\d+(?:\.\d+)?)",
        text,
        re.IGNORECASE,
    )
    if bmi_match:
        metrics["bmi"] = float(bmi_match.group(1))

    bp_match = re.search(
        r"(?:Systolic\s*BP|Blood\s*Pressure|BP)[\s:-]*(\d{2,3})",
        text,
        re.IGNORECASE,
    )
    if bp_match:
        metrics["systolic_bp"] = float(bp_match.group(1))

    chol_match = re.search(
        r"(?:Cholesterol|Total\s*Cholesterol)[\s:-]*(\d+(?:\.\d+)?)",
        text,
        re.IGNORECASE,
    )
    if chol_match:
        metrics["cholesterol"] = float(chol_match.group(1))

    return metrics


class Parser:
    """
    Backward-compatible wrapper used by MedicalReportAnalysisAgent.
    """

    @staticmethod
    def parse(text: str) -> dict:
        return extract_patient_metrics(text)

    @staticmethod
    def extract(text: str) -> dict:
        return extract_patient_metrics(text)

    @staticmethod
    def extract_patient_metrics(text: str) -> dict:
        return extract_patient_metrics(text)