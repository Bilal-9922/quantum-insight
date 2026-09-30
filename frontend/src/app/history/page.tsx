"use client";

import { useEffect, useState } from "react";
import { useRequireAuth } from "../../lib/auth";
import { Icon } from "../../components/Icons";

type HistoryItem = {
  id: number;
  circuit: string;
  metrics: {
    qubits: number;
    gate_count: number;
    depth: number;
    one_qubit_gates: number;
    two_qubit_gates: number;
    two_qubit_ratio: number;
    gate_density: number;
    measurement_ratio: number;
    gate_counts: Record<string, number>;
  };
  health_score: number;
  health_category: string;
  anomaly_score: number;
  recommendations: {
    summary: string;
    recommendations: string[];
    provider: string;
  };
  explanation: string;
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

export default function History() {
  const { loading: authLoading } = useRequireAuth();

  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [copyStatus, setCopyStatus] = useState("");
  const [exportStatus, setExportStatus] = useState("");
  const [deleteStatus, setDeleteStatus] = useState("");
  const [deleting, setDeleting] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] =
    useState(false);

  useEffect(() => {
    if (authLoading) return;

    const token = localStorage.getItem("qi_token");

    if (!token) {
      setLoading(false);
      return;
    }

    async function loadHistory() {
      try {
        setLoading(true);
        setError("");

        const response = await fetch(
          `${API}/api/history?limit=50`,
          {
            method: "GET",
            headers: {
              Authorization: `Bearer ${token}`,
              Accept: "application/json",
            },
          }
        );

        if (!response.ok) {
          throw new Error(
            `Failed to load history (${response.status})`
          );
        }

        const data: HistoryResponse =
          await response.json();

        setHistory(data.history || []);
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : "Failed to load analysis history."
        );
      } finally {
        setLoading(false);
      }
    }

    loadHistory();
  }, [authLoading]);

  async function copyHistory() {
    if (history.length === 0) {
      setCopyStatus("No history to copy.");

      window.setTimeout(() => {
        setCopyStatus("");
      }, 2500);

      return;
    }

    const historyText = history
      .map((item, index) => {
        const recommendations =
          item.recommendations?.recommendations?.length > 0
            ? item.recommendations.recommendations
                .map(
                  (recommendation) =>
                    `- ${recommendation}`
                )
                .join("\n")
            : "None";

        return [
          `==============================`,
          `Analysis ${index + 1}`,
          `==============================`,
          `Date: ${new Date(
            item.created_at
          ).toLocaleString()}`,
          `Quantum Health Index: ${item.health_score.toFixed(
            1
          )}/100`,
          `Health Category: ${item.health_category}`,
          `Qubits: ${item.metrics?.qubits ?? "—"}`,
          `Gates: ${item.metrics?.gate_count ?? "—"}`,
          `Depth: ${item.metrics?.depth ?? "—"}`,
          `Anomaly Score: ${item.anomaly_score ?? "—"}`,
          ``,
          `Circuit:`,
          item.circuit || "No circuit available.",
          ``,
          `Recommendations:`,
          recommendations,
          ``,
          `Explanation:`,
          item.explanation ||
            "No explanation available.",
          ``,
        ].join("\n");
      })
      .join("\n");

    const fullText = [
      "QuantumInsight — Analysis History",
      "=================================",
      `Total Records: ${history.length}`,
      `Exported: ${new Date().toLocaleString()}`,
      ``,
      historyText,
    ].join("\n");

    try {
      await navigator.clipboard.writeText(fullText);

      setCopyStatus("History copied!");

      window.setTimeout(() => {
        setCopyStatus("");
      }, 2500);
    } catch {
      setCopyStatus(
        "Unable to copy history. Please check browser permissions."
      );

      window.setTimeout(() => {
        setCopyStatus("");
      }, 3000);
    }
  }

  function escapeCsv(value: string | number) {
    const text = String(value ?? "");

    return `"${text.replace(/"/g, '""')}"`;
  }

  function exportHistoryCsv() {
    if (history.length === 0) {
      setExportStatus("No history to export.");

      window.setTimeout(() => {
        setExportStatus("");
      }, 2500);

      return;
    }

    const headers = [
      "Analysis ID",
      "Date",
      "QHI Score",
      "Health Category",
      "Qubits",
      "Gates",
      "Depth",
      "1Q Gates",
      "2Q Gates",
      "2Q Ratio",
      "Gate Density",
      "Measurement Ratio",
      "Anomaly Score",
      "AI Provider",
      "Recommendation Summary",
      "Recommendations",
      "Explanation",
      "Circuit",
    ];

    const rows = history.map((item) => {
      const recommendations =
        item.recommendations?.recommendations?.join(
          " | "
        ) || "";

      return [
        escapeCsv(item.id),
        escapeCsv(
          new Date(item.created_at).toLocaleString()
        ),
        escapeCsv(
          Number(item.health_score || 0).toFixed(1)
        ),
        escapeCsv(item.health_category || ""),
        escapeCsv(item.metrics?.qubits ?? ""),
        escapeCsv(item.metrics?.gate_count ?? ""),
        escapeCsv(item.metrics?.depth ?? ""),
        escapeCsv(
          item.metrics?.one_qubit_gates ?? ""
        ),
        escapeCsv(
          item.metrics?.two_qubit_gates ?? ""
        ),
        escapeCsv(
          item.metrics?.two_qubit_ratio ?? ""
        ),
        escapeCsv(
          item.metrics?.gate_density ?? ""
        ),
        escapeCsv(
          item.metrics?.measurement_ratio ?? ""
        ),
        escapeCsv(item.anomaly_score ?? ""),
        escapeCsv(
          item.recommendations?.provider ?? ""
        ),
        escapeCsv(
          item.recommendations?.summary ?? ""
        ),
        escapeCsv(recommendations),
        escapeCsv(item.explanation || ""),
        escapeCsv(item.circuit || ""),
      ].join(",");
    });

    const csv = [
      headers.map(escapeCsv).join(","),
      ...rows,
    ].join("\r\n");

    const blob = new Blob(
      ["\ufeff" + csv],
      {
        type: "text/csv;charset=utf-8;",
      }
    );

    const url = URL.createObjectURL(blob);

    const link = document.createElement("a");

    link.href = url;
    link.download = `quantuminsight-history-${Date.now()}.csv`;

    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    URL.revokeObjectURL(url);

    setExportStatus("History exported!");

    window.setTimeout(() => {
      setExportStatus("");
    }, 3000);
  }

  async function deleteHistory() {
    const token = localStorage.getItem("qi_token");

    if (!token) {
      setDeleteStatus(
        "Authentication session not found."
      );
      return;
    }

    try {
      setDeleting(true);
      setDeleteStatus("");

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
            : `Failed to delete history (${response.status})`
        );
      }

      setHistory([]);
      setShowDeleteConfirm(false);

      setDeleteStatus(
        `History deleted successfully${
          "deleted_count" in data
            ? ` (${data.deleted_count} records)`
            : ""
        }.`
      );

      window.setTimeout(() => {
        setDeleteStatus("");
      }, 4000);
    } catch (err) {
      setDeleteStatus(
        err instanceof Error
          ? err.message
          : "Failed to delete analysis history."
      );
    } finally {
      setDeleting(false);
    }
  }

  if (authLoading || loading) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <div className="flex items-center gap-3 text-sm text-slate-500">
          <span className="h-2 w-2 animate-pulse rounded-full bg-cyan-300" />
          Loading history…
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-7">
      {/* Header */}
      <section className="relative overflow-hidden rounded-3xl border border-cyan-400/10 bg-gradient-to-br from-cyan-500/[.08] via-slate-950/60 to-violet-600/[.08] p-6 shadow-[0_20px_80px_rgba(0,0,0,.15)] sm:p-8">
        <div className="pointer-events-none absolute -right-20 -top-24 h-64 w-64 rounded-full bg-cyan-400/10 blur-3xl" />

        <div className="relative flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
          <div className="max-w-2xl">
            <div className="flex items-center gap-2">
              <span className="h-1.5 w-1.5 rounded-full bg-cyan-300 shadow-[0_0_12px_rgba(34,211,238,.8)]" />

              <p className="section-kicker">
                Workspace records
              </p>
            </div>

            <h1 className="mt-3 text-3xl font-black tracking-tight text-white sm:text-4xl">
              Analysis History
            </h1>

            <p className="mt-3 max-w-xl text-sm leading-6 text-slate-400">
              Review your previously analyzed quantum
              circuits, health scores, anomalies and AI
              recommendations.
            </p>

            <div className="mt-5 flex flex-wrap items-center gap-3 text-[11px] text-slate-600">
              <span>
                {history.length} saved{" "}
                {history.length === 1
                  ? "analysis"
                  : "analyses"}
              </span>

              <span className="h-1 w-1 rounded-full bg-slate-700" />

              <span className="text-cyan-400/60">
                Personal workspace
              </span>
            </div>
          </div>

          {history.length > 0 && (
            <div className="flex flex-col gap-2 sm:flex-row sm:flex-wrap">
              <button
                type="button"
                onClick={copyHistory}
                className="btn btn-secondary inline-flex items-center justify-center gap-2"
              >
                <Icon name="copy" size={15} />

                {copyStatus || "Copy History"}
              </button>

              <button
                type="button"
                onClick={exportHistoryCsv}
                className="inline-flex items-center justify-center gap-2 rounded-xl border border-cyan-400/10 bg-cyan-400/5 px-4 py-2 text-sm font-semibold text-cyan-300 transition hover:border-cyan-400/20 hover:bg-cyan-400/10 hover:text-cyan-200"
              >
                <Icon name="download" size={15} />

                Export CSV
              </button>

              <button
                type="button"
                onClick={() => {
                  setDeleteStatus("");
                  setShowDeleteConfirm(true);
                }}
                className="inline-flex items-center justify-center gap-2 rounded-xl border border-rose-400/20 bg-rose-400/5 px-4 py-2 text-sm font-semibold text-rose-300 transition hover:border-rose-400/30 hover:bg-rose-400/10 hover:text-rose-200"
              >
                <Icon name="trash" size={15} />

                Delete History
              </button>
            </div>
          )}
        </div>
      </section>

      {/* Status messages */}
      {copyStatus &&
        copyStatus !== "History copied!" && (
          <div className="flex items-center gap-3 rounded-xl border border-white/10 bg-white/[.03] px-4 py-3 text-sm text-slate-300">
            <span className="grid h-6 w-6 place-items-center rounded-full bg-white/5">
              <Icon name="copy" size={13} />
            </span>

            {copyStatus}
          </div>
        )}

      {copyStatus === "History copied!" && (
        <div className="flex items-center gap-3 rounded-xl border border-cyan-400/20 bg-cyan-400/5 px-4 py-3 text-sm text-cyan-300">
          <span className="grid h-6 w-6 place-items-center rounded-full bg-cyan-400/10">
            <Icon name="check" size={13} />
          </span>

          History copied successfully.
        </div>
      )}

      {exportStatus && (
        <div className="flex items-center gap-3 rounded-xl border border-emerald-400/20 bg-emerald-400/5 px-4 py-3 text-sm text-emerald-300">
          <span className="grid h-6 w-6 place-items-center rounded-full bg-emerald-400/10">
            <Icon name="check" size={13} />
          </span>

          {exportStatus}
        </div>
      )}

      {deleteStatus && (
        <div className="flex items-center gap-3 rounded-xl border border-cyan-400/20 bg-cyan-400/5 px-4 py-3 text-sm text-cyan-300">
          <span className="grid h-6 w-6 place-items-center rounded-full bg-cyan-400/10">
            <Icon name="check" size={13} />
          </span>

          {deleteStatus}
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="card border border-red-400/20 bg-red-400/5 p-5">
          <div className="flex items-start gap-3">
            <div className="grid h-9 w-9 shrink-0 place-items-center rounded-lg bg-red-400/10 text-red-300">
              <Icon name="bug" size={16} />
            </div>

            <div>
              <p className="font-semibold text-red-300">
                Unable to load history
              </p>

              <p className="mt-1 text-sm text-slate-500">
                {error}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Empty state */}
      {!error && history.length === 0 && (
        <div className="card relative overflow-hidden p-10 text-center sm:p-14">
          <div className="pointer-events-none absolute left-1/2 top-0 h-32 w-72 -translate-x-1/2 rounded-full bg-cyan-400/5 blur-3xl" />

          <div className="relative">
            <div className="mx-auto grid h-16 w-16 place-items-center rounded-2xl border border-cyan-400/10 bg-cyan-400/10 text-cyan-300">
              <Icon name="history" size={26} />
            </div>

            <h2 className="mt-6 text-xl font-bold text-white">
              No saved analyses yet
            </h2>

            <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-slate-500">
              Run your first quantum circuit analysis
              and the result will automatically appear
              here.
            </p>

            <a
              href="/analyzer"
              className="btn btn-primary mt-6"
            >
              Analyze a circuit
              <Icon name="arrow" size={15} />
            </a>
          </div>
        </div>
      )}

      {/* History list */}
      {history.length > 0 && (
        <section className="space-y-4">
          <div className="flex items-center justify-between px-1">
            <div>
              <p className="section-kicker">
                Saved analyses
              </p>

              <h2 className="mt-1 text-lg font-bold text-white">
                Recent results
              </h2>
            </div>

            <span className="badge text-slate-400">
              {history.length} records
            </span>
          </div>

          {history.map((item, index) => (
            <HistoryCard
              key={item.id}
              item={item}
              index={index}
            />
          ))}
        </section>
      )}

      {/* Delete confirmation */}
      {showDeleteConfirm && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/70 px-4 backdrop-blur-sm">
          <div className="w-full max-w-md overflow-hidden rounded-2xl border border-white/10 bg-slate-950 shadow-2xl">
            <div className="border-b border-white/5 px-6 py-5">
              <div className="flex items-start gap-4">
                <div className="grid h-11 w-11 shrink-0 place-items-center rounded-xl bg-rose-400/10 text-rose-300">
                  <Icon name="trash" size={20} />
                </div>

                <div>
                  <h2 className="text-lg font-bold text-white">
                    Delete all history?
                  </h2>

                  <p className="mt-2 text-sm leading-6 text-slate-400">
                    This will permanently delete all your
                    saved analysis records. This action
                    cannot be undone.
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
                    setShowDeleteConfirm(false)
                  }
                  disabled={deleting}
                  className="rounded-xl border border-white/10 px-4 py-2.5 text-sm font-semibold text-slate-300 transition hover:bg-white/5 hover:text-white disabled:cursor-not-allowed disabled:opacity-50"
                >
                  Cancel
                </button>

                <button
                  type="button"
                  onClick={deleteHistory}
                  disabled={deleting}
                  className="rounded-xl bg-rose-500/90 px-4 py-2.5 text-sm font-bold text-white transition hover:bg-rose-500 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {deleting
                    ? "Deleting..."
                    : "Delete History"}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function HistoryCard({
  item,
  index,
}: {
  item: HistoryItem;
  index: number;
}) {
  const qhi = Number(item.health_score || 0);

  const qhiProgress = Math.max(
    0,
    Math.min(100, qhi)
  );

  return (
    <article className="card group overflow-hidden transition hover:border-cyan-400/10">
      {/* Main header */}
      <div className="relative p-5 sm:p-6">
        <div className="absolute right-5 top-5 text-[10px] font-bold tracking-[0.18em] text-slate-700">
          #{String(index + 1).padStart(2, "0")}
        </div>

        <div className="flex flex-col gap-5 lg:flex-row lg:items-center lg:justify-between">
          <div className="min-w-0">
            <div className="flex flex-wrap items-center gap-2">
              <span className="rounded-lg border border-cyan-400/10 bg-cyan-400/5 px-2.5 py-1 text-[10px] font-bold uppercase tracking-widest text-cyan-300">
                Analysis
              </span>

              <span className="rounded-lg border border-white/5 bg-white/[.03] px-2.5 py-1 text-[10px] font-semibold text-slate-500">
                {item.health_category}
              </span>
            </div>

            <p className="mt-3 text-xs text-slate-600">
              {new Date(
                item.created_at
              ).toLocaleString()}
            </p>
          </div>

          <div className="flex items-center gap-4 lg:min-w-[220px] lg:justify-end">
            <div className="hidden h-12 w-px bg-white/5 sm:block" />

            <div className="min-w-[120px]">
              <div className="flex items-center justify-between gap-4">
                <p className="text-[9px] font-bold uppercase tracking-[0.16em] text-slate-600">
                  Quantum Health
                </p>

                <span className="text-[10px] text-slate-600">
                  /100
                </span>
              </div>

              <div className="mt-1 text-3xl font-black tracking-tight text-cyan-300">
                {qhi.toFixed(1)}
              </div>

              <div className="mt-2 h-1 overflow-hidden rounded-full bg-white/5">
                <div
                  className="h-full rounded-full bg-gradient-to-r from-cyan-400 to-violet-500"
                  style={{
                    width: `${qhiProgress}%`,
                  }}
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Metrics */}
      <div className="grid gap-px border-y border-white/5 bg-white/5 sm:grid-cols-2 lg:grid-cols-4">
        <HistoryMetric
          label="Qubits"
          value={item.metrics?.qubits ?? "—"}
        />

        <HistoryMetric
          label="Gates"
          value={item.metrics?.gate_count ?? "—"}
        />

        <HistoryMetric
          label="Depth"
          value={item.metrics?.depth ?? "—"}
        />

        <HistoryMetric
          label="Anomaly"
          value={item.anomaly_score ?? "—"}
        />
      </div>

      {/* Details */}
      <details className="group/details">
        <summary className="flex cursor-pointer list-none items-center justify-between px-5 py-4 text-sm font-semibold text-slate-400 transition hover:bg-white/[.02] hover:text-white sm:px-6">
          <span className="flex items-center gap-2">
            <Icon name="analyze" size={15} />
            View circuit and analysis details
          </span>

          <span className="text-xs text-slate-600 transition group-open/details:rotate-180">
            ↓
          </span>
        </summary>

        <div className="space-y-6 border-t border-white/5 px-5 pb-6 pt-5 sm:px-6">
          {/* Circuit */}
          <div>
            <div className="mb-2 flex items-center justify-between">
              <p className="text-[10px] font-bold uppercase tracking-[0.16em] text-slate-600">
                Circuit
              </p>

              <span className="text-[9px] uppercase tracking-widest text-slate-700">
                Qiskit
              </span>
            </div>

            <pre className="max-h-80 overflow-auto rounded-xl border border-white/5 bg-black/30 p-4 text-xs leading-6 text-slate-300">
              {item.circuit}
            </pre>
          </div>

          {/* Recommendations */}
          {item.recommendations?.recommendations
            ?.length > 0 && (
            <div>
              <p className="mb-3 text-[10px] font-bold uppercase tracking-[0.16em] text-slate-600">
                AI Recommendations
              </p>

              <div className="space-y-2">
                {item.recommendations.recommendations.map(
                  (recommendation, recommendationIndex) => (
                    <div
                      key={recommendationIndex}
                      className="flex gap-3 rounded-xl border border-white/5 bg-white/[.018] px-4 py-3"
                    >
                      <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-cyan-300" />

                      <p className="text-sm leading-6 text-slate-300">
                        {recommendation}
                      </p>
                    </div>
                  )
                )}
              </div>
            </div>
          )}

          {/* Explanation */}
          {item.explanation && (
            <div>
              <p className="mb-3 text-[10px] font-bold uppercase tracking-[0.16em] text-slate-600">
                Analysis Explanation
              </p>

              <div className="rounded-xl border border-white/5 bg-white/[.018] p-4">
                <p className="text-sm leading-6 text-slate-400">
                  {item.explanation}
                </p>
              </div>
            </div>
          )}
        </div>
      </details>
    </article>
  );
}

function HistoryMetric({
  label,
  value,
}: {
  label: string;
  value: string | number;
}) {
  return (
    <div className="bg-slate-950/70 px-5 py-4 sm:px-6">
      <p className="text-[9px] font-bold uppercase tracking-[0.16em] text-slate-600">
        {label}
      </p>

      <p className="mt-1 text-lg font-bold text-slate-200">
        {value}
      </p>
    </div>
  );
}
