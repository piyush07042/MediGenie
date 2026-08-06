import { FileText } from "lucide-react";
import type { RecentReport } from "../../services/dashboardService";

export default function RecentReports({ data, loading }: { data: RecentReport[]; loading: boolean }) {
  return (
    <section className="rounded-3xl border border-slate-200 bg-white p-6 shadow-soft">
      <div className="mb-5 flex items-center justify-between gap-3">
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.28em] text-slate-400">Recent Reports</p>
          <h2 className="mt-2 text-xl font-semibold text-slate-900">Latest uploads</h2>
        </div>
        <div className="inline-flex h-12 w-12 items-center justify-center rounded-3xl bg-brand-100 text-brand-700">
          <FileText className="h-5 w-5" />
        </div>
      </div>
      {loading ? (
        <div className="space-y-3">
          {Array.from({ length: 3 }).map((_, index) => (
            <div key={index} className="h-14 rounded-3xl bg-slate-100" />
          ))}
        </div>
      ) : (
        <div className="space-y-4">
          {data.map((report) => (
            <div key={report.id} className="rounded-3xl bg-slate-50 px-4 py-4 text-sm text-slate-700">
              <div className="flex items-center justify-between gap-2">
                <p className="font-semibold text-slate-900">{report.filename}</p>
                <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold uppercase tracking-[0.22em] text-slate-500">
                  {report.status}
                </span>
              </div>
              <div className="mt-3 flex items-center gap-4 text-xs text-slate-500">
                <span>{report.uploadedAt}</span>
                <span>Report ID #{report.id}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}
