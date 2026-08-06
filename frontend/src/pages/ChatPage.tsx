import { useState } from "react";
import toast from "react-hot-toast";
import PageHeading from "../components/PageHeading";
import Card from "../components/Card";
import { sendChat } from "../api/chat";
import type { ChatPayload } from "../api/chat";

export default function ChatPage() {
  const [message, setMessage] = useState("");
  const [reply, setReply] = useState<string | null>(null);

  const handleSubmit = async () => {
    if (!message.trim()) {
      toast.error("Enter a message.");
      return;
    }

    try {
      const result = await sendChat({ message });
      setReply(result.data?.reply ?? "No reply available.");
      toast.success("Chat processed.");
    } catch (error) {
      toast.error("Chat interaction failed.");
    }
  };

  return (
    <div className="space-y-10">
      <PageHeading title="Clinical Chat" description="Ask the AI for explanations, recommendations, or workflow guidance." />
      <div className="grid gap-6 xl:grid-cols-3">
        <Card title="Ask a question">
          <textarea
            rows={6}
            value={message}
            onChange={(event) => setMessage(event.target.value)}
            className="w-full rounded-3xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-brand-400 focus:ring-4 focus:ring-brand-100"
            placeholder="Describe the clinical scenario or ask for treatment guidance."
          />
          <button
            onClick={handleSubmit}
            className="mt-4 w-full rounded-2xl bg-brand-600 px-4 py-3 text-sm font-semibold text-white transition hover:bg-brand-700"
          >
            Send message
          </button>
        </Card>

        <Card title="Assistant reply">
          <p className="text-sm text-slate-500">{reply || "Your clinical assistant reply will appear here."}</p>
        </Card>
      </div>
    </div>
  );
}
