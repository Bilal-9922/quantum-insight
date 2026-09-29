import { Analysis } from "../types/quantum";

export const API = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

async function request(path: string, options: RequestInit = {}) {
  const token = typeof window !== "undefined" ? window.localStorage.getItem("qi_token") : null;
  const headers = new Headers(options.headers || {});
  headers.set("Content-Type", "application/json");
  if (token) headers.set("Authorization", `Bearer ${token}`);
  const r = await fetch(`${API}${path}`, { ...options, headers });
  if (r.status === 401 && typeof window !== "undefined") window.dispatchEvent(new Event("qi-auth-expired"));
  const data = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(data.detail || data.message || "Request failed");
  return data;
}

export function analyze(code: string): Promise<Analysis> { return request("/api/analyze", { method: "POST", body: JSON.stringify({ code, language: "python" }) }); }
export function debug(code: string, error: string) { return request("/api/debug", { method: "POST", body: JSON.stringify({ code, error, language: "python" }) }); }
export function optimize(code: string) { return request("/api/optimize", { method: "POST", body: JSON.stringify({ code }) }); }
