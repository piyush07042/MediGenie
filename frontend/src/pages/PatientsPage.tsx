import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import toast from "react-hot-toast";
import PageHeading from "../components/PageHeading";
import Card from "../components/Card";
import FormField from "../components/FormField";
import { patientSchema } from "../utils/validation";
import { createPatient, listPatients } from "../api/patients";
import type { PatientFormValues } from "../types/form";
import { useAuthStore } from "../store/authStore";
import { type Patient, type ApiResponse } from "../types/api";
import { useQuery, useQueryClient } from "@tanstack/react-query";

export default function PatientsPage() {
  const queryClient = useQueryClient();
  const { data, isLoading } = useQuery<ApiResponse<Patient[]>>({
    queryKey: ["patients"],
    queryFn: listPatients,
  });
  const setUser = useAuthStore((state) => state.setUser);

  useEffect(() => {
    if (!data?.data?.length) return;
    if (!useAuthStore.getState().user) {
      const doctorPatient = data.data[0];
      if (doctorPatient?.doctor_id) {
        setUser({
          id: doctorPatient.doctor_id,
          email: "",
          full_name: "",
          role: "Doctor",
          created_at: new Date().toISOString(),
        });
      }
    }
  }, [data, setUser]);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<PatientFormValues>({
    resolver: zodResolver(patientSchema),
    defaultValues: {
      gender: "Male",
    },
  });

  const onSubmit = async (formValues: PatientFormValues) => {
    try {
      await createPatient({
        first_name: formValues.first_name,
        last_name: formValues.last_name,
        age: formValues.age,
        gender: formValues.gender,
        allergies: formValues.allergies ? formValues.allergies.split(",").map((item) => item.trim()) : [],
        current_medications: formValues.current_medications ? formValues.current_medications.split(",").map((item) => item.trim()) : [],
        medical_history: formValues.medical_history ? { notes: formValues.medical_history } : {},
      });
      toast.success("Patient record created.");
      reset();
      queryClient.invalidateQueries({ queryKey: ["patients"] });
    } catch (error) {
      toast.error("Unable to create patient. Please try again.");
    }
  };

  return (
    <div className="space-y-10">
      <PageHeading title="Patients" description="Register new patients and review your current patient list." />
      <div className="grid gap-6 lg:grid-cols-2">
        <Card title="Create patient">
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
            <FormField label="First name" placeholder="Jane" register={register("first_name")} error={errors.first_name} />
            <FormField label="Last name" placeholder="Doe" register={register("last_name")} error={errors.last_name} />
            <div className="grid gap-5 sm:grid-cols-2">
              <FormField label="Age" type="number" placeholder="42" register={register("age")} error={errors.age} />
              <FormField label="Gender" placeholder="Female" register={register("gender")} error={errors.gender} />
            </div>
            <FormField label="Allergies" placeholder="Peanuts, Penicillin" register={register("allergies")} error={errors.allergies} />
            <FormField label="Current medications" placeholder="Aspirin, Metformin" register={register("current_medications")} error={errors.current_medications} />
            <FormField label="Medical history" placeholder="Type patient history" register={register("medical_history")} error={errors.medical_history}>
              <textarea
                rows={4}
                {...register("medical_history")}
                className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-brand-400 focus:ring-4 focus:ring-brand-100"
              />
            </FormField>
            <button type="submit" disabled={isSubmitting} className="rounded-2xl bg-brand-600 px-4 py-3 text-sm font-semibold text-white transition hover:bg-brand-700 disabled:cursor-not-allowed disabled:bg-slate-300">
              {isSubmitting ? "Saving..." : "Save patient"}
            </button>
          </form>
        </Card>

        <Card title="Patient list">
          {isLoading ? (
            <p className="text-sm text-slate-500">Loading patients...</p>
          ) : (
            <div className="space-y-3">
              {data?.data?.length ? (
                data.data.map((patient: Patient) => (
                  <div key={patient.id} className="rounded-3xl border border-slate-200 bg-slate-50 p-4">
                    <p className="font-semibold text-slate-900">{patient.first_name} {patient.last_name}</p>
                    <p className="text-sm text-slate-500">Age {patient.age} • {patient.gender}</p>
                    <p className="text-sm text-slate-500">Allergies: {patient.allergies?.join(", ") || "None"}</p>
                  </div>
                ))
              ) : (
                <p className="text-sm text-slate-500">No patients found yet.</p>
              )}
            </div>
          )}
        </Card>
      </div>
    </div>
  );
}
