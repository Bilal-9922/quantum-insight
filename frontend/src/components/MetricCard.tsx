export default function MetricCard({
  label,
  value,
}: {
  label: string;
  value: string | number;
}) {
  return (
    <div className="card flex min-h-[110px] flex-col items-center justify-center text-center">
      <div className="text-sm font-medium text-slate-400">
        {label}
      </div>

      <div className="mt-2 text-2xl font-bold text-white">
        {value}
      </div>
    </div>
  );
}
