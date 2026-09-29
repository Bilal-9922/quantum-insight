export default function AIRecommendation({data}: {data:any}) {
  if (!data) return null;
  return <div className="card"><h3 className="font-bold text-cyan-400">AI Recommendations</h3>
    <p className="mt-2 text-slate-300">{data.summary}</p>
    <ul className="mt-4 list-disc space-y-2 pl-5 text-slate-300">{data.recommendations.map((x:string,i:number)=><li key={i}>{x}</li>)}</ul>
    <p className="mt-4 text-xs text-slate-500">Provider: {data.provider}</p>
  </div>;
}
