export default function HealthScore({
  score,
  category,
}: {
  score: number;
  category: string;
}) {
  const safeScore = Math.min(100, Math.max(0, score));

  return (
    <div className="card health-score-card p-6 text-center">
      <div className="text-sm font-semibold uppercase tracking-widest text-slate-400">
        Quantum Health Index
      </div>

      <div className="my-3 text-6xl font-black text-cyan-400">
        {safeScore}
      </div>

      <div className="text-base font-medium text-slate-200">
        /100 · {category}
      </div>

      <div className="mt-5 h-3 w-full overflow-hidden rounded-full bg-slate-800">
        <div
          className="h-full rounded-full bg-cyan-400 transition-all duration-500"
          style={{
            width: `${safeScore}%`,
          }}
        />
      </div>

      <div className="mt-2 flex justify-between text-xs text-slate-500">
        <span>0</span>
        <span>100</span>
      </div>
    </div>
  );
}
