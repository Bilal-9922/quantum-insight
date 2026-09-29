"use client";
import {useState} from "react"; import {optimize} from "../../services/api"; import OptimizationPanel from "../../components/OptimizationPanel"; import {Icon} from "../../components/Icons"; import {useRequireAuth} from "../../lib/auth";
const sample=`from qiskit import QuantumCircuit
qc = QuantumCircuit(2)
qc.h(0)
qc.x(0)
qc.x(0)
qc.cx(0,1)
qc.cx(0,1)
qc.measure_all()`;
export default function Optimizer(){const {loading}=useRequireAuth();const [code,setCode]=useState(sample);const [res,setRes]=useState<any>();const [busy,setBusy]=useState(false);async function run(){setBusy(true);try{setRes(await optimize(code))}finally{setBusy(false)}}if(loading)return <div className="py-20 text-center text-slate-500">Loading optimizer…</div>;return <div className="space-y-6"><div><p className="section-kicker">Circuit refinement</p><h1 className="mt-2 text-3xl font-black">Circuit Optimizer</h1><p className="mt-2 text-sm text-slate-500">Find redundant operations and compare the original circuit with an optimized version.</p></div><div className="card p-5"><div className="mb-4 flex items-center justify-between"><span className="text-xs font-bold">Original circuit</span><button onClick={()=>setCode(sample)} className="text-[11px] font-bold text-cyan-300">Load sample</button></div><textarea className="code-editor" value={code} onChange={e=>setCode(e.target.value)}/><div className="mt-4 flex justify-end"><button disabled={busy} onClick={run} className="btn btn-primary">{busy?"Optimizing…":"Optimize circuit"}<Icon name="zap" size={15}/></button></div></div><OptimizationPanel data={res}/></div>}
