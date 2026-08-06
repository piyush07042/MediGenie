export default function ConfidenceMeter({ confidence }: { confidence: number }) {
  const percent = Math.round(confidence * 100);
  const width = `${Math.min(100, Math.max(0, percent))}%`;
  const tone = percent >= 80 ? "bg-emerald-500" : percent >= 60 ? "bg-amber-500" : "bg-red-500";

  return (
    <div className="space-y-2 text-sm">
      <div className="flex items-center justify-between text-slate-700">
        <span className="font-semibold">Confidence</span>
        <span>{percent}%</span>
      </div>
      <div className="h-3 overflow-hidden rounded-full bg-slate-200">
        <div className={`h-full ${tone}`} style={{ width }} />
      </div>
    </div>
  );
}
