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

  if (qubitCount <= 0) return null;

  const normalizedGates = gates
    .map((gate, index) => ({
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
    }))
    .filter((gate) => gate.qubits.length > 0);

  function getLabel(name: string) {
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
      reset: "RESET",
      id: "I",
      identity: "I",
      measure: "M",
      measure_all: "M",
      barrier: "BARRIER",
    };

    return labels[name.toLowerCase()] ?? name.toUpperCase();
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
    <div className="grid gap-5 xl:grid-cols-[0.8fr_1.2fr]">
      {/* Circuit operations */}
      <div className="card overflow-hidden">
        <div className="border-b border-white/10 px-5 py-5">
          <div className="flex items-start justify-between gap-4">
            <div>
              <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-cyan-400">
                Circuit data
              </p>

              <h3 className="mt-1 text-lg font-semibold text-white">
                Circuit Operations
              </h3>

              <p className="mt-2 text-xs leading-5 text-slate-500">
                Operations detected from the analyzed quantum circuit.
              </p>
            </div>

            <div className="shrink-0 text-right">
              <p className="font-mono text-[10px] text-slate-600">
                OPS
              </p>

              <p className="mt-1 font-mono text-xs text-cyan-300">
                {normalizedGates.length}
              </p>
            </div>
          </div>
        </div>

        <div className="p-5">
          <div className="overflow-x-auto border border-white/10 bg-slate-950/70">
            <div className="min-w-max p-5">
              <div className="mb-4 flex items-center border-b border-white/5 pb-3">
                <div className="w-14 shrink-0" />

                <p className="font-mono text-[9px] uppercase tracking-wider text-slate-600">
                  Operation sequence
                </p>
              </div>

              <div className="space-y-2">
                {Array.from(
                  { length: qubitCount },
                  (_, qubit) => (
                    <div
                      key={`operation-row-${qubit}`}
                      className="flex items-center"
                    >
                      <div className="w-14 shrink-0">
                        <span className="font-mono text-xs text-slate-400">
                          q[{qubit}]
                        </span>
                      </div>

                      <div className="flex items-center">
                        {normalizedGates.map((gate) => {
                          const active =
                            gate.qubits.includes(qubit);

                          return (
                            <div
                              key={`${gate.id}-${qubit}`}
                              className="flex h-10 w-[68px] shrink-0 items-center justify-center"
                            >
                              {active ? (
                                <span
                                  className={`inline-flex min-w-9 items-center justify-center border px-2 py-1.5 font-mono text-[9px] font-semibold ${
                                    isMeasurement(gate.name)
                                      ? "border-emerald-400/30 bg-emerald-400/5 text-emerald-300"
                                      : isMultiQubit(gate)
                                      ? "border-violet-400/30 bg-violet-400/5 text-violet-300"
                                      : "border-cyan-400/30 bg-cyan-400/5 text-cyan-300"
                                  }`}
                                >
                                  {isMeasurement(gate.name)
                                    ? "M"
                                    : getLabel(gate.name)}
                                </span>
                              ) : (
                                <span className="text-[8px] text-slate-800">
                                  ·
                                </span>
                              )}
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  )
                )}
              </div>

              <div className="mt-4 flex border-t border-white/5 pt-3">
                <div className="w-14 shrink-0" />

                {normalizedGates.map((gate) => (
                  <div
                    key={`${gate.id}-label`}
                    className="w-[68px] shrink-0 text-center"
                  >
                    <span className="block truncate font-mono text-[8px] text-slate-600">
                      {gate.name}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        <div className="border-t border-white/10 px-5 py-4">
          <div className="grid grid-cols-2 gap-5">
            <div>
              <p className="text-[9px] uppercase tracking-wider text-slate-600">
                Qubits
              </p>

              <p className="mt-1 font-mono text-lg text-slate-300">
                {qubitCount}
              </p>
            </div>

            <div>
              <p className="text-[9px] uppercase tracking-wider text-slate-600">
                Operations
              </p>

              <p className="mt-1 font-mono text-lg text-slate-300">
                {normalizedGates.length}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Circuit visualizer */}
      <div className="card overflow-hidden">
        <div className="border-b border-white/10 px-5 py-5">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
            <div>
              <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-cyan-400">
                Quantum circuit
              </p>

              <h3 className="mt-1 text-lg font-semibold text-white">
                Circuit Visualizer
              </h3>

              <p className="mt-2 text-xs leading-5 text-slate-500">
                Gate-by-gate representation of the analyzed circuit.
              </p>
            </div>

            <div className="flex items-center gap-4 font-mono text-[10px]">
              <span className="text-cyan-300">
                {qubitCount}Q
              </span>

              <span className="text-slate-500">
                {normalizedGates.length}G
              </span>
            </div>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-5 border-b border-white/10 px-5 py-3">
          <div className="flex items-center gap-2 text-[10px] text-slate-500">
            <span className="h-1.5 w-1.5 bg-cyan-300" />
            Single-qubit
          </div>

          <div className="flex items-center gap-2 text-[10px] text-slate-500">
            <span className="h-1.5 w-1.5 bg-violet-300" />
            Multi-qubit
          </div>

          <div className="flex items-center gap-2 text-[10px] text-slate-500">
            <span className="h-1.5 w-1.5 bg-emerald-300" />
            Measurement
          </div>
        </div>

        <div className="overflow-x-auto p-5">
          <div
            className="min-w-max border border-white/10 bg-slate-950/70 p-5"
            style={{
              minWidth: `${Math.max(
                540,
                120 + normalizedGates.length * 85
              )}px`,
            }}
          >
            <div className="mb-3 flex border-b border-white/5 pb-3">
              <div className="w-16 shrink-0" />

              {normalizedGates.map((gate, index) => (
                <div
                  key={`${gate.id}-step`}
                  className="w-[85px] shrink-0 text-center"
                >
                  <span className="font-mono text-[8px] uppercase tracking-wider text-slate-700">
                    {String(index + 1).padStart(2, "0")}
                  </span>
                </div>
              ))}
            </div>

            <div className="relative">
              {Array.from(
                { length: qubitCount },
                (_, qubit) => (
                  <div
                    key={`visual-row-${qubit}`}
                    className="relative flex h-16 items-center"
                  >
                    <div className="w-16 shrink-0">
                      <span className="font-mono text-xs text-slate-400">
                        q[{qubit}]
                      </span>
                    </div>

                    <div className="relative flex flex-1 items-center">
                      <div className="absolute left-0 right-0 top-1/2 h-px bg-slate-700" />

                      {normalizedGates.map((gate) => {
                        const active =
                          gate.qubits.includes(qubit);

                        return (
                          <div
                            key={`${gate.id}-visual-${qubit}`}
                            className="relative flex h-16 w-[85px] shrink-0 items-center justify-center"
                          >
                            {active ? (
                              <div
                                className={`relative z-10 grid min-h-9 min-w-11 place-items-center border px-2 font-mono text-[9px] font-semibold ${
                                  isMeasurement(gate.name)
                                    ? "border-emerald-300/40 bg-emerald-400/5 text-emerald-300"
                                    : isMultiQubit(gate)
                                    ? "border-violet-300/40 bg-violet-400/5 text-violet-200"
                                    : "border-cyan-300/40 bg-cyan-400/5 text-cyan-300"
                                }`}
                              >
                                {isMeasurement(gate.name)
                                  ? "M"
                                  : getLabel(gate.name)}
                              </div>
                            ) : (
                              <span className="relative z-10 text-[8px] text-slate-800">
                                ·
                              </span>
                            )}
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )
              )}

              {/* Multi-qubit connections */}
              {normalizedGates.map((gate, gateIndex) => {
                if (
                  !isMultiQubit(gate) ||
                  gate.qubits.length < 2
                ) {
                  return null;
                }

                const minQubit = Math.min(...gate.qubits);
                const maxQubit = Math.max(...gate.qubits);

                const top = 32 + minQubit * 64;
                const height =
                  (maxQubit - minQubit) * 64;

                const left =
                  16 +
                  85 * gateIndex +
                  42.5;

                return (
                  <div
                    key={`${gate.id}-line`}
                    className="pointer-events-none absolute w-px bg-violet-300/60"
                    style={{
                      left: `${left}px`,
                      top: `${top}px`,
                      height: `${height}px`,
                    }}
                  >
                    {isCX(gate.name) && (
                      <>
                        <span className="absolute left-1/2 top-0 h-2.5 w-2.5 -translate-x-1/2 -translate-y-1/2 rounded-full bg-violet-300" />

                        <span className="absolute bottom-0 left-1/2 grid h-6 w-6 -translate-x-1/2 translate-y-1/2 place-items-center border border-violet-300/70 bg-slate-950 font-mono text-sm text-violet-200">
                          +
                        </span>
                      </>
                    )}
                  </div>
                );
              })}
            </div>

            <div className="mt-4 flex border-t border-white/5 pt-3">
              <div className="w-16 shrink-0" />

              {normalizedGates.map((gate) => (
                <div
                  key={`${gate.id}-label`}
                  className="w-[85px] shrink-0 text-center"
                >
                  <span className="block truncate font-mono text-[8px] text-slate-600">
                    {gate.name}
                  </span>

                  {gate.qubits.length > 1 && (
                    <span className="mt-1 block font-mono text-[8px] text-violet-400/70">
                      {gate.qubits.length}Q
                    </span>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="border-t border-white/10 px-5 py-3">
          <div className="flex items-center justify-between gap-4 font-mono text-[9px] text-slate-600">
            <span>
              LEFT → RIGHT
            </span>

            <span>
              {normalizedGates.length} operation
              {normalizedGates.length === 1 ? "" : "s"} detected
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
