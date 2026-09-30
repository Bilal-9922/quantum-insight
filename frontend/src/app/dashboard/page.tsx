"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useRequireAuth } from "../../lib/auth";
import { Icon } from "../../components/Icons";

type HistoryItem = {
  id: number;
  health_score: number;
  health_category: string;
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
  [
    "Analyzer",
    "Measure QHI, gates, depth and anomaly signals.",
    "/analyzer",
    "analyze",
  ],
  [
    "AI Debugger",
    "Find common errors and generate a fix.",
    "/debugger",
    "bug",
  ],
  [
    "Optimizer",
    "Remove redundant operations and compare metrics.",
    "/optimizer",
    "zap",
  ],
];

export default function Dashboard() {
  const { user, loading } = useRequireAuth();

  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [historyLoading, setHistoryLoading] = useState(true);

  const [showResetConfirm, setShowResetConfirm] =
    useState(false);

  const [resetting, setResetting] = useState(false);

  const [resetStatus, setResetStatus] =
    useState("");

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

      /*
       * Clear the local dashboard state immediately.
       * Because the dashboard metrics are calculated
       * from this state, all metrics reset automatically.
       */
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
      <div className="py-20 text-center text-slate-500">
        Loading workspace…
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

  const averageAnomaly =
    analyses > 0
      ? history.reduce(
          (sum, item) =>
            sum + Number(item.anomaly_score || 0),
          0
        ) / analyses
      : null;

  const latestQHI =
    analyses > 0
      ? Number(history[0].health_score || 0)
      : null;

  const qhiProgress =
    averageQHI !== null
      ? Math.max(0, Math.min(100, averageQHI))
      : 0;

  return (
    <div className="space-y-7">
      <section className="relative overflow-hidden rounded-3xl border border-cyan-400/10 bg-gradient-to-br from-cyan-500/[.10] via-slate-950/40 to-violet-600/[.12] p-6 sm:p-8">
        <div className="absolute right-[-60px] top-[-100px] h-64 w-64 rounded-full bg-cyan-400/10 blur-3xl" />

        <div className="relative flex flex-col justify-between gap-6 md:flex-row md:items-end">
          <div>
            <p className="section-kicker">
              Overview
            </p>

            <h1 className="mt-2 text-3xl font-black tracking-tight sm:text-4xl">
              Welcome back, {user.name.split(" ")[0]}.
            </h1>

            <p className="mt-3 max-w-xl text-sm leading-6 text-slate-400">
              Your quantum workspace is ready.
              Choose a workflow below or open the analyzer
              to inspect a circuit.
            </p>
          </div>

          <div className="flex flex-col gap-2 sm:flex-row">
            <Link
              href="/analyzer"
              className="btn btn-primary shrink-0"
            >
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
      </section>

      {resetStatus && (
        <div className="rounded-xl border border-cyan-400/20 bg-cyan-400/5 px-4 py-3 text-sm text-cyan-300">
          {resetStatus}
        </div>
      )}

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
              ? "Across your saved analyses"
              : "Run an analysis to calculate"
          }
        />

        <Metric
          label="Analyses"
          value={
            historyLoading
              ? "…"
              : String(analyses)
          }
          note="Saved workspace analyses"
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
        />

        <Metric
          label="Latest QHI"
          value={
            historyLoading
              ? "…"
              : latestQHI !== null
              ? latestQHI.toFixed(1)
              : "—"
          }
          note={
            latestQHI !== null
              ? history[0].health_category
              : "No analysis yet"
          }
        />
      </section>

      <section className="grid gap-5 xl:grid-cols-[1.6fr_.8fr]">
        <div className="card p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="section-kicker">
                Workflows
              </p>

              <h2 className="mt-1 text-xl font-bold">
                Choose your next move
              </h2>
            </div>

            <span className="badge text-slate-400">
              3 tools
            </span>
          </div>

          <div className="mt-5 grid gap-3 md:grid-cols-3">
            {actions.map(
              ([title, desc, href, icon]) => (
                <Link
                  key={title}
                  href={href}
                  className="card card-hover group p-5"
                >
                  <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-cyan-400/10 text-cyan-300">
                    <Icon name={icon} />
                  </div>

                  <h3 className="mt-5 font-bold">
                    {title}
                  </h3>

                  <p className="mt-2 text-xs leading-5 text-slate-500">
                    {desc}
                  </p>

                  <span className="mt-5 inline-flex items-center gap-2 text-xs font-bold text-cyan-300">
                    Open
                    <Icon name="arrow" size={13} />
                  </span>
                </Link>
              )
            )}
          </div>
        </div>

        <div className="card p-6">
          <p className="section-kicker">
            Quantum Health Index
          </p>

          <div className="mt-6 flex justify-center">
            <div
              className="grid h-44 w-44 place-items-center rounded-full"
              style={{
                background:
                  averageQHI !== null
                    ? `conic-gradient(#22d3ee 0deg, #6366f1 ${
                        qhiProgress * 3.6
                      }deg, rgba(255,255,255,.07) ${
                        qhiProgress * 3.6
                      }deg)`
                    : "conic-gradient(#22d3ee 0deg, #6366f1 0deg, rgba(255,255,255,.07) 0deg)",
              }}
            >
              <div className="grid h-36 w-36 place-items-center rounded-full bg-slate-950">
                <div className="text-center">
                  <div className="text-4xl font-black">
                    {historyLoading
                      ? "…"
                      : averageQHI !== null
                      ? averageQHI.toFixed(1)
                      : "—"}
                  </div>

                  <div className="mt-1 text-[10px] uppercase tracking-widest text-slate-500">
                    {averageQHI !== null
                      ? "Average QHI"
                      : "No score yet"}
                  </div>
                </div>
              </div>
            </div>
          </div>

          <p className="mt-5 text-center text-xs leading-5 text-slate-500">
            {averageQHI !== null
              ? "Based on your saved circuit analyses."
              : "Analyze your first circuit to populate the six QHI components."}
          </p>
        </div>
      </section>

      <section className="card p-6">
        <div className="flex items-center gap-3">
          <div className="grid h-10 w-10 place-items-center rounded-xl bg-violet-400/10 text-violet-300">
            <Icon name="spark" />
          </div>

          <div>
            <h2 className="font-bold">
              How QuantumInsight evaluates a circuit
            </h2>

            <p className="text-xs text-slate-500">
              The analyzer combines engineering metrics with ML signals.
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
          ].map((x, i) => (
            <div
              key={x}
              className="rounded-xl border border-white/5 bg-white/[.02] p-4"
            >
              <span className="text-[10px] font-bold text-cyan-300">
                0{i + 1}
              </span>

              <p className="mt-2 text-sm font-semibold">
                {x}
              </p>

              <div className="mt-3 h-1.5 overflow-hidden rounded-full bg-white/5">
                <div className="h-full w-2/3 rounded-full bg-gradient-to-r from-cyan-400 to-violet-500" />
              </div>
            </div>
          ))}
        </div>
      </section>

      {showResetConfirm && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/70 px-4 backdrop-blur-sm">
          <div className="w-full max-w-md rounded-2xl border border-white/10 bg-slate-950 p-6 shadow-2xl">
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
                  dashboard metrics to their empty state.
                </p>

                <p className="mt-3 text-xs leading-5 text-slate-600">
                  Your account, profile and authentication
                  will not be affected.
                </p>
              </div>
            </div>

            <div className="mt-6 flex flex-col-reverse gap-3 sm:flex-row sm:justify-end">
              <button
                type="button"
                onClick={() =>
                  setShowResetConfirm(false)
                }
                disabled={resetting}
                className="rounded-xl border border-white/10 px-4 py-2 text-sm font-semibold text-slate-300 transition hover:bg-white/5 hover:text-white disabled:cursor-not-allowed disabled:opacity-50"
              >
                Cancel
              </button>

              <button
                type="button"
                onClick={resetDashboardData}
                disabled={resetting}
                className="rounded-xl bg-rose-500/90 px-4 py-2 text-sm font-bold text-white transition hover:bg-rose-500 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {resetting
                  ? "Resetting..."
                  : "Reset Dashboard"}
              </button>
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
}: {
  label: string;
  value: string;
  note: string;
}) {
  return (
    <div className="metric">
      <p className="text-xs font-bold text-slate-500">
        {label}
      </p>

      <p className="metric-value mt-3">
        {value}
      </p>

      <p className="mt-1 text-[11px] text-slate-600">
        {note}
      </p>
    </div>
  );
}
