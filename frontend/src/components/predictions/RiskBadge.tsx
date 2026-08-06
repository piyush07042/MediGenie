export default function RiskBadge({ risk }: { risk: string }) {
  const tone = risk.toLowerCase().includes("high")
    ? "bg-red-50 text-red-700"
    : risk.toLowerCase().includes("moderate")
    ? "bg-amber-50 text-amber-700"
    : "bg-emerald-50 text-emerald-700";

  return <span className={`inline-flex rounded-full px-3 py-1 text-xs font-semibold ${tone}`}>{risk}</span>;
}
