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
    setRes(undefined);

    try {
      const result = await debug(code, err);
      setRes(result);
    } catch (error: any) {
      setRes({
        success: false,
        error: {
          type: "GENERAL_ERROR",
          message:
            error?.message ||
            "Unable to communicate with the debugger service.",
        },
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
          Loading debugger…
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
      <section className="relative overflow-hidden rounded-3xl border border-cyan-400/10 bg-gradient-to-br from-cyan-500/[.07] via-slate-950/60 to-violet-500/[.06] p-6 shadow-[0_20px_80px_rgba(0,0,0,.15)] sm:p-8">
        <div className="pointer-events-none absolute -right-20 -top-24 h-64 w-64 rounded-full bg-cyan-400/10 blur-3xl" />

        <div className="relative flex flex-col justify-between gap-5 lg:flex-row lg:items-end">
          <div className="max-w-2xl">
            <div className="flex items-center gap-2">
              <span className="h-1.5 w-1.5 rounded-full bg-cyan-300 shadow-[0_0_12px_rgba(103,232,249,.8)]" />

              <p className="section-kicker">
                Quantum code diagnosis
              </p>
            </div>

            <h1 className="mt-3 text-3xl font-black tracking-tight text-white sm:text-4xl">
              AI Quantum Debugger
            </h1>

            <p className="mt-3 text-sm leading-6 text-slate-400">
              Analyze Qiskit code, identify quantum programming
              errors, diagnose the problem and verify a proposed
              correction.
            </p>
          </div>

          <div className="flex items-center gap-2 self-start rounded-xl border border-cyan-400/10 bg-cyan-400/5 px-3 py-2 lg:self-auto">
            <span className="grid h-6 w-6 place-items-center rounded-lg bg-cyan-400/10 text-cyan-300">
              <Icon name="bug" size={13} />
            </span>

            <div>
              <p className="text-[9px] font-bold uppercase tracking-[0.16em] text-cyan-300">
                Debugging engine
              </p>

              <p className="text-[10px] text-slate-600">
                Detect · Diagnose · Verify
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Input */}
      <section className="grid gap-5 xl:grid-cols-[1.2fr_.8fr]">
        {/* Code */}
        <div className="card overflow-hidden">
          <div className="border-b border-white/5 px-5 py-4 sm:px-6">
            <div>
              <div className="flex items-center gap-2">
                <span className="grid h-7 w-7 place-items-center rounded-lg bg-cyan-400/10 text-cyan-300">
                  <Icon name="bug" size={14} />
                </span>

                <p className="text-sm font-bold text-slate-200">
                  Quantum code
                </p>
              </div>

              <p className="mt-1 text-[11px] text-slate-600">
                Paste the Qiskit circuit you want the AI debugger to
                inspect.
              </p>
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
              spellCheck={false}
              className="code-editor min-h-[300px] w-full resize-y"
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
                Python / Qiskit
              </span>
            </div>
          </div>
        </div>

        {/* Error input */}
        <div className="card overflow-hidden">
          <div className="border-b border-white/5 px-5 py-4 sm:px-6">
            <div className="flex items-center gap-2">
              <span className="grid h-7 w-7 place-items-center rounded-lg bg-rose-400/10 text-rose-300">
                <Icon name="bug" size={14} />
              </span>

              <p className="text-sm font-bold text-slate-200">
                Reported error
              </p>
            </div>

            <p className="mt-1 text-[11px] text-slate-600">
              Enter the error message reported by your quantum
              program.
            </p>
          </div>

          <div className="p-4 sm:p-5">
            <textarea
              spellCheck={false}
              className="code-editor min-h-[180px] w-full resize-y"
              value={err}
              onChange={(e) => {
                setErr(e.target.value);
                setRes(undefined);
              }}
              placeholder="Paste the Qiskit error message here..."
            />

            <button
              type="button"
              disabled={busy || !code.trim()}
              onClick={run}
              className="btn btn-primary mt-4 w-full justify-center"
            >
              {busy ? (
                <>
                  <span className="h-3.5 w-3.5 animate-spin rounded-full border-2 border-white/30 border-t-white" />
                  Debugging…
                </>
              ) : (
                <>
                  <Icon name="bug" size={15} />
                  Debug quantum code
                  <Icon name="arrow" size={15} />
                </>
              )}
            </button>
          </div>
        </div>
      </section>

      {/* Unsupported quantum code */}
      {isUnsupportedCode && (
        <section className="rounded-2xl border border-amber-400/20 bg-amber-400/[.04] p-5 sm:p-6">
          <div className="flex gap-4">
            <div className="grid h-11 w-11 shrink-0 place-items-center rounded-xl bg-amber-400/10 text-amber-300">
              <Icon name="shield" size={20} />
            </div>

            <div className="min-w-0">
              <p className="text-[10px] font-bold uppercase tracking-[0.18em] text-amber-300">
                Detection stopped
              </p>

              <h2 className="mt-1 text-lg font-bold text-white">
                Unsupported Quantum Code
              </h2>

              <p className="mt-2 text-sm leading-6 text-slate-400">
                {res?.error?.message ||
                  "QuantumInsight currently supports Qiskit quantum circuit code. The submitted source does not contain a recognizable quantum circuit."}
              </p>

              <div className="mt-4 rounded-xl border border-white/5 bg-black/10 px-4 py-3">
                <p className="text-xs font-semibold text-slate-300">
                  No debugging was performed.
                </p>

                <p className="mt-1 text-[11px] leading-5 text-slate-600">
                  Submit a real Qiskit QuantumCircuit so the debugger
                  can analyze the circuit and diagnose quantum
                  programming errors.
                </p>
              </div>
            </div>
          </div>
        </section>
      )}

      {/* General error */}
      {isGeneralError && (
        <section className="rounded-2xl border border-rose-400/20 bg-rose-400/[.04] p-5 sm:p-6">
          <div className="flex gap-4">
            <div className="grid h-11 w-11 shrink-0 place-items-center rounded-xl bg-rose-400/10 text-rose-300">
              <Icon name="bug" size={20} />
            </div>

            <div>
              <p className="text-[10px] font-bold uppercase tracking-[0.18em] text-rose-300">
                Debugging failed
              </p>

              <h2 className="mt-1 text-lg font-bold text-white">
                Unable to analyze code
              </h2>

              <p className="mt-2 text-sm leading-6 text-slate-400">
                {res?.error?.message ||
                  "The debugger service could not analyze the submitted code."}
              </p>
            </div>
          </div>
        </section>
      )}

      {/* Successful result */}
      {res && !isUnsupportedCode && !isGeneralError && (
        <section className="space-y-3">
          <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
            <div>
              <div className="flex items-center gap-2">
                <span className="h-1.5 w-1.5 rounded-full bg-cyan-300 shadow-[0_0_10px_rgba(103,232,249,.7)]" />

                <p className="section-kicker">
                  Debugging complete
                </p>
              </div>

              <h2 className="mt-1 text-xl font-bold text-white">
                Debug report
              </h2>
            </div>

            <span className="text-[10px] font-bold uppercase tracking-[0.16em] text-slate-600">
              QuantumInsight AI debugger
            </span>
          </div>

          <DebugPanel result={res} />
        </section>
      )}

      {/* Empty state */}
      {!res && !busy && (
        <div className="rounded-2xl border border-dashed border-white/5 bg-white/[.01] px-5 py-8 text-center">
          <div className="mx-auto grid h-10 w-10 place-items-center rounded-xl bg-cyan-400/5 text-cyan-300">
            <Icon name="bug" size={18} />
          </div>

          <p className="mt-3 text-sm font-semibold text-slate-400">
            Debug results will appear here
          </p>

          <p className="mx-auto mt-1 max-w-md text-xs leading-5 text-slate-700">
            Submit a Qiskit circuit and an error message to identify,
            diagnose and verify quantum programming issues.
          </p>
        </div>
      )}
    </div>
  );
}
