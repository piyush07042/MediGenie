import { useEffect, useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import toast from "react-hot-toast";
import PageHeading from "../components/PageHeading";
import Card from "../components/Card";
import { listPatients } from "../api/patients";
import { sendChat, type ChatPayload, type ChatResponseData } from "../api/chat";
import type { Patient } from "../types/api";

type ChatMessage = {
  id: string;
  role: "user" | "assistant";
  text: string;
  timestamp: string;
};

const CHAT_STORAGE_KEY = "medigenie_chat_history_v1";

const QUICK_PROMPTS = [
  "Summarize the patient's current risk profile and next steps.",
  "Review the latest clinical data and suggest a treatment plan.",
  "Identify any medication conflicts and allergy concerns.",
  "Explain this patient's potential diagnosis in plain terms.",
];

function formatTime(timestamp: string) {
  return new Intl.DateTimeFormat("en-US", {
    hour: "numeric",
    minute: "2-digit",
  }).format(new Date(timestamp));
}

function makeId() {
  return `${Date.now()}-${Math.random().toString(36).slice(2, 10)}`;
}

export default function ChatPage() {
  const [selectedPatientId, setSelectedPatientId] = useState<number | null>(null);
  const [message, setMessage] = useState("");
  const [symptoms, setSymptoms] = useState("");
  const [medications, setMedications] = useState("");
  const [allergies, setAllergies] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [clinicalSummary, setClinicalSummary] = useState<string | null>(null);
  const [isSending, setIsSending] = useState(false);

  const patientsQuery = useQuery({ queryKey: ["patients"], queryFn: listPatients, staleTime: 1000 * 60 * 5 });
  const patients = patientsQuery.data?.data ?? [];

  const selectedPatient = useMemo(
    () => patients.find((patient) => patient.id === selectedPatientId) ?? null,
    [patients, selectedPatientId]
  );

  useEffect(() => {
    const stored = localStorage.getItem(CHAT_STORAGE_KEY);
    if (stored) {
      try {
        const parsed = JSON.parse(stored) as ChatMessage[];
        setMessages(parsed);
      } catch {
        setMessages([]);
      }
    }
  }, []);

  useEffect(() => {
    localStorage.setItem(CHAT_STORAGE_KEY, JSON.stringify(messages));
  }, [messages]);

  const handleConversationReset = () => {
    setMessages([]);
    setClinicalSummary(null);
    localStorage.removeItem(CHAT_STORAGE_KEY);
  };

  const handleSend = async () => {
    if (!message.trim()) {
      toast.error("Please type a clinical question or prompt.");
      return;
    }

    const newUserMessage: ChatMessage = {
      id: makeId(),
      role: "user",
      text: message.trim(),
      timestamp: new Date().toISOString(),
    };
    setMessages((current) => [...current, newUserMessage]);
    setMessage("");
    setIsSending(true);

    const payload: ChatPayload = {
      message: newUserMessage.text,
    };

    if (selectedPatient) {
      payload.patient_context = {
        id: selectedPatient.id,
        first_name: selectedPatient.first_name,
        last_name: selectedPatient.last_name,
        age: selectedPatient.age,
        gender: selectedPatient.gender,
        allergies: selectedPatient.allergies || [],
        current_medications: selectedPatient.current_medications || [],
        medical_history: selectedPatient.medical_history || {},
      };
    }

    if (symptoms.trim()) {
      payload.symptoms = symptoms
        .split(",")
        .map((item) => item.trim())
        .filter(Boolean);
    }

    if (medications.trim()) {
      payload.medications = medications
        .split(",")
        .map((item) => item.trim())
        .filter(Boolean);
    }

    if (allergies.trim()) {
      payload.allergies = allergies
        .split(",")
        .map((item) => item.trim())
        .filter(Boolean);
    }

    try {
      const result = await sendChat(payload);
      const reply = result.data?.reply ?? "The assistant did not return a response.";
      const newAssistantMessage: ChatMessage = {
        id: makeId(),
        role: "assistant",
        text: reply,
        timestamp: new Date().toISOString(),
      };
      setMessages((current) => [...current, newAssistantMessage]);
      setClinicalSummary(result.data?.clinical_summary ?? null);
      toast.success("AI assistant replied successfully.");
    } catch (error) {
      toast.error("Unable to send your question. Check your connection and try again.");
    } finally {
      setIsSending(false);
    }
  };

  const handlePromptClick = (prompt: string) => {
    setMessage(prompt);
  };

  return (
    <div className="space-y-10">
      <PageHeading
        title="AI Medical Assistant"
        description="Use patient context, symptoms and clinical prompts to get fast, evidence-informed guidance from MediGenie."
      />

      <div className="grid gap-6 xl:grid-cols-[1.4fr_0.9fr]">
        <div className="space-y-6">
          <Card title="Clinical conversation">
            <div className="flex flex-col gap-4">
              <div className="rounded-3xl border border-slate-200 bg-slate-50 p-4">
                <p className="text-sm text-slate-500">
                  Ask questions about diagnosis, treatment planning, medication safety, or workflow next steps. Your selected patient profile will be used to provide more relevant clinical context.
                </p>
              </div>

              <div className="min-h-[420px] overflow-hidden rounded-[2rem] border border-slate-200 bg-white shadow-inner">
                <div className="flex h-full flex-col overflow-hidden">
                  <div className="flex-1 overflow-y-auto p-6 space-y-4 bg-slate-100">
                    {messages.length === 0 ? (
                      <div className="rounded-3xl border border-dashed border-slate-300 bg-white p-8 text-center text-slate-500">
                        <p className="text-lg font-semibold text-slate-900">Begin the chat with a clinical question</p>
                        <p className="mt-2 text-sm">Your messages and assistant responses will appear here.</p>
                      </div>
                    ) : (
                      messages.map((item) => (
                        <div
                          key={item.id}
                          className={`flex ${item.role === "assistant" ? "justify-start" : "justify-end"}`}
                        >
                          <div
                            className={`max-w-[85%] rounded-[2rem] p-5 shadow-sm ${
                              item.role === "assistant"
                                ? "bg-white text-slate-900 border border-slate-200"
                                : "bg-brand-600 text-white"
                            }`}
                          >
                            <div className="flex items-center justify-between gap-3 text-xs uppercase tracking-[0.2em] text-slate-500">
                              <span>{item.role === "assistant" ? "MediGenie Assistant" : "You"}</span>
                              <span>{formatTime(item.timestamp)}</span>
                            </div>
                            <p className="mt-3 whitespace-pre-wrap text-sm leading-6">
                              {item.text}
                            </p>
                          </div>
                        </div>
                      ))
                    )}
                    {isSending ? (
                      <div className="flex justify-start">
                        <div className="max-w-[70%] rounded-[2rem] bg-slate-200 p-5 shadow-sm">
                          <div className="h-3 w-24 animate-pulse rounded-full bg-slate-300" />
                          <div className="mt-3 grid gap-2">
                            <div className="h-3 rounded-full bg-slate-300" />
                            <div className="h-3 rounded-full bg-slate-300" />
                            <div className="h-3 rounded-full bg-slate-300" />
                          </div>
                        </div>
                      </div>
                    ) : null}
                  </div>

                  <div className="border-t border-slate-200 bg-white p-6">
                    <label htmlFor="assistant-message" className="sr-only">
                      Clinical question
                    </label>
                    <textarea
                      id="assistant-message"
                      rows={4}
                      value={message}
                      onChange={(event) => setMessage(event.target.value)}
                      className="w-full resize-none rounded-3xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-brand-400 focus:ring-4 focus:ring-brand-100"
                      placeholder="Type a clinical question, such as ‘What is the next step for this patient?’"
                    />
                    <div className="mt-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                      <div className="flex flex-wrap gap-2 text-sm text-slate-500">
                        <span>{selectedPatient ? `${selectedPatient.first_name} ${selectedPatient.last_name}` : "No patient selected"}</span>
                        <span className="text-slate-300">•</span>
                        <span>{selectedPatient ? `${selectedPatient.age} years · ${selectedPatient.gender}` : "Use the patient sidebar to add context."}</span>
                      </div>
                      <div className="flex gap-3">
                        <button
                          type="button"
                          onClick={handleConversationReset}
                          className="rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-50"
                        >
                          Reset conversation
                        </button>
                        <button
                          type="button"
                          onClick={handleSend}
                          disabled={isSending}
                          className="inline-flex items-center justify-center rounded-2xl bg-brand-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-brand-700 disabled:cursor-not-allowed disabled:bg-slate-300"
                        >
                          {isSending ? "Sending…" : "Send to assistant"}
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </Card>

          <Card title="Latest clinical summary">
            <p className="text-sm text-slate-600">
              The assistant will show a concise summary here when clinical context is available.
            </p>
            <div className="mt-4 min-h-[110px] rounded-3xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-700">
              {clinicalSummary ? (
                <p className="whitespace-pre-wrap">{clinicalSummary}</p>
              ) : (
                <p className="text-slate-500">No summary available yet. Ask a question to generate one.</p>
              )}
            </div>
          </Card>
        </div>

        <div className="space-y-6">
          <Card title="Patient context">
            <div className="space-y-4">
              <div>
                <label htmlFor="patient-select" className="block text-sm font-medium text-slate-700">
                  Select patient profile
                </label>
                <select
                  id="patient-select"
                  value={selectedPatientId ?? ""}
                  onChange={(event) => setSelectedPatientId(event.target.value ? Number(event.target.value) : null)}
                  className="mt-2 w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-brand-400 focus:ring-4 focus:ring-brand-100"
                >
                  <option value="">No patient selected</option>
                  {patients.map((patient) => (
                    <option key={patient.id} value={patient.id}>
                      {patient.first_name} {patient.last_name} · ID {patient.id}
                    </option>
                  ))}
                </select>
              </div>

              <div className="space-y-4">
                <div>
                  <label htmlFor="symptoms" className="block text-sm font-medium text-slate-700">
                    Symptoms
                  </label>
                  <input
                    id="symptoms"
                    type="text"
                    value={symptoms}
                    onChange={(event) => setSymptoms(event.target.value)}
                    placeholder="Fever, chest pain, fatigue"
                    className="mt-2 w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-brand-400 focus:ring-4 focus:ring-brand-100"
                  />
                </div>
                <div>
                  <label htmlFor="medications" className="block text-sm font-medium text-slate-700">
                    Medications
                  </label>
                  <input
                    id="medications"
                    type="text"
                    value={medications}
                    onChange={(event) => setMedications(event.target.value)}
                    placeholder="Aspirin, Lisinopril"
                    className="mt-2 w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-brand-400 focus:ring-4 focus:ring-brand-100"
                  />
                </div>
                <div>
                  <label htmlFor="allergies" className="block text-sm font-medium text-slate-700">
                    Allergies
                  </label>
                  <input
                    id="allergies"
                    type="text"
                    value={allergies}
                    onChange={(event) => setAllergies(event.target.value)}
                    placeholder="Penicillin, latex"
                    className="mt-2 w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-brand-400 focus:ring-4 focus:ring-brand-100"
                  />
                </div>
              </div>

              <div className="rounded-3xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-600">
                <p className="font-semibold text-slate-900">Patient record details</p>
                {selectedPatient ? (
                  <div className="mt-3 space-y-2 text-sm text-slate-700">
                    <p>{selectedPatient.first_name} {selectedPatient.last_name}</p>
                    <p>ID {selectedPatient.id}</p>
                    <p>Age {selectedPatient.age} · {selectedPatient.gender}</p>
                    <p>Medications: {selectedPatient.current_medications?.join(", ") || "None listed"}</p>
                    <p>Allergies: {selectedPatient.allergies?.join(", ") || "None listed"}</p>
                  </div>
                ) : (
                  <p className="mt-3 text-slate-500">Choose a patient above to include clinical context in your chat.</p>
                )}
              </div>
            </div>
          </Card>

          <Card title="Quick clinical prompts">
            <div className="space-y-3">
              <p className="text-sm text-slate-600">Jump-start the conversation with common medical review prompts.</p>
              <div className="grid gap-3">
                {QUICK_PROMPTS.map((prompt) => (
                  <button
                    type="button"
                    key={prompt}
                    onClick={() => handlePromptClick(prompt)}
                    className="rounded-3xl border border-slate-200 bg-white px-4 py-4 text-left text-sm text-slate-700 transition hover:border-brand-400 hover:bg-slate-50"
                  >
                    {prompt}
                  </button>
                ))}
              </div>
            </div>
          </Card>

          <Card title="Medicolegal guidance">
            <p className="text-sm text-slate-600">
              The AI assistant can help summarize risk factors, explain clinical recommendations, and highlight possible drug or allergy concerns based on the provided patient data.
            </p>
          </Card>
        </div>
      </div>
    </div>
  );
}
