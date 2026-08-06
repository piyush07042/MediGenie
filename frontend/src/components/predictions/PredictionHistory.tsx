import type { PredictionHistoryItem } from "../../utils/predictionHistory";

export default function PredictionHistory({ history }: { history: PredictionHistoryItem[] }) {
  if (!history.length) {
    return <p className="text-sm text-slate-500">No previous predictions are available for this patient.</p>;
  }

  return (
    <div className="space-y-4">
      {history.map((item) => (
        <div key={item.id} className="rounded-3xl border border-slate-200 bg-slate-50 p-4">
          <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <p className="font-semibold text-slate-900">{item.disease}</p>
              <p className="text-sm text-slate-500">{new Date(item.createdAt).toLocaleString()}</p>
            </div>
            <div className="flex flex-wrap items-center gap-2 text-sm text-slate-600">
              <span>Prediction: {item.prediction}</span>
              <span>Probability: {item.probability.toFixed(2)}</span>
              <span>Confidence: {Math.round(item.confidence * 100)}%</span>
              {item.confidenceLabel ? <span>{item.confidenceLabel}</span> : null}
            </div>
          </div>
          {item.summary ? <p className="mt-3 text-sm text-slate-700">{item.summary}</p> : null}
        </div>
      ))}
    </div>
  );
}
