import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from "recharts";
import type { LinePoint } from "../../services/dashboardService";

export default function MonthlyTrendChart({ data, isLoading }: { data: LinePoint[]; isLoading: boolean }) {
  return (
    <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-soft">
      <div className="mb-5 flex items-center justify-between gap-3">
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.28em] text-slate-400">Monthly Predictions</p>
          <h2 className="mt-2 text-xl font-semibold text-slate-900">Trend over time</h2>
        </div>
      </div>
      {isLoading ? (
        <div className="h-72 rounded-3xl bg-slate-100" />
      ) : (
        <div className="h-72">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis dataKey="month" tickLine={false} axisLine={false} />
              <YAxis tickLine={false} axisLine={false} />
              <Tooltip />
              <Legend verticalAlign="top" height={36} />
              <Line type="monotone" dataKey="predictions" stroke="#4f6dff" strokeWidth={3} dot={{ r: 4 }} />
              <Line type="monotone" dataKey="reports" stroke="#10b981" strokeWidth={3} dot={{ r: 4 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}
