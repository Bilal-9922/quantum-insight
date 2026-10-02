"use client";

import { useState } from "react";
import { debug } from "../../services/api";
import DebugPanel from "../../components/DebugPanel";
import { Icon } from "../../components/Icons";
import { useRequireAuth } from "../../lib/auth";

type TestSample = {
  name: string;
  description: string;
  code: string;
  error: string;
};

const TEST_SAMPLES: TestSample[] = [
  {
    name: "Valid Qiskit Code",
    description: "Valid circuit with no error",
    code: `from qiskit import QuantumCircuit

qc = QuantumCircuit(2)
qc.h(0)
qc.cx(0, 1)`,
    error: "",
  },

  {
    name: "Syntax Error",
    description: "Missing closing parenthesis",
    code: `from qiskit import QuantumCircuit

qc = QuantumCircuit(2)
qc.h(0
qc.cx(0, 1)`,
    error: "SyntaxError: '(' was never closed",
  },

  {
    name: "Qubit Index Error",
    description: "Qubit index is outside the circuit",
    code: `from qiskit import QuantumCircuit

qc = QuantumCircuit(2)
qc.h(0)
qc.cx(0, 1)
qc.x(3)`,
    error: "Index 3 out of range for size 2",
  },

  {
    name: "Gate Argument Error",
    description: "Two-qubit gate has only one argument",
    code: `from qiskit import QuantumCircuit

qc = QuantumCircuit(2)
qc.cx(0)`,
    error: "The cx gate requires 2 qubit arguments, but only 1 was provided.",
  },

  {
    name: "Classical Bit Error",
    description: "Measurement uses an invalid classical bit",
    code: `from qiskit import QuantumCircuit

qc = QuantumCircuit(2, 1)
qc.h(0)
qc.measure(1, 1)`,
    error:
      "Classical bit index 1 is out of range for a circuit with 1 classical bit.",
  },

  {
    name: "Name Error",
    description: "Undefined qubit variable",
    code: `from qiskit import QuantumCircuit

qc = QuantumCircuit(2)
qc.h(0)
qc.cx(0, 1)
qc.x(qubit)`,
    error: "NameError: name 'qubit' is not defined",
  },

  {
    name: "Unsupported / Fake Code",
    description: "Pseudo quantum code that is not real Qiskit",
    code: `class QuantumRegister:
    def __init__(self, size):
        self.size = size
        self.states = [0.0] * size


class PseudoQuantumCircuit:
    def __init__(self, qreg):
        self.qreg = qreg
        self.operations = []

    def h(self, qubit):
        self.operations.append(("H", qubit))

    def cx(self, control, target):
        self.operations.append(("CX", control, target))


qr = QuantumRegister(2)

qc = PseudoQuantumCircuit(qr)

qc.h(0)
qc.cx(0, 1)`,
    error: "This code is not a real Qiskit QuantumCircuit.",
  },
];

const defaultSample = TEST_SAMPLES[0];

export default function Debugger() {
  const { loading } = useRequireAuth();

  const [code, setCode] = useState(defaultSample.code);
  const [err, setErr] = useState(defaultSample.error);

  const [res, setRes] = useState<any>();
  const [busy, setBusy] = useState(false);

  const [selectedSample, setSelectedSample] = useState(
    defaultSample.name
  );

  function loadSample(sampleName: string) {
    const sample = TEST_SAMPLES.find(
      (item) => item.name === sampleName
    );

    if (!sample) return;

    setSelectedSample(sample.name);
    setCode(sample.code);
    setErr(sample.error);
    setRes(undefined);
  }

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

      {/* Test samples */}
      <section className="card overflow-hidden">
        <div className="border-b border-white/5 px-5 py-4 sm:px-6">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <div className="flex items-center gap-2">
                <span className="grid h-7 w-7 place-items-center rounded-lg bg-violet-400/10 text-violet-300">
                  <Icon name="code" size={14} />
                </span>

                <p className="text-sm font-bold text-slate-200">
                  Test samples
                </p>
              </div>

              <p className="mt-1 text-[11px] text-slate-600">
                Choose a built-in Qiskit debugging test case.
              </p>
            </div>

            <span className="text-[10px] font-bold uppercase tracking-[0.16em] text-slate-600">
              {TEST_SAMPLES.length} test cases
            </span>
          </div>
        </div>

        <div className="p-4 sm:p-5">
          <div className="flex flex-col gap-3 sm:flex-row">
            <select
              value={selectedSample}
              onChange={(e) => loadSample(e.target.value)}
              className="w-full rounded-xl border border-white/10 bg-slate-950 px-4 py-3 text-sm font-medium text-slate-200 outline-none transition focus:border-cyan-400/40 sm:flex-1"
            >
              {TEST_SAMPLES.map((sample) => (
                <option
                  key={sample.name}
                  value={sample.name}
                  className="bg-slate-950"
                >
                  {sample.name}
                </option>
              ))}
            </select>

            <button
              type="button"
              onClick={() => loadSample(selectedSample)}
              className="btn btn-secondary justify-center"
            >
              <Icon name="refresh" size={14} />
              Load Sample
            </button>
          </div>

          <div className="mt-3 rounded-xl border border-white/5 bg-black/10 px-4 py-3">
            <p className="text-xs font-semibold text-slate-300">
              {
                TEST_SAMPLES.find(
                  (sample) => sample.
