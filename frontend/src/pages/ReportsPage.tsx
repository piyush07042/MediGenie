import { useState } from "react";
import PageHeading from "../components/PageHeading";
import Card from "../components/Card";

export default function ReportsPage() {
  const [patientId, setPatientId] = useState(0);
  const [reportUrl, setReportUrl] = useState<string | null>(null);

  const handleViewPdf = () => {
    if (!patientId) return;
    setReportUrl(`${import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1"}/reports/${patientId}/pdf`);
  };

  const handleViewHtml = () => {
    if (!patientId) return;
    setReportUrl(`${import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1"}/reports/${patientId}/html`);
  };

  return (
    <div className="space-y-10">
      <PageHeading title="Clinical Reports" description="Preview generated clinical reports for your patients." />
      <div className="grid gap-6 xl:grid-cols-2">
        <Card title="Report actions">
          <div className="space-y-5">
            <label className="block text-sm font-medium text-slate-700">Patient ID</label>
            <input
              type="number"
              value={patientId || ""}
              onChange={(event) => setPatientId(Number(event.target.value))}
              className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-brand-400 focus:ring-4 focus:ring-brand-100"
              placeholder="Enter a patient ID"
            />
            <button onClick={handleViewPdf} className="w-full rounded-2xl bg-brand-600 px-4 py-3 text-sm font-semibold text-white transition hover:bg-brand-700">
              View PDF report
            </button>
            <button onClick={handleViewHtml} className="w-full rounded-2xl border border-slate-200 bg-slate-100 px-4 py-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-200">
              View HTML report
            </button>
          </div>
        </Card>

        <Card title="Report preview">
          {reportUrl ? (
            <iframe src={reportUrl} className="h-[520px] w-full rounded-3xl border border-slate-200" title="Report preview" />
          ) : (
            <p className="text-sm text-slate-500">Select a patient ID and choose a report type to preview.</p>
          )}
        </Card>
      </div>
    </div>
  );
}
