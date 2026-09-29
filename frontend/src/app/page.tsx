import Link from "next/link";
import Image from "next/image";
import { Icon } from "../components/Icons";

const features = [
  ["Quantum Health Index", "A six-factor score that turns circuit complexity, utilization and noise into one readable signal.", "analyze"],
  ["AI Quantum Debugger", "Inspect common circuit errors, understand the cause and generate a practical fix suggestion.", "bug"],
  ["Circuit Optimization", "Detect redundant gates and compare original versus optimized circuit metrics.", "zap"],
  ["Anomaly Detection", "Machine-learning based feature analysis helps flag unusual circuit behaviour.", "spark"],
];

export default function Home() {
  return <div className="relative overflow-hidden rounded-[30px] border border-white/5 hero-grid">
    <div className="glow-orb left-[-80px] top-24 h-72 w-72 bg-cyan-500"/><div className="glow-orb right-[-100px] top-10 h-80 w-80 bg-violet-600"/>
    <section className="relative px-6 pb-20 pt-12 sm:px-10 lg:px-16 lg:pt-20">
      <div className="flex items-center justify-between"><Link href="/" className="flex items-center gap-3"><Image src="/quantuminsight-logo.png" alt="QuantumInsight logo" width={180} height={85} className="h-auto w-[150px] object-contain sm:w-[180px]"/></Link><Link href="/login" className="btn btn-secondary">Sign in <Icon name="arrow" size={15}/></Link></div>
      <div className="mx-auto max-w-5xl pt-20 text-center">
        <div className="badge border-cyan-400/20 bg-cyan-400/5 text-cyan-300"><span className="h-1.5 w-1.5 rounded-full bg-cyan-300 shadow-[0_0_10px_#22d3ee]"/> Quantum circuit intelligence platform</div>
        <h1 className="mt-7 text-5xl font-black leading-[.98] tracking-[-.06em] sm:text-7xl lg:text-[88px]">Understand every <span className="gradient-text">quantum circuit.</span></h1>
        <p className="mx-auto mt-7 max-w-2xl text-base leading-7 text-slate-400 sm:text-lg">Analyze. Debug. Optimize. Explain. QuantumInsight brings Qiskit metrics, Quantum Health Index, anomaly detection and intelligent recommendations into one focused workspace.</p>
        <div className="mt-9 flex flex-col justify-center gap-3 sm:flex-row"><Link href="/register" className="btn btn-primary px-7 py-3.5">Create free account <Icon name="arrow" size={16}/></Link><Link href="/login" className="btn btn-secondary px-7 py-3.5">Open workspace</Link></div>
      </div>
      <div className="mx-auto mt-16 grid max-w-5xl gap-4 sm:grid-cols-3"><div className="card card-hover p-5"><p className="text-xs font-bold text-slate-500">ANALYSIS</p><p className="mt-2 text-3xl font-black">6-factor</p><p className="mt-1 text-xs text-slate-400">Quantum Health Index</p></div><div className="card card-hover p-5"><p className="text-xs font-bold text-slate-500">WORKFLOW</p><p className="mt-2 text-3xl font-black">4-in-1</p><p className="mt-1 text-xs text-slate-400">Analyze · Debug · Optimize · Explain</p></div><div className="card card-hover p-5"><p className="text-xs font-bold text-slate-500">ENGINE</p><p className="mt-2 text-3xl font-black">Qiskit</p><p className="mt-1 text-xs text-slate-400">Static-safe circuit parsing</p></div></div>
    </section>
    <section className="relative border-t border-white/5 bg-black/10 px-6 py-16 sm:px-10 lg:px-16"><div className="mx-auto max-w-6xl"><div className="max-w-2xl"><p className="section-kicker">Built for quantum developers</p><h2 className="mt-3 text-3xl font-black tracking-tight sm:text-5xl">From raw Qiskit code to an actionable circuit report.</h2></div><div className="mt-10 grid gap-4 md:grid-cols-2">{features.map(([title,desc,icon]) => <div key={title} className="card card-hover group p-6"><div className="mb-6 flex h-11 w-11 items-center justify-center rounded-xl bg-cyan-400/10 text-cyan-300"><Icon name={icon}/></div><h3 className="text-lg font-bold">{title}</h3><p className="mt-2 text-sm leading-6 text-slate-400">{desc}</p><Link href="/register" className="mt-5 inline-flex items-center gap-2 text-xs font-bold text-cyan-300 opacity-0 group-hover:opacity-100">Explore workspace <Icon name="arrow" size={14}/></Link></div>)}</div></div></section>
  </div>;
}
