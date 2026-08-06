import { NavLink } from "react-router-dom";
import {
  Cpu,
  Users,
  Upload,
  ShieldCheck,
  ClipboardPaste,
  MessageSquare,
  BookOpen,
  Settings,
} from "lucide-react";

const navItems = [
  { label: "Dashboard", path: "/", icon: Cpu },
  { label: "Patients", path: "/patients", icon: Users },
  { label: "Upload Medical Report", path: "/upload-report", icon: Upload },
  { label: "Disease Prediction", path: "/predictions", icon: ShieldCheck },
  { label: "AI Reports", path: "/reports", icon: ClipboardPaste },
  { label: "Drug Safety", path: "/drug-safety", icon: BookOpen },
  { label: "AI Chat", path: "/chat", icon: MessageSquare },
  { label: "Settings", path: "/settings", icon: Settings },
];

export default function Sidebar() {
  return (
    <aside className="hidden h-full w-80 flex-col gap-6 rounded-3xl border border-slate-200 bg-white px-6 py-8 shadow-soft xl:flex">
      <div className="space-y-2">
        <p className="text-sm font-semibold uppercase tracking-[0.3em] text-slate-400">Navigation</p>
        <h2 className="text-2xl font-semibold text-slate-900">MediGenie Suite</h2>
      </div>
      <nav className="flex flex-col gap-2">
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center gap-3 rounded-2xl px-4 py-3 text-sm font-medium transition ${
                  isActive ? "bg-brand-500 text-white" : "text-slate-600 hover:bg-slate-100"
                }`
              }
            >
              <span className="flex h-10 w-10 items-center justify-center rounded-2xl bg-slate-100 text-brand-600">
                <Icon className="h-5 w-5" />
              </span>
              {item.label}
            </NavLink>
          );
        })}
      </nav>
    </aside>
  );
}
