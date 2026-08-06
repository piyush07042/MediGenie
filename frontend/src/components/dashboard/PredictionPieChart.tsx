import { ResponsiveContainer, PieChart, Pie, Cell, Tooltip, Legend } from "recharts";
import type { PieSlice } from "../../services/dashboardService";

const COLORS = ["#4f6dff", "#7b95ff", "#4ade80", "#f59e0b", "#fb7185", "#10b981", "#6366f1", "#0ea5e9", "#8b5cf6"];

export default function PredictionPieChart({ data, isLoading }: { data: PieSlice[]; isLoading: boolean }) {
  return (
    <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-soft">
      <div className="mb-5 flex items-center justify-between gap-3">
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.28em] text-slate-400">Disease Prediction Distribution</p>
          <h2 className="mt-2 text-xl font-semibold text-slate-900">Prediction mix</h2>
        </div>
      </div>
      {isLoading ? (
        <div className="h-72 rounded-3xl bg-slate-100" />
      ) : (
        <div className="h-72">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie data={data} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={100} fill="#8884d8" label />
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
              <Tooltip formatter={(value: number) => `${value}%`} />
              <Legend verticalAlign="bottom" height={36} wrapperStyle={{ fontSize: 12 }} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}
