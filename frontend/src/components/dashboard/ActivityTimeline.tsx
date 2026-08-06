const events = [
  { id: 1, title: "Patient registered", description: "Dr. Ali added a new patient profile to the registry.", time: "2 hours ago" },
  { id: 2, title: "Prediction completed", description: "Heart disease risk prediction finished for Mia Chen.", time: "4 hours ago" },
  { id: 3, title: "Report uploaded", description: "Radiology report uploaded for Ethan Patel.", time: "6 hours ago" },
  { id: 4, title: "Drug interaction checked", description: "Medication review completed for a care plan.", time: "8 hours ago" },
  { id: 5, title: "OCR completed", description: "Document OCR finished and parsed into AI reports.", time: "Yesterday" },
];

export default function ActivityTimeline() {
  return (
    <section className="rounded-3xl border border-slate-200 bg-white p-6 shadow-soft">
      <div className="mb-5">
        <p className="text-sm font-semibold uppercase tracking-[0.28em] text-slate-400">Activity Timeline</p>
        <h2 className="mt-2 text-xl font-semibold text-slate-900">Platform events</h2>
      </div>
      <div className="space-y-4">
        {events.map((event) => (
          <div key={event.id} className="rounded-3xl border border-slate-100 bg-slate-50 p-4">
            <div className="flex items-center justify-between gap-3 text-sm text-slate-500">
              <p className="font-semibold text-slate-900">{event.title}</p>
              <span>{event.time}</span>
            </div>
            <p className="mt-2 text-sm text-slate-600">{event.description}</p>
          </div>
        ))}
      </div>
    </section>
  );
}
