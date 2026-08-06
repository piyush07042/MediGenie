export default function ExplainabilityPanel({ explanations }: { explanations?: Array<Record<string, any>> | null }) {
  if (!explanations?.length) {
    return <p className="text-sm text-slate-500">No explainability data is available.</p>;
  }

  return (
    <div className="space-y-4">
      {explanations.map((item, index) => (
        <div key={index} className="rounded-3xl border border-slate-200 bg-slate-50 p-4">
          <p className="text-sm font-semibold text-slate-900">{item.title ?? `Explanation ${index + 1}`}</p>
          <pre className="mt-3 whitespace-pre-wrap text-sm leading-6 text-slate-700">{JSON.stringify(item, null, 2)}</pre>
        </div>
      ))}
    </div>
  );
}
