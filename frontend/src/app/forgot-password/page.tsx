"use client";

import { FormEvent, useState } from "react";
import Link from "next/link";
import Image from "next/image";
import { Icon } from "../../components/Icons";

const API =
  process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();

    setLoading(true);
    setMessage("");
    setError("");

    try {
      const response = await fetch(
        `${API}/api/auth/forgot-password`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ email }),
        }
      );

      const data = await response.json().catch(() => ({}));

      if (!response.ok) {
        throw new Error(
          data.detail || "Unable to process your request."
        );
      }

      setMessage(
        data.message ||
          "If an account exists for this email, a reset link has been sent."
      );
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Something went wrong. Please try again."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="auth-shell">
      <div className="auth-panel">
        {/* Visual panel */}
        <div className="auth-art">
          <div className="relative z-10 flex items-center justify-between">
            <Link href="/" className="inline-block">
              <Image
                src="/quantuminsight-logo.png"
                alt="QuantumInsight"
                width={210}
                height={100}
                className="h-auto w-[190px] object-contain"
                priority
              />
            </Link>

            <div className="rounded-xl border border-cyan-400/10 bg-cyan-400/5 px-3 py-2">
              <div className="flex items-center gap-2">
                <span className="h-1.5 w-1.5 rounded-full bg-emerald-300 shadow-[0_0_10px_rgba(110,231,183,.8)]" />

                <span className="text-[9px] font-bold uppercase tracking-[0.16em] text-cyan-300">
                  Account recovery
                </span>
              </div>
            </div>
          </div>

          <div className="quantum-ring">
            <div className="relative z-10 text-center">
              <div className="text-5xl font-black gradient-text">
                Q
              </div>

              <p className="mt-2 text-[10px] font-bold uppercase tracking-[.22em] text-slate-400">
                Secure access
              </p>
            </div>
          </div>

          <div className="relative z-10 max-w-lg">
            <p className="section-kicker">
              Account recovery
            </p>

            <h1 className="mt-3 text-3xl font-black leading-tight sm:text-4xl">
              Get back into your quantum workspace.
            </h1>

            <p className="mt-4 max-w-md text-sm leading-6 text-slate-400">
              Request a secure password reset link and
              continue working with your QuantumInsight
              analyses, debugging and optimization tools.
            </p>

            <div className="mt-7 grid gap-3 sm:grid-cols-3">
              <Feature
                icon="mail"
                title="Request"
                text="Enter your account email"
              />

              <Feature
                icon="lock"
                title="Reset"
                text="Use your secure reset link"
              />

              <Feature
                icon="shield"
                title="Continue"
                text="Return to your workspace"
              />
            </div>
          </div>
        </div>

        {/* Form panel */}
        <div className="auth-form">
          <div className="mx-auto max-w-md">
            <Link
              href="/login"
              className="mb-9 inline-flex items-center gap-2 text-xs font-bold text-slate-500 transition hover:text-white"
            >
              <span>←</span>
              Back to Sign In
            </Link>

            <div className="mb-7">
              <p className="section-kicker">
                Account recovery
              </p>

              <h2 className="mt-2 text-3xl font-black tracking-tight text-white">
                Forgot your password?
              </h2>

              <p className="mt-2 text-sm leading-6 text-slate-400">
                Enter your email address and we&apos;ll send
                instructions for resetting your password.
              </p>
            </div>

            <form
              onSubmit={handleSubmit}
              className="space-y-5"
            >
              <label className="block">
                <span className="mb-2 block text-xs font-bold text-slate-300">
                  Email address
                </span>

                <div className="relative">
                  <Icon
                    name="mail"
                    size={17}
                    className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-600"
                  />

                  <input
                    id="email"
                    type="email"
                    required
                    autoComplete="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="you@example.com"
                    className="w-full pl-10"
                  />
                </div>
              </label>

              {error && (
                <div className="flex gap-3 rounded-xl border border-rose-400/20 bg-rose-400/[.07] p-3.5">
                  <span className="mt-0.5 grid h-5 w-5 shrink-0 place-items-center rounded-full bg-rose-400/10 text-[10px] font-black text-rose-300">
                    !
                  </span>

                  <p className="text-sm leading-5 text-rose-200/90">
                    {error}
                  </p>
                </div>
              )}

              {message && (
                <div className="flex gap-3 rounded-xl border border-emerald-400/15 bg-emerald-400/[.06] p-3.5">
                  <span className="mt-0.5 grid h-5 w-5 shrink-0 place-items-center rounded-full bg-emerald-400/10 text-[10px] font-black text-emerald-300">
                    ✓
                  </span>

                  <p className="text-sm leading-5 text-emerald-200/90">
                    {message}
                  </p>
                </div>
              )}

              <button
                type="submit"
                disabled={loading}
                className="btn btn-primary w-full justify-center py-3.5"
              >
                {loading ? (
                  <>
                    <span className="h-3.5 w-3.5 animate-spin rounded-full border-2 border-white/30 border-t-white" />
                    Sending reset link…
                  </>
                ) : (
                  <>
                    Send reset link
                    <Icon name="arrow" size={16} />
                  </>
                )}
              </button>
            </form>

            <div className="my-7 flex items-center gap-3 text-[10px] font-bold uppercase tracking-widest text-slate-600">
              <span className="h-px flex-1 bg-white/5" />
              Remembered your password?
              <span className="h-px flex-1 bg-white/5" />
            </div>

            <Link
              href="/login"
              className="btn btn-secondary w-full justify-center"
            >
              Sign in
              <Icon name="arrow" size={15} />
            </Link>

            <div className="mt-6 flex gap-3 rounded-xl border border-white/5 bg-white/[.015] p-3.5">
              <Icon
                name="shield"
                size={15}
                className="mt-0.5 shrink-0 text-cyan-300"
              />

              <p className="text-[10px] leading-5 text-slate-600">
                For account security, reset instructions are
                delivered through the email address associated
                with your account.
              </p>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}

function Feature({
  icon,
  title,
  text,
}: {
  icon: string;
  title: string;
  text: string;
}) {
  return (
    <div className="rounded-xl border border-white/5 bg-white/[.025] p-3">
      <div className="flex items-center gap-2">
        <span className="grid h-7 w-7 place-items-center rounded-lg bg-cyan-400/5 text-cyan-300">
          <Icon name={icon} size={13} />
        </span>

        <p className="text-[11px] font-bold text-slate-300">
          {title}
        </p>
      </div>

      <p className="mt-2 text-[10px] leading-4 text-slate-600">
        {text}
      </p>
    </div>
  );
}
