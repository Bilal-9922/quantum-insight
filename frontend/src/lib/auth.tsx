"use client";

import { createContext, useContext, useEffect, useState } from "react";
import { useRouter } from "next/navigation";

export type User = {
  id: number;
  name: string;
  email: string;
  created_at: string;
};

type AuthContextValue = {
  user: User | null;
  token: string | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (
    name: string,
    email: string,
    password: string
  ) => Promise<void>;
  googleLogin: () => Promise<void>;
  logout: () => Promise<void>;
};

const API =
  process.env.NEXT_PUBLIC_API_URL ||
  "https://quantuminsight-backend.onrender.com";

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const saved = window.localStorage.getItem("qi_token");

    if (!saved) {
      setLoading(false);
      return;
    }

    setToken(saved);

    fetch(`${API}/api/auth/me`, {
      headers: {
        Authorization: `Bearer ${saved}`,
      },
    })
      .then(async (r) => {
        if (!r.ok) {
          throw new Error();
        }

        return r.json();
      })
      .then((data) => {
        setUser(data.user);
      })
      .catch(() => {
        window.localStorage.removeItem("qi_token");
        setToken(null);
        setUser(null);
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);

  async function authRequest(
    path: string,
    body: object
  ) {
    const r = await fetch(`${API}${path}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
    });

    const data = await r.json().catch(() => ({}));

    if (!r.ok) {
      throw new Error(
        data.detail ||
          data.message ||
          "Authentication request failed."
      );
    }

    if (!data.token || !data.user) {
      throw new Error(
        "Authentication response is missing required login information."
      );
    }

    window.localStorage.setItem(
      "qi_token",
      data.token
    );

    setToken(data.token);
    setUser(data.user);
  }

  async function login(
    email: string,
    password: string
  ) {
    await authRequest(
      "/api/auth/login",
      {
        email,
        password,
      }
    );
  }

  async function googleLogin() {
    const { supabase } = await import("./supabase");

    const {
      data: { session },
      error,
    } = await supabase.auth.getSession();

    if (error || !session?.access_token) {
      throw new Error(
        "Google authentication session not found."
      );
    }

    await authRequest(
      "/api/auth/google",
      {
        access_token: session.access_token,
      }
    );
  }

  async function register(
    name: string,
    email: string,
    password: string
  ) {
    const r = await fetch(
      `${API}/api/auth/register`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          name,
          email,
          password,
        }),
      }
    );

    const data = await r.json().catch(() => ({}));

    if (!r.ok) {
      throw new Error(
        data.detail ||
          data.message ||
          "Unable to create your account."
      );
    }

    /*
     * Registration now requires email verification.
     *
     * The backend intentionally does NOT return a token
     * at this stage. The account is created only after
     * the verification code is successfully confirmed.
     */
    if (!data.verification_required) {
      throw new Error(
        "Email verification is required before continuing."
      );
    }
  }

  async function logout() {
    const { supabase } = await import("./supabase");

    await supabase.auth.signOut();

    window.localStorage.removeItem("qi_token");

    setToken(null);
    setUser(null);
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        loading,
        login,
        register,
        googleLogin,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const value = useContext(AuthContext);

  if (!value) {
    throw new Error(
      "useAuth must be used inside AuthProvider"
    );
  }

  return value;
}

export function useRequireAuth() {
  const auth = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!auth.loading && !auth.user) {
      router.replace("/login");
    }
  }, [
    auth.loading,
    auth.user,
    router,
  ]);

  return auth;
}
