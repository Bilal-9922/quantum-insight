"use client";

type CircuitGate = {
  name?: string;
  qubits?: number[];
};

type CircuitData = {
  qubits?: number;
  gates?: CircuitGate[];
};

export default function CircuitViewer({
  circuit,
}: {
  circuit: CircuitData | null | undefined;
}) {
  if (!circuit) return null;

  const qubitCount = Math.max(
    0,
    Number.isFinite(circuit.qubits)
      ? Number(circuit.qubits)
      : 0
  );

  const gates = Array.isArray(circuit.gates)
    ? circuit.gates
    : [];

  if (qubitCount === 0) {
    return null;
  }

  const normalizedGates = gates.map((gate, index) => {
    const qubits = Array.isArray(gate.qubits)
      ? gate.qubits
          .map((q) => Number(q))
          .filter(
            (q) =>
              Number.isInteger(q) &&
              q >= 0 &&
              q < qubitCount
          )
      : [];

    return {
      id: `${gate.name || "gate"}-${index}`,
      name: String(gate.name || "gate"),
      qubits,
    };
  });

  const displayGates = normalizedGates.filter(
    (gate) => gate.qubits.length > 0
  );

  const getGateLabel = (name: string) => {
    const labels: Record<string, string> = {
      h: "H",
      x: "X",
      y: "Y",
      z: "Z",
      s: "S",
      sdg: "S†",
      t: "T",
      tdg: "T†",
      cx: "CX",
      cnot: "CX",
      cz: "CZ",
      swap: "SWAP",
      ccx: "CCX",
      toffoli: "CCX",
      rx: "RX",
      ry: "RY",
      rz: "RZ",
      p: "P",
      u: "U",
      u1: "U1",
      u2: "U2",
      u3: "U3",
      measure: "M",
      measure_all: "M",
      barrier: "│",
      reset: "R",
      id: "I",
      identity: "I",
    };

    const normalized = name.toLowerCase();

    return labels[normalized] || name.toUpperCase();
  };

  const isMeasurement = (name: string) => {
    const normalized = name.toLowerCase();

    return (
      normalized === "measure" ||
      normalized === "measure_all" ||
      normalized.includes("measure")
    );
  };

  const isBarrier = (name: string) => {
    const normalized = name.toLowerCase();

    return (
      normalized === "barrier" ||
      normalized.includes("barrier")
    );
  };

  const isTwoQubitGate = (gate: {
    name: string;
    qubits: number[];
  }) => {
    return (
      gate.qubits.length >= 2 &&
      !isMeasurement(gate.name) &&
      !isBarrier(gate.name)
    );
  };

  const getGateClasses = (name: string) => {
    const normalized = name.toLowerCase();

    if (isMeasurement(name)) {
      return "border-emerald-400/40 bg-emerald-400/10 text-emerald-300";
    }

    if (isBarrier(name)) {
      return "border-violet-400/30 bg-violet-400/5 text-violet-300";
    }

    if (
      normalized === "cx" ||
      normalized === "cnot" ||
      normalized === "cz" ||
      normalized === "swap" ||
      normalized === "ccx" ||
      normalized === "toffoli"
    ) {
      return "border-violet-400/40 bg-violet-400/10 text-violet-300";
    }

    return "border-cyan-400/40 bg-cyan-400/10 text-cyan-300";
  };

  const getColumnHeight = () => {
    return Math.max(48, qubitCount * 58);
  };

  return (
    <div className="card overflow-hidden">
      {/* Header */}
      <div className="border-b border-white/5 px-5 py-4 sm:px-6">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <div className="flex items-center gap-2">
              <span className="grid h-8 w-8 place-items-center rounded-lg border border-cyan-400/10 bg-cyan-400/5 text-cyan-300">
                <svg
                  width="15"
                  height="15"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="1.8"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  aria-hidden="true"
                >
                  <path d="M4 6h16" />
                  <path d="M4 12h16" />
                  <path d="M4 18h16" />
                  <circle cx="8" cy="6" r="2" />
                  <circle cx="15" cy="12" r="2" />
                  <circle cx="11" cy="18" r="2" />
                </svg>
              </span>

              <div>
                <p className="text-sm font-bold text-slate-200">
                  Circuit Visualizer
                </p>

                <p className="text-[10px] uppercase tracking-[0.14em] text-slate-600">
                  Quantum gate sequence
                </p>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <span className="rounded-lg border border-cyan-400/10 bg-cyan-400/5 px-2.5 py-1.5 text-[10px] font-bold uppercase tracking-[0.1em] text-cyan-300">
              {qubitCount} qubit{qubitCount === 1 ? "" : "s"}
            </span>

            <span className="rounded-lg border border-white/5 bg-white/[.02] px-2.5 py-1.5 text-[10px] font-bold uppercase tracking-[0.1em] text-slate-500">
              {displayGates.length} operation
              {displayGates.length === 1 ? "" : "s"}
            </span>
          </div>
        </div>
      </div>

      {/* Legend */}
      <div className="flex flex-wrap items-center gap-x-5 gap-y-2 border-b border-white/5 bg-black/10 px-5 py-3 text-[10px] text-slate-500 sm:px-6">
        <div className="flex items-center gap-2">
          <span className="h-2 w-2 rounded-full bg-cyan-300" />
          Single-qubit gate
        </div>

        <div className="flex items-center gap-2">
          <span className="h-2 w-2 rounded-full bg-violet-300" />
          Multi-qubit gate
        </div>

        <div className="flex items-center gap-2">
          <span className="h-2 w-2 rounded-full bg-emerald-300" />
          Measurement
        </div>
      </div>

      {/* Visualizer */}
      <div className="overflow-x-auto p-5 sm:p-6">
        <div
          className="min-w-max"
          style={{
            minWidth: `${Math.max(
              620,
              150 + displayGates.length * 78
            )}px`,
          }}
        >
          {/* Time axis */}
          <div className="mb-2 flex">
            <div className="w-20 shrink-0" />

            {displayGates.map((gate, index) => (
              <div
                key={gate.id}
                className="flex w-[78px] shrink-0 justify-center"
              >
                <span className="text-[9px] font-bold uppercase tracking-[0.12em] text-slate-700">
                  {index + 1}
                </span>
              </div>
            ))}
          </div>

          {/* Circuit area */}
          <div
            className="relative rounded-2xl border border-white/5 bg-slate-950/50 px-2 py-4"
            style={{
              height: `${getColumnHeight() + 32}px`,
            }}
          >
            {/* Qubit rows */}
            <div className="relative h-full">
              {Array.from(
                { length: qubitCount },
                (_, qubitIndex) => {
                  const top =
                    16 + qubitIndex * 58 + 19;

                  return (
                    <div
                      key={qubitIndex}
                      className="absolute left-0 right-0 flex items-center"
                      style={{
                        top: `${top}px`,
                      }}
                    >
                      {/* Qubit label */}
                      <div className="w-20 shrink-0 px-2">
                        <span className="font-mono text-xs font-semibold text-slate-400">
                          q[{qubitIndex}]
                        </span>
                      </div>

                      {/* Wire */}
                      <div className="relative h-px flex-1 bg-slate-700/70">
                        {displayGates.map(
                          (gate, gateIndex) => {
                            const active =
                              gate.qubits.includes(
                                qubitIndex
                              );

                            return (
                              <div
                                key={`${gate.id}-wire-${qubitIndex}`}
                                className="absolute top-1/2 flex w-[78px] -translate-y-1/2 justify-center"
                                style={{
                                  left: `${gateIndex * 78}px`,
                                }}
                              >
                                {active ? (
                                  <div className="h-8 w-14" />
                                ) : (
                                  <span className="text-[9px] text-slate-800">
                                    ·
                                  </span>
                                )}
                              </div>
                            );
                          }
                        )}
                      </div>
                    </div>
                  );
                }
              )}

              {/* Gate columns */}
              <div className="absolute left-20 right-0 top-0">
                {displayGates.map(
                  (gate, gateIndex) => {
                    const gateTopValues =
                      gate.qubits.map(
                        (qubit) =>
                          16 +
                          qubit * 58 +
                          19
                      );

                    const minTop = Math.min(
                      ...gateTopValues
                    );

                    const maxTop = Math.max(
                      ...gateTopValues
                    );

                    const multi =
                      isTwoQubitGate(gate);

                    return (
                      <div
                        key={gate.id}
                        className="absolute top-0"
                        style={{
                          left: `${gateIndex * 78}px`,
                          width: "78px",
                          height: `${getColumnHeight()}px`,
                        }}
                      >
                        {/* Connection for multi-qubit gates */}
                        {multi &&
                          gate.qubits.length >=
                            2 && (
                            <div
                              className="absolute left-1/2 w-px -translate-x-1/2 bg-violet-300/60"
                              style={{
                                top: `${minTop}px`,
                                height: `${
                                  maxTop - minTop
                                }px`,
                              }}
                            />
                          )}

                        {/* Gate nodes */}
                        {gate.qubits.map(
                          (qubit) => {
                            const top =
                              16 +
                              qubit * 58 +
                              19;

                            const measurement =
                              isMeasurement(
                                gate.name
                              );

                            const barrier =
                              isBarrier(
                                gate.name
                              );

                            return (
                              <div
                                key={`${gate.id}-${qubit}`}
                                className="absolute left-1/2 flex -translate-x-1/2 -translate-y-1/2 items-center justify-center"
                                style={{
                                  top: `${top}px`,
                                }}
                              >
                                {multi &&
                                gate.qubits.length ===
                                  2 ? (
                                  gate.qubits[0] ===
                                  qubit ? (
                                    gate.name
                                      .toLowerCase() ===
                                      "cx" ||
                                    gate.name.toLowerCase() ===
                                      "cnot" ? (
                                      <div className="relative grid h-7 w-7 place-items-center rounded-full border border-violet-300/70 bg-violet-400/10">
                                        <span className="h-2.5 w-2.5 rounded-full bg-violet-300" />
                                      </div>
                                    ) : (
                                      <div className="grid h-7 w-7 place-items-center rounded-full border border-violet-300/60 bg-violet-400/10 text-[9px] font-black text-violet-300">
                                        {getGateLabel(
                                          gate.name
                                        )}
                                      </div>
                                    )
                                  ) : gate.name
                                      .toLowerCase() ===
                                      "cx" ||
                                    gate.name.toLowerCase() ===
                                      "cnot" ? (
                                    <div className="relative grid h-8 w-8 place-items-center rounded-full border border-violet-300/70 bg-violet-400/10">
                                      <span className="absolute h-5 w-px bg-violet-300/70" />
                                      <span className="absolute h-5 w-px rotate-90 bg-violet-300/70" />
                                      <span className="relative z-10 text-[11px] font-black text-violet-200">
                                        +
                                      </span>
                                    </div>
                                  ) : (
                                    <div className="rounded-md border border-violet-300/50 bg-violet-400/10 px-2 py-1 text-[8px] font-black text-violet-200">
                                      {getGateLabel(
                                        gate.name
                                      )}
                                    </div>
                                  )
                                ) : (
                                  <div
                                    className={`grid min-h-8 min-w-10 place-items-center rounded-lg border px-2 text-[9px] font-black uppercase tracking-wide shadow-[0_8px_20px_rgba(0,0,0,.18)] ${getGateClasses(
                                      gate.name
                                    )}`}
                                  >
                                    {measurement ? (
                                      <span className="flex items-center gap-1">
                                        <span className="text-[12px]">
                                          M
                                        </span>
                                        <span className="text-[8px] opacity-60">
                                          ↗
                                        </span>
                                      </span>
                                    ) : barrier ? (
                                      <span className="text-base">
                                        │
                                      </span>
                                    ) : (
                                      getGateLabel(
                                        gate.name
                                      )
                                    )}
                                  </div>
                                )}
                              </div>
                            );
                          }
                        )}
                      </div>
                    );
                  }
                )}
              </div>
            </div>
          </div>

          {/* Operation labels */}
          <div className="mt-3 flex">
            <div className="w-20 shrink-0" />

            {displayGates.map((gate, index) => (
              <div
                key={`${gate.id}-label`}
                className="w-[78px] shrink-0 px-1 text-center"
              >
                <span className="block truncate text-[9px] font-medium text-slate-600">
                  {gate.name}
                </span>

                {gate.qubits.length > 1 && (
                  <span className="mt-0.5 block text-[8px] text-violet-400/60">
                    {gate.qubits.length}Q
                  </span>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="border-t border-white/5 bg-black/10 px-5 py-3 sm:px-6">
        <div className="flex flex-col gap-1 text-[10px] leading-5 text-slate-600 sm:flex-row sm:items-center sm:justify-between">
          <span>
            Circuit flow is read from left to right.
          </span>

          <span>
            {displayGates.length} gate
            {displayGates.length === 1 ? "" : "s"} analyzed
          </span>
        </div>
      </div>
    </div>
  );
}
