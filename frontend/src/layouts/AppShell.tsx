import { ReactNode } from "react";
import Sidebar from "../components/dashboard/Sidebar";
import TopNavbar from "../components/dashboard/TopNavbar";

export default function AppShell({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <div className="mx-auto flex min-h-screen max-w-[1500px] gap-6 px-4 py-6 sm:px-6 lg:px-8">
        <Sidebar />
        <main className="flex-1 flex flex-col">
          <TopNavbar />
          <div className="flex-1 overflow-hidden">
            <div className="min-h-screen rounded-3xl border border-slate-200 bg-white px-6 py-6 shadow-soft sm:px-8 sm:py-8">
              {children}
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
