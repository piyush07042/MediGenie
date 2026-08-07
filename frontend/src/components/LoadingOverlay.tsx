import React from "react";

export default function LoadingOverlay({ visible }: { visible: boolean }) {
  if (!visible) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <div className="rounded-lg bg-white px-6 py-4 text-center shadow-lg">
        <div className="mb-2 text-lg font-semibold">Loading…</div>
        <div className="h-2 w-40 overflow-hidden rounded-full bg-slate-100">
          <div className="h-2 w-20 animate-pulse rounded-full bg-brand-600" />
        </div>
      </div>
    </div>
  );
}
