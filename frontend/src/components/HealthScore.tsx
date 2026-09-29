export default function HealthScore({score, category}: {score:number; category:string}) {
  return <div className="card text-center">
    <div className="text-sm uppercase tracking-widest text-slate-400">Quantum Health Index</div>
    <div className="my-3 text-6xl font-black text-cyan-400">{score}</div>
    <div className="text-slate-300">/100 · {category}</div>
    <div className="mt-5 h-3 overflow-hidden rounded-full bg-slate-800">
      <div className="h-full bg-cyan-400" style={{width:`${score}%`}} />
    </div>
  </div>;
}
