export default function DebugPanel({ result }: { result: any }) {
  if (!result) return null;

  return (
    <div className="card space-y-4">
      <h3 className="font-bold text-cyan-400">Debug result</h3>

      <p>
        <b>Type:</b> {result.error?.type}
      </p>

      <p>
        <b>Diagnosis:</b> {result.diagnosis}
      </p>

      <ul className="list-disc pl-5">
        {result.suggestions?.map((x: string, i: number) => (
          <li key={i}>{x}</li>
        ))}
      </ul>

      <p>
        <b>Verified:</b>{" "}
        <span
          className={
            result.verified
              ? "text-emerald-400"
              : "text-red-400"
          }
        >
          {String(result.verified)}
        </span>
      </p>

      {/* Patch information */}
      {result.changed !== undefined && (
        <div className="space-y-3 border-t border-white/10 pt-4">
          <p>
            <b>Automatic fix:</b>{" "}
            <span
              className={
                result.changed
                  ? "text-amber-300"
                  : "text-slate-400"
              }
            >
              {result.changed ? "Applied" : "Not applied"}
            </span>
          </p>

          {result.note && (
            <div className="rounded-xl border border-white/10 bg-black/20 p-3 text-sm leading-6 text-slate-300">
              <b className="text-slate-200">Patch note:</b>{" "}
              {result.note}
            </div>
          )}

          {result.changed && result.fixed_code && (
            <div>
              <p className="mb-2 text-xs font-bold uppercase tracking-wider text-slate-400">
                Fixed code
              </p>

              <pre className="overflow-x-auto rounded-xl border border-white/10 bg-black/30 p-4 text-sm leading-6 text-slate-200">
                <code>{result.fixed_code}</code>
              </pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
