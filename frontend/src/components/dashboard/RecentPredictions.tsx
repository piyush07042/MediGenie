import { Activity } from "lucide-react";
import type { RecentPrediction } from "../../services/dashboardService";

export default function RecentPredictions({ data, loading }: { data: RecentPrediction[]; loading: boolean }) {
  return (
    <section className="rounded-3xl border border-slate-200 bg-white p-6 shadow-soft">
      <div className="mb-5 flex items-center justify-between gap-3">
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.28em] text-slate-400">Recent Predictions</p>
          <h2 className="mt-2 text-xl font-semibold text-slate-900">Prediction history</h2>
        </div>
        <div className="inline-flex h-12 w-12 items-center justify-center rounded-3xl bg-brand-100 text-brand-700">
          <Activity className="h-5 w-5" />
        </div>
      </div>
      {loading ? (
        <div className="space-y-3">
          {Array.from({ length: 4 }).map((_, index) => (
            <div key={index} className="h-14 rounded-3xl bg-slate-100" />
          ))}
        </div>
      ) : (
        <div className="space-y-4">
          {data.map((item) => (
            <div key={item.id} className="rounded-3xl bg-slate-50 px-4 py-4 text-sm text-slate-700">
              <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <p className="font-semibold text-slate-900">{item.patient}</p>
                  <p className="text-sm text-slate-500">{item.disease}</p>
                </div>
                <div className="flex items-center gap-3 text-xs text-slate-500">
                  <span>{item.risk}</span>
                  <span>{item.confidence}</span>
                  <span>{item.date}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}
