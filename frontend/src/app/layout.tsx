import "./globals.css";
import { AuthProvider } from "../lib/auth";
import AppShell from "../components/AppShell";

export const metadata = {
  title: "QuantumInsight | Quantum Circuit Intelligence",
  description: "Analyze, debug and optimize quantum circuits with QuantumInsight."
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return <html lang="en"><body><AuthProvider><AppShell>{children}</AppShell></AuthProvider></body></html>;
}
