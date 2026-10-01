"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useRequireAuth } from "../../lib/auth";
import { Icon } from "../../components/Icons";

type HistoryItem = {
  id: number;
  health_score: number;
  health_category: string;
  qmi_score: number | null;
  anomaly_score: number;
  created_at: string;
};

type HistoryResponse = {
  success: boolean;
  count: number;
  history: HistoryItem[];
};

type DeleteHistoryResponse = {
  success: boolean;
  message: string;
  deleted_count: number;
};

const API =
  process.env.NEXT_PUBLIC_API_URL ||
  "http://127.0.0.1:8000";

const actions = [
  {
    title: "Analyzer",
    description:
      "Measure QHI, gates, depth and anomaly signals.",
    href: "/analyzer",
    icon: "analyze",
    number: "01",
  },
  {
    title: "AI Debugger",
    description:
      "Find common quantum errors and generate a fix.",
    href: "/debugger",
    icon: "bug",
    number: "02",
  },
  {
    title: "Optimizer",
    description:
      "Remove redundant operations and compare metrics.",
    href: "/optimizer",
    icon: "zap",
    number: "03",
  },
];

export default function Dashboard() {
  const { user, loading } = useRequireAuth();

  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [historyLoading, setHistoryLoading] =
    useState(true);

  const [showResetConfirm, setShowResetConfirm] =
    useState(false);

  const [resetting, setResetting] = useState(false);

  const [resetStatus, setResetStatus] = useState("");

  useEffect(() => {
    if (loading || !user) return;

    const token = localStorage.getItem("qi_token");

    if (!token) {
      setHistoryLoading(false);
      return;
    }

    async function loadHistory() {
      try {
        const response = await fetch(
          `${API}/api/history?limit=50`,
          {
            headers: {
              Authorization: `Bearer ${token}`,
              Accept: "application/json",
            },
          }
        );

        if (!response.ok) {
          throw new Error(
            "Failed to load dashboard history."
          );
        }

        const data: HistoryResponse =
          await response.json();

        setHistory(data.history || []);
      } catch (error) {
        console.error(
          "[QuantumInsight Dashboard]",
          error
        );
      } finally {
        setHistoryLoading(false);
      }
    }

    loadHistory();
  }, [loading, user]);

  async function resetDashboardData() {
    const token = localStorage.getItem("qi_token");

    if (!token) {
      setResetStatus(
        "Authentication session not found."
      );
      return;
    }

    try {
      setResetting(true);
      setResetStatus("");

      const response = await fetch(
        `${API}/api/history`,
        {
          method: "DELETE",
          headers: {
            Authorization: `Bearer ${token}`,
            Accept: "application/json",
          },
        }
      );

      const data:
        | DeleteHistoryResponse
        | { detail?: string } =
        await response
          .json()
          .catch(() => ({}));

      if (!response.ok) {
        throw new Error(
          "detail" in data && data.detail
            ? data.detail
            : `Failed to reset dashboard (${response.status})`
        );
      }

      setHistory([]);
      setShowResetConfirm(false);

      setResetStatus(
        `Dashboard data reset successfully${
          "deleted_count" in data
            ? ` (${data.deleted_count} analyses deleted)`
            : ""
        }.`
      );

      window.setTimeout(() => {
        setResetStatus("");
      }, 4000);
    } catch (error) {
      setResetStatus(
        error instanceof Error
          ? error.message
          : "Failed to reset dashboard data."
      );
    } finally {
      setResetting(false);
    }
  }

  if (loading || !user) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <div className="flex items-center gap-3 text-sm text-slate-500">
          <span className="h-2 w-2 animate-pulse rounded-full bg-cyan-300" />
          Loading workspace…
        </div>
      </div>
    );
  }

  const analyses = history.length;

  const averageQHI =
    analyses > 0
      ? history.reduce(
          (sum, item) =>
            sum + Number(item.health_score || 0),
          0
        ) / analyses
      : null;

  const qmiScores = history
    .map((item) => Number(item.qmi_score))
    .filter((score) => Number.isFinite(score));

  const averageQMI =
    qmiScores.length > 0
      ? qmiScores.reduce(
          (sum, score) => sum + score,
          0
        ) / qmiScores.length
      : null;

  const averageAnomaly =
    analyses > 0
      ? history.reduce(
          (sum, item) =>
            sum + Number(item.anomaly_score || 0),
          0
        ) / analyses
      : null;

  const qhiProgress =
    averageQHI !== null
      ? Math.max(0, Math.min(100, averageQHI))
      : 0;

  const qmiProgress =
    averageQMI !== null
      ? Math.max(0, Math.min(100, averageQMI))
      : 0;

  return (
    <div className="space-y-7">
      {/* Hero */}
      <section className="relative overflow-hidden rounded-3xl border border-cyan-400/10 bg-gradient-to-br from-cyan-500/[.10] via-slate-950/60 to-violet-600/[.12] p-6 shadow-[0_20px_80px_rgba(0,0,0,.18)] sm:p-8 lg:p-9">
        <div className="pointer-events-none absolute -right-20 -top-28 h-72 w-72 rounded-full bg-cyan-400/10 blur-3xl" />

        <div className="pointer-events-none absolute -bottom-32 left-1/3 h-56 w-56 rounded-full bg-violet-500/10 blur-3xl" />

        <div className="relative">
          <div className="flex flex-col justify-between gap-8 lg:flex-row lg:items-end">
            <div className="max-w-2xl">
              <div className="flex items-center gap-2">
                <span className="h-1.5 w-1.5 rounded-full bg-cyan-300 shadow-[0_0_12px_rgba(34,211,238,.8)]" />

                <p className="section-kicker">
                  Quantum workspace
                </p>
              </div>

              <h1 className="mt-3 text-3xl font-black tracking-tight text-white sm:text-4xl lg:text-[42px]">
                Welcome back,{" "}
                <span className="text-cyan-300">
                  {user.name.split(" ")[0]}.
                </span>
              </h1>

              <p className="mt-4 max-w-xl text-sm leading-7 text-slate-400">
                Analyze, debug and optimize your quantum
                circuits from one intelligent workspace.
              </p>
            </div>

            <div className="flex flex-col gap-2 sm:flex-row">
              <Link
                href="/analyzer"
                className="btn btn-primary shrink-0"
              >
                <Icon name="zap" size={15} />
                New circuit analysis
                <Icon name="arrow" size={15} />
              </Link>

              <button
                type="button"
                onClick={() => {
                  setResetStatus("");
                  setShowResetConfirm(true);
                }}
                disabled={history.length === 0}
                className="inline-flex shrink-0 items-center justify-center gap-2 rounded-xl border border-rose-400/20 bg-rose-400/5 px-4 py-2 text-sm font-semibold text-rose-300 transition hover:border-rose-400/30 hover:bg-rose-400/10 hover:text-rose-200 disabled:cursor-not-allowed disabled:opacity-40"
              >
                <Icon name="trash" size={15} />
                Reset Data
              </button>
            </div>
          </div>

          {/* Hero footer */}
          <div className="mt-8 flex flex-wrap items-center gap-x-6 gap-y-2 border-t border-white/5 pt-5 text-[11px] text-slate-600">
            <span>
              Personal quantum workspace
            </span>

            <span className="hidden h-1 w-1 rounded-full bg-slate-700 sm:block" />

            <span>
              {analyses} saved{" "}
              {analyses === 1 ? "analysis" : "analyses"}
            </span>

            <span className="hidden h-1 w-1 rounded-full bg-slate-700 sm:block" />

            <span className="text-cyan-400/60">
              AI-assisted analysis
            </span>
          </div>
        </div>
      </section>

      {/* Reset status */}
      {resetStatus && (
        <div className="flex items-center gap-3 rounded-xl border border-cyan-400/20 bg-cyan-400/5 px-4 py-3 text-sm text-cyan-300">
          <span className="grid h-6 w-6 place-items-center rounded-full bg-cyan-400/10">
            <Icon name="check" size={14} />
          </span>

          {resetStatus}
        </div>
      )}

      {/* Metrics */}
      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <Metric
          label="QHI average"
          value={
            historyLoading
              ? "…"
              : averageQHI !== null
              ? averageQHI.toFixed(1)
              : "—"
          }
          note={
            averageQHI !== null
              ? "Across saved analyses"
              : "Run an analysis to calculate"
          }
          icon="spark"
        />

        <Metric
          label="QMI average"
          value={
            historyLoading
              ? "…"
              : averageQMI !== null
              ? averageQMI.toFixed(1)
              : "—"
          }
          note={
            averageQMI !== null
              ? "Across analyzed circuits"
              : "Run an analysis to calculate"
          }
          icon="analyze"
        />

        <Metric
          label="Analyses"
          value={
            historyLoading
              ? "…"
              : String(analyses)
          }
          note="Saved workspace analyses"
          icon="history"
        />

        <Metric
          label="Anomalies"
          value={
            historyLoading
              ? "…"
              : averageAnomaly !== null
              ? averageAnomaly.toFixed(1)
              : "—"
          }
          note={
            averageAnomaly !== null
              ? "Average anomaly score"
              : "Awaiting circuit data"
          }
          icon="bug"
        />
      </section>

      {/* Workflows */}
      <section className="card p-6 sm:p-7">
        <div className="flex items-start justify-between gap-4">
          <div>
            <p className="section-kicker">
              Workflows
            </p>

            <h2 className="mt-1 text-xl font-bold text-white">
              Choose your next move
            </h2>

            <p className="mt-1 text-xs text-slate-600">
              Select a tool to continue working with your
              quantum circuits.
            </p>
          </div>

          <span className="badge shrink-0 text-slate-400">
            3 tools
          </span>
        </div>

        <div className="mt-6 grid gap-3 md:grid-cols-3">
          {actions.map((action) => (
            <Link
              key={action.title}
              href={action.href}
              className="group relative overflow-hidden rounded-2xl border border-white/5 bg-white/[.018] p-5 transition duration-200 hover:-translate-y-0.5 hover:border-cyan-400/15 hover:bg-cyan-400/[.025]"
            >
              <div className="absolute right-4 top-4 text-[10px] font-bold tracking-widest text-slate-700 transition group-hover:text-cyan-400/50">
                {action.number}
              </div>

              <div className="grid h-11 w-11 place-items-center rounded-xl border border-cyan-400/10 bg-cyan-400/10 text-cyan-300 transition group-hover:border-cyan-400/20 group-hover:bg-cyan-400/15">
                <Icon
                  name={action.icon}
                  size={19}
                />
              </div>

              <h3 className="mt-5 font-bold text-white">
                {action.title}
              </h3>

              <p className="mt-2 text-xs leading-5 text-slate-500">
                {action.description}
              </p>

              <div className="mt-5 flex items-center gap-2 text-xs font-bold text-cyan-300">
                Open workflow
                <span className="transition-transform group-hover:translate-x-1">
                  <Icon name="arrow" size={13} />
                </span>
              </div>
            </Link>
          ))}
        </div>
      </section>

      {/* QHI + QMI */}
      <section className="grid gap-5 lg:grid-cols-2">
        {/* QHI */}
        <div className="card relative overflow-hidden p-6 sm:p-7">
          <div className="absolute -right-16 -top-16 h-40 w-40 rounded-full bg-cyan-400/5 blur-3xl" />

          <div className="relative">
            <div className="flex items-start justify-between">
              <div>
                <p className="section-kicker">
                  Quantum Health Index
                </p>

                <h2 className="mt-1 text-xl font-bold text-white">
                  Overall health
                </h2>
              </div>

              <div className="grid h-8 w-8 place-items-center rounded-lg bg-cyan-400/5 text-cyan-300">
                <Icon name="shield" size={16} />
              </div>
            </div>

            <div className="mt-7 flex justify-center">
              <div
                className="relative grid h-44 w-44 place-items-center rounded-full"
                style={{
                  background:
                    averageQHI !== null
                      ? `conic-gradient(#22d3ee 0deg, #6366f1 ${
                          qhiProgress * 3.6
                        }deg, rgba(255,255,255,.07) ${
                          qhiProgress * 3.6
                        }deg)`
                      : "conic-gradient(rgba(255,255,255,.07) 0deg, rgba(255,255,255,.07) 360deg)",
                }}
              >
                <div className="absolute inset-[3px] rounded-full bg-slate-950/80" />

                <div className="relative grid h-36 w-36 place-items-center rounded-full border border-white/5 bg-slate-950">
                  <div className="text-center">
                    <div className="text-4xl font-black tracking-tight text-white">
                      {historyLoading
                        ? "…"
                        : averageQHI !== null
                        ? averageQHI.toFixed(1)
                        : "—"}
                    </div>

                    <div className="mt-1 text-[10px] uppercase tracking-[0.18em] text-slate-600">
                      {averageQHI !== null
                        ? "Average QHI"
                        : "No score yet"}
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div className="mt-6 rounded-xl border border-white/5 bg-white/[.02] px-4 py-3 text-center">
              <p className="text-xs leading-5 text-slate-500">
                {averageQHI !== null
                  ? "Based on your saved circuit analyses."
                  : "Analyze your first circuit to populate your QHI."}
              </p>
            </div>
          </div>
        </div>

        {/* QMI */}
        <div className="card relative overflow-hidden p-6 sm:p-7">
          <div className="absolute -right-16 -top-16 h-40 w-40 rounded-full bg-violet-400/5 blur-3xl" />

          <div className="relative">
            <div className="flex items-start justify-between">
              <div>
                <p className="section-kicker">
                  Quantum Maintainability Index
                </p>

                <h2 className="mt-1 text-xl font-bold text-white">
                  Circuit maintainability
                </h2>
              </div>

              <div className="grid h-8 w-8 place-items-center rounded-lg bg-violet-400/5 text-violet-300">
                <Icon name="analyze" size={16} />
              </div>
            </div>

            <div className="mt-7 flex justify-center">
              <div
                className="relative grid h-44 w-44 place-items-center rounded-full"
                style={{
                  background:
                    averageQMI !== null
                      ? `conic-gradient(#a78bfa 0deg, #22d3ee ${
                          qmiProgress * 3.6
                        }deg, rgba(255,255,255,.07) ${
                          qmiProgress * 3.6
                        }deg)`
                      : "conic-gradient(rgba(255,255,255,.07) 0deg, rgba(255,255,255,.07) 360deg)",
                }}
              >
                <div className="absolute inset-[3px] rounded-full bg-slate-950/80" />

                <div className="relative grid h-36 w-36 place-items-center rounded-full border border-white/5 bg-slate-950">
                  <div className="text-center">
                    <div className="text-4xl font-black tracking-tight text-white">
                      {historyLoading
                        ? "…"
                        : averageQMI !== null
                        ? averageQMI.toFixed(1)
                        : "—"}
                    </div>

                    <div className="mt-1 text-[10px] uppercase tracking-[0.18em] text-slate-600">
                      {averageQMI !== null
                        ? "Average QMI"
                        : "No score yet"}
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div className="mt-6 rounded-xl border border-white/5 bg-white/[.02] px-4 py-3 text-center">
              <p className="text-xs leading-5 text-slate-500">
                {averageQMI !== null
                  ? "Based on analyses with QMI measurements."
                  : "Analyze a circuit to populate your QMI."}
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* QHI components */}
      <section className="card p-6 sm:p-7">
        <div className="flex items-start gap-3">
          <div className="grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-violet-400/10 text-violet-300">
            <Icon name="spark" />
          </div>

          <div>
            <h2 className="font-bold text-white">
              How QuantumInsight evaluates a circuit
            </h2>

            <p className="mt-1 text-xs text-slate-500">
              The analyzer combines engineering metrics
              with ML signals.
            </p>
          </div>
        </div>

        <div className="mt-6 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {[
            "Depth efficiency",
            "Gate efficiency",
            "Qubit utilization",
            "2-qubit gate efficiency",
            "Noise exposure",
            "Optimization potential",
          ].map((item, index) => (
            <div
              key={item}
              className="group rounded-xl border border-white/5 bg-white/[.018] p-4 transition hover:border-cyan-400/10 hover:bg-white/[.025]"
            >
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-bold tracking-widest text-cyan-300/80">
                  {String(index + 1).padStart(2, "0")}
                </span>

                <span className="text-[9px] uppercase tracking-widest text-slate-700">
                  Signal
                </span>
              </div>

              <p className="mt-3 text-sm font-semibold text-slate-200">
                {item}
              </p>

              <div className="mt-4 h-1.5 overflow-hidden rounded-full bg-white/5">
                <div className="h-full w-2/3 rounded-full bg-gradient-to-r from-cyan-400 to-violet-500 transition-all group-hover:w-3/4" />
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Reset modal */}
      {showResetConfirm && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/70 px-4 backdrop-blur-sm">
          <div className="w-full max-w-md overflow-hidden rounded-2xl border border-white/10 bg-slate-950 shadow-2xl">
            <div className="border-b border-white/5 px-6 py-5">
              <div className="flex items-start gap-4">
                <div className="grid h-11 w-11 shrink-0 place-items-center rounded-xl bg-rose-400/10 text-rose-300">
                  <Icon name="trash" size={20} />
                </div>

                <div>
                  <h2 className="text-lg font-bold text-white">
                    Reset dashboard data?
                  </h2>

                  <p className="mt-2 text-sm leading-6 text-slate-400">
                    This will permanently delete all your
                    saved analysis history and reset the
                    dashboard metrics.
                  </p>
                </div>
              </div>
            </div>

            <div className="px-6 py-5">
              <div className="rounded-xl border border-white/5 bg-white/[.02] px-4 py-3">
                <p className="text-xs leading-5 text-slate-600">
                  Your account, profile and authentication
                  will not be affected.
                </p>
              </div>

              <div className="mt-5 flex flex-col-reverse gap-3 sm:flex-row sm:justify-end">
                <button
                  type="button"
                  onClick={() =>
                    setShowResetConfirm(false)
                  }
                  disabled={resetting}
                  className="rounded-xl border border-white/10 px-4 py-2.5 text-sm font-semibold text-slate-300 transition hover:bg-white/5 hover:text-white disabled:cursor-not-allowed disabled:opacity-50"
                >
                  Cancel
                </button>

                <button
                  type="button"
                  onClick={resetDashboardData}
                  disabled={resetting}
                  className="rounded-xl bg-rose-500/90 px-4 py-2.5 text-sm font-bold text-white transition hover:bg-rose-500 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {resetting
                    ? "Resetting..."
                    : "Reset Dashboard"}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function Metric({
  label,
  value,
  note,
  icon,
}: {
  label: string;
  value: string;
  note: string;
  icon: string;
}) {
  return (
    <div className="metric group relative overflow-hidden">
      <div className="flex items-center justify-between">
        <p className="text-xs font-bold text-slate-500">
          {label}
        </p>

        <span className="grid h-8 w-8 place-items-center rounded-lg bg-white/[.03] text-slate-600 transition group-hover:bg-cyan-400/10 group-hover:text-cyan-300">
          <Icon name={icon} size={15} />
        </span>
      </div>

      <p className="metric-value mt-3">
        {value}
      </p>

      <p className="mt-1 text-[11px] text-slate-600">
        {note}
      </p>
    </div>
  );
}
