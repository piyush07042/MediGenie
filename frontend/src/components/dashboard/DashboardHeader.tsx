import { ReactNode } from "react";

export default function DashboardHeader({
  greeting,
  subtitle,
  summary,
  children,
}: {
  greeting: string;
  subtitle: string;
  summary: string;
  children?: ReactNode;
}) {
  return (
    <div className="grid gap-4 rounded-3xl border border-slate-200 bg-slate-50 p-6 shadow-soft sm:grid-cols-[1.5fr_1fr] lg:p-8">
      <div>
        <p className="text-sm uppercase tracking-[0.24em] text-brand-600">Welcome</p>
        <h1 className="mt-3 text-3xl font-semibold text-slate-950 sm:text-4xl">{greeting}</h1>
        <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-600 sm:text-base">{subtitle}</p>
      </div>
      <div className="rounded-3xl bg-white p-6 shadow-sm ring-1 ring-slate-200 sm:p-8">
        <p className="text-sm font-medium uppercase tracking-[0.24em] text-slate-500">Today</p>
        <p className="mt-4 text-3xl font-semibold text-slate-900">{summary}</p>
        <p className="mt-3 text-sm text-slate-500">Your hospital AI workspace is up to date.</p>
      </div>
      {children ? <div className="sm:col-span-2">{children}</div> : null}
    </div>
  );
}
