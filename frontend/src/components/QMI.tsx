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
        label: "text-emerald-300",
        bar: "bg-emerald-400",
      };

    case "Good":
      return {
        label: "text-cyan-300",
        bar: "bg-cyan-400",
      };

    case "Moderate":
      return {
        label: "text-amber-300",
        bar: "bg-amber-400",
      };

    default:
      return {
        label: "text-rose-300",
        bar: "bg-rose-400",
      };
  }
}

export default function QMI({ data }: Props) {
  if (!data) return null;

  const styles = getCategoryClasses(data.category);

  const components = Object.keys(
    componentLabels
  ) as Array<keyof QMIType["components"]>;

  const safeScore = Math.max(
    0,
    Math.min(100, Number(data.score) || 0)
  );

  return (
    <section className="card overflow-hidden">
      {/* Header */}
      <div className="border-b border-white/10 px-5 py-5 sm:px-6">
        <div className="flex items-start justify-between gap-4">
          <div>
            <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-cyan-400">
              Maintainability analysis
            </p>

            <h3 className="mt-1 text-lg font-semibold text-white">
              Quantum Maintainability Index
            </h3>

            <p className="mt-2 max-w-xl text-xs leading-5 text-slate-500">
              Measures how easily the analyzed circuit can be
              understood, maintained, modified and scaled.
            </p>
          </div>

          <div className="shrink-0 text-right">
            <p className="font-mono text-[10px] text-slate-600">
              QMI
            </p>

            <p
              className={`mt-1 text-xs font-semibold ${styles.label}`}
            >
              {data.category || "Unknown"}
            </p>
          </div>
        </div>
      </div>

      {/* Score */}
      <div className="border-b border-white/10 p-5 sm:p-6">
        <div className="flex items-end justify-between gap-4">
          <div>
            <div
              className={`font-mono text-5xl font-semibold tracking-tight ${styles.label}`}
            >
              {typeof data.score === "number"
                ? data.score.toFixed(1)
                : "—"}
            </div>

            <div className="mt-2 flex items-center gap-2 text-xs">
              <span className="text-slate-500">
                Maintainability score
              </span>

              <span className="text-slate-700">
                ·
              </span>

              <span className={styles.label}>
                {data.category || "Unknown"}
              </span>
            </div>
          </div>

          <div className="text-right">
            <p className="font-mono text-xs text-slate-500">
              / 100
            </p>

            <p className="mt-1 text-[9px] uppercase tracking-wider text-slate-600">
              Normalized
            </p>
          </div>
        </div>

        <div className="mt-6">
          <div className="mb-2 flex items-center justify-between">
            <span className="text-[9px] uppercase tracking-wider text-slate-600">
              Maintainability scale
            </span>

            <span
              className={`font-mono text-[10px] ${styles.label}`}
            >
              {safeScore.toFixed(1)}%
            </span>
          </div>

          <div className="h-2 overflow-hidden rounded-sm bg-slate-800">
            <div
              className={`h-full transition-all duration-500 ${styles.bar}`}
              style={{
                width: `${safeScore}%`,
              }}
            />
          </div>

          <div className="mt-2 flex justify-between font-mono text-[9px] text-slate-600">
            <span>0</span>
            <span>25</span>
            <span>50</span>
            <span>75</span>
            <span>100</span>
          </div>
        </div>

        <p className="mt-5 border-t border-white/10 pt-4 text-[10px] leading-5 text-slate-600">
          Higher QMI indicates stronger maintainability based
          on the measured circuit characteristics.
        </p>
      </div>

      {/* Components */}
      <div className="p-5 sm:p-6">
        <div className="mb-4">
          <p className="text-sm font-semibold text-white">
            Maintainability components
          </p>

          <p className="mt-1 text-[10px] leading-5 text-slate-500">
            Weighted factors contributing to the overall QMI.
          </p>
        </div>

        <div className="space-y-3">
          {components.map((key) => {
            const value = Math.max(
              0,
              Math.min(
                100,
                Number(data.components?.[key]) || 0
              )
            );

            return (
              <div
                key={key}
                className="border-b border-white/5 pb-3 last:border-0 last:pb-0"
              >
                <div className="flex items-center justify-between gap-4">
                  <div className="min-w-0">
                    <p className="text-xs font-medium text-slate-200">
                      {componentLabels[key]}
                    </p>

                    <p className="mt-1 font-mono text-[9px] uppercase tracking-wider text-slate-600">
                      Weight {componentWeights[key]}
                    </p>
                  </div>

                  <span className="shrink-0 font-mono text-xs text-cyan-300">
                    {value.toFixed(1)}
                  </span>
                </div>

                <div className="mt-2 h-1.5 overflow-hidden rounded-sm bg-slate-800">
                  <div
                    className="h-full bg-cyan-400 transition-all duration-500"
                    style={{
                      width: `${value}%`,
                    }}
                  />
                </div>
              </div>
            );
          })}
        </div>

        {/* Analysis basis */}
        {data.basis && (
          <div className="mt-6 border-t border-white/10 pt-5">
            <div className="mb-4">
              <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-slate-400">
                Analysis basis
              </p>

              <p className="mt-1 text-[10px] leading-5 text-slate-600">
                Circuit characteristics used to calculate
                maintainability.
              </p>
            </div>

            <div className="grid grid-cols-2 gap-x-6 gap-y-4 sm:grid-cols-4">
              <div>
                <p className="text-[9px] uppercase tracking-wider text-slate-600">
                  Qubits
                </p>

                <p className="mt-1 font-mono text-xs text-slate-300">
                  {data.basis.qubits ?? "—"}
                </p>
              </div>

              <div>
                <p className="text-[9px] uppercase tracking-wider text-slate-600">
                  Gates
                </p>

                <p className="mt-1 font-mono text-xs text-slate-300">
                  {data.basis.gate_count ?? "—"}
                </p>
              </div>

              <div>
                <p className="text-[9px] uppercase tracking-wider text-slate-600">
                  Depth
                </p>

                <p className="mt-1 font-mono text-xs text-slate-300">
                  {data.basis.depth ?? "—"}
                </p>
              </div>

              <div>
                <p className="text-[9px] uppercase tracking-wider text-slate-600">
                  Gate types
                </p>

                <p className="mt-1 font-mono text-xs text-slate-300">
                  {data.basis.unique_gate_types ?? "—"}
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </section>
  );
}
