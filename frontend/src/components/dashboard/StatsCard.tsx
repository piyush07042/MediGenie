import { ArrowDown, ArrowUp } from "lucide-react";

export default function StatsCard({
  title,
  value,
  trend,
  label,
  positive,
}: {
  title: string;
  value: string;
  trend: string;
  label: string;
  positive: boolean;
}) {
  return (
    <div className="rounded-2xl border border-slate-100 bg-white p-4 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md">
      <div className="flex items-center justify-between gap-3">
        <div>
          <p className="text-xs font-semibold text-slate-500">{title}</p>
          <p className="mt-2 text-2xl font-semibold text-slate-900">{value}</p>
        </div>
        <div className={`inline-flex h-9 w-9 items-center justify-center rounded-lg ${positive ? "bg-emerald-50 text-emerald-700" : "bg-rose-50 text-rose-700"}`}>
          {positive ? <ArrowUp className="h-4 w-4" /> : <ArrowDown className="h-4 w-4" />}
        </div>
      </div>
      <div className="mt-3 flex items-center justify-between">
        <p className="text-xs text-slate-500">{label}</p>
        <p className={`text-xs font-semibold ${positive ? "text-emerald-700" : "text-rose-700"}`}>{trend}</p>
      </div>
    </div>
  );
}
