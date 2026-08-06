import { useMemo } from "react";
import { useNavigate } from "react-router-dom";
import { jsPDF } from "jspdf";
import PredictionPanel from "./PredictionPanel";
import RiskBadge from "./RiskBadge";
import ConfidenceMeter from "./ConfidenceMeter";
import RecommendationPanel from "./RecommendationPanel";
import ExplainabilityPanel from "./ExplainabilityPanel";
import DrugSafetyPanel from "./DrugSafetyPanel";
import type { Patient } from "../../types/api";

export default function PredictionResultView({
  result,
  patient,
  timestamp,
  onNewPrediction,
}: {
  result: Record<string, any>;
  patient?: Patient | null;
  timestamp: string;
  onNewPrediction: () => void;
}) {
  const navigate = useNavigate();
  const confidenceValue = typeof result.confidence === "number" ? result.confidence : Number(result.confidence) || 0;
  const riskLabel = result.confidence_label || result.risk || "Unknown";

  const pdfContent = useMemo(() => {
    const lines: string[] = [];
    lines.push(`Prediction report for ${patient?.first_name ?? "Patient"} ${patient?.last_name ?? ""}`.trim());
    lines.push(" ");
    lines.push(`Disease: ${result.disease ?? "N/A"}`);
    lines.push(`Prediction: ${result.prediction ?? "N/A"}`);
    lines.push(`Probability: ${typeof result.probability === "number" ? result.probability.toFixed(2) : result.probability ?? "N/A"}`);
    lines.push(`Confidence: ${typeof result.confidence === "number" ? result.confidence.toFixed(2) : result.confidence ?? "N/A"}`);
    lines.push(`Risk: ${riskLabel}`);
    lines.push(`Timestamp: ${timestamp}`);
    lines.push(" ");
    lines.push("Recommendations:");
    if (Array.isArray(result.recommendations) && result.recommendations.length) {
      result.recommendations.forEach((item: any, index: number) => {
        const text = typeof item === "object" ? item.recommendation || JSON.stringify(item) : String(item);
        lines.push(`${index + 1}. ${text}`);
      });
    } else {
      lines.push("None");
    }
    lines.push(" ");
    lines.push("Final AI report:");
    if (result.final_report) {
      lines.push(JSON.stringify(result.final_report, null, 2));
    } else {
      lines.push("Not provided.");
    }
    return lines;
  }, [patient, result, riskLabel, timestamp]);

  const downloadPdf = () => {
    const doc = new jsPDF({ unit: "pt", format: "letter" });
    let y = 40;
    doc.setFontSize(14);
    pdfContent.forEach((line) => {
      const split = doc.splitTextToSize(line, 520);
      doc.text(split, 40, y);
      y += split.length * 16;
      if (y > 720) {
        doc.addPage();
        y = 40;
      }
    });
    doc.save(`${result.disease ?? "prediction"}-report.pdf`);
  };

  const printReport = () => {
    window.print();
  };

  return (
    <div className="space-y-6">
      <PredictionPanel title="Summary">
        <div className="grid gap-4 xl:grid-cols-3">
          <div className="space-y-2">
            <p className="text-sm text-slate-500">Disease</p>
            <p className="text-2xl font-semibold text-slate-900">{result.disease ?? "Unknown"}</p>
          </div>
          <div className="space-y-2">
            <p className="text-sm text-slate-500">Prediction</p>
            <p className="text-2xl font-semibold text-slate-900">{result.prediction ?? "N/A"}</p>
          </div>
          <div className="space-y-2">
            <p className="text-sm text-slate-500">Risk</p>
            <RiskBadge risk={riskLabel} />
          </div>
        </div>
        <div className="grid gap-4 xl:grid-cols-3 pt-6">
          <div className="rounded-3xl border border-slate-200 bg-slate-50 p-5">
            <p className="text-sm text-slate-500">Probability</p>
            <p className="mt-2 text-3xl font-semibold text-slate-900">{typeof result.probability === "number" ? result.probability.toFixed(2) : result.probability ?? "N/A"}</p>
          </div>
          <div className="rounded-3xl border border-slate-200 bg-slate-50 p-5">
            <p className="text-sm text-slate-500">Confidence</p>
            <ConfidenceMeter confidence={confidenceValue} />
          </div>
          <div className="rounded-3xl border border-slate-200 bg-slate-50 p-5">
            <p className="text-sm text-slate-500">Timestamp</p>
            <p className="mt-2 text-3xl font-semibold text-slate-900">{timestamp}</p>
          </div>
        </div>
      </PredictionPanel>

      {patient ? (
        <PredictionPanel title="Patient summary">
          <div className="space-y-3 text-sm text-slate-700">
            <p className="font-semibold text-slate-900">{patient.first_name} {patient.last_name}</p>
            <p>Age: {patient.age}</p>
            <p>Gender: {patient.gender}</p>
            <p className="text-slate-500">Created: {new Date(patient.created_at).toLocaleString()}</p>
          </div>
        </PredictionPanel>
      ) : null}

      <div className="grid gap-6 xl:grid-cols-2">
        <PredictionPanel title="Explainability & feature importance">
          <ExplainabilityPanel explanations={result.explanations} />
          {result.feature_importance ? (
            <div className="mt-6 rounded-3xl border border-slate-200 bg-slate-50 p-4">
              <p className="text-sm font-semibold text-slate-900">Feature importance</p>
              <pre className="mt-3 whitespace-pre-wrap text-sm leading-6 text-slate-700">
                {JSON.stringify(result.feature_importance, null, 2)}
              </pre>
            </div>
          ) : null}
          {result.shap || result.shap_values ? (
            <div className="mt-6 rounded-3xl border border-slate-200 bg-slate-50 p-4">
              <p className="text-sm font-semibold text-slate-900">SHAP explanation</p>
              <pre className="mt-3 whitespace-pre-wrap text-sm leading-6 text-slate-700">
                {JSON.stringify(result.shap || result.shap_values, null, 2)}
              </pre>
            </div>
          ) : null}
        </PredictionPanel>

        <PredictionPanel title="Recommendations & drug safety">
          <RecommendationPanel recommendations={result.recommendations} />
          <div className="mt-6">
            <DrugSafetyPanel drugSafety={result.drug_safety} />
          </div>
        </PredictionPanel>
      </div>

      <PredictionPanel title="Generated AI report">
        {result.final_report ? (
          <pre className="max-h-[420px] overflow-auto rounded-3xl bg-slate-950 p-4 text-sm text-slate-100">
            {JSON.stringify(result.final_report, null, 2)}
          </pre>
        ) : (
          <p className="text-sm text-slate-500">No generated AI report was returned by the backend.</p>
        )}
      </PredictionPanel>

      <div className="flex flex-col gap-3 lg:flex-row">
        <button
          type="button"
          onClick={downloadPdf}
          className="w-full rounded-2xl bg-brand-600 px-4 py-3 text-sm font-semibold text-white transition hover:bg-brand-700 lg:w-auto"
        >
          Download PDF
        </button>
        <button
          type="button"
          onClick={printReport}
          className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-100 lg:w-auto"
        >
          Print Report
        </button>
        <button
          type="button"
          onClick={() => navigate("/")}
          className="w-full rounded-2xl border border-brand-500 bg-brand-50 px-4 py-3 text-sm font-semibold text-brand-700 transition hover:bg-brand-100 lg:w-auto"
        >
          Return to Dashboard
        </button>
        <button
          type="button"
          onClick={onNewPrediction}
          className="w-full rounded-2xl bg-slate-900 px-4 py-3 text-sm font-semibold text-white transition hover:bg-slate-800 lg:w-auto"
        >
          Run Another Prediction
        </button>
      </div>
    </div>
  );
}
