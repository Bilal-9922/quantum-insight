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

  const qubitCount = Number(circuit.qubits ?? 0);

  const gates: CircuitGate[] = Array.isArray(circuit.gates)
    ? circuit.gates
    : [];

  if (qubitCount <= 0) {
    return null;
  }

  const normalizedGates = gates.map((gate, index) => ({
    id: `${gate.name ?? "gate"}-${index}`,
    name: String(gate.name ?? "gate"),
    qubits: Array.isArray(gate.qubits)
      ? gate.qubits
          .map(Number)
          .filter(
            (q) =>
              Number.isInteger(q) &&
              q >= 0 &&
              q < qubitCount
          )
      : [],
  }));

  const visibleGates = normalizedGates.filter(
    (gate) => gate.qubits.length > 0
  );

  function label(name: string) {
    const n = name.toLowerCase();

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
      id: "I",
      identity: "I",
      reset: "RESET",
      measure: "M",
      measure_all: "M",
      barrier: "BARRIER",
    };

    return labels[n] ?? name.toUpperCase();
  }

  function isMeasurement(name: string) {
    const n = name.toLowerCase();

    return (
      n === "measure" ||
      n === "measure_all" ||
      n.includes("measure")
    );
  }

  function isBarrier(name: string) {
    return name.toLowerCase().includes("barrier");
  }

  function isCX(name: string) {
    const n = name.toLowerCase();

    return n === "cx" || n === "cnot";
  }

  function isMultiQubit(gate: {
    name: string;
    qubits: number[];
  }) {
    return (
      gate.qubits.length >= 2 &&
      !isMeasurement(gate.name) &&
      !isBarrier(gate.name)
    );
  }

  return (
    <div className="card overflow-hidden">
      {/* Header */}
      <div className="border-b border-white/5 px-5 py-4 sm:px-6">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="section-kicker">
              Quantum circuit
            </p>

            <h3 className="mt-1 text-lg font-bold text-white">
              Circuit Visualizer
            </h3>

            <p className="mt-1 text-xs text-slate-500">
              Gate-by-gate visual representation of the analyzed circuit.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <span className="rounded-lg border border-cyan-400/10 bg-cyan-400/5 px-3 py-1.5 text-[10px] font-bold uppercase tracking-[0.1em] text-cyan-300">
              {qubitCount} Qubit{qubitCount === 1 ? "" : "s"}
            </span>

            <span className="rounded-lg border border-white/5 bg-white/[.02] px-3 py-1.5 text-[10px] font-bold uppercase tracking-[0.1em] text-slate-500">
              {visibleGates.length} Gate
              {visibleGates.length === 1 ? "" : "s"}
            </span>
          </div>
        </div>
      </div>

      {/* Legend */}
      <div className="flex flex-wrap items-center gap-5 border-b border-white/5 bg-black/10 px-5 py-3 sm:px-6">
        <div className="flex items-center gap-2 text-[10px] text-slate-500">
          <span className="h-2 w-2 rounded-full bg-cyan-300" />
          Single-qubit gate
        </div>

        <div className="flex items-center gap-2 text-[10px] text-slate-500">
          <span className="h-2 w-2 rounded-full bg-violet-300" />
          Multi-qubit gate
        </div>

        <div className="flex items-center gap-2 text-[10px] text-slate-500">
          <span className="h-2 w-2 rounded-full bg-emerald-300" />
          Measurement
        </div>
      </div>

      {/* Circuit */}
      <div className="overflow-x-auto p-5 sm:p-6">
        <div
          className="relative min-w-max rounded-2xl border border-white/5 bg-slate-950/70 p-5"
          style={{
            minWidth: `${Math.max(
              620,
              120 + visibleGates.length * 90
            )}px`,
          }}
        >
          {/* Column numbers */}
          <div className="mb-4 flex">
            <div className="w-20 shrink-0" />

            {visibleGates.map((gate, index) => (
              <div
                key={`${gate.id}-number`}
                className="w-[90px] shrink-0 text-center"
              >
                <span className="text-[9px] font-bold uppercase tracking-[0.15em] text-slate-700">
                  Step {index + 1}
                </span>
              </div>
            ))}
          </div>

          {/* Rows */}
          <div className="relative">
            {Array.from(
              { length: qubitCount },
              (_, qubit) => (
                <div
                  key={`row-${qubit}`}
                  className="relative flex h-16 items-center"
                >
                  {/* Qubit label */}
                  <div className="w-20 shrink-0">
                    <span className="font-mono text-sm font-semibold text-slate-300">
                      q[{qubit}]
                    </span>
                  </div>

                  {/* Wire area */}
                  <div className="relative flex h-full flex-1 items-center">
                    {/* Horizontal wire */}
                    <div className="absolute left-0 right-0 top-1/2 h-px bg-slate-700" />

                    {/* Gate columns */}
                    {visibleGates.map(
                      (gate, gateIndex) => {
                        const active =
                          gate.qubits.includes(qubit);

                        return (
                          <div
                            key={`${gate.id}-column-${qubit}`}
                            className="relative flex h-full w-[90px] shrink-0 items-center justify-center"
                          >
                            {active ? (
                              <div
                                className={`relative z-10 grid min-h-9 min-w-12 place-items-center rounded-lg border px-2 text-[10px] font-black tracking-wide shadow-[0_8px_25px_rgba(0,0,0,.3)] ${
                                  isMeasurement(
                                    gate.name
                                  )
                                    ? "border-emerald-300/50 bg-emerald-400/10 text-emerald-300"
                                    : isMultiQubit(
                                        gate
                                      )
                                    ? "border-violet-300/50 bg-violet-400/10 text-violet-200"
                                    : "border-cyan-300/50 bg-cyan-400/10 text-cyan-300"
                                }`}
                              >
                                {isMeasurement(
                                  gate.name
                                ) ? (
                                  <span className="flex items-center gap-1">
                                    <span className="text-sm">
                                      M
                                    </span>
                                    <span className="text-[8px] opacity-60">
                                      ↗
                                    </span>
                                  </span>
                                ) : (
                                  label(gate.name)
                                )}
                              </div>
                            ) : (
                              <span className="relative z-10 text-[10px] text-slate-800">
                                ·
                              </span>
                            )}
                          </div>
                        );
                      }
                    )}
                  </div>
                </div>
              )
            )}

            {/* Multi-qubit connections */}
            {visibleGates.map(
              (gate, gateIndex) => {
                if (!isMultiQubit(gate)) {
                  return null;
                }

                if (gate.qubits.length < 2) {
                  return null;
                }

                const minQubit = Math.min(
                  ...gate.qubits
                );

                const maxQubit = Math.max(
                  ...gate.qubits
                );

                const top =
                  32 + minQubit * 64;

                const height =
                  (maxQubit - minQubit) * 64;

                const left =
                  80 +
                  gateIndex * 90 +
                  45;

                return (
                  <div
                    key={`${gate.id}-connection`}
                    className="pointer-events-none absolute w-px bg-violet-300/70"
                    style={{
                      left: `${left}px`,
                      top: `${top}px`,
                      height: `${height}px`,
                    }}
                  >
                    {/* CX control */}
                    {isCX(gate.name) && (
                      <>
                        <span
                          className="absolute left-1/2 top-0 h-3 w-3 -translate-x-1/2 -translate-y-1/2 rounded-full bg-violet-300 shadow-[0_0_12px_rgba(167,139,250,.6)]"
                        />

                        {/* Target marker */}
                        <span
                          className="absolute bottom-0 left-1/2 grid h-7 w-7 -translate-x-1/2 translate-y-1/2 place-items-center rounded-full border border-violet-300/80 bg-slate-950 text-sm font-black text-violet-200"
                        >
                          +
                        </span>
                      </>
                    )}
                  </div>
                );
              }
            )}
          </div>

          {/* Gate names */}
          <div className="mt-4 flex">
            <div className="w-20 shrink-0" />

            {visibleGates.map((gate) => (
              <div
                key={`${gate.id}-name`}
                className="w-[90px] shrink-0 px-2 text-center"
              >
                <span className="block truncate text-[9px] text-slate-600">
                  {gate.name}
                </span>

                {gate.qubits.length > 1 && (
                  <span className="mt-1 block text-[8px] font-semibold text-violet-400/70">
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
        <div className="flex flex-col gap-1 text-[10px] text-slate-600 sm:flex-row sm:items-center sm:justify-between">
          <span>
            Circuit flow runs from left to right.
          </span>

          <span>
            {visibleGates.length} operation
            {visibleGates.length === 1 ? "" : "s"} detected
          </span>
        </div>
      </div>
    </div>
  );
}
