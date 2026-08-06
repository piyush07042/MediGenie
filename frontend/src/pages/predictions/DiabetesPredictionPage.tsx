import PredictionPageShell, { type PredictionField } from "../../components/predictions/PredictionPageShell";
import { diabetesSchema } from "../../utils/predictions";
import { predictDiabetes } from "../../api/predictions";
import type { DiabetesFormValues } from "../../types/form";
import type { DiabetesPredictionResponse } from "../../types/api";

const defaultValues: DiabetesFormValues = {
  age: 55,
  bmi: 32.5,
  glucose: 160,
  systolic_bp: 140,
  insulin: 85,
  name: "",
};

const fields: Array<PredictionField<DiabetesFormValues>> = [
  { name: "age", label: "Age", type: "number", placeholder: "55" },
  { name: "bmi", label: "BMI", type: "number", placeholder: "32.5" },
  { name: "glucose", label: "Glucose", type: "number", placeholder: "160" },
  { name: "systolic_bp", label: "Systolic BP", type: "number", placeholder: "140" },
  { name: "insulin", label: "Insulin", type: "number", placeholder: "85" },
  { name: "name", label: "Patient name", type: "text", placeholder: "Patient" },
];

export default function DiabetesPredictionPage() {
  return (
    <PredictionPageShell<DiabetesFormValues, DiabetesPredictionResponse>
      title="Diabetes Prediction"
      description="Submit diabetes inputs exactly as the backend expects."
      schema={diabetesSchema}
      defaultValues={defaultValues}
      fields={fields}
      predict={predictDiabetes}
      successMessage="Diabetes prediction completed."
    />
  );
}
