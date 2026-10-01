export default function HealthScore({
  score,
  category,
}: {
  score: number;
  category: string;
}) {
  const safeScore = Math.min(100, Math.max(0, score));

  return (
    <div className="card p-5 sm:p-6">
      <div className="flex items-start justify-between gap-4 border-b border-white/10 pb-4">
        <div>
          <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-cyan-400">
            Circuit quality
          </p>

          <h3 className="mt-1 text-sm font-semibold text-white">
            Quantum Health Index
          </h3>

          <p className="mt-1 text-xs leading-5 text-slate-500">
            Overall structural health score derived from circuit characteristics.
          </p>
        </div>

        <div className="font-mono text-[10px] text-slate-600">
          QHI
        </div>
      </div>

      <div className="mt-6 flex items-end justify-between gap-4">
        <div>
          <div className="font-mono text-5xl font-semibold tracking-tight text-cyan-300">
            {safeScore.toFixed(1)}
          </div>

          <div className="mt-2 flex items-center gap-2 text-xs">
            <span className="text-slate-500">Score</span>
            <span className="text-slate-700">·</span>
            <span className="font-medium text-slate-300">
              {category}
            </span>
          </div>
        </div>

        <div className="text-right">
          <div className="font-mono text-xs text-slate-500">
            / 100
          </div>

          <div className="mt-1 text-[10px] uppercase tracking-wider text-slate-600">
            Normalized
          </div>
        </div>
      </div>

      <div className="mt-6">
        <div className="mb-2 flex items-center justify-between">
          <span className="text-[10px] uppercase tracking-wider text-slate-600">
            Health scale
          </span>

          <span className="font-mono text-[10px] text-slate-500">
            {safeScore.toFixed(1)}%
          </span>
        </div>

        <div className="h-2 w-full overflow-hidden rounded-sm bg-slate-800">
          <div
            className="h-full bg-cyan-400 transition-all duration-500"
            style={{
              width: `${safeScore}%`,
            }}
          />
        </div>

        <div className="mt-2 flex justify-between font-mono text-[9px] text-slate-600">
          <span>0</span>
          <span>25</span>
          <span>50</span>
          <span>75</span>
          <span>100</span>
        </div>
      </div>

      <div className="mt-5 border-t border-white/10 pt-4">
        <div className="grid grid-cols-2 gap-3 text-xs">
          <div>
            <p className="text-[9px] uppercase tracking-wider text-slate-600">
              Interpretation
            </p>
            <p className="mt-1 text-slate-400">
              {category}
            </p>
          </div>

          <div>
            <p className="text-[9px] uppercase tracking-wider text-slate-600">
              Measurement
            </p>
            <p className="mt-1 text-slate-400">
              0–100 normalized scale
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
