export default function DebugPanel({result}: {result:any}) {
  if (!result) return null;
  return <div className="card space-y-3"><h3 className="font-bold text-cyan-400">Debug result</h3>
    <p><b>Type:</b> {result.error?.type}</p>
    <p><b>Diagnosis:</b> {result.diagnosis}</p>
    <ul className="list-disc pl-5">{result.suggestions?.map((x:string,i:number)=><li key={i}>{x}</li>)}</ul>
    <p><b>Verified:</b> {String(result.verified)}</p>
  </div>;
}
