import { Users } from "lucide-react";
import type { RecentPatient } from "../../services/dashboardService";

export default function RecentPatients({ data, loading }: { data: RecentPatient[]; loading: boolean }) {
  return (
    <section className="rounded-3xl border border-slate-200 bg-white p-6 shadow-soft">
      <div className="mb-5 flex items-center justify-between gap-3">
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.28em] text-slate-400">Recent Patients</p>
          <h2 className="mt-2 text-xl font-semibold text-slate-900">Patient activity</h2>
        </div>
        <div className="inline-flex h-12 w-12 items-center justify-center rounded-3xl bg-brand-100 text-brand-700">
          <Users className="h-5 w-5" />
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
          <div className="grid grid-cols-12 gap-4 text-xs uppercase tracking-[0.24em] text-slate-400">
            <span className="col-span-4">Name</span>
            <span className="col-span-2">Age</span>
            <span className="col-span-3">Gender</span>
            <span className="col-span-3">Last Visit</span>
          </div>
          {data.map((patient) => (
            <div key={patient.id} className="grid grid-cols-12 gap-4 rounded-3xl bg-slate-50 px-4 py-4 text-sm text-slate-700">
              <span className="col-span-4 font-semibold text-slate-900">{patient.name}</span>
              <span className="col-span-2">{patient.age}</span>
              <span className="col-span-3">{patient.gender}</span>
              <span className="col-span-3 text-slate-500">{patient.lastVisit}</span>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}
