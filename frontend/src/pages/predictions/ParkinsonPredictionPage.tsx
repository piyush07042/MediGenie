import PredictionPageShell, { type PredictionField } from "../../components/predictions/PredictionPageShell";
import { parkinsonsSchema } from "../../utils/predictions";
import { predictParkinsons } from "../../api/predictions";
import type { ParkinsonsFormValues } from "../../types/form";
import type { ParkinsonsPredictionResponse } from "../../types/api";

const defaultValues: ParkinsonsFormValues = {
  age: 60,
  motor_UPDRS: 20.0,
  total_UPDRS: 35.0,
  Jitter_local: 0.005,
  Shimmer_local: 0.02,
  name: "",
};

const fields: Array<PredictionField<ParkinsonsFormValues>> = [
  { name: "age", label: "Age", type: "number", placeholder: "60" },
  { name: "motor_UPDRS", label: "Motor UPDRS", type: "number", placeholder: "20.0" },
  { name: "total_UPDRS", label: "Total UPDRS", type: "number", placeholder: "35.0" },
  { name: "Jitter_local", label: "Jitter local", type: "number", placeholder: "0.005" },
  { name: "Shimmer_local", label: "Shimmer local", type: "number", placeholder: "0.02" },
  { name: "name", label: "Patient name", type: "text", placeholder: "Patient" },
];

export default function ParkinsonPredictionPage() {
  return (
    <PredictionPageShell<ParkinsonsFormValues, ParkinsonsPredictionResponse>
      title="Parkinson's Disease Prediction"
      description="Submit Parkinson's disease inputs exactly as the backend expects."
      schema={parkinsonsSchema}
      defaultValues={defaultValues}
      fields={fields}
      predict={predictParkinsons}
      successMessage="Parkinson's disease prediction completed."
    />
  );
}
