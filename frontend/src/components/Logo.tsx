import Image from "next/image";
import Link from "next/link";

export default function Logo({ compact = false }: { compact?: boolean }) {
  return (
    <Link href="/" className="flex items-center">
      <Image
        src="/quantuminsight-logo.png"
        alt="QuantumInsight"
        width={compact ? 48 : 180}
        height={48}
        priority
      />
    </Link>
  );
}
