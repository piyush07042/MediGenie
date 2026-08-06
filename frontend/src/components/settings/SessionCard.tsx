import { useMemo } from "react";
import { useAuthStore } from "../../store/authStore";
import Card from "../Card";
import type { User } from "../../types/api";

function formatDate(value: string | null) {
  if (!value) {
    return "Unknown";
  }

  return new Intl.DateTimeFormat("en-US", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

export default function SessionCard({ user, token }: { user: User | null; token: string | null }) {
  const logout = useAuthStore((state) => state.logout);

  const browser = useMemo(() => {
    if (typeof navigator === "undefined") return "Browser";
    return `${navigator.platform} · ${navigator.userAgent.split(" ")[0]}`;
  }, []);

  const expiry = useMemo(() => {
    if (!token) return null;
    try {
      const payload = JSON.parse(atob(token.split(".")[1]));
      return payload.exp ? new Date(payload.exp * 1000).toISOString() : null;
    } catch {
      return null;
    }
  }, [token]);

  const currentLogin = useMemo(() => {
    if (!token) return null;
    try {
      const payload = JSON.parse(atob(token.split(".")[1]));
      return payload.iat ? new Date(payload.iat * 1000).toISOString() : null;
    } catch {
      return null;
    }
  }, [token]);

  return (
    <Card title="Session">
      <div className="space-y-5">
        <div className="rounded-3xl border border-slate-200 bg-slate-50 p-4">
          <p className="text-sm text-slate-500">Login status</p>
          <p className="mt-2 text-base font-semibold text-slate-900">{user ? "Signed in" : "Not signed in"}</p>
        </div>

        <div className="grid gap-3 sm:grid-cols-2">
          <div className="rounded-3xl border border-slate-200 bg-white p-4">
            <p className="text-sm text-slate-500">Current login</p>
            <p className="mt-2 text-sm font-semibold text-slate-900">{currentLogin ? formatDate(currentLogin) : "Unavailable"}</p>
          </div>
          <div className="rounded-3xl border border-slate-200 bg-white p-4">
            <p className="text-sm text-slate-500">JWT expiry</p>
            <p className="mt-2 text-sm font-semibold text-slate-900">{expiry ? formatDate(expiry) : "Unavailable"}</p>
          </div>
        </div>

        <div className="rounded-3xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-700">
          <p className="font-semibold text-slate-900">Current browser</p>
          <p className="mt-2 text-slate-500">{browser}</p>
        </div>

        {user ? (
          <button
            type="button"
            onClick={() => void logout()}
            className="w-full rounded-2xl bg-red-600 px-4 py-3 text-sm font-semibold text-white transition hover:bg-red-700"
          >
            Logout
          </button>
        ) : null}
      </div>
    </Card>
  );
}
