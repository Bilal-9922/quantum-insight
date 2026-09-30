"use client";

import { useState } from "react";
import { analyze } from "../../services/api";
import { Analysis } from "../../types/quantum";
import MetricCard from "../../components/MetricCard";
import HealthScore from "../../components/HealthScore";
import HealthChart from "../../components/HealthChart";
import CircuitViewer from "../../components/CircuitViewer";
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
  const [data, setData] = useState<Analysis | null>(
    null
  );
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function run() {
    setError("");
    setBusy(true);

    try {
      setData(await analyze(code));
    } catch (e: any) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }

  if (loading) return <Loading />;

  return (
    <div className="space-y-7">
      {/* Header */}
      <section className="relative overflow-hidden rounded-3xl border border-cyan-400/10 bg-gradient-to-br from-cyan-500/[.08] via-slate-950/60 to-violet-600/[.08] p-6 shadow-[0_20px_80px_rgba(0,0,0,.15)] sm:p-8">
        <div className="pointer-events-none absolute -right-20 -top-24 h-64 w-64 rounded-full bg-cyan-400/10 blur-3xl" />

        <div className="relative flex flex-col justify-between gap-5 lg:flex-row lg:items-end">
          <div className="max-w-2xl">
            <div className="flex items-center gap-2">
              <span className="h-1.5 w-1.5 rounded-full bg-cyan-300 shadow-[0_0_12px_rgba(34,211,238,.8)]" />

              <p className="section-kicker">
                Quantum analysis
              </p>
            </div>

            <h1 className="mt-3 text-3xl font-black tracking-tight text-white sm:text-4xl">
              Circuit Analyzer
            </h1>

            <p className="mt-3 text-sm leading-6 text-slate-400">
              Turn Qiskit Python into engineering metrics,
              quantum health signals, anomaly detection and
              AI-powered recommendations.
            </p>
          </div>

          <div className="flex items-center gap-2 self-start rounded-xl border border-cyan-400/10 bg-cyan-400/5 px-3 py-2 lg:self-auto">
            <span className="grid h-6 w-6 place-items-center rounded-lg bg-cyan-400/10 text-cyan-300">
              <Icon name="shield" size={13} />
            </span>

            <div>
              <p className="text-[9px] font-bold uppercase tracking-[0.16em] text-cyan-300">
                Static-safe parser
              </p>

              <p className="text-[10px] text-slate-600">
                Source is analyzed safely
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Editor + information */}
      <section className="grid gap-5 xl:grid-cols-[1.2fr_.8fr]">
        {/* Code editor */}
        <div className="card overflow-hidden">
          <div className="border-b border-white/5 px-5 py-4 sm:px-6">
            <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <div className="flex items-center gap-2">
                  <span className="grid h-7 w-7 place-items-center rounded-lg bg-cyan-400/10 text-cyan-300">
                    <Icon name="analyze" size={14} />
                  </span>

                  <p className="text-sm font-bold text-slate-200">
                    Circuit source
                  </p>
                </div>

                <p className="mt-1 text-[11px] text-slate-600">
                  Paste your Qiskit Python circuit below.
                </p>
              </div>

              <button
                type="button"
                onClick={() => setCode(sample)}
                className="self-start rounded-lg border border-white/5 bg-white/[.02] px-3 py-2 text-[11px] font-bold text-cyan-300 transition hover:border-cyan-400/10 hover:bg-cyan-400/5 sm:self-auto"
              >
                Load sample
              </button>
            </div>
          </div>

          {/* Editor toolbar */}
          <div className="flex items-center justify-between border-b border-white/5 bg-black/10 px-4 py-2">
            <div className="flex items-center gap-2">
              <span className="h-2 w-2 rounded-full bg-rose-400/60" />
              <span className="h-2 w-2 rounded-full bg-amber-400/60" />
              <span className="h-2 w-2 rounded-full bg-emerald-400/60" />
            </div>

            <span className="text-[9px] font-bold uppercase tracking-[0.18em] text-slate-700">
              Python
            </span>
          </div>

          <div className="p-4 sm:p-5">
            <textarea
              spellCheck={false}
              className="code-editor min-h-[320px] w-full resize-y"
              value={code}
              onChange={(e) =>
                setCode(e.target.value)
              }
              placeholder="Paste your Qiskit circuit here..."
            />

            <div className="mt-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <div className="flex flex-wrap items-center gap-3 text-[11px] text-slate-600">
                <span>
                  {code.split("\n").length} lines
                </span>

                <span className="h-1 w-1 rounded-full bg-slate-700" />

                <span>
                  {code.length} characters
                </span>

                <span className="h-1 w-1 rounded-full bg-slate-700" />

                <span className="text-cyan-400/60">
                  Python
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

        {/* What you get */}
        <div className="card relative overflow-hidden p-5 sm:p-6">
          <div className="pointer-events-none absolute -right-16 -top-16 h-40 w-40 rounded-full bg-violet-400/5 blur-3xl" />

          <div className="relative">
            <div className="flex items-start justify-between">
              <div>
                <p className="section-kicker">
                  Analysis pipeline
                </p>

                <h2 className="mt-1 text-xl font-bold text-white">
                  What you get
                </h2>
              </div>

              <div className="grid h-9 w-9 place-items-center rounded-xl bg-violet-400/10 text-violet-300">
                <Icon name="spark" size={17} />
              </div>
            </div>

            <div className="mt-6 space-y-2">
              {[
                [
                  "01",
                  "Circuit metrics",
                  "Qubits, gates, depth and 2-qubit ratio",
                  "analyze",
                ],
                [
                  "02",
                  "Quantum Health Index",
                  "Six normalized health components",
                  "shield",
                ],
                [
                  "03",
                  "Anomaly signal",
                  "ML-based feature outlier detection",
                  "bug",
                ],
                [
                  "04",
                  "Recommendations",
                  "Actionable optimization guidance",
                  "spark",
                ],
              ].map(([number, title, description, icon]) => (
                <div
                  key={number}
                  className="group rounded-2xl border border-white/5 bg-white/[.018] p-4 transition hover:border-cyan-400/10 hover:bg-cyan-400/[.02]"
                >
                  <div className="flex gap-3">
                    <span className="grid h-8 w-8 shrink-0 place-items-center rounded-lg bg-cyan-400/5 text-[10px] font-black text-cyan-300">
                      {number}
                    </span>

                    <div className="min-w-0 flex-1">
                      <div className="flex items-center justify-between gap-3">
                        <p className="text-sm font-bold text-slate-200">
                          {title}
                        </p>

                        <Icon
                          name={icon}
                          size={14}
                          className="shrink-0 text-slate-700 transition group-hover:text-cyan-300"
                        />
                      </div>

                      <p className="mt-1 text-xs leading-5 text-slate-600">
                        {description}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-5 rounded-xl border border-white/5 bg-black/10 px-4 py-3">
              <p className="text-[10px] leading-5 text-slate-600">
                Your submitted source is analyzed by the
                QuantumInsight backend parser. The analyzer
                does not directly execute your submitted
                circuit.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Error */}
      {error && (
        <div className="flex items-start gap-3 rounded-2xl border border-rose-400/20 bg-rose-400/5 p-4">
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

      {/* Results */}
      {data && (
        <section className="space-y-5">
          <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
            <div>
              <div className="flex items-center gap-2">
                <span className="h-1.5 w-1.5 rounded-full bg-emerald-300 shadow-[0_0_10px_rgba(110,231,183,.7)]" />

                <p className="section-kicker">
                  Analysis complete
                </p>
              </div>

              <h2 className="mt-1 text-xl font-bold text-white">
                Circuit health report
              </h2>
            </div>

            <span className="text-[10px] font-bold uppercase tracking-[0.16em] text-slate-600">
              QuantumInsight analysis
            </span>
          </div>

          {/* Metrics */}
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

          {/* Health */}
          <div className="grid gap-5 lg:grid-cols-2">
            <HealthScore
              score={data.health.score}
              category={data.health.category}
            />

            <HealthChart
              components={data.health.components}
            />
          </div>

          {/* Circuit */}
          <CircuitViewer circuit={data.circuit} />

          {/* Recommendations */}
          <AIRecommendation
            data={data.recommendations}
          />
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
