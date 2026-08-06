import { useEffect, useMemo, useState } from "react";
import { zodResolver } from "@hookform/resolvers/zod";
import { type DefaultValues, type FieldValues, useForm } from "react-hook-form";
import toast from "react-hot-toast";
import PageHeading from "../../components/PageHeading";
import Card from "../../components/Card";
import PredictionForm from "./PredictionForm";
import PredictionPanel from "./PredictionPanel";
import PredictionResultView from "./PredictionResultView";
import PredictionHistory from "./PredictionHistory";
import { usePredictionContext } from "../../hooks/usePredictionContext";
import { addPredictionHistory, getPredictionHistory } from "../../utils/predictionHistory";
import { buildPredictionFormValues } from "../../utils/predictionPrefill";
import type { PredictionHistoryItem } from "../../utils/predictionHistory";
import type { Patient } from "../../types/api";
import type { ZodType } from "zod";

export type PredictionField<TValues extends FieldValues> = {
  name: keyof TValues;
  label: string;
  placeholder?: string;
  type?: "text" | "number";
};

type PredictionPageShellProps<TValues extends FieldValues, TResponse extends Record<string, any>> = {
  title: string;
  description: string;
  schema: ZodType<TValues, any>;
  defaultValues: TValues;
  fields: Array<PredictionField<TValues>>;
  predict: (payload: TValues) => Promise<TResponse>;
  successMessage?: string;
  submitLabel?: string;
};

export default function PredictionPageShell<
  TValues extends Record<string, any>,
  TResponse extends Record<string, any>,
>({
  title,
  description,
  schema,
  defaultValues,
  fields,
  predict,
  successMessage,
  submitLabel = "Run prediction",
}: PredictionPageShellProps<TValues, TResponse>) {
  const { patientId, patient, patientContext, extractedMetrics } = usePredictionContext();
  const [result, setResult] = useState<TResponse | null>(null);
  const [history, setHistory] = useState<PredictionHistoryItem[]>([]);
  const [prefillApplied, setPrefillApplied] = useState(false);

  const currentPatient = useMemo<Patient | null>(() => {
    if (patient) return patient;
    if (!patientContext) return null;
    return {
      id: Number(patientContext.id ?? -1),
      doctor_id: Number(patientContext.doctor_id ?? 0),
      first_name: String(patientContext.first_name ?? patientContext.name ?? "Patient"),
      last_name: String(patientContext.last_name ?? ""),
      age: Number(patientContext.age ?? 0),
      gender: String(patientContext.gender ?? "Unknown"),
      medical_history: patientContext.medical_history,
      allergies: Array.isArray(patientContext.allergies) ? patientContext.allergies : [],
      current_medications: Array.isArray(patientContext.current_medications) ? patientContext.current_medications : [],
      created_at: String(patientContext.created_at ?? new Date().toISOString()),
    };
  }, [patient, patientContext]);

  const prefillValues = useMemo(() => {
    return buildPredictionFormValues(defaultValues, extractedMetrics, patientContext);
  }, [defaultValues, extractedMetrics, patientContext]);

  const { register, handleSubmit, reset, formState } = useForm<TValues>({
    defaultValues: prefillValues as DefaultValues<TValues>,
    resolver: zodResolver(schema),
  });

  useEffect(() => {
    if (!prefillApplied && (Object.keys(extractedMetrics ?? {}).length > 0 || patientContext)) {
      reset(prefillValues);
      setPrefillApplied(true);
    }
  }, [prefillApplied, extractedMetrics, patientContext, prefillValues, reset]);

  useEffect(() => {
    if (patientId) {
      setHistory(getPredictionHistory(patientId));
    } else {
      setHistory([]);
    }
  }, [patientId]);

  const onSubmit = async (values: TValues) => {
    try {
      const prediction = await predict(values);
      setResult(prediction);
      toast.success(successMessage ?? `${title} completed.`);

      if (patientId) {
        const summary = Array.isArray(prediction.recommendations)
          ? prediction.recommendations.slice(0, 2).map((item) => (typeof item === "string" ? item : item.recommendation || JSON.stringify(item))).join("; ")
          : undefined;

        const historyItem: PredictionHistoryItem = {
          id: `${patientId}-${title}-${Date.now()}`,
          patientId,
          disease: prediction.disease ?? title,
          createdAt: new Date().toISOString(),
          prediction: prediction.prediction ?? "unknown",
          probability: typeof prediction.probability === "number" ? prediction.probability : Number(prediction.probability) || 0,
          confidence: typeof prediction.confidence === "number" ? prediction.confidence : Number(prediction.confidence) || 0,
          confidenceLabel: prediction.confidence_label ?? null,
          summary,
          result: prediction,
        };

        addPredictionHistory(historyItem);
        setHistory((current) => [historyItem, ...current]);
      }
    } catch (error) {
      toast.error("Prediction failed. Check inputs or backend status.");
    }
  };

  const onReset = () => {
    reset(defaultValues);
    setResult(null);
  };

  return (
    <div className="space-y-10">
      <PageHeading title={title} description={description} />

      <div className="grid gap-6 xl:grid-cols-[1.4fr_0.9fr]">
        <Card title="Model inputs">
          <PredictionForm handleSubmit={handleSubmit} onSubmit={onSubmit} isSubmitting={formState.isSubmitting} onReset={onReset} submitLabel={submitLabel}>
            <div className="grid gap-5">
              {fields.map((field) => (
                <div key={String(field.name)}>
                  <label className="block text-sm font-medium text-slate-700">{field.label}</label>
                  <input
                    type={field.type ?? "text"}
                    placeholder={field.placeholder}
                    {...register(field.name as any)}
                    className="mt-2 block w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 shadow-sm outline-none transition focus:border-brand-500 focus:ring-2 focus:ring-brand-100"
                  />
                </div>
              ))}
            </div>
          </PredictionForm>
        </Card>

        <div className="space-y-6">
          <PredictionPanel title="Patient context">
            {currentPatient ? (
              <div className="space-y-3 text-sm text-slate-700">
                <p className="text-base font-semibold text-slate-900">{currentPatient.first_name} {currentPatient.last_name}</p>
                <p>Age: {currentPatient.age}</p>
                <p>Gender: {currentPatient.gender}</p>
                <p>Allergies: {currentPatient.allergies?.join(", ") || "None"}</p>
                <p>Medications: {currentPatient.current_medications?.join(", ") || "None"}</p>
                <p className="text-slate-500">Created: {new Date(currentPatient.created_at).toLocaleString()}</p>
              </div>
            ) : (
              <p className="text-sm text-slate-500">No saved patient context is available. Use report upload or add a patient ID to your URL.</p>
            )}
          </PredictionPanel>

          <PredictionPanel title="Previous predictions">
            <PredictionHistory history={history} />
          </PredictionPanel>

          {Object.keys(extractedMetrics ?? {}).length > 0 ? (
            <PredictionPanel title="OCR extracted metrics">
              <pre className="max-h-[280px] overflow-auto rounded-3xl bg-slate-950 p-4 text-sm text-slate-100">
                {JSON.stringify(extractedMetrics, null, 2)}
              </pre>
            </PredictionPanel>
          ) : null}
        </div>
      </div>

      <PredictionPanel title="Prediction result">
        {result ? (
          <PredictionResultView result={result} patient={patient} timestamp={new Date().toLocaleString()} onNewPrediction={onReset} />
        ) : (
          <p className="text-sm text-slate-500">Submit the form to run a prediction and view the model result, recommendations, and report output here.</p>
        )}
      </PredictionPanel>
    </div>
  );
}
