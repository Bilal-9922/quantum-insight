export default function CircuitViewer({circuit}: {circuit:any}) {
  if (!circuit) return null;
  return <div className="card overflow-auto"><h3 className="mb-3 font-bold">Circuit operations</h3>
    {Array.from({length: circuit.qubits}, (_,q)=><div key={q} className="mb-2 flex min-w-max items-center gap-2">
      <span className="w-16 text-slate-400">q[{q}]</span>
      {circuit.gates.map((g:any,i:number)=><span key={i} className={`rounded border px-3 py-2 text-xs ${g.qubits.includes(q) ? "border-cyan-400 bg-cyan-500/10" : "border-slate-800 opacity-30"}`}>{g.qubits.includes(q) ? g.name : "·"}</span>)}
    </div>)}
  </div>;
}
