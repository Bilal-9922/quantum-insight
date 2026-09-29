"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import Logo from "./Logo";
import { Icon } from "./Icons";
import { useAuth } from "../lib/auth";

const nav = [
  ["/dashboard", "Dashboard", "grid"],
  ["/analyzer", "Analyzer", "analyze"],
  ["/debugger", "AI Debugger", "bug"],
  ["/optimizer", "Optimizer", "zap"],
  ["/history", "History", "history"],
  ["/profile", "Profile", "user"],
];

export default function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const { user, loading, logout } = useAuth();
  const [open, setOpen] = useState(false);
  const authPage = pathname === "/login" || pathname === "/register";

  if (authPage) return <>{children}</>;

  return <div className="app-bg min-h-screen">
    <aside className={`sidebar ${open ? "sidebar-open" : ""}`}>
      <div className="flex items-center justify-between px-5 py-5"><Logo compact /><button className="icon-btn lg:hidden" onClick={() => setOpen(false)}><Icon name="close"/></button></div>
      <div className="px-4 pb-5"><div className="side-label">Workspace</div>{nav.map(([href,label,icon]) => <Link key={href} href={href} onClick={() => setOpen(false)} className={`side-link ${pathname === href ? "active" : ""}`}><Icon name={icon}/><span>{label}</span></Link>)}</div>
      <div className="mt-auto p-4"><div className="upgrade-card"><div className="flex items-center gap-2 text-cyan-300"><Icon name="spark" size={16}/><span className="text-xs font-bold uppercase tracking-widest">Quantum Lab</span></div><p className="mt-2 text-sm text-slate-300">Run deeper analysis and keep your circuits organized.</p><Link href="/analyzer" className="mt-4 block rounded-xl bg-white/10 px-3 py-2 text-center text-xs font-bold text-white hover:bg-white/15">Start analysis</Link></div></div>
      <div className="border-t border-white/5 p-4"><button onClick={logout} className="side-link w-full text-rose-300"><Icon name="logout"/><span>Log out</span></button></div>
    </aside>
    <div className="lg:pl-[248px]">
      <header className="topbar"><button className="icon-btn lg:hidden" onClick={() => setOpen(true)}><Icon name="menu"/></button><div className="hidden text-sm text-slate-400 sm:block">Quantum circuit intelligence</div><div className="ml-auto flex items-center gap-3"><Link href="/analyzer" className="top-action hidden sm:flex"><Icon name="zap" size={15}/> New analysis</Link><Link href="/profile" className="avatar" title={user?.name || "Profile"}>{user?.name?.slice(0,1).toUpperCase() || "Q"}</Link></div></header>
      <main className="mx-auto min-h-screen max-w-[1500px] px-4 pb-14 pt-7 sm:px-6 lg:px-8">{children}</main>
    </div>
    {open && <button aria-label="Close menu" onClick={() => setOpen(false)} className="fixed inset-0 z-40 bg-black/60 lg:hidden"/>}
    {loading && <div className="fixed bottom-4 right-4 z-50 rounded-xl border border-white/10 bg-slate-950/90 px-4 py-3 text-xs text-slate-300">Restoring session…</div>}
  </div>;
}
