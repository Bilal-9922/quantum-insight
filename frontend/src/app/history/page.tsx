"use client";

// Cloudflare build verification

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

const API =
  process.env.NEXT_PUBLIC_API_URL ||
  "http://127.0.0.1:8000";

export default function History() {
  const { loading: authLoading } = useRequireAuth();

  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

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

        const response = await fetch(`${API}/api/history?limit=50`, {
          method: "GET",
          headers: {
            Authorization: `Bearer ${token}`,
            Accept: "application/json",
          },
        });

        if (!response.ok) {
          throw new Error(
            `Failed to load history (${response.status})`
          );
        }

        const data: HistoryResponse = await response.json();

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

  if (authLoading || loading) {
    return (
      <div className="py-20 text-center text-slate-500">
        Loading history…
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <p className="section-kicker">
          Workspace records
        </p>

        <h1 className="mt-2 text-3xl font-black">
          Analysis History
        </h1>

        <p className="mt-2 text-sm text-slate-500">
          View your previously analyzed quantum circuits and
          their Quantum Health Index results.
        </p>
      </div>

      {error && (
        <div className="card border border-red-400/20 bg-red-400/5 p-5">
          <p className="font-semibold text-red-300">
            Unable to load history
          </p>

          <p className="mt-1 text-sm text-slate-500">
            {error}
          </p>
        </div>
      )}

      {!error && history.length === 0 && (
        <div className="card p-10 text-center">
          <div className="mx-auto grid h-14 w-14 place-items-center rounded-2xl bg-cyan-400/10 text-cyan-300">
            <Icon name="history" size={24} />
          </div>

          <h2 className="mt-5 text-xl font-bold">
            No saved analyses yet
          </h2>

          <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-slate-500">
            Run an analysis first. Your completed analyses
            will automatically appear here.
          </p>

          <a
            href="/analyzer"
            className="btn btn-primary mt-6"
          >
            Analyze a circuit{" "}
            <Icon name="arrow" size={15} />
          </a>
        </div>
      )}

      {history.length > 0 && (
        <div className="space-y-4">
          {history.map((item) => (
            <div
              key={item.id}
              className="card overflow-hidden"
            >
              <div className="flex flex-col gap-4 p-6 lg:flex-row lg:items-center lg:justify-between">
                <div>
                  <div className="flex flex-wrap items-center gap-3">
                    <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">
                      Analysis
                    </span>

                    <span className="rounded-full bg-cyan-400/10 px-3 py-1 text-xs font-semibold text-cyan-300">
                      {item.health_category}
                    </span>
                  </div>

                  <p className="mt-2 text-sm text-slate-500">
                    {new Date(
                      item.created_at
                    ).toLocaleString()}
                  </p>
                </div>

                <div className="text-left lg:text-right">
                  <p className="text-xs uppercase tracking-widest text-slate-500">
                    Quantum Health Index
                  </p>

                  <p className="mt-1 text-3xl font-black text-cyan-300">
                    {item.health_score.toFixed(1)}
                  </p>
                </div>
              </div>

              <div className="grid gap-3 border-t border-white/5 bg-white/[0.02] p-6 sm:grid-cols-2 lg:grid-cols-4">
                <div>
                  <p className="text-xs uppercase tracking-wider text-slate-500">
                    Qubits
                  </p>

                  <p className="mt-1 font-bold">
                    {item.metrics?.qubits ?? "—"}
                  </p>
                </div>

                <div>
                  <p className="text-xs uppercase tracking-wider text-slate-500">
                    Gates
                  </p>

                  <p className="mt-1 font-bold">
                    {item.metrics?.gate_count ?? "—"}
                  </p>
                </div>

                <div>
                  <p className="text-xs uppercase tracking-wider text-slate-500">
                    Depth
                  </p>

                  <p className="mt-1 font-bold">
                    {item.metrics?.depth ?? "—"}
                  </p>
                </div>

                <div>
                  <p className="text-xs uppercase tracking-wider text-slate-500">
                    Anomaly
                  </p>

                  <p className="mt-1 font-bold">
                    {item.anomaly_score ?? "—"}
                  </p>
                </div>
              </div>

              <details className="border-t border-white/5">
                <summary className="cursor-pointer px-6 py-4 text-sm font-semibold text-slate-300 hover:text-white">
                  View circuit and analysis details
                </summary>

                <div className="space-y-5 px-6 pb-6">
                  <div>
                    <p className="mb-2 text-xs uppercase tracking-wider text-slate-500">
                      Circuit
                    </p>

                    <pre className="overflow-x-auto rounded-xl bg-black/30 p-4 text-xs leading-6 text-slate-300">
                      {item.circuit}
                    </pre>
                  </div>

                  {item.recommendations?.recommendations
                    ?.length > 0 && (
                    <div>
                      <p className="mb-2 text-xs uppercase tracking-wider text-slate-500">
                        Recommendations
                      </p>

                      <ul className="space-y-2">
                        {item.recommendations.recommendations.map(
                          (recommendation, index) => (
                            <li
                              key={index}
                              className="text-sm text-slate-300"
                            >
                              • {recommendation}
                            </li>
                          )
                        )}
                      </ul>
                    </div>
                  )}

                  {item.explanation && (
                    <div>
                      <p className="mb-2 text-xs uppercase tracking-wider text-slate-500">
                        Explanation
                      </p>

                      <p className="text-sm leading-6 text-slate-400">
                        {item.explanation}
                      </p>
                    </div>
                  )}
                </div>
              </details>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
