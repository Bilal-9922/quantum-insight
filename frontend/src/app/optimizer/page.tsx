"use client";
import {useState} from "react"; import {optimize} from "../../services/api"; import OptimizationPanel from "../../components/OptimizationPanel";
const sample=`from qiskit import QuantumCircuit
qc = QuantumCircuit(2)
qc.h(0)
qc.x(0)
qc.x(0)
qc.cx(0,1)
qc.cx(0,1)
qc.measure_all()`;
export default function Optimizer(){const [code,setCode]=useState(sample);const [res,setRes]=useState<any>();return <div className="space-y-6"><h1 className="text-3xl font-bold">Circuit Optimizer</h1><textarea className="min-h-72 w-full font-mono" value={code} onChange={e=>setCode(e.target.value)}/><button className="btn btn-primary" onClick={async()=>setRes(await optimize(code))}>Optimize</button><OptimizationPanel data={res}/></div>}
