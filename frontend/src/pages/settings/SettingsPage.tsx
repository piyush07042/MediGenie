import { useNavigate } from "react-router-dom";
import PageHeading from "../../components/PageHeading";
import ProfileCard from "../../components/settings/ProfileCard";
import ThemeSettings from "../../components/settings/ThemeSettings";
import NotificationSettings from "../../components/settings/NotificationSettings";
import LanguageSettings from "../../components/settings/LanguageSettings";
import SessionCard from "../../components/settings/SessionCard";
import AccountInformation from "../../components/settings/AccountInformation";
import { useAuthStore } from "../../store/authStore";

export default function SettingsPage() {
  const navigate = useNavigate();
  const user = useAuthStore((state) => state.user);
  const token = useAuthStore((state) => state.token);

  return (
    <div className="space-y-10">
      <div className="flex flex-col gap-4 xl:flex-row xl:items-center xl:justify-between">
        <PageHeading title="Settings" description="Manage your MediGenie preferences, session details, and local client settings." />
        <button
          type="button"
          onClick={() => navigate("/settings/profile")}
          className="inline-flex items-center justify-center rounded-2xl bg-brand-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-brand-700"
        >
          Open profile details
        </button>
      </div>

      <div className="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
        <div className="space-y-6">
          <ProfileCard user={user} />
          <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-soft">
            <h2 className="text-xl font-semibold text-slate-900">Security</h2>
            <p className="mt-2 text-sm text-slate-500">Change password is unavailable until backend support is implemented.</p>
            <div className="mt-6 space-y-4">
              <div>
                <label className="mb-2 block text-sm font-medium text-slate-700" htmlFor="current-password">
                  Current Password
                </label>
                <input
                  id="current-password"
                  type="password"
                  disabled
                  className="w-full rounded-2xl border border-slate-200 bg-slate-100 px-4 py-3 text-sm text-slate-500 outline-none"
                  placeholder="Current password"
                />
              </div>
              <div>
                <label className="mb-2 block text-sm font-medium text-slate-700" htmlFor="new-password">
                  New Password
                </label>
                <input
                  id="new-password"
                  type="password"
                  disabled
                  className="w-full rounded-2xl border border-slate-200 bg-slate-100 px-4 py-3 text-sm text-slate-500 outline-none"
                  placeholder="New password"
                />
              </div>
              <div>
                <label className="mb-2 block text-sm font-medium text-slate-700" htmlFor="confirm-password">
                  Confirm Password
                </label>
                <input
                  id="confirm-password"
                  type="password"
                  disabled
                  className="w-full rounded-2xl border border-slate-200 bg-slate-100 px-4 py-3 text-sm text-slate-500 outline-none"
                  placeholder="Confirm new password"
                />
              </div>
              <button type="button" disabled className="w-full rounded-2xl bg-slate-300 px-4 py-3 text-sm font-semibold text-slate-600" >
                Change Password
              </button>
            </div>
          </div>
          <ThemeSettings />
          <NotificationSettings />
          <LanguageSettings />
        </div>

        <div className="space-y-6">
          <SessionCard user={user} token={token} />
          <AccountInformation user={user} />
          <div className="rounded-3xl border border-slate-200 bg-slate-50 p-6">
            <h2 className="text-xl font-semibold text-slate-900">Backend support required</h2>
            <div className="mt-4 space-y-3 text-sm text-slate-600">
              <p>Features below are disabled until backend support is added:</p>
              <ul className="list-inside list-disc space-y-2">
                <li>Edit profile</li>
                <li>Avatar upload</li>
                <li>Login history</li>
                <li>Device management</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
