"use client";

import { useState } from "react";
import { debug } from "../../services/api";
import DebugPanel from "../../components/DebugPanel";
import { Icon } from "../../components/Icons";
import { useRequireAuth } from "../../lib/auth";

const sample = `from qiskit import QuantumCircuit
qc = QuantumCircuit(2)
qc.h(0)
qc.cx(0, 1)`;

export default function Debugger() {
  const { loading } = useRequireAuth();

  const [code, setCode] = useState(sample);

  const [err, setErr] = useState(
    "Qubit index error: qubit 3 is outside the circuit"
  );

  const [res, setRes] = useState<any>();

  const [busy, setBusy] = useState(false);

  async function run() {
    setBusy(true);

    try {
      const result = await debug(code, err);
      setRes(result);
    } catch (error: any) {
      setRes({
        error: {
          type: "GENERAL_ERROR",
        },
        diagnosis:
          error?.message ||
          "Unable to communicate with the debugger service.",
        suggestions: [
          "Check that the backend service is running.",
          "Verify the API connection.",
          "Try again after the backend becomes available.",
        ],
        verified: false,
      });
    } finally {
      setBusy(false);
    }
  }

  function applySuggestedFix(fixedCode: string) {
    setCode(fixedCode);
    setRes(undefined);
  }

  if (loading) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <div className="flex items-center gap-3 text-sm text-slate-500">
          <span className="h-2 w-2 animate-pulse rounded-full bg-cyan-300" />
          Loading debugger…
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-7">
      {/* Header */}
      <section className="relative overflow-hidden rounded-3xl border border-violet-400/10 bg-gradient-to-br from-violet-500/[.08] via-slate-950/60 to-cyan-500/[.06] p-6 shadow-[0_20px_80px_rgba(0,0,0,.15)] sm:p-8">
        <div className="pointer-events-none absolute -right-20 -top-24 h-64 w-64 rounded-full bg-violet-400/10 blur-3xl" />

        <div className="relative flex flex-col justify-between gap-5 lg:flex-row lg:items-end">
          <div className="max-w-2xl">
            <div className="flex items-center gap-2">
              <span className="h-1.5 w-1.5 rounded-full bg-violet-300 shadow-[0_0_12px_rgba(196,181,253,.8)]" />

              <p className="section-kicker">
                Assisted debugging
              </p>
            </div>

            <h1 className="mt-3 text-3xl font-black tracking-tight text-white sm:text-4xl">
              AI Quantum Debugger
            </h1>

            <p className="mt-3 text-sm leading-6 text-slate-400">
              Submit your quantum circuit and the reported
              error. QuantumInsight classifies the issue,
              explains the cause and proposes a corrective
              patch.
            </p>
          </div>

          <div className="flex items-center gap-2 self-start rounded-xl border border-violet-400/10 bg-violet-400/5 px-3 py-2 lg:self-auto">
            <span className="grid h-6 w-6 place-items-center rounded-lg bg-violet-400/10 text-violet-300">
              <Icon name="bug" size={13} />
            </span>

            <div>
              <p className="text-[9px] font-bold uppercase tracking-[0.16em] text-violet-300">
                AI-assisted
              </p>

              <p className="text-[10px] text-slate-600">
                Diagnose · Explain · Patch
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Debug input */}
      <section className="grid gap-5 xl:grid-cols-[1.15fr_.85fr]">
        {/* Quantum code */}
        <div className="card overflow-hidden">
          <div className="border-b border-white/5 px-5 py-4 sm:px-6">
            <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <div className="flex items-center gap-2">
                  <span className="grid h-7 w-7 place-items-center rounded-lg bg-cyan-400/10 text-cyan-300">
                    <Icon name="analyze" size={14} />
                  </span>

                  <p className="text-sm font-bold text-slate-200">
                    Quantum code
                  </p>
                </div>

                <p className="mt-1 text-[11px] text-slate-600">
                  Paste the circuit that produced the error.
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
                Reset sample
              </button>
            </div>
          </div>

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
              className="code-editor min-h-[320px] w-full resize-y"
              value={code}
              onChange={(e) => {
                setCode(e.target.value);
                setRes(undefined);
              }}
              spellCheck={false}
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
          </div>
        </div>

        {/* Error message */}
        <div className="card overflow-hidden">
          <div className="border-b border-white/5 px-5 py-4 sm:px-6">
            <div className="flex items-center gap-2">
              <span className="grid h-7 w-7 place-items-center rounded-lg bg-rose-400/10 text-rose-300">
                <Icon name="bug" size={14} />
              </span>

              <div>
                <p className="text-sm font-bold text-slate-200">
                  Error message
                </p>

                <p className="mt-1 text-[11px] text-slate-600">
                  Include the complete error when possible.
                </p>
              </div>
            </div>
          </div>

          <div className="p-4 sm:p-5">
            <textarea
              className="min-h-[250px] w-full resize-y"
              value={err}
              onChange={(e) => setErr(e.target.value)}
              placeholder="Paste the error message or traceback…"
            />

            <div className="mt-4 rounded-xl border border-amber-400/10 bg-amber-400/5 p-3">
              <div className="flex gap-2">
                <Icon
                  name="spark"
                  size={14}
                  className="mt-0.5 shrink-0 text-amber-300"
                />

                <p className="text-xs leading-5 text-amber-200/70">
                  Tip: include the complete traceback or
                  compiler message. More context gives the
                  debugger more information to classify the
                  problem.
                </p>
              </div>
            </div>

            <button
              disabled={busy || !code.trim() || !err.trim()}
              className="btn btn-primary mt-4 w-full justify-center"
              onClick={run}
            >
              {busy ? (
                <>
                  <span className="h-3.5 w-3.5 animate-spin rounded-full border-2 border-white/30 border-t-white" />
                  Inspecting circuit…
                </>
              ) : (
                <>
                  <Icon name="spark" size={15} />
                  Diagnose & suggest fix
                  <Icon name="arrow" size={15} />
                </>
              )}
            </button>
          </div>
        </div>
      </section>

      {/* Debug result */}
      {res && (
        <section className="space-y-3">
          <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
            <div>
              <div className="flex items-center gap-2">
                <span className="h-1.5 w-1.5 rounded-full bg-violet-300 shadow-[0_0_10px_rgba(196,181,253,.7)]" />

                <p className="section-kicker">
                  Diagnostic result
                </p>
              </div>

              <h2 className="mt-1 text-xl font-bold text-white">
                Debug analysis
              </h2>
            </div>

            <span className="text-[10px] font-bold uppercase tracking-[0.16em] text-slate-600">
              AI Quantum Debugger
            </span>
          </div>

          <DebugPanel
            result={res}
            onApplyFix={applySuggestedFix}
          />
        </section>
      )}

      {/* Empty state */}
      {!res && !busy && (
        <div className="rounded-2xl border border-dashed border-white/5 bg-white/[.01] px-5 py-8 text-center">
          <div className="mx-auto grid h-10 w-10 place-items-center rounded-xl bg-violet-400/5 text-violet-300">
            <Icon name="bug" size={18} />
          </div>

          <p className="mt-3 text-sm font-semibold text-slate-400">
            Debug results will appear here
          </p>

          <p className="mx-auto mt-1 max-w-md text-xs leading-5 text-slate-700">
            Submit your circuit and error message to
            classify the issue and generate a suggested
            correction.
          </p>
        </div>
      )}
    </div>
  );
}
