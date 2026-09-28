import { Analysis } from "../types/quantum";

const API = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export async function analyze(code: string): Promise<Analysis> {
  const r = await fetch(`${API}/api/analyze`, {
    method: "POST", headers: {"Content-Type": "application/json"},
    body: JSON.stringify({ code, language: "python" })
  });
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

export async function debug(code: string, error: string) {
  const r = await fetch(`${API}/api/debug`, {
    method: "POST", headers: {"Content-Type": "application/json"},
    body: JSON.stringify({ code, error, language: "python" })
  });
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

export async function optimize(code: string) {
  const r = await fetch(`${API}/api/optimize`, {
    method: "POST", headers: {"Content-Type": "application/json"},
    body: JSON.stringify({ code })
  });
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}
