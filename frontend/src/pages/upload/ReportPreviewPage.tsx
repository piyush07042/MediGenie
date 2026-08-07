import { useMemo, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import PageHeading from "../../components/PageHeading";
import Card from "../../components/Card";
import { UploadReportResponse } from "../../types/api";

export default function ReportPreviewPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const state = location.state as { result?: UploadReportResponse; fileName?: string } | null;
  const result = state?.result;
  const fileName = state?.fileName;
  const [editedText, setEditedText] = useState("");
  const [savedCorrection, setSavedCorrection] = useState(false);

  if (!result) {
    return (
      <div className="space-y-10">
        <PageHeading title="Report preview" description="No report data is available yet." />
        <Card title="No report available">
          <p className="text-sm text-slate-500">Please upload a report first, then use this page to inspect the processed result.</p>
          <button
            type="button"
            onClick={() => navigate("/upload-report")}
            className="mt-4 w-full rounded-2xl bg-brand-600 px-4 py-3 text-sm font-semibold text-white transition hover:bg-brand-700"
          >
            Upload a new report
          </button>
        </Card>
      </div>
    );
  }

  const workflow = result.workflow_state;
  const ocrText = useMemo(() => {
    const rawText = workflow?.report_text ?? workflow?.ocr_result?.text ?? workflow?.ocr_result?.full_text ?? "";
    if (typeof rawText === "string") {
      return rawText;
    }
    return JSON.stringify(rawText, null, 2);
  }, [workflow]);

  useMemo(() => {
    setEditedText(ocrText);
  }, [ocrText]);

  const handleSaveCorrection = () => {
    setSavedCorrection(true);
    const nextWorkflow = {
      ...(workflow ?? {}),
      report_text: editedText,
      metadata: {
        ...(workflow?.metadata ?? {}),
        ocr_correction_saved: true,
      },
    };

    localStorage.setItem("medigenie_ocr_correction", JSON.stringify({ fileName, editedText, savedAt: new Date().toISOString() }));
    navigate("/upload-report/preview", {
      state: {
        result: { ...result, workflow_state: nextWorkflow },
        fileName,
      },
      replace: true,
    });
  };

  return (
    <div className="space-y-10">
      <PageHeading title="Report preview" description="Review the extracted OCR text, AI risk analysis, and recommendations." />

      <div className="grid gap-6 xl:grid-cols-3">
        <Card title="Report summary">
          <div className="space-y-3 text-sm text-slate-700">
            <p>
              <span className="font-semibold">File</span>: {fileName ?? "Uploaded report"}
            </p>
            <p>
              <span className="font-semibold">Workflow status</span>: {workflow?.metadata?.workflow_status ?? "completed"}
            </p>
            <p>
              <span className="font-semibold">Warnings</span>: {workflow?.warnings?.length ?? 0}
            </p>
            <p>
              <span className="font-semibold">Errors</span>: {workflow?.errors?.length ?? 0}
            </p>
            <p>
              <span className="font-semibold">Extracted metrics</span>: {Object.keys((workflow?.extracted_metrics ?? {}) as Record<string, unknown>).length}
            </p>
          </div>
        </Card>

        <Card title="Patient context">
          {workflow?.patient ? (
            <pre className="max-h-[260px] overflow-auto rounded-3xl bg-slate-950 p-4 text-sm text-slate-100">
              {JSON.stringify(workflow.patient, null, 2)}
            </pre>
          ) : (
            <p className="text-sm text-slate-500">No patient context was provided with this upload.</p>
          )}
        </Card>

        <Card title="Risk analysis">
          {workflow?.disease_risk ? (
            <pre className="max-h-[260px] overflow-auto rounded-3xl bg-slate-950 p-4 text-sm text-slate-100">
              {JSON.stringify(workflow.disease_risk, null, 2)}
            </pre>
          ) : (
            <p className="text-sm text-slate-500">Risk analysis was not produced for this report.</p>
          )}
        </Card>
      </div>

      <div className="grid gap-6 xl:grid-cols-2">
        <Card title="OCR result">
          <div className="space-y-3">
            <div className="flex items-center justify-between gap-3">
              <p className="text-sm text-slate-500">Edit extracted OCR text before moving to the next step.</p>
              <button
                type="button"
                onClick={handleSaveCorrection}
                className="rounded-2xl border border-brand-600 bg-brand-50 px-3 py-2 text-sm font-semibold text-brand-700 transition hover:bg-brand-100"
              >
                Save correction
              </button>
            </div>
            {ocrText ? (
              <textarea
                rows={12}
                value={editedText}
                onChange={(event) => {
                  setEditedText(event.target.value);
                  setSavedCorrection(false);
                }}
                className="min-h-[260px] w-full rounded-3xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-brand-400 focus:ring-4 focus:ring-brand-100"
              />
            ) : (
              <p className="text-sm text-slate-500">No OCR output was extracted from this report.</p>
            )}
            {savedCorrection ? <p className="text-sm text-emerald-600">Correction saved locally for this session.</p> : null}
          </div>
        </Card>

        <Card title="Recommendations">
          {workflow?.recommendations?.length ? (
            <div className="space-y-3 text-sm text-slate-700">
              {workflow.recommendations.map((recommendation, index) => (
                <div key={index} className="rounded-2xl bg-slate-50 p-4">
                  <pre className="whitespace-pre-wrap text-sm text-slate-800">{JSON.stringify(recommendation, null, 2)}</pre>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-slate-500">No recommendations were generated for this upload.</p>
          )}
        </Card>
      </div>

      <Card title="Raw workflow response">
        <pre className="max-h-[420px] overflow-auto rounded-3xl bg-slate-950 p-4 text-sm text-slate-100">
          {JSON.stringify(result, null, 2)}
        </pre>
      </Card>

      <div className="flex flex-col gap-3 lg:flex-row">
        <button
          type="button"
          onClick={() => navigate("/upload-report")}
          className="w-full rounded-2xl bg-slate-100 px-4 py-3 text-sm font-semibold text-slate-900 transition hover:bg-slate-200 lg:w-auto"
        >
          Upload another report
        </button>
        <button
          type="button"
          onClick={() => navigate("/predictions", { state: { result } })}
          className="w-full rounded-2xl border border-brand-500 bg-white px-4 py-3 text-sm font-semibold text-brand-700 transition hover:bg-brand-50 lg:w-auto"
        >
          Run disease prediction
        </button>
        <button
          type="button"
          onClick={() => navigate("/upload-report/processing", {
            state: {
              status: "completed",
              fileName,
              progress: 100,
              startedAt: new Date().toISOString(),
            },
          })}
          className="w-full rounded-2xl bg-brand-600 px-4 py-3 text-sm font-semibold text-white transition hover:bg-brand-700 lg:w-auto"
        >
          View processing status
        </button>
      </div>
    </div>
  );
}
