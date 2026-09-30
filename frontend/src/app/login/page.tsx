"use client";

import Image from "next/image";
import Link from "next/link";
import { FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Icon } from "../../components/Icons";
import { useAuth } from "../../lib/auth";
import { supabase } from "../../lib/supabase";

export default function LoginPage() {
  const { login, user, loading } = useAuth();
  const router = useRouter();
  async function signInWithGoogle() {
    setError("");
    setBusy(true);

    const { error } = await supabase.auth.signInWithOAuth({
      provider: "google",
      options: {
        redirectTo: window.location.origin + "/login",
      },
    });

    if (error) {
      setError(error.message);
      setBusy(false);
    }
  }
  

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [show, setShow] = useState(false);

  useEffect(() => {
    if (!loading && user) {
      router.replace("/dashboard");
    }
  }, [loading, user, router]);

  async function submit(e: FormEvent) {
    e.preventDefault();
    setError("");
    setBusy(true);

    try {
      await login(email, password);
      router.replace("/dashboard");
    } catch (err: any) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="auth-shell">
      <div className="auth-panel">

        <div className="auth-art">
          <Link href="/">
            <Image
              src="/quantuminsight-logo.png"
              alt="QuantumInsight"
              width={210}
              height={100}
              className="h-auto w-[190px] object-contain"
            />
          </Link>

          <div className="quantum-ring">
            <div className="relative z-10 text-center">
              <div className="text-5xl font-black gradient-text">
                Q
              </div>

              <p className="mt-2 text-[10px] font-bold uppercase tracking-[.22em] text-slate-400">
                Circuit intelligence
              </p>
            </div>
          </div>

          <div className="relative z-10">
            <p className="section-kicker">
              Your quantum workspace
            </p>

            <h1 className="mt-3 text-3xl font-black leading-tight">
              Turn complex circuits into clear engineering decisions.
            </h1>

            <p className="mt-4 text-sm leading-6 text-slate-400">
              Your analyses, optimization experiments and debugging
              workflow stay together in one secure workspace.
            </p>
          </div>
        </div>

        <div className="auth-form">
          <div className="mx-auto max-w-md">

            <Link
              href="/"
              className="mb-10 block text-xs font-bold text-slate-500 hover:text-white"
            >
              ← Back to QuantumInsight
            </Link>

            <p className="section-kicker">
              Welcome back
            </p>

            <h2 className="mt-2 text-3xl font-black">
              Sign in to your workspace
            </h2>

            <p className="mt-2 text-sm text-slate-400">
              Use your QuantumInsight account to continue.
            </p>

            <button
              type="button"
              onClick={signInWithGoogle}
              disabled={busy}
              className="btn btn-secondary w-full py-3.5"
            >
              <span className="text-base font-bold">G</span>
              Continue with Google
            </button>

            <div className="my-6 flex items-center gap-3 text-[10px] font-bold uppercase tracking-widest text-slate-600">
              <span className="h-px flex-1 bg-white/5" />
              or continue with email
              <span className="h-px flex-1 bg-white/5" />
            </div>
            
            <form
              onSubmit={submit}
              className="mt-8 space-y-5"
            >

              {/* Email */}
              <label className="block">
                <span className="mb-2 block text-xs font-bold text-slate-300">
                  Email address
                </span>

                <div className="relative">
                  <Icon name="mail" size={17} />

                  <input
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    type="email"
                    required
                    placeholder="you@example.com"
                    className="pl-10"
                  />
                </div>
              </label>

              {/* Password */}
              <label className="block">

                <div className="mb-2 flex items-center justify-between">
                  <span className="text-xs font-bold text-slate-300">
                    Password
                  </span>

                  <Link
                    href="/forgot-password"
                    className="text-xs font-semibold text-blue-400 transition hover:text-blue-300"
                  >
                    Forgot password?
                  </Link>
                </div>

                <div className="relative">
                  <Icon name="lock" size={17} />

                  <input
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    type={show ? "text" : "password"}
                    required
                    placeholder="••••••••"
                    className="pl-10 pr-12"
                  />

                  <button
                    type="button"
                    onClick={() => setShow(!show)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-slate-500 hover:text-white"
                  >
                    {show ? "Hide" : "Show"}
                  </button>
                </div>
              </label>

              {/* Error */}
              {error && (
                <div className="rounded-xl border border-rose-400/20 bg-rose-400/10 p-3 text-sm text-rose-200">
                  {error}
                </div>
              )}

              {/* Sign in button */}
              <button
                disabled={busy}
                className="btn btn-primary w-full py-3.5"
              >
                {busy ? "Signing in…" : "Sign in"}
                <Icon name="arrow" size={16} />
              </button>
            </form>

            <div className="my-7 flex items-center gap-3 text-[10px] font-bold uppercase tracking-widest text-slate-600">
              <span className="h-px flex-1 bg-white/5" />
              New here?
              <span className="h-px flex-1 bg-white/5" />
            </div>

            <Link
              href="/register"
              className="btn btn-secondary w-full"
            >
              Create an account
            </Link>

            <p className="mt-6 text-center text-[11px] leading-5 text-slate-600">
              Authentication uses password hashing and signed session
              tokens on the QuantumInsight API.
            </p>

          </div>
        </div>

      </div>
    </div>
  );
}
