import { ReactNode } from "react";
import { NavLink } from "react-router-dom";
import { LogOut, Cpu, Upload, ClipboardPaste, MessageSquare, ShieldCheck, BookOpen, Users } from "lucide-react";
import { useAuthStore } from "../store/authStore";

const navItems = [
  { label: "Dashboard", path: "/" },
  { label: "Patients", path: "/patients" },
  { label: "Stroke", path: "/stroke" },
  { label: "Upload Report", path: "/upload-report" },
  { label: "Drug Safety", path: "/drug-safety" },
  { label: "Knowledge", path: "/knowledge" },
  { label: "Chat", path: "/chat" },
  { label: "Reports", path: "/reports" },
];

const iconMap: Record<string, ReactNode> = {
  Dashboard: <Cpu className="h-4 w-4" />,
  Patients: <Users className="h-4 w-4" />,
  Stroke: <ShieldCheck className="h-4 w-4" />,
  "Upload Report": <Upload className="h-4 w-4" />,
  "Drug Safety": <ClipboardPaste className="h-4 w-4" />,
  Knowledge: <BookOpen className="h-4 w-4" />,
  Chat: <MessageSquare className="h-4 w-4" />,
  Reports: <ClipboardPaste className="h-4 w-4" />,
};

export default function AppShell({ children }: { children: ReactNode }) {
  const logout = useAuthStore((state) => state.logout);
  const user = useAuthStore((state) => state.user);

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <div className="mx-auto flex min-h-screen max-w-[1400px] gap-6 px-4 py-6 sm:px-6 lg:px-8">
        <aside className="hidden w-72 flex-col gap-6 rounded-3xl border border-slate-200 bg-white px-5 py-8 shadow-soft md:flex">
          <div className="space-y-2">
            <div className="text-2xl font-semibold text-slate-900">MediGenie</div>
            <p className="text-sm text-slate-500">Clinical risk prediction and AI workflow platform.</p>
            {user ? <p className="text-sm font-medium text-brand-600">{user.full_name || user.email}</p> : null}
          </div>

          <nav className="flex flex-1 flex-col gap-2">
            {navItems.map((item) => (
              <NavLink
                key={item.label}
                to={item.path}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-2xl px-4 py-3 text-sm font-medium transition ${
                    isActive ? "bg-brand-500 text-white" : "text-slate-600 hover:bg-slate-100"
                  }`
                }
              >
                <span className="text-brand-300">{iconMap[item.label]}</span>
                {item.label}
              </NavLink>
            ))}
          </nav>

          <button
            type="button"
            onClick={() => void logout()}
            className="mt-auto flex items-center justify-center gap-2 rounded-2xl bg-slate-100 px-4 py-3 text-sm text-slate-700 transition hover:bg-slate-200"
          >
            <LogOut className="h-4 w-4" />
            Logout
          </button>
        </aside>

        <main className="flex-1">
          <div className="rounded-3xl border border-slate-200 bg-white px-6 py-6 shadow-soft sm:px-8 sm:py-8">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}
