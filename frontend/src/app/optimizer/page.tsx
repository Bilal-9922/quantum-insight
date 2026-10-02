"use client";

import { useState } from "react";
import { optimize } from "../../services/api";
import OptimizationPanel from "../../components/OptimizationPanel";
import { Icon } from "../../components/Icons";
import { useRequireAuth } from "../../lib/auth";

const sample = `from qiskit import QuantumCircuit
qc = QuantumCircuit(2)
qc.h(0)
qc.x(0)
qc.x(0)
qc.cx(0,1)
qc.cx(0,1)
qc.measure_all()`;

export default function Optimizer() {
  const { loading } = useRequireAuth();

  const [code, setCode] = useState(sample);
  const [res, setRes] = useState<any>();
  const [busy, setBusy] = useState(false);

  async function run() {
    setBusy(true);
    setRes(undefined);

    try {
      const result = await optimize(code);
      setRes(result);
    } catch (error: any) {
      setRes({
        success: false,
        error: {
          type: "GENERAL_ERROR",
          message:
            error?.message ||
            "Unable to communicate with the optimizer service.",
        },
        message:
          error?.message ||
          "Unable to communicate with the optimizer service.",
      });
    } finally {
      setBusy(false);
    }
  }

  if (loading) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <div className="flex items-center gap-3 text-sm text-slate-500">
          <span className="h-2 w-2 animate-pulse rounded-full bg-cyan-300" />
          Loading optimizer…
        </div>
      </div>
    );
  }

  const isUnsupportedCode =
    res?.success === false &&
    res?.error?.type === "UNSUPPORTED_QUANTUM_CODE";

  const isGeneralError =
    res?.success === false &&
    res?.error?.type !== "UNSUPPORTED_QUANTUM_CODE";

  return (
    <div className="space-y-7">
      {/* Header */}
      <section className="relative overflow-hidden rounded-3xl border border-emerald-400/10 bg-gradient-to-br from-emerald-500/[.07] via-slate-950/60 to-cyan-500/[.06] p-6 shadow-[0_20px_80px_rgba(0,0,0,.15)] sm:p-8">
        <div className="pointer-events-none absolute -right-20 -top-24 h-64 w-64 rounded-full bg-emerald-400/10 blur-3xl" />

        <div className="relative flex flex-col justify-between gap-5 lg:flex-row lg:items-end">
          <div className="max-w-2xl">
            <div className="flex items-center gap-2">
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-300 shadow-[0_0_12px_rgba(110,231,183,.8)]" />

              <p className="section-kicker">
                Circuit refinement
              </p>
            </div>

            <h1 className="mt-3 text-3xl font-black tracking-tight text-white sm:text-4xl">
              Circuit Optimizer
            </h1>

            <p className="mt-3 text-sm leading-6 text-slate-400">
              Find redundant quantum operations and compare
              the original circuit with an optimized version
              while preserving its intended behavior.
            </p>
          </div>

          <div className="flex items-center gap-2 self-start rounded-xl border border-emerald-400/10 bg-emerald-400/5 px-3 py-2 lg:self-auto">
            <span className="grid h-6 w-6 place-items-center rounded-lg bg-emerald-400/10 text-emerald-300">
              <Icon name="zap" size={13} />
            </span>

            <div>
              <p className="text-[9px] font-bold uppercase tracking-[0.16em] text-emerald-300">
                Optimization engine
              </p>

              <p className="text-[10px] text-slate-600">
                Reduce · Compare · Verify
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Input */}
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
                    Original circuit
                  </p>
                </div>

                <p className="mt-1 text-[11px] text-slate-600">
                  Paste the Qiskit circuit you want to optimize.
                </p>
              </div>

              <button
                type="button"
                onClick={() => {
                  setCode(sample);
                  setRes(undefined);
                }}
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
              Qiskit Python
            </span>
          </div>

          <div className="p-4 sm:p-5">
            <textarea
              spellCheck={false}
              className="code-editor min-h-[330px] w-full resize-y"
              value={code}
              onChange={(e) => {
                setCode(e.target.value);
                setRes(undefined);
              }}
              placeholder="Paste your Qiskit circuit here..."
            />

            <div className="mt-3 flex flex-wrap items-center gap-3 text-[11px] text-slate-600">
              <span>{code.split("\n").length} lines</span>

              <span className="h-1 w-1 rounded-full bg-slate-700" />

              <span>{code.length} characters</span>

              <span className="h-1 w-1 rounded-full bg-slate-700" />

              <span className="text-cyan-400/60">
                Python
              </span>
            </div>

            <div className="mt-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <div className="flex items-center gap-2 text-[11px] text-slate-600">
                <span className="grid h-6 w-6 place-items-center rounded-lg bg-emerald-400/5 text-emerald-300">
                  <Icon name="shield" size={12} />
                </span>

                <span>
                  Optimization preserves circuit intent.
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
                    Optimizing…
                  </>
                ) : (
                  <>
                    <Icon name="zap" size={15} />
                    Optimize circuit
                    <Icon name="arrow" size={15} />
                  </>
                )}
              </button>
            </div>
          </div>
        </div>

        {/* Optimization overview */}
        <div className="card relative overflow-hidden p-5 sm:p-6">
          <div className="pointer-events-none absolute -right-16 -top-16 h-40 w-40 rounded-full bg-emerald-400/5 blur-3xl" />

          <div className="relative">
            <div className="flex items-start justify-between">
              <div>
                <p className="section-kicker">
                  Optimization pipeline
                </p>

                <h2 className="mt-1 text-xl font-bold text-white">
                  What happens
                </h2>
              </div>

              <div className="grid h-9 w-9 place-items-center rounded-xl bg-emerald-400/10 text-emerald-300">
                <Icon name="zap" size={17} />
              </div>
            </div>

            <div className="mt-6 space-y-2">
              {[
                [
                  "01",
                  "Inspect",
                  "Analyze gates, depth and circuit structure.",
                  "analyze",
                ],
                [
                  "02",
                  "Detect",
                  "Find redundant or canceling operations.",
                  "bug",
                ],
                [
                  "03",
                  "Optimize",
                  "Apply safe transformations to the circuit.",
                  "zap",
                ],
                [
                  "04",
                  "Compare",
                  "Measure the original and optimized circuits.",
                  "arrow",
                ],
              ].map(([number, title, description, icon]) => (
                <div
                  key={number}
                  className="group rounded-2xl border border-white/5 bg-white/[.018] p-4 transition hover:border-emerald-400/10 hover:bg-emerald-400/[.02]"
                >
                  <div className="flex gap-3">
                    <span className="grid h-8 w-8 shrink-0 place-items-center rounded-lg bg-emerald-400/5 text-[10px] font-black text-emerald-300">
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
                          className="shrink-0 text-slate-700 transition group-hover:text-emerald-300"
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
                The optimizer focuses on safe circuit
                transformations and reports the resulting
                resource changes.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Results */}
      {res && (
        <section className="space-y-3">
          <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
            <div>
              <div className="flex items-center gap-2">
                <span
                  className={
                    isUnsupportedCode || isGeneralError
                      ? "h-1.5 w-1.5 rounded-full bg-amber-300 shadow-[0_0_10px_rgba(252,211,77,.7)]"
                      : "h-1.5 w-1.5 rounded-full bg-emerald-300 shadow-[0_0_10px_rgba(110,231,183,.7)]"
                  }
                />

                <p className="section-kicker">
                  {isUnsupportedCode || isGeneralError
                    ? "Optimization stopped"
                    : "Optimization complete"}
                </p>
              </div>

              <h2 className="mt-1 text-xl font-bold text-white">
                {isUnsupportedCode || isGeneralError
                  ? "Optimization could not be performed"
                  : "Optimization report"}
              </h2>
            </div>

            <span className="text-[10px] font-bold uppercase tracking-[0.16em] text-slate-600">
              QuantumInsight optimization
            </span>
          </div>

          {/* Unsupported Qiskit code */}
          {isUnsupportedCode && (
            <div className="overflow-hidden rounded-2xl border border-amber-400/20 bg-amber-400/[.04]">
              <div className="border-b border-amber-400/10 bg-amber-400/[.05] px-5 py-4">
                <div className="flex items-center gap-3">
                  <span className="grid h-9 w-9 place-items-center rounded-xl bg-amber-400/10 text-amber-300">
                    <Icon name="bug" size={17} />
                  </span>

                  <div>
                    <p className="text-sm font-bold text-amber-200">
                      Unsupported Quantum Code
                    </p>

                    <p className="mt-1 text-[10px] font-bold uppercase tracking-[0.15em] text-amber-300/50">
                      Detection stopped
                    </p>
                  </div>
                </div>
              </div>

              <div className="p-5">
                <p className="text-sm leading-6 text-slate-300">
                  {res.error?.message ||
                    res.message ||
                    "The submitted source is not recognized as a valid Qiskit quantum circuit."}
                </p>

                <div className="mt-4 rounded-xl border border-white/5 bg-black/20 p-4">
                  <p className="text-[10px] font-bold uppercase tracking-[0.16em] text-slate-500">
                    Supported input
                  </p>

                  <p className="mt-2 text-xs leading-5 text-slate-400">
                    Circuit Optimizer accepts real Qiskit
                    quantum circuit code only. Normal Python,
                    pseudo quantum code, Java, C++, and other
                    non-Qiskit source code cannot be optimized.
                  </p>
                </div>

                <div className="mt-4 flex items-center gap-2 text-xs text-amber-300/70">
                  <span className="h-1.5 w-1.5 rounded-full bg-amber-300" />

                  No optimization was performed.
                </div>
              </div>
            </div>
          )}

          {/* General error */}
          {isGeneralError && (
            <div className="overflow-hidden rounded-2xl border border-rose-400/20 bg-rose-400/[.04]">
              <div className="border-b border-rose-400/10 bg-rose-400/[.05] px-5 py-4">
                <div className="flex items-center gap-3">
                  <span className="grid h-9 w-9 place-items-center rounded-xl bg-rose-400/10 text-rose-300">
                    <Icon name="bug" size={17} />
                  </span>

                  <div>
                    <p className="text-sm font-bold text-rose-200">
                      Optimization failed
                    </p>

                    <p className="mt-1 text-[10px] font-bold uppercase tracking-[0.15em] text-rose-300/50">
                      Service error
                    </p>
                  </div>
                </div>
              </div>

              <div className="p-5">
                <p className="text-sm leading-6 text-slate-300">
                  {res.error?.message ||
                    res.message ||
                    "Unable to process the submitted circuit."}
                </p>
              </div>
            </div>
          )}

          {/* Normal successful optimization result */}
          {res?.success !== false && (
            <OptimizationPanel data={res} />
          )}
        </section>
      )}

      {/* Empty state */}
      {!res && !busy && (
        <div className="rounded-2xl border border-dashed border-white/5 bg-white/[.01] px-5 py-8 text-center">
          <div className="mx-auto grid h-10 w-10 place-items-center rounded-xl bg-emerald-400/5 text-emerald-300">
            <Icon name="zap" size={18} />
          </div>

          <p className="mt-3 text-sm font-semibold text-slate-400">
            Optimization results will appear here
          </p>

          <p className="mx-auto mt-1 max-w-md text-xs leading-5 text-slate-700">
            Submit a quantum circuit to identify redundant
            operations and compare the optimized result.
          </p>
        </div>
      )}
    </div>
  );
}
