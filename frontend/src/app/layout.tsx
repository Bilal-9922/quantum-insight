import "./globals.css";
import Link from "next/link";

export const metadata = {
  title: "QuantumInsight",
  description: "AI-powered quantum circuit intelligence"
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <header className="border-b border-slate-800 bg-slate-950/90">
          <nav className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
            <Link href="/" className="text-xl font-bold text-cyan-400">QuantumInsight</Link>
            <div className="flex gap-4 text-sm text-slate-300">
              <Link href="/dashboard">Dashboard</Link>
              <Link href="/analyzer">Analyzer</Link>
              <Link href="/debugger">Debugger</Link>
              <Link href="/optimizer">Optimizer</Link>
              <Link href="/history">History</Link>
            </div>
          </nav>
        </header>
        <main className="mx-auto min-h-screen max-w-7xl px-6 py-8">{children}</main>
      </body>
    </html>
  );
}
