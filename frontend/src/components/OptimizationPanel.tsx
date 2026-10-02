"use client";

import { useState } from "react";

export default function OptimizationPanel({
  data,
}: {
  data: any;
}) {
  const [copied, setCopied] = useState(false);

  if (!data) return null;

  const optimizedCode = data.optimized_code || "";

  const copyOptimizedCode = async () => {
    if (!optimizedCode) return;

    try {
      await navigator.clipboard.writeText(optimizedCode);
      setCopied(true);

      setTimeout(() => {
        setCopied(false);
      }, 2000);
    } catch {
      setCopied(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Before vs After */}
      <div className="card">
        <h3 className="mb-4 font-bold text-cyan-400">
          Before vs After
        </h3>

        <div className="grid gap-3 md:grid-cols-3">
          {[
            [
              "Gates",
              data.original.gate_count,
              data.optimized.gate_count,
              data.improvement.gate_reduction_percent,
            ],
            [
              "Depth",
              data.original.depth,
              data.optimized.depth,
              data.improvement.depth_reduction_percent,
            ],
            [
              "2Q Gates",
              data.original.two_qubit_gates,
              data.optimized.two_qubit_gates,
              data.improvement.two_qubit_reduction_percent,
            ],
          ].map(([name, a, b, p]: any) => (
            <div
              key={name}
              className="rounded-xl bg-slate-950 p-4"
            >
              <div className="text-slate-400">
                {name}
              </div>

              <div className="mt-2 text-lg font-semibold text-white">
                {a} → {b}
              </div>

              <div className="mt-1 text-cyan-400">
                ↓ {p}%
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Optimization Status */}
      <div className="card">
        <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
          <div>
            <h3 className="font-bold text-white">
              Optimization result
            </h3>

            <p className="mt-1 text-sm text-slate-400">
              The optimized circuit was generated from the
              supported static circuit representation.
            </p>
          </div>

          <div
            className={`inline-flex w-fit items-center rounded-full px-3 py-1 text-xs font-semibold ${
              data.optimization_applied
                ? "bg-cyan-400/10 text-cyan-400"
                : "bg-slate-800 text-slate-400"
            }`}
          >
            {data.optimization_applied
              ? "Optimization applied"
              : "No optimization applied"}
          </div>
        </div>
      </div>

      {/* Optimized Qiskit Code */}
      {optimizedCode && (
        <div className="card">
          <div className="mb-4 flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
            <div>
              <h3 className="font-bold text-cyan-400">
                Optimized Qiskit Code
              </h3>

              <p className="mt-1 text-sm text-slate-400">
                Generated Qiskit code after applying the
                optimization rules.
              </p>
            </div>

            <button
              type="button"
              onClick={copyOptimizedCode}
              className="rounded-lg border border-cyan-400/30 bg-cyan-400/10 px-4 py-2 text-sm font-medium text-cyan-400 transition hover:bg-cyan-400/20"
            >
              {copied
                ? "✓ Copied"
                : "Copy optimized code"}
            </button>
          </div>

          <div className="overflow-hidden rounded-xl border border-slate-800 bg-slate-950">
            <div className="flex items-center justify-between border-b border-slate-800 px-4 py-2">
              <span className="text-xs font-medium uppercase tracking-wider text-slate-500">
                Python
              </span>

              <span className="text-xs text-slate-500">
                Optimized circuit
              </span>
            </div>

            <pre className="overflow-x-auto p-5 text-sm leading-6 text-slate-200">
              <code>{optimizedCode}</code>
            </pre>
          </div>
        </div>
      )}

      {/* Optimization Summary */}
      <div className="card">
        <h3 className="mb-4 font-bold text-white">
          Optimization summary
        </h3>

        <div className="space-y-3 text-sm">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <span className="text-slate-400">
              Gate reduction
            </span>

            <span className="font-medium text-cyan-400">
              {data.improvement.gate_reduction_percent}%
            </span>
          </div>

          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <span className="text-slate-400">
              Depth reduction
            </span>

            <span className="font-medium text-cyan-400">
              {data.improvement.depth_reduction_percent}%
            </span>
          </div>

          <div className="flex items-center justify-between">
            <span className="text-slate-400">
              Two-qubit gate reduction
            </span>

            <span className="font-medium text-cyan-400">
              {data.improvement.two_qubit_reduction_percent}%
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
