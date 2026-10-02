"use client";

import Image from "next/image";
import Link from "next/link";
import { FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Icon } from "../../components/Icons";
import { useAuth } from "../../lib/auth";

export default function RegisterPage() {
  const { register, user, loading } = useAuth();
  const router = useRouter();

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [verificationCode, setVerificationCode] = useState("");

  const [verificationStep, setVerificationStep] = useState(false);

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

    if (password.length < 8) {
      setError("Password must contain at least 8 characters.");
      return;
    }

    if (password !== confirm) {
      setError("Passwords do not match.");
      return;
    }

    setBusy(true);

    try {
      await register(name, email, password);

      setVerificationStep(true);
      setVerificationCode("");
    } catch (err: any) {
      setError(
        err?.message ||
          "Unable to create the verification request."
      );
    } finally {
      setBusy(false);
    }
  }

  async function verifyEmail(e: FormEvent) {
    e.preventDefault();
    setError("");

    const code = verificationCode.trim();

    if (!/^\d{6}$/.test(code)) {
      setError("Enter the 6-digit verification code.");
      return;
    }

    setBusy(true);

    try {
      const apiBase =
        process.env.NEXT_PUBLIC_API_URL ||
        "https://quantuminsight-backend.onrender.com";

      const response = await fetch(
        `${apiBase}/api/auth/verify-email`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            email: email.trim(),
            code,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data?.detail ||
            data?.message ||
            "Unable to verify your email."
        );
      }

      if (!data.token) {
        throw new Error(
          "Email verified, but no login token was returned."
        );
      }

      localStorage.setItem("qi_token", data.token);
      sessionStorage.setItem("qi_new_account", "true");

      router.replace("/dashboard");
    } catch (err: any) {
      setError(
        err?.message ||
          "The verification code could not be verified."
      );
    } finally {
      setBusy(false);
    }
  }

  function changeEmail() {
    setVerificationStep(false);
    setVerificationCode("");
    setError("");
  }

  if (loading) {
    return (
      <div className="auth-shell">
        <div className="flex min-h-screen items-center justify-center">
          <div className="flex items-center gap-3 text-sm text-slate-500">
            <span className="h-2 w-2 animate-pulse rounded-full bg-cyan-300" />
            Loading…
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="auth-shell">
      <div className="auth-panel">
        {/* Left visual panel */}
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

            <div className="rounded-xl border border-violet-400/10 bg-violet-400/5 px-3 py-2">
              <div className="flex items-center gap-2">
                <span className="h-1.5 w-1.5 rounded-full bg-violet-300 shadow-[0_0_10px_rgba(196,181,253,.8)]" />

                <span className="text-[9px] font-bold uppercase tracking-[0.16em] text-violet-300">
                  Quantum workspace
                </span>
              </div>
            </div>
          </div>

          {/* Quantum visual */}
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

          <div className="relative z-10 max-w-lg">
            <p className="section-kicker">
              Get started
            </p>

            <h1 className="mt-3 text-3xl font-black leading-tight sm:text-4xl">
              Build better quantum circuits with a smarter feedback loop.
            </h1>

            <p className="mt-4 max-w-md text-sm leading-6 text-slate-400">
              Create your account and bring analysis, debugging,
              optimization, anomaly signals and circuit history
              into one workspace.
            </p>

            {/* Features */}
            <div className="mt-7 grid gap-3 sm:grid-cols-3">
              <Feature
                icon="shield"
                title="QHI"
                text="Six-factor circuit health"
              />

              <Feature
                icon="bug"
                title="Debugger"
                text="AI-assisted diagnostics"
              />

              <Feature
                icon="zap"
                title="Optimizer"
                text="Circuit refinement"
              />
            </div>

            <div className="mt-5 space-y-2">
              {[
                "Quantum Health Index analysis",
                "AI-style debugging recommendations",
                "Optimization and circuit comparisons",
              ].map((item) => (
                <div
                  key={item}
                  className="flex items-center gap-3 text-xs text-slate-400"
                >
                  <span className="grid h-5 w-5 shrink-0 place-items-center rounded-full bg-cyan-400/10 text-cyan-300">
                    <Icon name="check" size={12} />
                  </span>

                  {item}
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Registration / verification panel */}
        <div className="auth-form">
          <div className="mx-auto max-w-md">
            <Link
              href="/"
              className="mb-9 inline-flex items-center gap-2 text-xs font-bold text-slate-500 transition hover:text-white"
            >
              <span>←</span>
              Back to QuantumInsight
            </Link>

            {!verificationStep ? (
              <>
                <div className="mb-7">
                  <p className="section-kicker">
                    Get started
                  </p>

                  <h2 className="mt-2 text-3xl font-black tracking-tight text-white">
                    Create your account
                  </h2>

                  <p className="mt-2 text-sm leading-6 text-slate-400">
                    Start analyzing quantum circuits in a few
                    seconds.
                  </p>
                </div>

                <form
                  onSubmit={submit}
                  className="space-y-5"
                >
                  {/* Full name */}
                  <label className="block">
                    <span className="mb-2 block text-xs font-bold text-slate-300">
                      Full name
                    </span>

                    <div className="relative">
                      <Icon
                        name="user"
                        size={17}
                        className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-600"
                      />

                      <input
                        value={name}
                        onChange={(e) =>
                          setName(e.target.value)
                        }
                        required
                        minLength={2}
                        autoComplete="name"
                        placeholder="Your name"
                        className="w-full pl-10"
                      />
                    </div>
                  </label>

                  {/* Email */}
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
                        value={email}
                        onChange={(e) =>
                          setEmail(e.target.value)
                        }
                        required
                        type="email"
                        autoComplete="email"
                        placeholder="you@example.com"
                        className="w-full pl-10"
                      />
                    </div>
                  </label>

                  {/* Password */}
                  <label className="block">
                    <span className="mb-2 block text-xs font-bold text-slate-300">
                      Password
                    </span>

                    <div className="relative">
                      <Icon
                        name="lock"
                        size={17}
                        className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-600"
                      />

                      <input
                        value={password}
                        onChange={(e) =>
                          setPassword(e.target.value)
                        }
                        required
                        type={show ? "text" : "password"}
                        minLength={8}
                        autoComplete="new-password"
                        placeholder="At least 8 characters"
                        className="w-full pl-10 pr-16"
                      />

                      <button
                        type="button"
                        onClick={() => setShow(!show)}
                        className="absolute right-3 top-1/2 -translate-y-1/2 rounded-md px-1 text-[10px] font-bold uppercase tracking-wider text-slate-600 transition hover:text-white"
                      >
                        {show ? "Hide" : "Show"}
                      </button>
                    </div>

                    <p className="mt-2 text-[10px] text-slate-700">
                      Use at least 8 characters for your password.
                    </p>
                  </label>

                  {/* Confirm password */}
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
                        value={confirm}
                        onChange={(e) =>
                          setConfirm(e.target.value)
                        }
                        required
                        type={show ? "text" : "password"}
                        autoComplete="new-password"
                        placeholder="Repeat your password"
                        className="w-full pl-10"
                      />
                    </div>
                  </label>

                  {/* Error */}
                  {error && (
                    <ErrorMessage message={error} />
                  )}

                  {/* Submit */}
                  <button
                    type="submit"
                    disabled={busy}
                    className="btn btn-primary w-full justify-center py-3.5"
                  >
                    {busy ? (
                      <>
                        <span className="h-3.5 w-3.5 animate-spin rounded-full border-2 border-white/30 border-t-white" />
                        Sending verification code…
                      </>
                    ) : (
                      <>
                        Continue
                        <Icon name="arrow" size={16} />
                      </>
                    )}
                  </button>
                </form>

                {/* Existing account */}
                <div className="my-7 flex items-center gap-3 text-[10px] font-bold uppercase tracking-widest text-slate-600">
                  <span className="h-px flex-1 bg-white/5" />
                  Already registered?
                  <span className="h-px flex-1 bg-white/5" />
                </div>

                <Link
                  href="/login"
                  className="btn btn-secondary w-full justify-center"
                >
                  Sign in
                  <Icon name="arrow" size={15} />
                </Link>

                {/* Security note */}
                <div className="mt-6 flex gap-3 rounded-xl border border-white/5 bg-white/[.015] p-3.5">
                  <Icon
                    name="shield"
                    size={15}
                    className="mt-0.5 shrink-0 text-cyan-300"
                  />

                  <p className="text-[10px] leading-5 text-slate-600">
                    Your password is protected using server-side
                    password hashing. QuantumInsight never needs to
                    display your stored password.
                  </p>
                </div>
              </>
            ) : (
              <>
                {/* Verification screen */}
                <div className="mb-7">
                  <p className="section-kicker">
                    Verify email
                  </p>

                  <h2 className="mt-2 text-3xl font-black tracking-tight text-white">
                    Check your email
                  </h2>

                  <p className="mt-3 text-sm leading-6 text-slate-400">
                    We sent a 6-digit verification code to:
                  </p>

                  <p className="mt-2 break-all text-sm font-bold text-cyan-300">
                    {email}
                  </p>
                </div>

                <form
                  onSubmit={verifyEmail}
                  className="space-y-5"
                >
                  <label className="block">
                    <span className="mb-2 block text-xs font-bold text-slate-300">
                      Verification code
                    </span>

                    <div className="relative">
                      <Icon
                        name="shield"
                        size={17}
                        className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-600"
                      />

                      <input
                        value={verificationCode}
                        onChange={(e) =>
                          setVerificationCode(
                            e.target.value
                              .replace(/\D/g, "")
                              .slice(0, 6)
                          )
                        }
                        required
                        inputMode="numeric"
                        autoComplete="one-time-code"
                        maxLength={6}
                        placeholder="000000"
                        className="w-full pl-10 text-center text-xl font-bold tracking-[0.45em]"
                      />
                    </div>

                    <p className="mt-2 text-[10px] leading-5 text-slate-600">
                      Enter the 6-digit code from the email.
                      The code expires in 10 minutes.
                    </p>
                  </label>

                  {error && (
                    <ErrorMessage message={error} />
                  )}

                  <button
                    type="submit"
                    disabled={busy || verificationCode.length !== 6}
                    className="btn btn-primary w-full justify-center py-3.5"
                  >
                    {busy ? (
                      <>
                        <span className="h-3.5 w-3.5 animate-spin rounded-full border-2 border-white/30 border-t-white" />
                        Verifying…
                      </>
                    ) : (
                      <>
                        Verify email
                        <Icon name="check" size={16} />
                      </>
                    )}
                  </button>
                </form>

                <button
                  type="button"
                  onClick={changeEmail}
                  disabled={busy}
                  className="mt-4 w-full rounded-xl border border-white/5 bg-white/[.02] px-4 py-3 text-xs font-bold text-slate-400 transition hover:border-white/10 hover:text-white"
                >
                  ← Use a different email
                </button>

                <div className="mt-6 flex gap-3 rounded-xl border border-cyan-400/10 bg-cyan-400/[.03] p-3.5">
                  <Icon
                    name="mail"
                    size={15}
                    className="mt-0.5 shrink-0 text-cyan-300"
                  />

                  <p className="text-[10px] leading-5 text-slate-500">
                    Your account will only be created after
                    the email verification code is successfully
                    confirmed.
                  </p>
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function ErrorMessage({
  message,
}: {
  message: string;
}) {
  return (
    <div className="flex gap-3 rounded-xl border border-rose-400/20 bg-rose-400/[.07] p-3.5">
      <span className="mt-0.5 grid h-5 w-5 shrink-0 place-items-center rounded-full bg-rose-400/10 text-[10px] font-black text-rose-300">
        !
      </span>

      <p className="text-sm leading-5 text-rose-200/90">
        {message}
      </p>
    </div>
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
        <span className="grid h-7 w-7 place-items-center rounded-lg bg-violet-400/5 text-violet-300">
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
