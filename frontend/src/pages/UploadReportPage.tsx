import { useState } from "react";
import toast from "react-hot-toast";
import { useDropzone } from "react-dropzone";
import PageHeading from "../components/PageHeading";
import Card from "../components/Card";
import { uploadReport } from "../api/upload";

export default function UploadReportPage() {
  const [file, setFile] = useState<File | null>(null);
  const [result, setResult] = useState<any>(null);

  const { getRootProps, getInputProps } = useDropzone({
    accept: { "application/pdf": [".pdf"], "text/plain": [".txt"] },
    maxFiles: 1,
    onDrop: (acceptedFiles) => {
      setFile(acceptedFiles[0] ?? null);
    },
  });

  const handleUpload = async () => {
    if (!file) {
      toast.error("Select a file before uploading.");
      return;
    }

    try {
      const response = await uploadReport(file);
      setResult(response.data);
      toast.success("Report uploaded successfully.");
    } catch (error) {
      toast.error("Upload failed. Please try again.");
    }
  };

  return (
    <div className="space-y-10">
      <PageHeading title="Upload Clinical Report" description="Upload a PDF or text report for AI processing and workflow analysis." />
      <div className="grid gap-6 xl:grid-cols-2">
        <Card title="Upload report">
          <div {...getRootProps()} className="rounded-3xl border border-dashed border-slate-300 bg-slate-50 p-10 text-center transition hover:border-brand-400 hover:bg-slate-100">
            <input {...getInputProps()} />
            <p className="text-sm text-slate-600">Drag and drop a report here, or click to choose a file.</p>
            {file ? <p className="mt-4 text-sm text-slate-900">Selected file: {file.name}</p> : null}
          </div>
          <button onClick={handleUpload} className="mt-6 w-full rounded-2xl bg-brand-600 px-4 py-3 text-sm font-semibold text-white transition hover:bg-brand-700">
            Upload and process
          </button>
        </Card>

        <Card title="Processing output">
          {result ? (
            <pre className="max-h-[420px] overflow-auto rounded-3xl bg-slate-950 p-4 text-sm text-slate-100">
              {JSON.stringify(result, null, 2)}
            </pre>
          ) : (
            <p className="text-sm text-slate-500">Upload a report to see workflow outputs and any extracted recommendations.</p>
          )}
        </Card>
      </div>
    </div>
  );
}
