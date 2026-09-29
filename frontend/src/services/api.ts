import { Analysis } from "../types/quantum";

const API =
  process.env.NEXT_PUBLIC_API_URL ||
  "https://quantuminsight-backend.onrender.com";

function getToken(): string | null {
  if (typeof window === "undefined") {
    return null;
  }

  return window.localStorage.getItem("qi_token");
}

async function apiRequest(
  path: string,
  options: RequestInit = {}
): Promise<Response> {
  const token = getToken();

  const headers = new Headers(options.headers);

  headers.set("Content-Type", "application/json");

  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(`${API}${path}`, {
    ...options,
    headers,
  });

  return response;
}

async function getErrorMessage(response: Response): Promise<string> {
  const text = await response.text();

  try {
    const data = JSON.parse(text);

    if (typeof data.detail === "string") {
      return data.detail;
    }

    return text || `Request failed with status ${response.status}`;
  } catch {
    return text || `Request failed with status ${response.status}`;
  }
}

export async function analyze(code: string): Promise<Analysis> {
  const response = await apiRequest("/api/analyze", {
    method: "POST",
    body: JSON.stringify({
      code,
      language: "python",
    }),
  });

  if (!response.ok) {
    throw new Error(await getErrorMessage(response));
  }

  return response.json();
}

export async function debug(code: string, error: string) {
  const response = await apiRequest("/api/debug", {
    method: "POST",
    body: JSON.stringify({
      code,
      error,
      language: "python",
    }),
  });

  if (!response.ok) {
    throw new Error(await getErrorMessage(response));
  }

  return response.json();
}

export async function optimize(code: string) {
  const response = await apiRequest("/api/optimize", {
    method: "POST",
    body: JSON.stringify({
      code,
    }),
  });

  if (!response.ok) {
    throw new Error(await getErrorMessage(response));
  }

  return response.json();
}
