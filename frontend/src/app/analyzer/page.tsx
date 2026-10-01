"use client";

import { useState } from "react";
import { analyze } from "../../services/api";
import { Analysis } from "../../types/quantum";
import MetricCard from "../../components/MetricCard";
import HealthScore from "../../components/HealthScore";
import QMI from "../../components/QMI";
import HealthChart from "../../components/HealthChart";
import CircuitViewer from "../../components/CircuitViewer";
import HardwareRecommendations from "../../components/HardwareRecommendations";
import AIRecommendation from "../../components/AIRecommendation";
import { Icon } from "../../components/Icons";
import { useRequireAuth } from "../../lib/auth";

const sample = `from qiskit import QuantumCircuit

qc = QuantumCircuit(2)
qc.h(0)
qc.cx(0, 1)
qc.measure_all()`;

export default function Analyzer() {
  const { loading } = useRequireAuth();

  const [code, setCode] = useState(sample);
  const [data, setData] = useState<Analysis | null>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [exported, setExported] = useState(false);

  async function run() {
    setError("");
    setExported(false);
    setBusy(true);

    try {
      setData(await analyze(code));
    } catch (e: any) {
      setError(e.message || "Unable to analyze the circuit.");
    } finally {
      setBusy(false);
    }
  }

  function exportReport() {
    if (!data) return;

    const report = {
      application: "QuantumInsight",
      report_type: "Quantum Circuit Analysis",
      generated_at: new Date().toISOString(),

      source_code: code,

      metrics: {
        qubits: data.metrics.qubits,
        gates: data.metrics.gate_count,
        depth: data.metrics.depth,
        two_qubit_gates: data.metrics.two_qubit_gates,
      },

      quantum_health: {
        score: data.health.score,
        category: data.health.category,
        components: data.health.components,
      },

      quantum_maintainability: data.qmi,

      circuit: data.circuit,

      hardware_recommendations:
        data.hardware_recommendations,

      recommendations: data.recommendations,
    };

    const blob = new Blob(
      [JSON.stringify(report, null, 2)],
      {
        type: "application/json",
      }
    );

    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");

    link.href = url;
    link.download = `quantuminsight-report-${Date.now()}.json`;

    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    URL.revokeObjectURL(url);

    setExported(true);

    window.setTimeout(() => {
      setExported(false);
    }, 2500);
  }

  if (loading) return <Loading />;

  return (
    <div className="space-y-6">

      {/* =====================================================
          PAGE HEADER
      ===================================================== */}

      <section className="border-b border-white/10 pb-6">

        <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">

          <div className="max-w-3xl">

            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-cyan-400">
              Circuit analysis
            </p>

            <h1 className="mt-2 text-3xl font-bold tracking-tight text-white sm:text-4xl">
              Circuit Analyzer
            </h1>

            <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-400">
              Inspect a Qiskit circuit and extract measurable engineering
              characteristics, health indicators and optimization signals.
            </p>

          </div>

          <div className="flex shrink-0 items-center gap-2 rounded-lg border border-white/10 bg-slate-900/60 px-3 py-2">

            <span className="grid h-7 w-7 place-items-center rounded-md border border-emerald-400/15 bg-emerald-400/5 text-emerald-300">
              <Icon name="shield" size={14} />
            </span>

            <div>
              <p className="text-[10px] font-semibold uppercase tracking-wider text-emerald-300">
                Static analysis
              </p>

              <p className="text-[10px] text-slate-500">
                Submitted source is not executed directly
              </p>
            </div>

          </div>

        </div>

      </section>

      {/* =====================================================
          SOURCE + ANALYSIS INFORMATION
      ===================================================== */}

      <section className="grid gap-5 xl:grid-cols-[1.35fr_.65fr]">

        {/* Source editor */}

        <div className="card overflow-hidden">

          <div className="border-b border-white/10 px-5 py-4 sm:px-6">

            <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">

              <div>

                <div className="flex items-center gap-2">

                  <span className="grid h-7 w-7 place-items-center rounded-md border border-cyan-400/15 bg-cyan-400/5 text-cyan-300">
                    <Icon name="analyze" size={14} />
                  </span>

                  <p className="text-sm font-semibold text-white">
                    Circuit source
                  </p>

                </div>

                <p className="mt-1 text-xs text-slate-500">
                  Paste Qiskit Python for static analysis.
                </p>

              </div>

              <button
                type="button"
                onClick={() => {
                  setCode(sample);
                  setError("");
                  setData(null);
                  setExported(false);
                }}
                className="rounded-lg border border-white/10 bg-slate-900 px-3 py-2 text-xs font-medium text-slate-300 transition hover:border-cyan-400/20 hover:text-cyan-300"
              >
                Load sample
              </button>

            </div>

          </div>

          {/* Editor header */}

          <div className="flex items-center justify-between border-b border-white/10 bg-slate-950 px-4 py-2">

            <div className="flex items-center gap-2">

              <span className="h-2 w-2 rounded-full bg-slate-600" />
              <span className="h-2 w-2 rounded-full bg-slate-600" />
              <span className="h-2 w-2 rounded-full bg-slate-600" />

            </div>

            <span className="font-mono text-[10px] text-slate-600">
              qiskit.py
            </span>

          </div>

          <div className="p-4 sm:p-5">

            <textarea
              spellCheck={false}
              className="code-editor min-h-[340px] w-full resize-y"
              value={code}
              onChange={(e) => {
                setCode(e.target.value);
                setExported(false);
              }}
              placeholder="Paste your Qiskit circuit here..."
            />

            <div className="mt-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">

              <div className="flex flex-wrap items-center gap-3 font-mono text-[10px] text-slate-600">

                <span>
                  {code.split("\n").length} lines
                </span>

                <span className="h-1 w-1 rounded-full bg-slate-700" />

                <span>
                  {code.length} characters
                </span>

              </div>

              <button
                type="button"
                disabled={busy || !code.trim()}
                onClick={run}
                className="btn btn-primary justify-center sm:min-w-[170px]"
              >
                {busy ? (
                  <>
                    <span className="h-3.5 w-3.5 animate-spin rounded-full border-2 border-white/30 border-t-white" />
                    Analyzing…
                  </>
                ) : (
                  <>
                    <Icon name="zap" size={15} />
                    Analyze circuit
                    <Icon name="arrow" size={15} />
                  </>
                )}
              </button>

            </div>

          </div>

        </div>

        {/* Analysis scope */}

        <div className="card p-5 sm:p-6">

          <div>

            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-cyan-400">
              Analysis scope
            </p>

            <h2 className="mt-2 text-xl font-bold text-white">
              What is measured
            </h2>

            <p className="mt-2 text-sm leading-6 text-slate-500">
              The analyzer converts circuit structure into measurable
              characteristics and engineering signals.
            </p>

          </div>

          <div className="mt-6 space-y-3">

            {[
              [
                "01",
                "Circuit metrics",
                "Qubits, gates, depth and two-qubit operations.",
                "analyze",
              ],
              [
                "02",
                "Circuit health",
                "Six components contributing to the QHI score.",
                "shield",
              ],
              [
                "03",
                "Maintainability",
                "Readability, efficiency, modularity and scalability.",
                "spark",
              ],
              [
                "04",
                "Anomaly detection",
                "Feature-based detection of unusual circuit patterns.",
                "bug",
              ],
              [
                "05",
                "Recommendations",
                "Potential improvements based on detected characteristics.",
                "zap",
              ],
            ].map(([number, title, description, icon]) => (
              <div
                key={number}
                className="border-b border-white/5 pb-3 last:border-0 last:pb-0"
              >
                <div className="flex gap-3">

                  <span className="font-mono text-[10px] text-cyan-500">
                    {number}
                  </span>

                  <div className="min-w-0 flex-1">

                    <div className="flex items-center gap-2">

                      <Icon
                        name={icon}
                        size={13}
                        className="shrink-0 text-slate-500"
                      />

                      <p className="text-sm font-semibold text-slate-200">
                        {title}
                      </p>

                    </div>

                    <p className="mt-1 text-xs leading-5 text-slate-500">
                      {description}
                    </p>

                  </div>

                </div>
              </div>
            ))}

          </div>

          <div className="mt-6 border-t border-white/10 pt-4">

            <p className="text-[10px] leading-5 text-slate-600">
              QuantumInsight performs static analysis of submitted source.
              The circuit is not directly executed by the analyzer.
            </p>

          </div>

        </div>

      </section>

      {/* =====================================================
          ERROR
      ===================================================== */}

      {error && (
        <div className="flex items-start gap-3 rounded-xl border border-rose-400/20 bg-rose-400/5 p-4">

          <div className="grid h-9 w-9 shrink-0 place-items-center rounded-lg bg-rose-400/10 text-rose-300">
            <Icon name="bug" size={16} />
          </div>

          <div>

            <p className="font-semibold text-rose-200">
              Analysis failed
            </p>

            <p className="mt-1 text-sm leading-6 text-slate-500">
              {error}
            </p>

          </div>

        </div>
      )}

      {/* =====================================================
          EXPORT CONFIRMATION
      ===================================================== */}

      {exported && (
        <div className="flex items-center gap-3 rounded-xl border border-emerald-400/15 bg-emerald-400/5 p-4">

          <div className="grid h-9 w-9 shrink-0 place-items-center rounded-lg bg-emerald-400/10 text-emerald-300">
            <Icon name="check" size={16} />
          </div>

          <div>

            <p className="font-semibold text-emerald-200">
              Report exported
            </p>

            <p className="mt-1 text-sm text-slate-500">
              Your QuantumInsight analysis report has been downloaded.
            </p>

          </div>

        </div>
      )}

      {/* =====================================================
          RESULTS
      ===================================================== */}

      {data && (
        <section className="space-y-5">

          {/* Results heading */}

          <div className="flex flex-col gap-3 border-b border-white/10 pb-4 sm:flex-row sm:items-end sm:justify-between">

            <div>

              <p className="text-xs font-semibold uppercase tracking-[0.18em] text-emerald-400">
                Analysis complete
              </p>

              <h2 className="mt-2 text-2xl font-bold text-white">
                Circuit analysis results
              </h2>

              <p className="mt-1 text-sm text-slate-500">
                Structural metrics, health indicators and engineering
                recommendations for the submitted circuit.
              </p>

            </div>

            <button
              type="button"
              onClick={exportReport}
              className="inline-flex shrink-0 items-center justify-center gap-2 rounded-lg border border-white/10 bg-slate-900 px-3 py-2 text-xs font-medium text-slate-300 transition hover:border-cyan-400/20 hover:text-cyan-300"
            >
              <Icon name="copy" size={13} />
              Export report
            </button>

          </div>

          {/* =================================================
              CORE METRICS
          ================================================= */}

          <div>

            <div className="mb-3 flex items-center gap-3">

              <h3 className="text-sm font-semibold text-white">
                Circuit metrics
              </h3>

              <span className="h-px flex-1 bg-white/10" />

            </div>

            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">

              <MetricCard
                label="Qubits"
                value={data.metrics.qubits}
              />

              <MetricCard
                label="Gates"
                value={data.metrics.gate_count}
              />

              <MetricCard
                label="Depth"
                value={data.metrics.depth}
              />

              <MetricCard
                label="2Q Gates"
                value={data.metrics.two_qubit_gates}
              />

            </div>

          </div>

          {/* =================================================
              QHI + QMI
          ================================================= */}

          <div>

            <div className="mb-3 flex items-center gap-3">

              <h3 className="text-sm font-semibold text-white">
                Circuit quality
              </h3>

              <span className="h-px flex-1 bg-white/10" />

            </div>

            <div className="grid gap-5 lg:grid-cols-2">

              <div className="min-w-0">

                <HealthScore
                  score={data.health.score}
                  category={data.health.category}
                />

                <div className="mt-5">
                  <HealthChart
                    components={data.health.components}
                  />
                </div>

              </div>

              <div className="min-w-0">
                <QMI data={data.qmi} />
              </div>

            </div>

          </div>

          {/* =================================================
              CIRCUIT
          ================================================= */}

          <div>

            <div className="mb-3 flex items-center gap-3">

              <h3 className="text-sm font-semibold text-white">
                Circuit structure
              </h3>

              <span className="h-px flex-1 bg-white/10" />

            </div>

            <CircuitViewer
              circuit={data.circuit}
            />

          </div>

          {/* =================================================
              HARDWARE
          ================================================= */}

          <div>

            <div className="mb-3 flex items-center gap-3">

              <h3 className="text-sm font-semibold text-white">
                Hardware assessment
              </h3>

              <span className="h-px flex-1 bg-white/10" />

            </div>

            <HardwareRecommendations
              data={data.hardware_recommendations}
            />

          </div>

          {/* =================================================
              RECOMMENDATIONS
          ================================================= */}

          <div>

            <div className="mb-3 flex items-center gap-3">

              <h3 className="text-sm font-semibold text-white">
                Recommendations
              </h3>

              <span className="h-px flex-1 bg-white/10" />

            </div>

            <AIRecommendation
              data={data.recommendations}
            />

          </div>

        </section>
      )}

    </div>
  );
}

function Loading() {
  return (
    <div className="flex min-h-[60vh] items-center justify-center">

      <div className="flex items-center gap-3 text-sm text-slate-500">

        <span className="h-2 w-2 animate-pulse rounded-full bg-cyan-300" />

        Loading analyzer…

      </div>

    </div>
  );
}
