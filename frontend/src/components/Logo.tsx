import Image from "next/image";
import Link from "next/link";

export default function Logo({ compact = false }: { compact?: boolean }) {
  return (
    <Link href="/" className="flex items-center gap-3">
      <Image
        src="/quantuminsight-logo.png"
        alt="QuantumInsight"
        width={compact ? 48 : 180}
        height={compact ? 48 : 48}
        className="object-contain"
        priority
      />

      {!compact && (
        <span className="text-base font-extrabold tracking-tight">
          Quantum<span className="gradient-text">Insight</span>
        </span>
      )}
    </Link>
  );
}
