export default function MetricCard({label, value}: {label: string; value: string | number}) {
  return <div className="card"><div className="text-sm text-slate-400">{label}</div><div className="mt-2 text-2xl font-bold">{value}</div></div>;
}
