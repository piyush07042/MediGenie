import InteractionSeverity from "./InteractionSeverity";

export default function DrugInteractionCard({
  interaction,
}: {
  interaction: {
    drugs_involved: string[];
    severity: string;
    explanation: string;
    recommendation: string;
  };
}) {
  return (
    <div className="rounded-3xl border border-slate-200 bg-slate-50 p-5">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p className="text-sm font-semibold text-slate-900">{interaction.drugs_involved.join(" ↔ ")}</p>
          <p className="mt-2 text-sm text-slate-600">{interaction.explanation}</p>
        </div>
        <InteractionSeverity severity={interaction.severity} />
      </div>
      <div className="mt-4 rounded-2xl border border-slate-200 bg-white p-4">
        <p className="text-sm font-semibold text-slate-900">Recommendation</p>
        <p className="mt-2 text-sm leading-6 text-slate-700">{interaction.recommendation}</p>
      </div>
    </div>
  );
}
