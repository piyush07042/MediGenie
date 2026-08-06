import { useState } from "react";
import toast from "react-hot-toast";
import PageHeading from "../components/PageHeading";
import Card from "../components/Card";
import { sendChat } from "../api/chat";
import type { ChatPayload } from "../api/chat";

export default function KnowledgePage() {
  const [query, setQuery] = useState("");
  const [response, setResponse] = useState<string | null>(null);

  const handleSubmit = async () => {
    if (!query.trim()) {
      toast.error("Enter a knowledge query.");
      return;
    }

    try {
      const result = await sendChat({ message: query });
      setResponse(result.data?.reply ?? "No response.");
      toast.success("Query sent.");
    } catch (error) {
      toast.error("Knowledge request failed.");
    }
  };

  return (
    <div className="space-y-10">
      <PageHeading title="Knowledge Base" description="Search clinical knowledge and AI-driven summaries." />
      <div className="grid gap-6 xl:grid-cols-3">
        <Card title="Ask MediGenie">
          <textarea
            rows={6}
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            className="w-full rounded-3xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-brand-400 focus:ring-4 focus:ring-brand-100"
            placeholder="Ask about stroke risk, patient symptoms, or medication guidelines."
          />
          <button
            onClick={handleSubmit}
            className="mt-4 w-full rounded-2xl bg-brand-600 px-4 py-3 text-sm font-semibold text-white transition hover:bg-brand-700"
          >
            Query knowledge
          </button>
        </Card>

        <Card title="Response">
          <p className="text-sm text-slate-500">{response || "Ask a clinical question to get a reply."}</p>
        </Card>
      </div>
    </div>
  );
}
