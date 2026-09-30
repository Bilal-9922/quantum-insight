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

    /*
     * Clear the previous result so the user knows
     * that the updated code has not been verified yet.
     */
    setRes(undefined);
  }

  if (loading) {
    return (
      <div className="py-20 text-center text-slate-500">
        Loading debugger…
      </div>
    );
  }

  return (
    <div className="space-y-6">

      {/* Header */}
      <div>
        <p className="section-kicker">
          Assisted debugging
        </p>

        <h1 className="mt-2 text-3xl font-black">
          AI Quantum Debugger
        </h1>

        <p className="mt-2 text-sm text-slate-500">
          Give the debugger your circuit and the error
          message. It will classify the issue and propose
          a patch.
        </p>
      </div>

      {/* Editor + Error message */}
      <div className="grid gap-5 xl:grid-cols-[1.1fr_.9fr]">

        {/* Quantum code */}
        <div className="card p-5">

          <div className="mb-3 flex justify-between">
            <span className="text-xs font-bold">
              Quantum code
            </span>

            <button
              type="button"
              onClick={() => {
                setCode(sample);
                setRes(undefined);
              }}
              className="text-[11px] font-bold text-cyan-300"
            >
              Reset sample
            </button>
          </div>

          <textarea
            className="code-editor"
            value={code}
            onChange={(e) => {
              setCode(e.target.value);
              setRes(undefined);
            }}
            spellCheck={false}
          />

        </div>

        {/* Error message */}
        <div className="card p-5">

          <span className="text-xs font-bold">
            Error message
          </span>

          <textarea
            className="mt-3 min-h-44"
            value={err}
            onChange={(e) =>
              setErr(e.target.value)
            }
            placeholder="Paste the error message…"
          />

          <div className="mt-4 rounded-xl border border-amber-400/10 bg-amber-400/5 p-3 text-xs leading-5 text-amber-200/70">
            Tip: include the complete traceback or
            compiler message when possible.
          </div>

          <button
            disabled={busy}
            className="btn btn-primary mt-4 w-full"
            onClick={run}
          >
            {busy
              ? "Inspecting circuit…"
              : "Diagnose & suggest fix"}

            <Icon
              name="spark"
              size={15}
            />
          </button>

        </div>
      </div>

      {/* Debug result */}
      <DebugPanel
        result={res}
        onApplyFix={applySuggestedFix}
      />

    </div>
  );
}
