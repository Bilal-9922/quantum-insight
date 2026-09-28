import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";
export default function HealthChart({components}: {components: Record<string, number>}) {
  const data = Object.entries(components).map(([name,value])=>({name:name.replaceAll("_"," "), value}));
  return <div className="card h-80"><h3 className="mb-2 font-bold">Health Components</h3><ResponsiveContainer width="100%" height="90%"><BarChart data={data}><XAxis dataKey="name" hide/><YAxis domain={[0,100]}/><Tooltip/><Bar dataKey="value"/></BarChart></ResponsiveContainer></div>;
}
