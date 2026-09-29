import Image from "next/image";
import Link from "next/link";

export default function Logo({ compact = false }: { compact?: boolean }) {
  return <Link href="/" className="flex items-center gap-3 group">
    <Image src="/quantuminsight-logo.png" alt="QuantumInsight" width={compact ? 42 : 54} height={compact ? 25 : 26} className="h-auto w-auto object-contain drop-shadow-[0_0_14px_rgba(34,211,238,.22)]" priority />
    {!compact && <span className="hidden text-base font-extrabold tracking-tight sm:block">Quantum<span className="gradient-text">Insight</span></span>}
  </Link>;
}
