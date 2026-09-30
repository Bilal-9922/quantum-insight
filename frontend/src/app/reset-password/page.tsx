"use client";

import { FormEvent, useEffect, useState } from "react";
import Link from "next/link";
import Image from "next/image";
import { Icon } from "../../components/Icons";

const API =
  process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export default function ResetPasswordPage() {
  const [token, setToken] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const resetToken = params.get("token");

    if (resetToken) {
      setToken(resetToken);
    } else {
      setError("Invalid or missing password reset link.");
    }
  }, []);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();

    setError("");
    setMessage("");

    if (!token) {
      setError("Invalid or missing password reset token.");
      return;
    }

    if (password.length < 8) {
      setError("Password must be at least 8 characters long.");
      return;
    }

    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    setLoading(true);

    try {
      const response = await fetch(
        `${API}/api/auth/reset-password`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            token,
            password,
          }),
        }
      );

      const data = await response.json().catch(() => ({}));

      if (!response.ok) {
        throw new Error(
          data.detail || "Unable to reset your password."
        );
      }

      setSuccess(true);

      setMessage(
        data.message ||
          "Password reset successfully. You can now sign in."
      );

      setPassword("");
      setConfirmPassword("");
    } catch {
      setError(
        "Unable to reset your password. The reset link may have expired or is no longer valid."
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
                  Secure reset
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
                Protected account
              </p>
            </div>
          </div>

          <div className="relative z-10 max-w-lg">
            <p className="section-kicker">
              Secure password reset
            </p>

            <h1 className="mt-3 text-3xl font-black leading-tight sm:text-4xl">
              Create a new password and get back to your workspace.
            </h1>

            <p className="mt-4 max-w-md text-sm leading-6 text-slate-400">
              Choose a strong password for your QuantumInsight
              account and continue working with your quantum
              analysis tools.
            </p>

            <div className="mt-7 grid gap-3 sm:grid-cols-3">
              <Feature
                icon="lock"
                title="Secure"
                text="Use at least 8 characters"
              />

              <Feature
                icon="shield"
                title="Protected"
                text="Your reset token is verified"
              />

              <Feature
                icon="check"
                title="Continue"
                text="Sign in with your new password"
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
                Account security
              </p>

              <h2 className="mt-2 text-3xl font-black tracking-tight text-white">
                Reset your password
              </h2>

              <p className="mt-2 text-sm leading-6 text-slate-400">
                Create a new password for your QuantumInsight
                account.
              </p>
            </div>

            {success ? (
              <div className="space-y-5">
                <div className="rounded-2xl border border-emerald-400/15 bg-emerald-400/[.06] p-5">
                  <div className="flex items-start gap-3">
                    <span className="grid h-8 w-8 shrink-0 place-items-center rounded-full bg-emerald-400/10 text-sm font-black text-emerald-300">
                      ✓
                    </span>

                    <div>
                      <h3 className="text-sm font-bold text-emerald-200">
                        Password updated
                      </h3>

                      <p className="mt-1 text-sm leading-5 text-emerald-200/70">
                        {message}
                      </p>
                    </div>
                  </div>
                </div>

                <Link
                  href="/login"
                  className="btn btn-primary w-full justify-center py-3.5"
                >
                  Go to Sign In
                  <Icon name="arrow" size={16} />
                </Link>
              </div>
            ) : (
              <form
                onSubmit={handleSubmit}
                className="space-y-5"
              >
                <label className="block">
                  <span className="mb-2 block text-xs font-bold text-slate-300">
                    New password
                  </span>

                  <div className="relative">
                    <Icon
                      name="lock"
                      size={17}
                      className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-600"
                    />

                    <input
                      id="password"
                      type="password"
                      required
                      minLength={8}
                      autoComplete="new-password"
                      value={password}
                      onChange={(e) =>
                        setPassword(e.target.value)
                      }
                      placeholder="Enter new password"
                      className="w-full pl-10"
                    />
                  </div>
                </label>

                <label className="block">
                  <span className="mb-2 block text-xs font-bold text-slate-300">
                    Confirm password
                  </span>

                  <div className="relative">
                    <Icon
                      name="lock"
                      size={17}
                      className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-600"
                    />

                    <input
                      id="confirmPassword"
                      type="password"
                      required
                      minLength={8}
                      autoComplete="new-password"
                      value={confirmPassword}
                      onChange={(e) =>
                        setConfirmPassword(e.target.value)
                      }
                      placeholder="Confirm new password"
                      className="w-full pl-10"
                    />
                  </div>
                </label>

                <div className="rounded-xl border border-white/5 bg-white/[.02] px-4 py-3">
                  <div className="flex items-center gap-2">
                    <Icon
                      name="shield"
                      size={14}
                      className="text-cyan-300"
                    />

                    <span className="text-[10px] font-bold uppercase tracking-widest text-slate-500">
                      Password requirements
                    </span>
                  </div>

                  <p className="mt-2 text-xs leading-5 text-slate-600">
                    Your password must contain at least 8
                    characters.
                  </p>
                </div>

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

                <button
                  type="submit"
                  disabled={loading || !token}
                  className="btn btn-primary w-full justify-center py-3.5"
                >
                  {loading ? (
                    <>
                      <span className="h-3.5 w-3.5 animate-spin rounded-full border-2 border-white/30 border-t-white" />
                      Resetting password…
                    </>
                  ) : (
                    <>
                      Reset password
                      <Icon name="arrow" size={16} />
                    </>
                  )}
                </button>

                <div className="pt-1 text-center">
                  <Link
                    href="/login"
                    className="text-xs font-bold text-slate-500 transition hover:text-white"
                  >
                    ← Back to Sign In
                  </Link>
                </div>
              </form>
            )}

            <div className="mt-7 flex gap-3 rounded-xl border border-white/5 bg-white/[.015] p-3.5">
              <Icon
                name="shield"
                size={15}
                className="mt-0.5 shrink-0 text-cyan-300"
              />

              <p className="text-[10px] leading-5 text-slate-600">
                Your password reset token is processed securely.
                Never share your reset link with anyone else.
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
