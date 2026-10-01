"use client";

import { Icon } from "./Icons";

type HardwareRecommendation = {
  type?: string;
  priority?: "low" | "moderate" | "high" | string;
  title?: string;
  message?: string;
  metric?: number;
};

type HardwareData = {
  available?: boolean;
  execution_level?: "favorable" | "moderate" | "challenging" | string;
  summary?: string;

  hardware_detection?: {
    detected?: boolean;
    provider?: string;
    platform?: string;
    execution_target?: string;
    backend_name?: string;
    circuit_qubits?: number;
    requested_minimum_qubits?: number;
    backend_selection?: string;
    simulator_requested?: boolean | null;
    constraints?: string[];
  };

  recommended_hardware?: {
    system?: string;
    reason?: string;
    circuit_qubits?: number;
    requested_minimum_qubits?: number;
    connectivity_requirement?: string;
    gate_fidelity_requirement?: string;
    noise_sensitivity?: string;
  };

  hardware_characteristics?: {
    circuit_qubits?: number;
    requested_minimum_qubits?: number;
    connectivity_importance?: string;
    gate_fidelity_importance?: string;
    noise_sensitivity?: string;
    recommended_hardware_system?: string;
  };

  recommendations?: HardwareRecommendation[];

  basis?: {
    qubits?: number;
    gate_count?: number;
    depth?: number;
    two_qubit_gates?: number;
    two_qubit_ratio?: number;
    gate_density?: number;
    qubit_utilization?: number;
    noise_score?: number;
    noise_exposure_percent?: number;
  };

  disclaimer?: string;
};

function getPriorityClasses(priority?: string) {
  switch (priority) {
    case "high":
      return {
        badge:
          "border-rose-400/20 bg-rose-400/10 text-rose-300",
        dot: "bg-rose-300",
      };

    case "moderate":
      return {
        badge:
          "border-amber-400/20 bg-amber-400/10 text-amber-300",
        dot: "bg-amber-300",
      };

    default:
      return {
        badge:
          "border-emerald-400/20 bg-emerald-400/10 text-emerald-300",
        dot: "bg-emerald-300",
      };
  }
}

function getExecutionClasses(level?: string) {
  switch (level) {
    case "challenging":
      return "border-rose-400/20 bg-rose-400/10 text-rose-300";

    case "moderate":
      return "border-amber-400/20 bg-amber-400/10 text-amber-300";

    default:
      return "border-emerald-400/20 bg-emerald-400/10 text-emerald-300";
  }
}

function formatPercent(value?: number) {
  if (typeof value !== "number") return "—";

  return `${(value * 100).toFixed(1)}%`;
}

export default function HardwareRecommendations({
  data,
}: {
  data: HardwareData | null | undefined;
}) {
  if (!data?.available) return null;

  const detection = data.hardware_detection;
  const characteristics = data.hardware_characteristics;

  const recommendations = Array.isArray(data.recommendations)
    ? data.recommendations
    : [];

  const recommendedHardware = data.recommended_hardware;

  return (
    <section className="card overflow-hidden">
      {/* HEADER */}

      <div className="border-b border-white/5 px-5 py-5 sm:px-6">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
          <div className="flex items-start gap-3">
            <div className="grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-violet-400/10 text-violet-300">
              <Icon name="shield" size={18} />
            </div>

            <div>
              <p className="section-kicker">
                Hardware readiness
              </p>

              <h3 className="mt-1 text-lg font-bold text-white">
                Hardware Recommendations
              </h3>

              <p className="mt-1 max-w-2xl text-xs leading-5 text-slate-300">
                Hardware guidance based on circuit characteristics
                and hardware information detected from the submitted
                source code.
              </p>
            </div>
          </div>

          <span
            className={`inline-flex w-fit items-center gap-2 rounded-full border px-3 py-1.5 text-[10px] font-bold uppercase tracking-[0.12em] ${getExecutionClasses(
              data.execution_level
            )}`}
          >
            <span className="h-1.5 w-1.5 rounded-full bg-current" />

            {data.execution_level || "unknown"}
          </span>
        </div>

        {data.summary && (
          <div className="mt-5 rounded-xl border border-white/10 bg-white/[.025] px-4 py-3">
            <p className="text-xs leading-5 text-slate-300">
              {data.summary}
            </p>
          </div>
        )}
      </div>

      {/* DETECTED HARDWARE */}

      {detection?.detected && (
        <div className="border-b border-white/5 p-5 sm:p-6">
          <div className="rounded-2xl border border-cyan-400/20 bg-cyan-400/[.04] p-5">
            <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
              <div className="flex items-start gap-3">
                <div className="grid h-10 w-10 shrink-0 place-items-center rounded-xl border border-cyan-400/20 bg-cyan-400/10 text-cyan-300">
                  <Icon name="zap" size={18} />
                </div>

                <div>
                  <p className="text-[10px] font-bold uppercase tracking-[0.14em] text-cyan-300/80">
                    Detected Hardware Target
                  </p>

                  <h4 className="mt-1 text-xl font-black text-white">
                    {detection.provider || "Hardware provider detected"}
                  </h4>

                  {detection.platform && (
                    <p className="mt-1 text-xs font-semibold text-cyan-300">
                      {detection.platform}
                    </p>
                  )}
                </div>
              </div>

              <span className="inline-flex w-fit shrink-0 rounded-full border border-cyan-400/20 bg-cyan-400/10 px-3 py-1.5 text-[9px] font-bold uppercase tracking-[0.12em] text-cyan-300">
                Source detected
              </span>
            </div>

            <div className="mt-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
              <div className="rounded-xl border border-white/10 bg-black/20 p-3">
                <p className="text-[9px] font-bold uppercase tracking-[0.12em] text-slate-400">
                  Circuit Qubits
                </p>

                <p className="mt-1 text-base font-black text-white">
                  {detection.circuit_qubits ?? "—"}
                </p>
              </div>

              <div className="rounded-xl border border-white/10 bg-black/20 p-3">
                <p className="text-[9px] font-bold uppercase tracking-[0.12em] text-slate-400">
                  Requested Backend
                </p>

                <p className="mt-1 text-base font-black text-white">
                  {detection.requested_minimum_qubits
                    ? `≥ ${detection.requested_minimum_qubits}`
                    : "Not specified"}
                </p>

                <p className="mt-1 text-[9px] text-slate-500">
                  minimum qubits
                </p>
              </div>

              <div className="rounded-xl border border-white/10 bg-black/20 p-3">
                <p className="text-[9px] font-bold uppercase tracking-[0.12em] text-slate-400">
                  Execution
                </p>

                <p className="mt-1 text-sm font-bold text-cyan-300">
                  {detection.execution_target || "Not specified"}
                </p>
              </div>

              <div className="rounded-xl border border-white/10 bg-black/20 p-3">
                <p className="text-[9px] font-bold uppercase tracking-[0.12em] text-slate-400">
                  Selection
                </p>

                <p className="mt-1 text-sm font-bold text-cyan-300">
                  {detection.backend_selection || "Not specified"}
                </p>
              </div>
            </div>

            {detection.backend_name && (
              <div className="mt-3 rounded-xl border border-white/10 bg-black/20 px-3 py-3">
                <p className="text-[9px] font-bold uppercase tracking-[0.12em] text-slate-400">
                  Explicit Backend
                </p>

                <p className="mt-1 text-xs font-bold text-white">
                  {detection.backend_name}
                </p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* RECOMMENDED HARDWARE */}

      {recommendedHardware?.system && (
        <div className="border-b border-white/5 p-5 sm:p-6">
          <div className="rounded-2xl border border-violet-400/20 bg-violet-400/[.045] p-5">
            <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
              <div className="flex items-start gap-3">
                <div className="grid h-10 w-10 shrink-0 place-items-center rounded-xl border border-violet-400/20 bg-violet-400/10 text-violet-300">
                  <Icon name="zap" size={18} />
                </div>

                <div>
                  <p className="text-[10px] font-bold uppercase tracking-[0.14em] text-violet-300/80">
                    Recommended Hardware System
                  </p>

                  <h4 className="mt-1 text-xl font-black text-white">
                    {recommendedHardware.system}
                  </h4>

                  {recommendedHardware.reason && (
                    <p className="mt-2 max-w-3xl text-xs leading-6 text-slate-300">
                      {recommendedHardware.reason}
                    </p>
                  )}
                </div>
              </div>

              <span className="inline-flex w-fit shrink-0 rounded-full border border-violet-400/20 bg-violet-400/10 px-3 py-1.5 text-[9px] font-bold uppercase tracking-[0.12em] text-violet-300">
                Circuit + source
              </span>
            </div>

            <div className="mt-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
              <div className="rounded-xl border border-white/10 bg-black/20 p-3">
                <p className="text-[9px] font-bold uppercase tracking-[0.12em] text-slate-400">
                  Circuit Qubits
                </p>

                <p className="mt-1 text-base font-black text-white">
                  {recommendedHardware.circuit_qubits ?? "—"}
                </p>
              </div>

              <div className="rounded-xl border border-white/10 bg-black/20 p-3">
                <p className="text-[9px] font-bold uppercase tracking-[0.12em] text-slate-400">
                  Requested Backend
                </p>

                <p className="mt-1 text-base font-black text-white">
                  {recommendedHardware.requested_minimum_qubits
                    ? `≥ ${recommendedHardware.requested_minimum_qubits}`
                    : "Not specified"}
                </p>
              </div>

              <div className="rounded-xl border border-white/10 bg-black/20 p-3">
                <p className="text-[9px] font-bold uppercase tracking-[0.12em] text-slate-400">
                  Connectivity
                </p>

                <p className="mt-1 text-sm font-bold capitalize text-cyan-300">
                  {recommendedHardware.connectivity_requirement ||
                    "—"}
                </p>
              </div>

              <div className="rounded-xl border border-white/10 bg-black/20 p-3">
                <p className="text-[9px] font-bold uppercase tracking-[0.12em] text-slate-400">
                  Gate Fidelity
                </p>

                <p className="mt-1 text-sm font-bold capitalize text-cyan-300">
                  {recommendedHardware.gate_fidelity_requirement ||
                    "—"}
                </p>
              </div>
            </div>

            <div className="mt-3 rounded-xl border border-white/10 bg-black/20 p-3">
              <p className="text-[9px] font-bold uppercase tracking-[0.12em] text-slate-400">
                Noise Sensitivity
              </p>

              <p className="mt-1 text-sm font-bold capitalize text-cyan-300">
                {recommendedHardware.noise_sensitivity || "—"}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* HARDWARE CHARACTERISTICS */}

      {characteristics && (
        <div className="grid gap-px border-b border-white/5 bg-white/5 sm:grid-cols-4">
          <div className="bg-[#070b18] px-4 py-4">
            <p className="text-[9px] font-bold uppercase tracking-[0.14em] text-slate-400">
              Circuit Qubits
            </p>

            <p className="mt-1 text-lg font-black text-white">
              {characteristics.circuit_qubits ?? "—"}
            </p>
          </div>

          <div className="bg-[#070b18] px-4 py-4">
            <p className="text-[9px] font-bold uppercase tracking-[0.14em] text-slate-400">
              Requested Backend
            </p>

            <p className="mt-1 text-sm font-bold text-cyan-300">
              {characteristics.requested_minimum_qubits
                ? `≥ ${characteristics.requested_minimum_qubits}`
                : "Not specified"}
            </p>
          </div>

          <div className="bg-[#070b18] px-4 py-4">
            <p className="text-[9px] font-bold uppercase tracking-[0.14em] text-slate-400">
              Connectivity
            </p>

            <p className="mt-1 text-sm font-bold capitalize text-cyan-300">
              {characteristics.connectivity_importance || "—"}
            </p>
          </div>

          <div className="bg-[#070b18] px-4 py-4">
            <p className="text-[9px] font-bold uppercase tracking-[0.14em] text-slate-400">
              Gate Fidelity
            </p>

            <p className="mt-1 text-sm font-bold capitalize text-cyan-300">
              {characteristics.gate_fidelity_importance || "—"}
            </p>
          </div>
        </div>
      )}

      {/* RECOMMENDATIONS */}

      <div className="p-5 sm:p-6">
        <div className="mb-4 flex items-center justify-between">
          <div>
            <p className="text-sm font-bold text-white">
              Execution guidance
            </p>

            <p className="mt-1 text-[11px] text-slate-400">
              Circuit and hardware considerations before execution
            </p>
          </div>

          <span className="rounded-lg border border-white/10 bg-white/[.03] px-2.5 py-1 text-[10px] font-bold text-slate-300">
            {recommendations.length} checks
          </span>
        </div>

        <div className="grid gap-3 lg:grid-cols-2">
          {recommendations.map((item, index) => {
            const classes = getPriorityClasses(item.priority);

            return (
              <div
                key={`${item.type || "recommendation"}-${index}`}
                className="rounded-2xl border border-white/10 bg-white/[.025] p-4 transition hover:border-violet-400/20 hover:bg-violet-400/[.035]"
              >
                <div className="flex items-start gap-3">
                  <div className="mt-1 grid h-8 w-8 shrink-0 place-items-center rounded-lg bg-violet-400/10 text-violet-300">
                    <Icon name="zap" size={14} />
                  </div>

                  <div className="min-w-0 flex-1">
                    <div className="flex flex-wrap items-center justify-between gap-2">
                      <p className="text-sm font-bold text-white">
                        {item.title || "Hardware consideration"}
                      </p>

                      <span
                        className={`inline-flex items-center gap-1.5 rounded-full border px-2 py-1 text-[9px] font-bold uppercase tracking-[0.1em] ${classes.badge}`}
                      >
                        <span
                          className={`h-1.5 w-1.5 rounded-full ${classes.dot}`}
                        />

                        {item.priority || "low"}
                      </span>
                    </div>

                    <p className="mt-2 text-xs leading-6 text-slate-300">
                      {item.message}
                    </p>

                    {typeof item.metric === "number" && (
                      <div className="mt-3 flex items-center">
                        <span className="text-[9px] font-bold uppercase tracking-[0.12em] text-slate-400">
                          Metric
                        </span>

                        <span className="ml-2 text-[10px] font-semibold text-slate-200">
                          {item.type === "connectivity"
                            ? formatPercent(item.metric)
                            : item.metric}
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* ANALYSIS BASIS */}

        {data.basis && (
          <div className="mt-5 rounded-2xl border border-white/10 bg-black/15 p-4">
            <div className="mb-3">
              <p className="text-[10px] font-bold uppercase tracking-[0.14em] text-slate-400">
                Analysis basis
              </p>

              <p className="mt-1 text-[10px] text-slate-500">
                Circuit metrics used alongside detected hardware
                information.
              </p>
            </div>

            <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
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
                  2Q Gates
                </p>

                <p className="mt-1 text-xs font-bold text-white">
                  {data.basis.two_qubit_gates ?? "—"}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* DISCLAIMER */}

        {data.disclaimer && (
          <div className="mt-4 flex items-start gap-2 rounded-xl border border-amber-400/15 bg-amber-400/[.04] px-3 py-3">
            <Icon
              name="shield"
              size={13}
              className="mt-0.5 shrink-0 text-amber-300"
            />

            <p className="text-[10px] leading-5 text-slate-400">
              {data.disclaimer}
            </p>
          </div>
        )}
      </div>
    </section>
  );
}
