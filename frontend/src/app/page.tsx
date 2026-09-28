import Link from "next/link";

export default function Home() {
  return <section className="py-20">
    <div className="max-w-4xl">
      <p className="mb-4 text-sm font-bold uppercase tracking-[.3em] text-cyan-400">Quantum circuit intelligence</p>
      <h1 className="text-5xl font-black leading-tight md:text-7xl">Analyze. Debug. Optimize. Explain.</h1>
      <p className="mt-6 max-w-2xl text-lg text-slate-400">QuantumInsight combines Qiskit analysis, a custom Quantum Health Index, ML anomaly detection, optimization and AI-style recommendations in one dashboard.</p>
      <div className="mt-8 flex gap-3"><Link className="btn btn-primary" href="/analyzer">Analyze Circuit</Link><Link className="btn btn-secondary" href="/debugger">Open Debugger</Link></div>
    </div>
  </section>;
}
