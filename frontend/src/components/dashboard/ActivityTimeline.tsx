import EmptyState from "./EmptyState";
import DashboardSkeleton from "./DashboardSkeleton";
import type { ActivityEvent } from "../../services/dashboardService";

export default function ActivityTimeline({
  data,
  loading,
}: {
  data: ActivityEvent[];
  loading: boolean;
}) {
  return (
    <section className="rounded-3xl border border-slate-200 bg-white p-4 shadow-soft sm:p-6">
      <div className="mb-5">
        <p className="text-sm font-semibold uppercase tracking-[0.28em] text-slate-400">Activity Timeline</p>
        <h2 className="mt-2 text-xl font-semibold text-slate-900">Platform events</h2>
      </div>
      {loading ? (
        <DashboardSkeleton rows={5} />
      ) : data.length === 0 ? (
        <EmptyState
          title="No recent activity"
          description="Patient registrations, uploads, and predictions will show up here as you use the platform."
        />
      ) : (
        <div className="space-y-4">
          {data.map((event) => (
            <div key={event.id} className="rounded-3xl border border-slate-100 bg-slate-50 p-4">
              <div className="flex flex-col gap-2 text-sm text-slate-500 sm:flex-row sm:items-center sm:justify-between">
                <p className="font-semibold text-slate-900">{event.title}</p>
                <span>{event.time}</span>
              </div>
              <p className="mt-2 text-sm leading-6 text-slate-600">{event.description}</p>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}
