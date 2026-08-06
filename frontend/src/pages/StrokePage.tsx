import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import toast from "react-hot-toast";
import PageHeading from "../components/PageHeading";
import Card from "../components/Card";
import FormField from "../components/FormField";
import { strokeSchema } from "../utils/validation";
import { predictStroke } from "../api/stroke";
import type { StrokeFormValues } from "../types/form";
import { type StrokePredictionResponse } from "../types/api";

export default function StrokePage() {
  const [result, setResult] = useState<StrokePredictionResponse | null>(null);
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<StrokeFormValues>({
    resolver: zodResolver(strokeSchema),
  });

  const onSubmit = async (values: StrokeFormValues) => {
    try {
      const prediction = await predictStroke(values);
      setResult(prediction);
      toast.success("Stroke risk prediction completed.");
    } catch (error) {
      toast.error("Prediction failed. Check inputs or backend status.");
    }
  };

  return (
    <div className="space-y-10">
      <PageHeading title="Stroke Risk" description="Evaluate stroke risk using clinical inputs and AI recommendations." />
      <div className="grid gap-6 xl:grid-cols-2">
        <Card title="Stroke prediction">
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
            <FormField label="Patient name" placeholder="John Doe" register={register("name")} error={errors.name} />
            <FormField label="Age" type="number" placeholder="67" register={register("age")} error={errors.age} />
            <FormField label="Hypertension (0/1)" type="number" placeholder="1" register={register("hypertension")} error={errors.hypertension} />
            <FormField label="Heart disease (0/1)" type="number" placeholder="1" register={register("heart_disease")} error={errors.heart_disease} />
            <FormField label="Avg glucose level" type="number" placeholder="228.69" register={register("avg_glucose_level")} error={errors.avg_glucose_level} />
            <FormField label="BMI" type="number" placeholder="36.6" register={register("bmi")} error={errors.bmi} />
            <FormField label="Smoking status" placeholder="formerly smoked" register={register("smoking_status")} error={errors.smoking_status} />
            <button type="submit" disabled={isSubmitting} className="rounded-2xl bg-brand-600 px-4 py-3 text-sm font-semibold text-white transition hover:bg-brand-700 disabled:cursor-not-allowed disabled:bg-slate-300">
              {isSubmitting ? "Predicting..." : "Run prediction"}
            </button>
            <button type="button" onClick={() => { reset(); setResult(null); }} className="rounded-2xl border border-slate-200 bg-slate-100 px-4 py-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-200">
              Reset form
            </button>
          </form>
        </Card>

        <Card title="Prediction results">
          {result ? (
            <div className="space-y-4 text-sm text-slate-700">
              <p><span className="font-semibold">Disease:</span> {result.disease}</p>
              <p><span className="font-semibold">Prediction:</span> {result.prediction}</p>
              <p><span className="font-semibold">Probability:</span> {result.probability.toFixed(2)}</p>
              <p><span className="font-semibold">Confidence:</span> {result.confidence.toFixed(2)} ({result.confidence_label})</p>
              <div>
                <h3 className="font-semibold">Recommendations</h3>
                {result.recommendations?.length ? (
                  <ul className="list-disc space-y-2 pl-5 text-slate-600">
                    {result.recommendations.map((item, index) => (
                      <li key={index}>{typeof item === "string" ? item : item.recommendation || JSON.stringify(item)}</li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-slate-500">No recommendations returned.</p>
                )}
              </div>
            </div>
          ) : (
            <p className="text-sm text-slate-500">Run a stroke prediction to see the result summary.</p>
          )}
        </Card>
      </div>
    </div>
  );
}
