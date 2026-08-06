import { Link } from "react-router-dom";
import { ArrowRight } from "lucide-react";

export default function QuickActionCard({ title, subtitle, to }: { title: string; subtitle: string; to: string }) {
  return (
    <Link to={to} className="group block rounded-3xl border border-slate-200 bg-slate-50 p-5 transition hover:-translate-y-1 hover:border-brand-200 hover:bg-white">
      <div className="flex items-center justify-between gap-3">
        <div>
          <p className="text-sm font-semibold text-slate-900">{title}</p>
          <p className="mt-2 text-sm text-slate-500">{subtitle}</p>
        </div>
        <div className="inline-flex h-11 w-11 items-center justify-center rounded-2xl bg-brand-600 text-white transition group-hover:bg-brand-700">
          <ArrowRight className="h-4 w-4" />
        </div>
      </div>
    </Link>
  );
}
