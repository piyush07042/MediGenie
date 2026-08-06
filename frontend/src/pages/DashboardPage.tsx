import { Link } from "react-router-dom";
import PageHeading from "../components/PageHeading";
import Card from "../components/Card";

const tiles = [
  { title: "Patient Registry", description: "Manage patient records and histories.", path: "/patients" },
  { title: "Stroke Risk", description: "Run stroke prediction workflows.", path: "/stroke" },
  { title: "Report Upload", description: "Upload clinical reports for AI analysis.", path: "/upload-report" },
  { title: "Drug Safety", description: "Analyze medication interactions.", path: "/drug-safety" },
  { title: "Knowledge Base", description: "Search indexed clinical knowledge.", path: "/knowledge" },
  { title: "Clinical Chat", description: "Ask questions and get workflow guidance.", path: "/chat" },
  { title: "Reports", description: "Download PDF and HTML patient reports.", path: "/reports" },
];

export default function DashboardPage() {
  return (
    <div className="space-y-10">
      <PageHeading title="Welcome to MediGenie" description="A clinical AI assistant for risk prediction, drug safety, and patient workflows." />
      <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-3">
        {tiles.map((tile) => (
          <Link key={tile.title} to={tile.path} className="group rounded-3xl border border-slate-200 bg-white p-6 shadow-soft transition hover:-translate-y-1 hover:border-brand-200">
            <h2 className="text-xl font-semibold text-slate-900">{tile.title}</h2>
            <p className="mt-3 text-sm text-slate-500">{tile.description}</p>
            <span className="mt-5 inline-flex items-center gap-2 text-brand-600 transition group-hover:translate-x-1">Explore →</span>
          </Link>
        ))}
      </div>
    </div>
  );
}
