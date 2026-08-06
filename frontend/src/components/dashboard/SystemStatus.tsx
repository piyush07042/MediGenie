import type { ReactNode } from "react";
import { CircleDot, ShieldCheck, ServerCog, Database, Sparkles, KeyRound, BookOpen } from "lucide-react";
import type { SystemStatusItem } from "../../services/dashboardService";

const statusStyles: Record<string, string> = {
  Online: "bg-emerald-100 text-emerald-700",
  Degraded: "bg-amber-100 text-amber-700",
  Offline: "bg-rose-100 text-rose-700",
};

const iconMap: Record<string, ReactNode> = {
  "Backend API": <ServerCog className="h-4 w-4" />,
  Database: <Database className="h-4 w-4" />,
  "OCR Service": <CircleDot className="h-4 w-4" />,
  "AI Models Loaded": <Sparkles className="h-4 w-4" />,
  "Knowledge Base": <BookOpen className="h-4 w-4" />,
  Authentication: <KeyRound className="h-4 w-4" />,
};

export default function SystemStatus({ data, loading }: { data: SystemStatusItem[]; loading: boolean }) {
  return (
    <section className="rounded-3xl border border-slate-200 bg-white p-6 shadow-soft">
      <div className="mb-5 flex items-center justify-between gap-3">
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.28em] text-slate-400">System Health</p>
          <h2 className="mt-2 text-xl font-semibold text-slate-900">Operational status</h2>
        </div>
      </div>
      <div className="grid gap-4 sm:grid-cols-2">
        {loading
          ? Array.from({ length: 4 }).map((_, index) => (
              <div key={index} className="h-24 rounded-3xl bg-slate-100" />
            ))
          : data.map((item) => (
              <div key={item.service} className="flex items-center justify-between rounded-3xl bg-slate-50 px-4 py-4">
                <div className="flex items-center gap-3">
                  <div className="flex h-12 w-12 items-center justify-center rounded-3xl bg-slate-100 text-brand-600">
                    {iconMap[item.service] ?? <ShieldCheck className="h-4 w-4" />}
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-slate-900">{item.service}</p>
                    <p className="text-sm text-slate-500">{item.description}</p>
                  </div>
                </div>
                <span className={`rounded-full px-3 py-1 text-xs font-semibold ${statusStyles[item.status] ?? "bg-slate-100 text-slate-700"}`}>
                  {item.status}
                </span>
              </div>
            ))}
      </div>
    </section>
  );
}
