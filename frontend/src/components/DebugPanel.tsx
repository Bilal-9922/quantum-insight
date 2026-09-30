export default function DebugPanel({ result }: { result: any }) {
  if (!result) return null;

  const suggestedFix = result.suggested_fix;

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

          {/* Automatic fix status */}
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

          {/* Patch note */}
          {result.note && (
            <div className="rounded-xl border border-white/10 bg-black/20 p-3 text-sm leading-6 text-slate-300">
              <b className="text-slate-200">Patch note:</b>{" "}
              {result.note}
            </div>
          )}

          {/* Suggested fix */}
          {suggestedFix?.code && (
            <div className="space-y-3">

              <div>
                <p className="mb-2 text-xs font-bold uppercase tracking-wider text-cyan-300">
                  Suggested Fix
                </p>

                <pre className="overflow-x-auto rounded-xl border border-cyan-400/20 bg-black/30 p-4 text-sm leading-6 text-slate-200">
                  <code>{suggestedFix.code}</code>
                </pre>
              </div>

              {/* Suggestion details */}
              <div className="rounded-xl border border-amber-400/20 bg-amber-400/5 p-3 text-sm leading-6 text-amber-200/80">
                <p>
                  <b>Suggested change:</b>{" "}
                  Qubit {suggestedFix.invalid_qubit} →{" "}
                  Qubit {suggestedFix.suggested_qubit}
                </p>

                <p className="mt-1">
                  <b>Gate:</b> {suggestedFix.gate}
                </p>

                <p className="mt-1">
                  <b>Line:</b> {suggestedFix.line}
                </p>

                {suggestedFix.warning && (
                  <p className="mt-2">
                    ⚠ {suggestedFix.warning}
                  </p>
                )}
              </div>

            </div>
          )}

          {/* Automatically fixed code */}
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
