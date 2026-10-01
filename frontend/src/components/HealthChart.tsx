import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";

export default function HealthChart({
  components,
}: {
  components: Record<string, number>;
}) {
  const data = Object.entries(components).map(([name, value]) => ({
    name: name
      .replaceAll("_", " ")
      .replace(/\b\w/g, (char) => char.toUpperCase()),
    value: Math.max(0, Math.min(100, Number(value) || 0)),
  }));

  return (
    <div className="card h-80 overflow-hidden p-5">
      <div className="mb-4 flex items-end justify-between gap-4">
        <div>
          <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-cyan-400">
            QHI components
          </p>

          <h3 className="mt-1 text-sm font-semibold text-white">
            Health component scores
          </h3>

          <p className="mt-1 text-[10px] leading-5 text-slate-600">
            Normalized contribution of each measured health factor.
          </p>
        </div>

        <span className="font-mono text-[9px] uppercase tracking-wider text-slate-600">
          0–100
        </span>
      </div>

      <ResponsiveContainer width="100%" height="78%">
        <BarChart
          data={data}
          margin={{
            top: 5,
            right: 8,
            left: -8,
            bottom: 8,
          }}
        >
          <CartesianGrid
            stroke="rgba(148, 163, 184, 0.10)"
            vertical={false}
          />

          <XAxis
            dataKey="name"
            tick={{
              fill: "#94a3b8",
              fontSize: 9,
            }}
            axisLine={{
              stroke: "rgba(148, 163, 184, 0.16)",
            }}
            tickLine={false}
            interval={0}
            angle={-25}
            textAnchor="end"
            height={48}
          />

          <YAxis
            domain={[0, 100]}
            ticks={[0, 25, 50, 75, 100]}
            tick={{
              fill: "#64748b",
              fontSize: 9,
            }}
            axisLine={false}
            tickLine={false}
          />

          <Tooltip
            cursor={{
              fill: "rgba(34, 211, 238, 0.04)",
            }}
            contentStyle={{
              background: "#0b1224",
              border: "1px solid rgba(148, 163, 184, 0.18)",
              borderRadius: "6px",
              padding: "8px 10px",
              boxShadow: "none",
            }}
            labelStyle={{
              color: "#e2e8f0",
              fontSize: 10,
              fontWeight: 600,
              marginBottom: 3,
            }}
            itemStyle={{
              color: "#67e8f9",
              fontSize: 10,
            }}
            formatter={(value: number | undefined) => [
              `${Number(value ?? 0).toFixed(1)}`,
              "Score",
            ]}
          />

          <Bar
            dataKey="value"
            fill="#22d3ee"
            radius={[2, 2, 0, 0]}
            maxBarSize={42}
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
