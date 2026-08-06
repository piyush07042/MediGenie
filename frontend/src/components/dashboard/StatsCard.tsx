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
    <div className="rounded-3xl border border-slate-200 bg-white p-5 shadow-soft transition hover:-translate-y-1 hover:shadow-lg">
      <div className="flex items-center justify-between gap-4">
        <div>
          <p className="text-sm font-semibold text-slate-500">{title}</p>
          <p className="mt-3 text-3xl font-semibold text-slate-900">{value}</p>
        </div>
        <div className={`inline-flex h-11 w-11 items-center justify-center rounded-2xl ${positive ? "bg-emerald-100 text-emerald-700" : "bg-rose-100 text-rose-700"}`}>
          {positive ? <ArrowUp className="h-5 w-5" /> : <ArrowDown className="h-5 w-5" />}
        </div>
      </div>
      <p className="mt-4 text-sm text-slate-500">{label}</p>
      <p className={`mt-2 text-sm font-semibold ${positive ? "text-emerald-700" : "text-rose-700"}`}>{trend}</p>
    </div>
  );
}
