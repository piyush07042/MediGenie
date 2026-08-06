import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useDropzone } from "react-dropzone";
import toast from "react-hot-toast";
import PageHeading from "../../components/PageHeading";
import Card from "../../components/Card";
import { uploadReport } from "../../api/upload";
import { UploadReportResponse } from "../../types/api";

export default function UploadReportPage() {
  const navigate = useNavigate();
  const [file, setFile] = useState<File | null>(null);
  const [patientId, setPatientId] = useState<number | "">("");
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [result, setResult] = useState<UploadReportResponse | null>(null);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: {
      "application/pdf": [".pdf"],
      "image/png": [".png"],
      "image/jpeg": [".jpg", ".jpeg"],
    },
    maxFiles: 1,
    onDrop: (acceptedFiles) => {
      setFile(acceptedFiles[0] ?? null);
    },
  });

  const handleUpload = async () => {
    if (!file) {
      toast.error("Please select a report file to upload.");
      return;
    }

    setErrorMessage(null);
    setUploading(true);
    setProgress(0);

    try {
      const patientContext = patientId ? { id: patientId } : undefined;
      const response = await uploadReport(
        file,
        patientContext,
        setProgress,
        new AbortController().signal
      );

      if (!response.success || !response.data) {
        throw new Error(response.message || "Upload did not complete successfully.");
      }

      setResult(response.data);
      toast.success("Report uploaded successfully.");
      navigate("/upload-report/preview", {
        state: { result: response.data, fileName: file.name },
      });
    } catch (error) {
      const message = error instanceof Error ? error.message : "Upload failed. Please try again.";
      setErrorMessage(message);
      toast.error(message);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="space-y-10">
      <PageHeading
        title="Upload Clinical Report"
        description="Upload a PDF or image report to run OCR and AI workflow processing."
      />

      <div className="grid gap-6 xl:grid-cols-2">
        <Card title="Upload report">
          <div
            {...getRootProps()}
            className="rounded-3xl border border-dashed border-slate-300 bg-slate-50 p-10 text-center transition hover:border-brand-400 hover:bg-slate-100"
          >
            <input {...getInputProps()} />
            <p className="text-sm text-slate-600">
              Drag and drop a PDF, PNG, or JPEG file here, or click to choose a file.
            </p>
            {file ? (
              <div className="mt-4 text-left text-sm text-slate-900">
                <p className="font-semibold">Selected file</p>
                <p>{file.name}</p>
                <p>{(file.size / 1024 / 1024).toFixed(2)} MB</p>
              </div>
            ) : isDragActive ? (
              <p className="mt-4 text-sm font-semibold text-brand-600">Drop the report to upload it.</p>
            ) : null}
          </div>

          <div className="mt-6 space-y-4">
            <label className="block text-sm font-medium text-slate-700">Patient ID (optional)</label>
            <input
              type="number"
              value={patientId}
              onChange={(event) => setPatientId(event.target.value === "" ? "" : Number(event.target.value))}
              placeholder="Enter a patient ID to attach this report"
              className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-brand-400 focus:ring-4 focus:ring-brand-100"
            />
            <button
              type="button"
              onClick={handleUpload}
              disabled={uploading}
              className="w-full rounded-2xl bg-brand-600 px-4 py-3 text-sm font-semibold text-white transition hover:bg-brand-700 disabled:cursor-not-allowed disabled:bg-slate-400"
            >
              {uploading ? "Uploading report..." : "Upload and process report"}
            </button>
          </div>

          {uploading ? (
            <div className="mt-4 rounded-2xl bg-slate-100 p-4 text-sm text-slate-700">
              <p className="font-medium">Processing report</p>
              <div className="mt-3 h-3 overflow-hidden rounded-full bg-slate-200">
                <div className="h-full rounded-full bg-brand-600" style={{ width: `${progress}%` }} />
              </div>
              <p className="mt-2 text-xs text-slate-500">{progress}% complete</p>
            </div>
          ) : null}

          {errorMessage ? (
            <div className="mt-4 rounded-2xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
              <p className="font-semibold">Upload error</p>
              <p>{errorMessage}</p>
            </div>
          ) : null}
        </Card>

        <Card title="Upload summary">
          {result ? (
            <div className="space-y-4 text-sm text-slate-700">
              <p>
                <span className="font-semibold">Workflow status:</span> {result.workflow_state?.metadata?.workflow_status ?? "Completed"}
              </p>
              <p>
                <span className="font-semibold">Detected warnings:</span> {result.workflow_state?.warnings?.length ?? 0}
              </p>
              <p>
                <span className="font-semibold">Detected errors:</span> {result.workflow_state?.errors?.length ?? 0}
              </p>
              <button
                type="button"
                onClick={() => navigate("/upload-report/preview", {
                  state: { result, fileName: file?.name ?? "Uploaded report" },
                })}
                className="w-full rounded-2xl border border-brand-600 bg-white px-4 py-3 text-sm font-semibold text-brand-600 transition hover:bg-brand-50"
              >
                View extracted report details
              </button>
            </div>
          ) : (
            <p className="text-sm text-slate-500">
              Upload a report to preview OCR text, extracted metrics, AI risk analysis, and recommendations.
            </p>
          )}
        </Card>
      </div>
    </div>
  );
}
