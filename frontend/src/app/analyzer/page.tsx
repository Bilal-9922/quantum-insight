"use client";
import {useState} from "react";
import {analyze} from "../../services/api";
import {Analysis} from "../../types/quantum";
import MetricCard from "../../components/MetricCard";
import HealthScore from "../../components/HealthScore";
import HealthChart from "../../components/HealthChart";
import CircuitViewer from "../../components/CircuitViewer";
import AIRecommendation from "../../components/AIRecommendation";

const sample = `from qiskit import QuantumCircuit

qc = QuantumCircuit(2)
qc.h(0)
qc.cx(0, 1)
qc.measure_all()`;

export default function Analyzer() {
  const [code,setCode]=useState(sample); const [data,setData]=useState<Analysis|null>(null); const [error,setError]=useState("");
  async function run(){setError(""); try{setData(await analyze(code));}catch(e:any){setError(e.message)}}
  return <div className="space-y-6"><div><h1 className="text-3xl font-bold">Circuit Analyzer</h1><p className="text-slate-400">Paste Qiskit Python and analyze it.</p></div>
    <textarea className="min-h-72 w-full font-mono text-sm" value={code} onChange={e=>setCode(e.target.value)}/>
    <button className="btn btn-primary" onClick={run}>Analyze Circuit</button>
    {error && <div className="rounded-xl border border-red-500/40 bg-red-500/10 p-4">{error}</div>}
    {data && <><div className="grid gap-4 md:grid-cols-4"><MetricCard label="Qubits" value={data.metrics.qubits}/><MetricCard label="Gates" value={data.metrics.gate_count}/><MetricCard label="Depth" value={data.metrics.depth}/><MetricCard label="2Q Gates" value={data.metrics.two_qubit_gates}/></div>
      <div className="grid gap-6 md:grid-cols-2"><HealthScore score={data.health.score} category={data.health.category}/><HealthChart components={data.health.components}/></div>
      <CircuitViewer circuit={data.circuit}/><AIRecommendation data={data.recommendations}/></>}
  </div>;
}
