"use client";

import { QMI as QMIType } from "../types/quantum";

type Props = {
  data?: QMIType | null;
};

const componentLabels: Record<
  keyof QMIType["components"],
  string
> = {
  readability: "Readability",
  gate_efficiency: "Gate Efficiency",
  modularity: "Modularity",
  scalability: "Scalability",
  gate_diversity: "Gate Diversity",
  complexity: "Circuit Complexity",
};

const componentWeights: Record<
  keyof QMIType["components"],
  string
> = {
  readability: "20%",
  gate_efficiency: "20%",
  modularity: "20%",
  scalability: "15%",
  gate_diversity: "15%",
  complexity: "10%",
};

function getCategoryClasses(category?: string) {
  switch (category) {
    case "Excellent":
      return {
        badge:
          "border-emerald-400/20 bg-emerald-400/10 text-emerald-300",
        score: "text-emerald-300",
        bar: "bg-emerald-400",
      };

    case "Good":
      return {
        badge:
          "border-cyan-400/20 bg-cyan-400/10 text-cyan-300",
        score: "text-cyan-300",
        bar: "bg-cyan-400",
      };

    case "Moderate":
      return {
        badge:
          "border-amber-400/20 bg-amber-400/10 text-amber-300",
        score: "text-amber-300",
        bar: "bg-amber-400",
      };

    default:
      return {
        badge:
          "border-rose-400/20 bg-rose-400/10 text-rose-300",
        score: "text-rose-300",
        bar: "bg-rose-400",
      };
  }
}

export default function QMI({ data }: Props) {
  if (!data) return null;

  const styles = getCategoryClasses(
    data.category
  );

  const components = Object.keys(
    componentLabels
  ) as Array<keyof QMIType["components"]>;

  return (
    <section className="card overflow-hidden">

      {/* =====================================================
          HEADER
      ===================================================== */}

      <div className="border-b border-white/5 px-5 py-5 sm:px-6">

        <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">

          <div>

            <p className="section-kicker">
              Maintainability analysis
            </p>

            <h3 className="mt-1 text-lg font-bold text-white">
              Quantum Maintainability Index
            </h3>

            <p className="mt-1 max-w-2xl text-xs leading-5 text-slate-300">
              Measures how easy the analyzed quantum circuit is
              to understand, maintain, modify and scale.
            </p>

          </div>

          <span
            className={`inline-flex w-fit items-center rounded-full border px-3 py-1.5 text-[10px] font-bold uppercase tracking-[0.12em] ${styles.badge}`}
          >
            {data.category || "Unknown"}
          </span>

        </div>

      </div>

      {/* =====================================================
          SCORE
      ===================================================== */}

      <div className="grid gap-5 border-b border-white/5 p-5 sm:grid-cols-[180px_1fr] sm:items-center sm:p-6">

        <div className="text-center sm:text-left">

          <div
            className={`text-5xl font-black tracking-tight ${styles.score}`}
          >
            {typeof data.score === "number"
              ? data.score.toFixed(1)
              : "—"}
          </div>

          <div className="mt-1 text-xs font-semibold text-slate-400">
            / 100
          </div>

          <div className="mt-2 text-[10px] font-bold uppercase tracking-[0.14em] text-slate-500">
            Maintainability Score
          </div>

        </div>

        <div>

          <div className="mb-2 flex items-center justify-between">

            <span className="text-[10px] font-bold uppercase tracking-[0.12em] text-slate-400">
              Overall QMI
            </span>

            <span className={`text-xs font-bold ${styles.score}`}>
              {data.category}
            </span>

          </div>

          <div className="h-3 overflow-hidden rounded-full bg-white/5">

            <div
              className={`h-full rounded-full transition-all duration-700 ${styles.bar}`}
              style={{
                width: `${Math.max(
                  0,
                  Math.min(
                    100,
                    data.score || 0
                  )
                )}%`,
              }}
            />

          </div>

          <p className="mt-3 text-[11px] leading-5 text-slate-400">
            Higher QMI indicates a circuit that is generally
            easier to understand, maintain and extend.
          </p>

        </div>

      </div>

      {/* =====================================================
          COMPONENT SCORES
      ===================================================== */}

      <div className="p-5 sm:p-6">

        <div className="mb-4">

          <p className="text-sm font-bold text-white">
            Maintainability components
          </p>

          <p className="mt-1 text-[11px] text-slate-400">
            Weighted factors contributing to the QMI score.
          </p>

        </div>

        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">

          {components.map(
            (key) => {

              const value =
                data.components?.[key] ?? 0;

              return (
                <div
                  key={key}
                  className="rounded-2xl border border-white/10 bg-white/[.025] p-4"
                >

                  <div className="flex items-start justify-between gap-3">

                    <div>

                      <p className="text-xs font-bold text-white">
                        {componentLabels[key]}
                      </p>

                      <p className="mt-1 text-[9px] font-semibold uppercase tracking-[0.12em] text-slate-500">
                        Weight{" "}
                        {componentWeights[key]}
                      </p>

                    </div>

                    <span className="text-sm font-black text-cyan-300">
                      {value.toFixed(1)}
                    </span>

                  </div>

                  <div className="mt-3 h-1.5 overflow-hidden rounded-full bg-white/5">

                    <div
                      className="h-full rounded-full bg-cyan-400"
                      style={{
                        width: `${Math.max(
                          0,
                          Math.min(
                            100,
                            value
                          )
                        )}%`,
                      }}
                    />

                  </div>

                </div>
              );
            }
          )}

        </div>

        {/* =================================================
            SCORE BASIS
        ================================================= */}

        {data.basis && (
          <div className="mt-5 rounded-2xl border border-white/10 bg-black/15 p-4">

            <div className="mb-3">

              <p className="text-[10px] font-bold uppercase tracking-[0.14em] text-slate-400">
                Analysis basis
              </p>

              <p className="mt-1 text-[10px] text-slate-500">
                Circuit characteristics used to calculate
                maintainability.
              </p>

            </div>

            <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">

              <div>
                <p className="text-[9px] text-slate-400">
                  Qubits
                </p>

                <p className="mt-1 text-xs font-bold text-white">
                  {data.basis.qubits ?? "—"}
                </p>
              </div>

              <div>
                <p className="text-[9px] text-slate-400">
                  Gates
                </p>

                <p className="mt-1 text-xs font-bold text-white">
                  {data.basis.gate_count ?? "—"}
                </p>
              </div>

              <div>
                <p className="text-[9px] text-slate-400">
                  Depth
                </p>

                <p className="mt-1 text-xs font-bold text-white">
                  {data.basis.depth ?? "—"}
                </p>
              </div>

              <div>
                <p className="text-[9px] text-slate-400">
                  Gate Types
                </p>

                <p className="mt-1 text-xs font-bold text-white">
                  {data.basis
                    .unique_gate_types ?? "—"}
                </p>
              </div>

            </div>

          </div>
        )}

      </div>

    </section>
  );
}
