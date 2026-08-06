import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import toast from "react-hot-toast";
import PageHeading from "../components/PageHeading";
import Card from "../components/Card";
import FormField from "../components/FormField";
import { drugSafetySchema } from "../utils/validation";
import { analyzeDrugSafety } from "../api/drugSafety";
import type { DrugSafetyFormValues } from "../types/form";

export default function DrugSafetyPage() {
  const [result, setResult] = useState<string | null>(null);
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<DrugSafetyFormValues>({
    resolver: zodResolver(drugSafetySchema),
  });

  const onSubmit = async (data: DrugSafetyFormValues) => {
    try {
      const response = await analyzeDrugSafety({
        medications: data.medications.split(",").map((item) => item.trim()),
        allergies: data.allergies ? data.allergies.split(",").map((item) => item.trim()) : [],
      });
      const value = response.data;
      setResult(typeof value === "string" ? value : JSON.stringify(value, null, 2));
      toast.success("Drug safety analysis complete.");
    } catch (error) {
      toast.error("Unable to analyze medications.");
    }
  };

  return (
    <div className="space-y-10">
      <PageHeading title="Drug Safety" description="Identify medication risk patterns and analyze patient-specific interactions." />
      <div className="grid gap-6 xl:grid-cols-2">
        <Card title="Drug safety analysis">
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
            <FormField label="Medications" placeholder="Aspirin, Metformin" register={register("medications")} error={errors.medications} description="Comma-separated medication list." />
            <FormField label="Allergies" placeholder="Penicillin" register={register("allergies")} error={errors.allergies} description="Comma-separated allergy list." />
            <button type="submit" disabled={isSubmitting} className="rounded-2xl bg-brand-600 px-4 py-3 text-sm font-semibold text-white transition hover:bg-brand-700 disabled:cursor-not-allowed disabled:bg-slate-300">
              {isSubmitting ? "Analyzing..." : "Analyze medications"}
            </button>
          </form>
        </Card>

        <Card title="Assessment result">
          {result ? (
            <p className="text-sm text-slate-700">{result}</p>
          ) : (
            <p className="text-sm text-slate-500">Enter medications to receive a safety assessment from the backend.</p>
          )}
        </Card>
      </div>
    </div>
  );
}
