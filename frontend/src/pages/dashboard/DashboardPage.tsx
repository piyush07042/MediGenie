import { useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { useAuthStore } from "../../store/authStore";
import DashboardHeader from "../../components/dashboard/DashboardHeader";
import StatsCard from "../../components/dashboard/StatsCard";
import QuickActionCard from "../../components/dashboard/QuickActionCard";
import PredictionPieChart from "../../components/dashboard/PredictionPieChart";
import MonthlyTrendChart from "../../components/dashboard/MonthlyTrendChart";
import RiskChart from "../../components/dashboard/RiskChart";
import ReportsChart from "../../components/dashboard/ReportsChart";
import RecentPatients from "../../components/dashboard/RecentPatients";
import RecentReports from "../../components/dashboard/RecentReports";
import RecentPredictions from "../../components/dashboard/RecentPredictions";
import SystemStatus from "../../components/dashboard/SystemStatus";
import ActivityTimeline from "../../components/dashboard/ActivityTimeline";
import type {
  AreaData,
  BarSlice,
  DashboardStat,
  LinePoint,
  PieSlice,
  RecentPatient,
  RecentPrediction,
  RecentReport,
  SystemStatusItem,
} from "../../services/dashboardService";
import {
  getDashboardStats,
  getMonthlyPredictions,
  getPredictionDistribution,
  getRecentPatients,
  getRecentPredictions,
  getRecentReports,
  getReportsAreaData,
  getRiskDistribution,
  getSystemStatus,
} from "../../services/dashboardService";

const actions = [
  { title: "Add Patient", subtitle: "New patient intake", to: "/patients" },
  { title: "Upload Report", subtitle: "Scan a new file", to: "/upload-report" },
  { title: "New Prediction", subtitle: "Run risk analysis", to: "/predictions" },
  { title: "AI Chat", subtitle: "Clinical assistant", to: "/chat" },
  { title: "Drug Safety", subtitle: "Medication review", to: "/drug-safety" },
  { title: "View Reports", subtitle: "Audit reports", to: "/reports" },
];

const cardIcons = [
  "users",
  "clipboard",
  "shield",
  "cpu",
  "alert-circle",
  "file-text",
] as const;

export default function DashboardPage() {
  const user = useAuthStore((state) => state.user);
  const statsQuery = useQuery<DashboardStat[]>({ queryKey: ["dashboard", "stats"], queryFn: getDashboardStats, staleTime: 1000 * 60 * 5 });
  const patientsQuery = useQuery<RecentPatient[]>({ queryKey: ["dashboard", "recentPatients"], queryFn: getRecentPatients, staleTime: 1000 * 60 * 5 });
  const reportsQuery = useQuery<RecentReport[]>({ queryKey: ["dashboard", "recentReports"], queryFn: getRecentReports, staleTime: 1000 * 60 * 5 });
  const predictionsQuery = useQuery<RecentPrediction[]>({ queryKey: ["dashboard", "recentPredictions"], queryFn: getRecentPredictions, staleTime: 1000 * 60 * 5 });
  const statusQuery = useQuery<SystemStatusItem[]>({ queryKey: ["dashboard", "status"], queryFn: getSystemStatus, staleTime: 1000 * 60 * 5 });
  const distributionQuery = useQuery<PieSlice[]>({ queryKey: ["dashboard", "predictionDistribution"], queryFn: getPredictionDistribution, staleTime: 1000 * 60 * 5 });
  const monthlyQuery = useQuery<LinePoint[]>({ queryKey: ["dashboard", "monthlyPredictions"], queryFn: getMonthlyPredictions, staleTime: 1000 * 60 * 5 });
  const riskQuery = useQuery<BarSlice[]>({ queryKey: ["dashboard", "riskDistribution"], queryFn: getRiskDistribution, staleTime: 1000 * 60 * 5 });
  const reportsAreaQuery = useQuery<AreaData[]>({ queryKey: ["dashboard", "reportsArea"], queryFn: getReportsAreaData, staleTime: 1000 * 60 * 5 });

  const greeting = useMemo(() => {
    if (!user) return "Welcome back";
    return `Welcome back, ${user.full_name ?? user.email}`;
  }, [user]);

  const currentDate = useMemo(() => new Date().toLocaleDateString(undefined, { weekday: "long", month: "long", day: "numeric" }), [user]);
  const summary = useMemo(() => "You have 18 pending reports and 4 high-risk patients today.", []);

  const isLoading = [
    statsQuery.isLoading,
    patientsQuery.isLoading,
    reportsQuery.isLoading,
    predictionsQuery.isLoading,
    statusQuery.isLoading,
    distributionQuery.isLoading,
    monthlyQuery.isLoading,
    riskQuery.isLoading,
    reportsAreaQuery.isLoading,
  ].some(Boolean);

  return (
    <div className="space-y-8">
      <DashboardHeader greeting={greeting} subtitle={`Current date: ${currentDate}`} summary={summary} />

      <section className="grid gap-5 xl:grid-cols-[1.5fr_1fr]">
        <div className="space-y-5">
          <div className="grid gap-5 sm:grid-cols-2 xl:grid-cols-3">
            {statsQuery.data?.map((stat) => (
              <StatsCard key={stat.title} title={stat.title} value={stat.value} trend={stat.trend} label={stat.label} positive={stat.positive} />
            ))}
          </div>

          <div className="grid gap-5 xl:grid-cols-2">
            <PredictionPieChart data={distributionQuery.data ?? []} isLoading={distributionQuery.isLoading} />
            <MonthlyTrendChart data={monthlyQuery.data ?? []} isLoading={monthlyQuery.isLoading} />
          </div>

          <div className="grid gap-5 xl:grid-cols-2">
            <RiskChart data={riskQuery.data ?? []} isLoading={riskQuery.isLoading} />
            <ReportsChart data={reportsAreaQuery.data ?? []} isLoading={reportsAreaQuery.isLoading} />
          </div>
        </div>

        <div className="space-y-5">
          <div className="rounded-3xl border border-slate-200 bg-white p-5 shadow-soft">
            <div className="mb-5 flex items-center justify-between">
              <div>
                <p className="text-sm font-semibold uppercase tracking-[0.28em] text-slate-400">Quick Actions</p>
                <h2 className="mt-2 text-xl font-semibold text-slate-900">Fast workflow access</h2>
              </div>
            </div>
            <div className="grid gap-4 md:grid-cols-2">
              {actions.map((action) => (
                <QuickActionCard key={action.title} title={action.title} subtitle={action.subtitle} to={action.to} />
              ))}
            </div>
          </div>

          <SystemStatus data={statusQuery.data ?? []} loading={statusQuery.isLoading} />
          <ActivityTimeline />
        </div>
      </section>

      <section className="grid gap-5 xl:grid-cols-[1.3fr_0.7fr]">
        <RecentPatients data={patientsQuery.data ?? []} loading={patientsQuery.isLoading} />
        <div className="space-y-5">
          <RecentReports data={reportsQuery.data ?? []} loading={reportsQuery.isLoading} />
          <RecentPredictions data={predictionsQuery.data ?? []} loading={predictionsQuery.isLoading} />
        </div>
      </section>

      {isLoading ? (
        <div className="rounded-3xl border border-slate-200 bg-white p-8 shadow-soft">
          <div className="animate-pulse space-y-4">
            <div className="h-5 w-56 rounded-full bg-slate-200" />
            <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
              {Array.from({ length: 4 }).map((_, index) => (
                <div key={index} className="h-24 rounded-3xl bg-slate-100" />
              ))}
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}
