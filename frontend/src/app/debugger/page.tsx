"use client";
import {useState} from "react";
import {debug} from "../../services/api";
import DebugPanel from "../../components/DebugPanel";
const sample=`from qiskit import QuantumCircuit
qc = QuantumCircuit(2)
qc.h(0)
qc.cx(0, 1)`;
export default function Debugger(){const [code,setCode]=useState(sample);const [err,setErr]=useState("Qubit index error: qubit 3 is outside the circuit");const [res,setRes]=useState<any>();const [busy,setBusy]=useState(false);
async function run(){setBusy(true);try{setRes(await debug(code,err))}finally{setBusy(false)}}
return <div className="space-y-6"><h1 className="text-3xl font-bold">AI Quantum Debugger</h1><div className="grid gap-6 md:grid-cols-2"><textarea className="min-h-80 font-mono" value={code} onChange={e=>setCode(e.target.value)}/><div className="space-y-3"><textarea className="min-h-40 w-full" value={err} onChange={e=>setErr(e.target.value)}/><button className="btn btn-primary" onClick={run}>{busy?"Analyzing...":"Fix With AI"}</button></div></div><DebugPanel result={res}/></div>}
