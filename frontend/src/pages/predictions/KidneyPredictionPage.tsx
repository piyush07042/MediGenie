import PredictionPageShell, { type PredictionField } from "../../components/predictions/PredictionPageShell";
import { kidneyDiseaseSchema } from "../../utils/predictions";
import { predictKidneyDisease } from "../../api/predictions";
import type { KidneyDiseaseFormValues } from "../../types/form";
import type { KidneyDiseasePredictionResponse } from "../../types/api";

const defaultValues: KidneyDiseaseFormValues = {
  age: 55,
  creatinine: 1.2,
  blood_urea: 30.0,
  sgpt: 35.0,
  albumin: 4.2,
  name: "",
};

const fields: Array<PredictionField<KidneyDiseaseFormValues>> = [
  { name: "age", label: "Age", type: "number", placeholder: "55" },
  { name: "creatinine", label: "Serum creatinine", type: "number", placeholder: "1.2" },
  { name: "blood_urea", label: "Blood urea", type: "number", placeholder: "30.0" },
  { name: "sgpt", label: "SGPT / ALT", type: "number", placeholder: "35.0" },
  { name: "albumin", label: "Serum albumin", type: "number", placeholder: "4.2" },
  { name: "name", label: "Patient name", type: "text", placeholder: "Patient" },
];

export default function KidneyPredictionPage() {
  return (
    <PredictionPageShell<KidneyDiseaseFormValues, KidneyDiseasePredictionResponse>
      title="Chronic Kidney Disease Prediction"
      description="Submit kidney disease inputs exactly as the backend expects."
      schema={kidneyDiseaseSchema}
      defaultValues={defaultValues}
      fields={fields}
      predict={predictKidneyDisease}
      successMessage="Kidney disease prediction completed."
    />
  );
}
