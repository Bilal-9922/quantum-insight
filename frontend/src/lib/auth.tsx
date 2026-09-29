"use client";

import { createContext, useContext, useEffect, useState } from "react";
import { useRouter } from "next/navigation";

export type User = { id: number; name: string; email: string; created_at: string };
type AuthContextValue = {
  user: User | null;
  token: string | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (name: string, email: string, password: string) => Promise<void>;
  logout: () => void;
};

const API = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const saved = window.localStorage.getItem("qi_token");
    if (!saved) { setLoading(false); return; }
    setToken(saved);
    fetch(`${API}/api/auth/me`, { headers: { Authorization: `Bearer ${saved}` } })
      .then(async r => { if (!r.ok) throw new Error(); return r.json(); })
      .then(data => setUser(data.user))
      .catch(() => { window.localStorage.removeItem("qi_token"); setToken(null); })
      .finally(() => setLoading(false));
  }, []);

  async function authRequest(path: string, body: object) {
    const r = await fetch(`${API}${path}`, {
      method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body)
    });
    const data = await r.json().catch(() => ({}));
    if (!r.ok) throw new Error(data.detail || "Authentication request failed.");
    window.localStorage.setItem("qi_token", data.token);
    setToken(data.token); setUser(data.user);
  }

  async function login(email: string, password: string) { await authRequest("/api/auth/login", { email, password }); }
  async function register(name: string, email: string, password: string) { await authRequest("/api/auth/register", { name, email, password }); }
  function logout() { window.localStorage.removeItem("qi_token"); setToken(null); setUser(null); }

  return <AuthContext.Provider value={{ user, token, loading, login, register, logout }}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const value = useContext(AuthContext);
  if (!value) throw new Error("useAuth must be used inside AuthProvider");
  return value;
}

export function useRequireAuth() {
  const auth = useAuth();
  const router = useRouter();
  useEffect(() => {
    if (!auth.loading && !auth.user) router.replace("/login");
  }, [auth.loading, auth.user, router]);
  return auth;
}
