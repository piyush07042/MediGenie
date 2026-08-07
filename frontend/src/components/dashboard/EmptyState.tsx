import type { ReactNode } from "react";
import { Inbox } from "lucide-react";
import { Link } from "react-router-dom";

export default function EmptyState({
  title,
  description,
  icon,
}: {
  title: string;
  description: string;
  icon?: ReactNode;
}) {
  return (
    <div className="flex flex-col items-center justify-center rounded-3xl border border-dashed border-slate-200 bg-slate-50 px-6 py-8 text-center">
      <div className="mb-3 inline-flex h-12 w-12 items-center justify-center rounded-3xl bg-white text-brand-600 shadow-sm ring-1 ring-slate-200">
        {icon ?? <Inbox className="h-5 w-5" />}
      </div>
      <p className="text-sm font-semibold text-slate-900">{title}</p>
      <p className="mt-2 max-w-xs text-sm leading-6 text-slate-500">{description}</p>
      <div className="mt-4 flex gap-3">
        <Link to="/predictions" className="inline-flex items-center gap-2 rounded-full border border-transparent bg-brand-600 px-3 py-1.5 text-sm font-medium text-white shadow-sm hover:bg-brand-700">Run prediction</Link>
        <Link to="/upload-report" className="inline-flex items-center gap-2 rounded-full border border-slate-200 bg-white px-3 py-1.5 text-sm font-medium text-slate-700 shadow-sm hover:bg-slate-100">Upload report</Link>
      </div>
    </div>
  );
}
