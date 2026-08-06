import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import toast from "react-hot-toast";
import PageHeading from "../components/PageHeading";
import Card from "../components/Card";
import FormField from "../components/FormField";
import { patientSchema } from "../utils/validation";
import { createPatient, deletePatient, listPatients, updatePatient } from "../api/patients";
import type { PatientFormValues } from "../types/form";
import type { Patient, ApiResponse } from "../types/api";
import { useQuery, useQueryClient } from "@tanstack/react-query";

type PatientSortKey = "created_at" | "first_name" | "age" | "gender";
const PAGE_SIZE_OPTIONS = [5, 8, 12];

function formatPatientNotes(patient: Patient) {
  if (!patient.medical_history) {
    return "No medical history recorded.";
  }

  if (typeof patient.medical_history === "string") {
    return patient.medical_history;
  }

  if (patient.medical_history.notes) {
    return String(patient.medical_history.notes);
  }

  return JSON.stringify(patient.medical_history, null, 2);
}

export default function PatientsPage() {
  const queryClient = useQueryClient();
  const { data, isLoading } = useQuery<ApiResponse<Patient[]>>({
    queryKey: ["patients"],
    queryFn: listPatients,
    staleTime: 1000 * 60 * 5,
  });

  const [searchTerm, setSearchTerm] = useState("");
  const [genderFilter, setGenderFilter] = useState("all");
  const [sortKey, setSortKey] = useState<PatientSortKey>("created_at");
  const [sortDirection, setSortDirection] = useState<"asc" | "desc">("desc");
  const [pageSize, setPageSize] = useState(PAGE_SIZE_OPTIONS[1]);
  const [currentPage, setCurrentPage] = useState(1);
  const [selectedPatientId, setSelectedPatientId] = useState<number | null>(null);
  const [patientOverrides, setPatientOverrides] = useState<Record<number, Patient>>({});
  const [deletedPatientIds, setDeletedPatientIds] = useState<Set<number>>(new Set());
  const [isEditing, setIsEditing] = useState(false);

  const createForm = useForm<PatientFormValues>({
    resolver: zodResolver(patientSchema),
    defaultValues: {
      gender: "Male",
    },
  });

  const editForm = useForm<PatientFormValues>({
    resolver: zodResolver(patientSchema),
    defaultValues: {
      gender: "Male",
    },
  });

  const patients = data?.data ?? [];

  const mergedPatients = useMemo(() => {
    const active: Patient[] = [];

    patients.forEach((patient) => {
      if (deletedPatientIds.has(patient.id)) {
        return;
      }

      active.push(patientOverrides[patient.id] ?? patient);
    });

    return active;
  }, [patients, patientOverrides, deletedPatientIds]);

  const filteredPatients = useMemo(() => {
    const normalizedSearch = searchTerm.trim().toLowerCase();

    return mergedPatients
      .filter((patient) => {
        const matchesSearch = normalizedSearch
          ? `${patient.first_name} ${patient.last_name}`.toLowerCase().includes(normalizedSearch) ||
            patient.allergies?.join(", ").toLowerCase().includes(normalizedSearch) ||
            patient.current_medications?.join(", ").toLowerCase().includes(normalizedSearch)
          : true;

        const matchesGender = genderFilter === "all" ? true : patient.gender.toLowerCase() === genderFilter.toLowerCase();

        return matchesSearch && matchesGender;
      })
      .sort((a, b) => {
        const direction = sortDirection === "asc" ? 1 : -1;

        if (sortKey === "age") {
          return direction * (a.age - b.age);
        }

        if (sortKey === "created_at") {
          return direction * (new Date(a.created_at).getTime() - new Date(b.created_at).getTime());
        }

        return direction * a[sortKey].toString().localeCompare(b[sortKey].toString(), undefined, { numeric: true });
      });
  }, [mergedPatients, searchTerm, genderFilter, sortKey, sortDirection]);

  const pageCount = Math.max(1, Math.ceil(filteredPatients.length / pageSize));
  const pagedPatients = filteredPatients.slice((currentPage - 1) * pageSize, currentPage * pageSize);

  useEffect(() => {
    if (currentPage > pageCount) {
      setCurrentPage(1);
    }
  }, [currentPage, pageCount]);

  useEffect(() => {
    setCurrentPage(1);
  }, [searchTerm, genderFilter, sortKey, sortDirection, pageSize]);

  useEffect(() => {
    if (!selectedPatientId && filteredPatients.length > 0) {
      setSelectedPatientId(filteredPatients[0].id);
    }

    if (selectedPatientId && !filteredPatients.some((patient) => patient.id === selectedPatientId)) {
      setSelectedPatientId(filteredPatients[0]?.id ?? null);
    }
  }, [filteredPatients, selectedPatientId]);

  useEffect(() => {
    if (!selectedPatientId && filteredPatients.length > 0) {
      setSelectedPatientId(filteredPatients[0].id);
    }
  }, [filteredPatients, selectedPatientId]);

  useEffect(() => {
    if (selectedPatientId && !isEditing) {
      const selectedPatient = filteredPatients.find((patient) => patient.id === selectedPatientId);
      if (selectedPatient) {
        editForm.reset({
          first_name: selectedPatient.first_name,
          last_name: selectedPatient.last_name,
          age: selectedPatient.age,
          gender: selectedPatient.gender,
          allergies: selectedPatient.allergies?.join(", ") ?? "",
          current_medications: selectedPatient.current_medications?.join(", ") ?? "",
          medical_history: selectedPatient.medical_history?.notes ? String(selectedPatient.medical_history.notes) : "",
        });
      }
    }
  }, [selectedPatientId, filteredPatients, editForm, isEditing]);

  const selectedPatient = selectedPatientId ? filteredPatients.find((patient) => patient.id === selectedPatientId) : filteredPatients[0] ?? null;

  const totalPatients = mergedPatients.length;
  const recentlyAddedCount = mergedPatients.filter((patient) => Date.now() - new Date(patient.created_at).getTime() <= 1000 * 60 * 60 * 24 * 30).length;
  const highRiskCount = mergedPatients.filter((patient) => patient.age >= 65).length;

  const recentPatients = useMemo(
    () =>
      [...mergedPatients]
        .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
        .slice(0, 5),
    [mergedPatients]
  );

  const genderOptions = useMemo(
    () => ["all", ...Array.from(new Set(mergedPatients.map((patient) => patient.gender || "Unknown")))],
    [mergedPatients]
  );

  const handleCreatePatient = async (values: PatientFormValues) => {
    try {
      await createPatient({
        first_name: values.first_name,
        last_name: values.last_name,
        age: values.age,
        gender: values.gender,
        allergies: values.allergies ? values.allergies.split(",").map((item) => item.trim()) : [],
        current_medications: values.current_medications ? values.current_medications.split(",").map((item) => item.trim()) : [],
        medical_history: values.medical_history ? { notes: values.medical_history } : {},
      });
      toast.success("Patient record created.");
      createForm.reset({ gender: "Male" });
      queryClient.invalidateQueries({ queryKey: ["patients"] });
    } catch (error) {
      toast.error("Unable to create patient. Please try again.");
    }
  };

  const handleSelectPatient = (patientId: number) => {
    setSelectedPatientId(patientId);
    setIsEditing(false);
  };

  const handleEditPatient = async (values: PatientFormValues) => {
    if (!selectedPatient) {
      return;
    }

    const payload = {
      first_name: values.first_name,
      last_name: values.last_name,
      age: values.age,
      gender: values.gender,
      allergies: values.allergies ? values.allergies.split(",").map((item) => item.trim()) : [],
      current_medications: values.current_medications ? values.current_medications.split(",").map((item) => item.trim()) : [],
      medical_history: values.medical_history ? { notes: values.medical_history } : {},
    };

    try {
      await updatePatient(selectedPatient.id, payload);
      setPatientOverrides((prev) => ({
        ...prev,
        [selectedPatient.id]: {
          ...selectedPatient,
          ...payload,
        },
      }));
      toast.success("Patient updated successfully.");
      setIsEditing(false);
    } catch (error) {
      setPatientOverrides((prev) => ({
        ...prev,
        [selectedPatient.id]: {
          ...selectedPatient,
          ...payload,
        },
      }));
      toast.success("Patient updated locally. Backend update not available yet.");
      setIsEditing(false);
    }
  };

  const handleDeletePatient = async (patientId: number) => {
    if (!window.confirm("Delete this patient record?")) {
      return;
    }

    try {
      await deletePatient(patientId);
      setDeletedPatientIds((prev) => new Set(prev).add(patientId));
      toast.success("Patient deleted successfully.");
      setSelectedPatientId(null);
    } catch (error) {
      setDeletedPatientIds((prev) => new Set(prev).add(patientId));
      toast.success("Patient removed locally. Backend delete not available yet.");
      setSelectedPatientId(null);
    }
  };

  const handleCancelEdit = () => {
    setIsEditing(false);
    if (selectedPatient) {
      editForm.reset({
        first_name: selectedPatient.first_name,
        last_name: selectedPatient.last_name,
        age: selectedPatient.age,
        gender: selectedPatient.gender,
        allergies: selectedPatient.allergies?.join(", ") ?? "",
        current_medications: selectedPatient.current_medications?.join(", ") ?? "",
        medical_history: selectedPatient.medical_history?.notes ? String(selectedPatient.medical_history.notes) : "",
      });
    }
  };

  return (
    <div className="space-y-10">
      <PageHeading title="Patient Management" description="Manage your patient roster, review clinical history, and access reports and predictions." />

      <div className="grid gap-6 xl:grid-cols-[1.4fr_0.95fr]">
        <div className="space-y-6">
          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
            <Card title="Total patients">
              <p className="text-4xl font-semibold text-slate-900">{totalPatients}</p>
              <p className="mt-3 text-sm text-slate-500">Patients under your care.</p>
            </Card>
            <Card title="High-risk patients">
              <p className="text-4xl font-semibold text-slate-900">{highRiskCount}</p>
              <p className="mt-3 text-sm text-slate-500">Age 65+ patients with additional monitoring needs.</p>
            </Card>
            <Card title="Added in 30 days">
              <p className="text-4xl font-semibold text-slate-900">{recentlyAddedCount}</p>
              <p className="mt-3 text-sm text-slate-500">Patients registered in the last 30 days.</p>
            </Card>
          </div>

          <Card title="Patient list">
            <div className="space-y-5">
              <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-[1.5fr_1fr_1fr]">
                <label className="block">
                  <span className="mb-2 block text-sm font-medium text-slate-700">Search</span>
                  <input
                    value={searchTerm}
                    onChange={(event) => setSearchTerm(event.target.value)}
                    placeholder="Name, allergy, medication"
                    className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-brand-400 focus:ring-4 focus:ring-brand-100"
                  />
                </label>
                <label className="block">
                  <span className="mb-2 block text-sm font-medium text-slate-700">Gender</span>
                  <select
                    value={genderFilter}
                    onChange={(event) => setGenderFilter(event.target.value)}
                    className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-brand-400 focus:ring-4 focus:ring-brand-100"
                  >
                    {genderOptions.map((gender) => (
                      <option key={gender} value={gender === "all" ? "all" : gender}>
                        {gender === "all" ? "All genders" : gender}
                      </option>
                    ))}
                  </select>
                </label>
                <label className="block">
                  <span className="mb-2 block text-sm font-medium text-slate-700">Sort</span>
                  <select
                    value={`${sortKey}_${sortDirection}`}
                    onChange={(event) => {
                      const [key, direction] = event.target.value.split("_") as [PatientSortKey, "asc" | "desc"];
                      setSortKey(key);
                      setSortDirection(direction);
                    }}
                    className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-brand-400 focus:ring-4 focus:ring-brand-100"
                  >
                    <option value="created_at_desc">Newest first</option>
                    <option value="created_at_asc">Oldest first</option>
                    <option value="first_name_asc">Name A–Z</option>
                    <option value="first_name_desc">Name Z–A</option>
                    <option value="age_desc">Age high to low</option>
                    <option value="age_asc">Age low to high</option>
                  </select>
                </label>
              </div>

              <div className="overflow-hidden rounded-3xl border border-slate-200">
                <table className="min-w-full border-collapse text-left text-sm text-slate-700">
                  <thead className="bg-slate-50 text-slate-500">
                    <tr>
                      <th className="px-4 py-4 font-medium">Patient</th>
                      <th className="px-4 py-4 font-medium">Age</th>
                      <th className="px-4 py-4 font-medium">Gender</th>
                      <th className="px-4 py-4 font-medium">Allergies</th>
                      <th className="px-4 py-4 font-medium">Created</th>
                      <th className="px-4 py-4 font-medium">Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {isLoading ? (
                      <tr>
                        <td colSpan={6} className="px-4 py-6 text-sm text-slate-500">
                          Loading patients...
                        </td>
                      </tr>
                    ) : pagedPatients.length ? (
                      pagedPatients.map((patient) => (
                        <tr
                          key={patient.id}
                          onClick={() => handleSelectPatient(patient.id)}
                          className={`cursor-pointer transition hover:bg-slate-50 ${selectedPatientId === patient.id ? "bg-slate-100" : ""}`}
                        >
                          <td className="px-4 py-4 font-semibold text-slate-900">
                            {patient.first_name} {patient.last_name}
                          </td>
                          <td className="px-4 py-4">{patient.age}</td>
                          <td className="px-4 py-4">{patient.gender}</td>
                          <td className="px-4 py-4">{patient.allergies?.join(", ") || "None"}</td>
                          <td className="px-4 py-4">{new Date(patient.created_at).toLocaleDateString()}</td>
                          <td className="px-4 py-4">
                            <button
                              type="button"
                              onClick={(event) => {
                                event.stopPropagation();
                                handleSelectPatient(patient.id);
                              }}
                              className="rounded-full border border-slate-200 bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-600 transition hover:bg-slate-200"
                            >
                              View
                            </button>
                          </td>
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td colSpan={6} className="px-4 py-6 text-sm text-slate-500">
                          No patients match the current filters.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>

              <div className="flex flex-col gap-4 border-t border-slate-200 px-4 py-4 sm:flex-row sm:items-center sm:justify-between">
                <p className="text-sm text-slate-500">
                  Showing {pagedPatients.length} of {filteredPatients.length} patients.
                </p>
                <div className="flex flex-wrap items-center gap-2">
                  <button
                    type="button"
                    disabled={currentPage <= 1}
                    onClick={() => setCurrentPage((value) => Math.max(1, value - 1))}
                    className="rounded-2xl border border-slate-200 bg-white px-4 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    Previous
                  </button>
                  <button
                    type="button"
                    disabled={currentPage >= pageCount}
                    onClick={() => setCurrentPage((value) => Math.min(pageCount, value + 1))}
                    className="rounded-2xl border border-slate-200 bg-white px-4 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    Next
                  </button>
                  <select
                    value={pageSize}
                    onChange={(event) => setPageSize(Number(event.target.value))}
                    className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-2 text-sm text-slate-900 outline-none transition focus:border-brand-400 focus:ring-4 focus:ring-brand-100"
                  >
                    {PAGE_SIZE_OPTIONS.map((size) => (
                      <option key={size} value={size}>
                        {size} per page
                      </option>
                    ))}
                  </select>
                </div>
              </div>
            </div>
          </Card>

          <Card title="Recent patient activity">
            <div className="space-y-4">
              {recentPatients.length ? (
                recentPatients.map((patient) => (
                  <div key={patient.id} className="rounded-3xl bg-slate-50 px-4 py-4">
                    <p className="font-semibold text-slate-900">{patient.first_name} {patient.last_name}</p>
                    <p className="text-sm text-slate-500">Added {new Date(patient.created_at).toLocaleDateString()}</p>
                  </div>
                ))
              ) : (
                <p className="text-sm text-slate-500">No recent activity yet.</p>
              )}
            </div>
          </Card>
        </div>

        <div className="space-y-6">
          <Card title="Add patient">
            <form onSubmit={createForm.handleSubmit(handleCreatePatient)} className="space-y-5">
              <FormField label="First name" placeholder="Jane" register={createForm.register("first_name")} error={createForm.formState.errors.first_name} />
              <FormField label="Last name" placeholder="Doe" register={createForm.register("last_name")} error={createForm.formState.errors.last_name} />
              <div className="grid gap-5 sm:grid-cols-2">
                <FormField label="Age" type="number" placeholder="42" register={createForm.register("age")} error={createForm.formState.errors.age} />
                <FormField label="Gender" placeholder="Female" register={createForm.register("gender")} error={createForm.formState.errors.gender} />
              </div>
              <FormField label="Allergies" placeholder="Peanuts, Penicillin" register={createForm.register("allergies")} error={createForm.formState.errors.allergies} />
              <FormField label="Current medications" placeholder="Aspirin, Metformin" register={createForm.register("current_medications")} error={createForm.formState.errors.current_medications} />
              <FormField label="Medical history" placeholder="Type patient history" register={createForm.register("medical_history")} error={createForm.formState.errors.medical_history}>
                <textarea
                  rows={4}
                  {...createForm.register("medical_history")}
                  className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-brand-400 focus:ring-4 focus:ring-brand-100"
                />
              </FormField>
              <button
                type="submit"
                disabled={createForm.formState.isSubmitting}
                className="rounded-2xl bg-brand-600 px-4 py-3 text-sm font-semibold text-white transition hover:bg-brand-700 disabled:cursor-not-allowed disabled:bg-slate-300"
              >
                {createForm.formState.isSubmitting ? "Saving..." : "Save patient"}
              </button>
            </form>
          </Card>

          <Card title="Patient details">
            {selectedPatient ? (
              <div className="space-y-5">
                {!isEditing ? (
                  <div className="space-y-5">
                    <div className="rounded-3xl bg-slate-50 p-5">
                      <p className="text-lg font-semibold text-slate-900">{selectedPatient.first_name} {selectedPatient.last_name}</p>
                      <p className="text-sm text-slate-500">Age {selectedPatient.age} • {selectedPatient.gender}</p>
                      <p className="mt-4 text-sm leading-7 text-slate-700">{formatPatientNotes(selectedPatient)}</p>
                    </div>

                    <div className="grid gap-3 sm:grid-cols-2">
                      <div className="rounded-3xl bg-slate-50 p-5">
                        <p className="text-sm uppercase tracking-[0.24em] text-slate-400">Allergies</p>
                        <p className="mt-3 text-sm text-slate-700">{selectedPatient.allergies?.join(", ") || "None recorded"}</p>
                      </div>
                      <div className="rounded-3xl bg-slate-50 p-5">
                        <p className="text-sm uppercase tracking-[0.24em] text-slate-400">Medications</p>
                        <p className="mt-3 text-sm text-slate-700">{selectedPatient.current_medications?.join(", ") || "No active medications"}</p>
                      </div>
                    </div>

                    <div className="grid gap-3 sm:grid-cols-2">
                      <div className="rounded-3xl bg-slate-50 p-5">
                        <p className="text-sm uppercase tracking-[0.24em] text-slate-400">Created</p>
                        <p className="mt-3 text-sm text-slate-700">{new Date(selectedPatient.created_at).toLocaleString()}</p>
                      </div>
                      <div className="rounded-3xl bg-slate-50 p-5">
                        <p className="text-sm uppercase tracking-[0.24em] text-slate-400">Doctor ID</p>
                        <p className="mt-3 text-sm text-slate-700">{selectedPatient.doctor_id}</p>
                      </div>
                    </div>

                    <div className="grid gap-3 sm:grid-cols-2">
                      <Link
                        to={`/reports?patientId=${selectedPatient.id}`}
                        className="inline-flex items-center justify-center rounded-2xl border border-brand-500 bg-brand-50 px-4 py-3 text-sm font-semibold text-brand-700 transition hover:bg-brand-100"
                      >
                        View AI reports
                      </Link>
                      <Link
                        to={`/stroke?patientId=${selectedPatient.id}`}
                        className="inline-flex items-center justify-center rounded-2xl bg-brand-600 px-4 py-3 text-sm font-semibold text-white transition hover:bg-brand-700"
                      >
                        Run prediction
                      </Link>
                    </div>

                    <div className="flex flex-wrap gap-3">
                      <button
                        type="button"
                        onClick={() => setIsEditing(true)}
                        className="rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-50"
                      >
                        Edit record
                      </button>
                      <button
                        type="button"
                        onClick={() => handleDeletePatient(selectedPatient.id)}
                        className="rounded-2xl bg-red-600 px-4 py-3 text-sm font-semibold text-white transition hover:bg-red-700"
                      >
                        Delete patient
                      </button>
                    </div>

                    <div className="rounded-3xl border border-amber-100 bg-amber-50 px-4 py-4 text-sm text-amber-700">
                      Note: Edit and delete are applied locally when backend endpoints are unavailable.
                    </div>
                  </div>
                ) : (
                  <form onSubmit={editForm.handleSubmit(handleEditPatient)} className="space-y-5">
                    <FormField label="First name" placeholder="Jane" register={editForm.register("first_name")} error={editForm.formState.errors.first_name} />
                    <FormField label="Last name" placeholder="Doe" register={editForm.register("last_name")} error={editForm.formState.errors.last_name} />
                    <div className="grid gap-5 sm:grid-cols-2">
                      <FormField label="Age" type="number" placeholder="42" register={editForm.register("age")} error={editForm.formState.errors.age} />
                      <FormField label="Gender" placeholder="Female" register={editForm.register("gender")} error={editForm.formState.errors.gender} />
                    </div>
                    <FormField label="Allergies" placeholder="Peanuts, Penicillin" register={editForm.register("allergies")} error={editForm.formState.errors.allergies} />
                    <FormField label="Current medications" placeholder="Aspirin, Metformin" register={editForm.register("current_medications")} error={editForm.formState.errors.current_medications} />
                    <FormField label="Medical history" placeholder="Type patient history" register={editForm.register("medical_history")} error={editForm.formState.errors.medical_history}>
                      <textarea
                        rows={4}
                        {...editForm.register("medical_history")}
                        className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-brand-400 focus:ring-4 focus:ring-brand-100"
                      />
                    </FormField>
                    <div className="flex flex-wrap gap-3">
                      <button
                        type="submit"
                        className="rounded-2xl bg-brand-600 px-4 py-3 text-sm font-semibold text-white transition hover:bg-brand-700"
                      >
                        Save changes
                      </button>
                      <button
                        type="button"
                        onClick={handleCancelEdit}
                        className="rounded-2xl border border-slate-200 bg-slate-100 px-4 py-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-200"
                      >
                        Cancel
                      </button>
                    </div>
                  </form>
                )}
              </div>
            ) : (
              <p className="text-sm text-slate-500">Select a patient from the list to view details.</p>
            )}
          </Card>
        </div>
      </div>
    </div>
  );
}
