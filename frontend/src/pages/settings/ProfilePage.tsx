import { useMemo } from "react";
import PageHeading from "../../components/PageHeading";
import Card from "../../components/Card";
import { useAuthStore } from "../../store/authStore";

export default function ProfilePage() {
  const user = useAuthStore((state) => state.user);
  const token = useAuthStore((state) => state.token);

  const sessionExpiry = useMemo(() => {
    if (!token) return null;

    try {
      const payload = JSON.parse(atob(token.split(".")[1]));
      return payload.exp ? new Date(payload.exp * 1000).toLocaleString() : null;
    } catch {
      return null;
    }
  }, [token]);

  return (
    <div className="space-y-10">
      <PageHeading title="User profile" description="Review your authenticated account details and current browser session." />

      <div className="grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
        <div className="space-y-6">
          <Card title="Account overview">
            <div className="space-y-5">
              <div className="rounded-3xl border border-slate-200 bg-slate-50 p-5">
                <p className="text-sm text-slate-500">Full name</p>
                <p className="mt-2 text-lg font-semibold text-slate-900">{user?.full_name ?? "Unknown"}</p>
              </div>
              <div className="rounded-3xl border border-slate-200 bg-slate-50 p-5">
                <p className="text-sm text-slate-500">Email address</p>
                <p className="mt-2 text-lg font-semibold text-slate-900">{user?.email ?? "Unknown"}</p>
              </div>
              <div className="grid gap-4 sm:grid-cols-2">
                <div className="rounded-3xl border border-slate-200 bg-white p-5">
                  <p className="text-sm text-slate-500">Role</p>
                  <p className="mt-2 text-sm font-semibold text-slate-900">{user?.role ?? "Not available"}</p>
                </div>
                <div className="rounded-3xl border border-slate-200 bg-white p-5">
                  <p className="text-sm text-slate-500">Account status</p>
                  <p className="mt-2 text-sm font-semibold text-slate-900">{user ? "Active" : "Not signed in"}</p>
                </div>
              </div>
            </div>
          </Card>

          <Card title="Session and security">
            <div className="space-y-4 text-sm text-slate-700">
              <p>
                <span className="font-semibold text-slate-900">Signed in:</span> {user ? "Yes" : "No"}
              </p>
              <p>
                <span className="font-semibold text-slate-900">Login source:</span> {typeof navigator !== "undefined" ? `${navigator.platform}` : "Browser"}
              </p>
              <p>
                <span className="font-semibold text-slate-900">Token expiry:</span> {sessionExpiry ?? "Unknown"}
              </p>
            </div>
          </Card>
        </div>

        <div className="space-y-6">
          <Card title="Profile actions">
            <div className="space-y-4 text-sm text-slate-600">
              <p>This page shows profile data from the authenticated session. Backend updates for profile editing and password change are not available.</p>
              <div className="rounded-3xl border border-slate-200 bg-slate-50 p-4">
                <p className="text-sm font-semibold text-slate-900">Edit profile</p>
                <p className="mt-2 text-slate-500">Available when backend support is implemented.</p>
              </div>
              <div className="rounded-3xl border border-slate-200 bg-slate-50 p-4">
                <p className="text-sm font-semibold text-slate-900">Change password</p>
                <p className="mt-2 text-slate-500">Available when backend support is implemented.</p>
              </div>
              <div className="rounded-3xl border border-slate-200 bg-slate-50 p-4">
                <p className="text-sm font-semibold text-slate-900">Avatar upload</p>
                <p className="mt-2 text-slate-500">Available when backend support is implemented.</p>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
