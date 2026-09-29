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
    name: name.replaceAll("_", " "),
    value,
  }));

  return (
    <div className="card health-card h-80 p-5">
      <h3 className="mb-3 font-bold text-white">
        Health Components
      </h3>

      <ResponsiveContainer width="100%" height="85%">
        <BarChart
          data={data}
          margin={{
            top: 10,
            right: 10,
            left: 0,
            bottom: 10,
          }}
        >
          <CartesianGrid
            stroke="rgba(148, 163, 184, 0.12)"
            vertical={false}
          />

          <XAxis
            dataKey="name"
            tick={{
              fill: "#94a3b8",
              fontSize: 11,
            }}
            axisLine={{
              stroke: "rgba(148, 163, 184, 0.2)",
            }}
            tickLine={false}
            interval={0}
            angle={-25}
            textAnchor="end"
            height={50}
          />

          <YAxis
            domain={[0, 100]}
            tick={{
              fill: "#94a3b8",
              fontSize: 11,
            }}
            axisLine={false}
            tickLine={false}
          />

          <Tooltip
            cursor={{
              fill: "rgba(34, 211, 238, 0.06)",
            }}
            contentStyle={{
              background: "#0b1224",
              border: "1px solid rgba(148, 163, 184, 0.2)",
              borderRadius: "10px",
              color: "#ffffff",
            }}
            labelStyle={{
              color: "#ffffff",
              fontWeight: 700,
            }}
            itemStyle={{
              color: "#67e8f9",
            }}
          />

          <Bar
            dataKey="value"
            fill="#22d3ee"
            radius={[6, 6, 0, 0]}
            maxBarSize={55}
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
