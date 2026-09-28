export default function OptimizationPanel({data}: {data:any}) {
  if (!data) return null;
  return <div className="card"><h3 className="mb-4 font-bold text-cyan-400">Before vs After</h3>
    <div className="grid gap-3 md:grid-cols-3">
      {[
        ["Gates", data.original.gate_count, data.optimized.gate_count, data.improvement.gate_reduction_percent],
        ["Depth", data.original.depth, data.optimized.depth, data.improvement.depth_reduction_percent],
        ["2Q Gates", data.original.two_qubit_gates, data.optimized.two_qubit_gates, data.improvement.two_qubit_reduction_percent]
      ].map(([name,a,b,p]:any)=><div key={name} className="rounded-xl bg-slate-950 p-4">
        <div className="text-slate-400">{name}</div><div className="mt-2">{a} → {b}</div><div className="mt-1 text-cyan-400">↓ {p}%</div>
      </div>)}
    </div>
  </div>;
}
