"use client";
import {useState} from "react";
import {analyze} from "../../services/api";
import {Analysis} from "../../types/quantum";
import MetricCard from "../../components/MetricCard";
import HealthScore from "../../components/HealthScore";
import HealthChart from "../../components/HealthChart";
import CircuitViewer from "../../components/CircuitViewer";
import AIRecommendation from "../../components/AIRecommendation";
import {Icon} from "../../components/Icons";
import {useRequireAuth} from "../../lib/auth";

const sample=`from qiskit import QuantumCircuit

qc = QuantumCircuit(2)
qc.h(0)
qc.cx(0, 1)
qc.measure_all()`;

export default function Analyzer(){const {loading}=useRequireAuth();const [code,setCode]=useState(sample);const [data,setData]=useState<Analysis|null>(null);const [error,setError]=useState("");const [busy,setBusy]=useState(false);async function run(){setError("");setBusy(true);try{setData(await analyze(code))}catch(e:any){setError(e.message)}finally{setBusy(false)}}if(loading)return <Loading/>;return <div className="space-y-6"><div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-end"><div><p className="section-kicker">Quantum analysis</p><h1 className="mt-2 text-3xl font-black">Circuit Analyzer</h1><p className="mt-2 text-sm text-slate-500">Paste Qiskit Python and turn it into engineering metrics, health signals and recommendations.</p></div><span className="badge text-cyan-300">Static-safe parser</span></div>
  <div className="grid gap-5 xl:grid-cols-[1.15fr_.85fr]"><div className="card p-5"><div className="mb-4 flex items-center justify-between"><div><p className="text-xs font-bold text-slate-300">Circuit source</p><p className="mt-1 text-[11px] text-slate-600">No submitted code is executed directly.</p></div><button onClick={()=>setCode(sample)} className="text-[11px] font-bold text-cyan-300">Load sample</button></div><textarea className="code-editor" value={code} onChange={e=>setCode(e.target.value)}/><div className="mt-4 flex items-center justify-between gap-3"><span className="text-[11px] text-slate-600">{code.split("\n").length} lines · Python</span><button disabled={busy} onClick={run} className="btn btn-primary">{busy?"Analyzing…":"Analyze circuit"}<Icon name="arrow" size={15}/></button></div></div><div className="card p-5"><p className="section-kicker">What you get</p><div className="mt-5 space-y-3">{[["01","Circuit metrics","Qubits, gates, depth and 2-qubit ratio"],["02","Quantum Health Index","Six normalized health components"],["03","Anomaly signal","ML-based feature outlier detection"],["04","Recommendations","Actionable optimization guidance"]].map(([n,t,d])=><div key={n} className="rounded-2xl border border-white/5 bg-white/[.02] p-4"><div className="flex gap-3"><span className="text-xs font-black text-cyan-300">{n}</span><div><p className="text-sm font-bold">{t}</p><p className="mt-1 text-xs leading-5 text-slate-500">{d}</p></div></div></div>)}</div></div></div>
  {error&&<div className="rounded-2xl border border-rose-400/20 bg-rose-400/10 p-4 text-sm text-rose-200">{error}</div>}
  {data&&<div className="space-y-5"><div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4"><MetricCard label="Qubits" value={data.metrics.qubits}/><MetricCard label="Gates" value={data.metrics.gate_count}/><MetricCard label="Depth" value={data.metrics.depth}/><MetricCard label="2Q Gates" value={data.metrics.two_qubit_gates}/></div><div className="grid gap-5 lg:grid-cols-2"><HealthScore score={data.health.score} category={data.health.category}/><HealthChart components={data.health.components}/></div><CircuitViewer circuit={data.circuit}/><AIRecommendation data={data.recommendations}/></div>}
</div>}
function Loading(){return <div className="py-20 text-center text-slate-500">Loading analyzer…</div>}
