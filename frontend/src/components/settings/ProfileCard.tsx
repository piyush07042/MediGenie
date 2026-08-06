import { Link } from "react-router-dom";
import Card from "../../components/Card";
import type { User } from "../../types/api";

export default function ProfileCard({ user }: { user: User | null }) {
  const displayName = user?.full_name || user?.email || "Guest";
  const initial = displayName.charAt(0).toUpperCase() || "U";

  return (
    <Card title="Profile">
      <div className="space-y-6">
        <div className="flex items-center gap-4">
          <div className="flex h-16 w-16 items-center justify-center rounded-3xl bg-brand-100 text-brand-700 text-2xl font-semibold">
            {initial}
          </div>
          <div>
            <p className="text-lg font-semibold text-slate-900">{displayName}</p>
            <p className="text-sm text-slate-500">{user ? user.email : "No authenticated user"}</p>
          </div>
        </div>

        <div className="grid gap-3 sm:grid-cols-2">
          <div className="rounded-3xl border border-slate-200 bg-slate-50 p-4">
            <p className="text-sm text-slate-500">Name</p>
            <p className="mt-2 text-sm font-semibold text-slate-900">{user?.full_name || "Unavailable"}</p>
          </div>
          <div className="rounded-3xl border border-slate-200 bg-slate-50 p-4">
            <p className="text-sm text-slate-500">Role</p>
            <p className="mt-2 text-sm font-semibold text-slate-900">{user?.role || "Unavailable"}</p>
          </div>
        </div>

        <div className="rounded-3xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-700">
          <p className="font-semibold text-slate-900">Edit profile</p>
          <p className="mt-2 text-slate-500">Editing your profile requires backend support and is not available yet.</p>
        </div>
      </div>
    </Card>
  );
}
