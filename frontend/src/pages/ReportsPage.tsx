import { useEffect, useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import PageHeading from "../components/PageHeading";
import Card from "../components/Card";
import { listPatients } from "../api/patients";
import { getReportHtmlUrl, getReportPdfUrl, listReportTemplates } from "../api/reports";
import type { Patient, ReportTemplateResponse } from "../types/api";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";

export default function ReportsPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const queryPatientIdString = searchParams.get("patientId");
  const queryPatientId = queryPatientIdString ? Number(queryPatientIdString) : NaN;
  const initialPatientId = Number.isInteger(queryPatientId) && queryPatientId > 0 ? queryPatientId : null;
  const [selectedPatientId, setSelectedPatientId] = useState<number | null>(initialPatientId);
  const [selectedTemplate, setSelectedTemplate] = useState<string>("report_template.html");
  const [reportMode, setReportMode] = useState<"html" | "pdf">("html");
  const [filter, setFilter] = useState("");

  const patientsQuery = useQuery({ queryKey: ["patients"], queryFn: listPatients, staleTime: 1000 * 60 * 5 });
  const templatesQuery = useQuery<ReportTemplateResponse>({ queryKey: ["reportTemplates"], queryFn: listReportTemplates, staleTime: 1000 * 60 * 10 });

  const patients = patientsQuery.data?.data ?? [];
  const selectedPatient = useMemo(
    () => patients.find((patient) => patient.id === selectedPatientId) ?? null,
    [patients, selectedPatientId]
  );

  useEffect(() => {
    if (initialPatientId && initialPatientId !== selectedPatientId) {
      setSelectedPatientId(initialPatientId);
    }
  }, [initialPatientId, selectedPatientId]);

  useEffect(() => {
    if (templatesQuery.data?.templates?.length) {
      setSelectedTemplate(templatesQuery.data.templates[0]);
    }
  }, [templatesQuery.data]);

  const filteredPatients = useMemo(() => {
    if (!filter.trim()) return patients;
    const text = filter.toLowerCase();
    return patients.filter((patient) => {
      const fullName = `${patient.first_name} ${patient.last_name}`.toLowerCase();
      return (
        fullName.includes(text) ||
        String(patient.id).includes(text) ||
        patient.gender.toLowerCase().includes(text)
      );
    });
  }, [filter, patients]);

  const reportUrl = useMemo(() => {
    if (!selectedPatientId) return null;
    if (reportMode === "pdf") {
      return `${API_BASE_URL}${getReportPdfUrl(selectedPatientId)}`;
    }
    return `${API_BASE_URL}${getReportHtmlUrl(selectedPatientId, selectedTemplate)}`;
  }, [reportMode, selectedPatientId, selectedTemplate]);

  const handlePatientSelect = (patientId: number) => {
    setSelectedPatientId(patientId);
    setSearchParams({ patientId: String(patientId) });
  };

  return (
    <div className="space-y-10">
      <PageHeading title="AI Report Center" description="Search patients and preview generated clinical reports with a single click." />

      <div className="grid gap-6 xl:grid-cols-[0.9fr_1.4fr]">
        <Card title="Patient reports">
          <div className="space-y-5">
            <div>
              <label htmlFor="patient-search" className="block text-sm font-medium text-slate-700">
                Search patients
              </label>
              <input
                id="patient-search"
                type="search"
                value={filter}
                onChange={(event) => setFilter(event.target.value)}
                placeholder="Search by name, ID, or gender"
                className="mt-2 w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-brand-400 focus:ring-4 focus:ring-brand-100"
              />
            </div>

            {patientsQuery.isLoading ? (
              <div className="space-y-3 py-4">
                {Array.from({ length: 4 }).map((_, index) => (
                  <div key={index} className="h-16 rounded-3xl bg-slate-100" />
                ))}
              </div>
            ) : patients.length === 0 ? (
              <p className="text-sm text-slate-500">No patients found. Add a patient or upload a report to see available reports.</p>
            ) : (
              <div className="space-y-3">
                {filteredPatients.slice(0, 20).map((patient) => (
                  <button
                    key={patient.id}
                    type="button"
                    onClick={() => handlePatientSelect(patient.id)}
                    className={`w-full rounded-3xl border px-4 py-4 text-left transition ${
                      selectedPatientId === patient.id
                        ? "border-brand-500 bg-brand-50"
                        : "border-slate-200 bg-white hover:border-slate-300 hover:bg-slate-50"
                    }`}
                  >
                    <p className="font-semibold text-slate-900">{patient.first_name} {patient.last_name}</p>
                    <p className="mt-2 text-sm text-slate-500">ID {patient.id} · Age {patient.age} · {patient.gender}</p>
                  </button>
                ))}
              </div>
            )}
          </div>
        </Card>

        <div className="space-y-6">
          <Card title="Report preview">
            <div className="grid gap-4 md:grid-cols-[1fr_1fr]">
              <div className="space-y-4">
                <div className="rounded-3xl border border-slate-200 bg-slate-50 p-4">
                  <p className="text-sm text-slate-500">Selected patient</p>
                  {selectedPatient ? (
                    <div className="mt-3 space-y-1 text-sm text-slate-800">
                      <p className="font-semibold text-slate-900">{selectedPatient.first_name} {selectedPatient.last_name}</p>
                      <p>ID {selectedPatient.id}</p>
                      <p>Age {selectedPatient.age} · {selectedPatient.gender}</p>
                    </div>
                  ) : (
                    <p className="mt-3 text-sm text-slate-500">Choose a patient from the list to preview a report.</p>
                  )}
                </div>

                <div className="space-y-3">
                  <div className="flex flex-wrap gap-2">
                    <button
                      type="button"
                      onClick={() => setReportMode("html")}
                      className={`rounded-2xl px-4 py-3 text-sm font-semibold transition ${
                        reportMode === "html" ? "bg-brand-600 text-white" : "border border-slate-200 bg-white text-slate-700 hover:bg-slate-50"
                      }`}
                    >
                      HTML Preview
                    </button>
                    <button
                      type="button"
                      onClick={() => setReportMode("pdf")}
                      className={`rounded-2xl px-4 py-3 text-sm font-semibold transition ${
                        reportMode === "pdf" ? "bg-brand-600 text-white" : "border border-slate-200 bg-white text-slate-700 hover:bg-slate-50"
                      }`}
                    >
                      PDF Preview
                    </button>
                  </div>

                  <div className="grid gap-3 sm:grid-cols-2">
                    <div>
                      <label htmlFor="template" className="block text-sm font-medium text-slate-700">
                        Report template
                      </label>
                      <select
                        id="template"
                        value={selectedTemplate}
                        onChange={(event) => setSelectedTemplate(event.target.value)}
                        className="mt-2 w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-brand-400 focus:ring-4 focus:ring-brand-100"
                        disabled={templatesQuery.isLoading || !templatesQuery.data?.templates?.length}
                      >
                        {templatesQuery.data?.templates?.map((template) => (
                          <option key={template} value={template}>
                            {template}
                          </option>
                        ))}
                      </select>
                    </div>

                    <div className="space-y-2">
                      <p className="text-sm font-medium text-slate-700">Actions</p>
                      <a
                        href={selectedPatientId ? `${API_BASE_URL}${getReportPdfUrl(selectedPatientId)}` : "#"}
                        target="_blank"
                        rel="noreferrer"
                        className={`inline-flex min-w-[160px] items-center justify-center rounded-2xl px-4 py-3 text-sm font-semibold text-white transition ${
                          selectedPatientId ? "bg-brand-600 hover:bg-brand-700" : "bg-slate-300 text-slate-500 cursor-not-allowed"
                        }`}
                        aria-disabled={!selectedPatientId}
                      >
                        Download PDF
                      </a>
                    </div>
                  </div>
                </div>
              </div>

              <div className="rounded-3xl border border-slate-200 bg-slate-950 p-4">
                {reportUrl ? (
                  <iframe
                    src={reportUrl}
                    title="Report viewer"
                    className="h-[520px] w-full rounded-3xl border border-slate-800 bg-white"
                  />
                ) : (
                  <div className="flex h-[520px] flex-col items-center justify-center rounded-3xl border border-dashed border-slate-400 bg-slate-800 p-6 text-center">
                    <p className="mb-3 text-lg font-semibold text-white">Pick a patient to preview the report</p>
                    <p className="max-w-[28rem] text-sm text-slate-300">
                      Reports are generated on the server using the patient&apos;s latest AI summary. If the report fails to load, confirm that the selected patient has a saved AI report.
                    </p>
                  </div>
                )}
              </div>
            </div>
          </Card>

          <Card title="Report notes">
            <p className="text-sm text-slate-500">
              Use this page to review AI-generated clinical notes and export finished reports. For the best experience, upload or analyze a patient record first so the backend can save the corresponding AI summary.
            </p>
          </Card>
        </div>
      </div>
    </div>
  );
}
