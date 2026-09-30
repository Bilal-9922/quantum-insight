"use client";

import { useRequireAuth } from "../../lib/auth";
import { Icon } from "../../components/Icons";

export default function Profile() {
  const { user, loading, logout } = useRequireAuth();

  if (loading || !user) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <div className="flex items-center gap-3 text-sm text-slate-500">
          <span className="h-2 w-2 animate-pulse rounded-full bg-cyan-300" />
          Loading profile…
        </div>
      </div>
    );
  }

  const initial = user.name?.slice(0, 1).toUpperCase() || "U";

  return (
    <div className="space-y-7">
      {/* Header */}
      <section className="relative overflow-hidden rounded-3xl border border-cyan-400/10 bg-gradient-to-br from-cyan-500/[.07] via-slate-950/60 to-violet-500/[.06] p-6 shadow-[0_20px_80px_rgba(0,0,0,.15)] sm:p-8">
        <div className="pointer-events-none absolute -right-20 -top-24 h-64 w-64 rounded-full bg-cyan-400/10 blur-3xl" />

        <div className="relative flex flex-col justify-between gap-5 lg:flex-row lg:items-end">
          <div className="max-w-2xl">
            <div className="flex items-center gap-2">
              <span className="h-1.5 w-1.5 rounded-full bg-cyan-300 shadow-[0_0_12px_rgba(103,232,249,.8)]" />

              <p className="section-kicker">
                Account
              </p>
            </div>

            <h1 className="mt-3 text-3xl font-black tracking-tight text-white sm:text-4xl">
              Profile & Security
            </h1>

            <p className="mt-3 text-sm leading-6 text-slate-400">
              Manage the identity attached to your
              QuantumInsight workspace and review your
              account security details.
            </p>
          </div>

          <div className="flex items-center gap-2 self-start rounded-xl border border-cyan-400/10 bg-cyan-400/5 px-3 py-2 lg:self-auto">
            <span className="grid h-6 w-6 place-items-center rounded-lg bg-cyan-400/10 text-cyan-300">
              <Icon name="user" size={13} />
            </span>

            <div>
              <p className="text-[9px] font-bold uppercase tracking-[0.16em] text-cyan-300">
                Account status
              </p>

              <p className="text-[10px] text-slate-600">
                Active · Protected
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Account content */}
      <section className="grid gap-5 lg:grid-cols-[.75fr_1.25fr]">
        {/* Identity card */}
        <div className="card relative overflow-hidden p-6 sm:p-7">
          <div className="pointer-events-none absolute -right-16 -top-16 h-40 w-40 rounded-full bg-cyan-400/5 blur-3xl" />

          <div className="relative">
            <div className="flex items-center justify-between">
              <p className="section-kicker">
                Identity
              </p>

              <span className="grid h-8 w-8 place-items-center rounded-xl border border-white/5 bg-white/[.02] text-slate-600">
                <Icon name="user" size={15} />
              </span>
            </div>

            <div className="mt-6 flex flex-col items-start">
              <div className="grid h-24 w-24 place-items-center rounded-3xl bg-gradient-to-br from-cyan-400 to-violet-500 text-3xl font-black text-slate-950 shadow-[0_12px_40px_rgba(34,211,238,.12)]">
                {initial}
              </div>

              <h2 className="mt-5 text-xl font-bold text-white">
                {user.name}
              </h2>

              <p className="mt-1 break-all text-sm text-slate-500">
                {user.email}
              </p>

              <div className="mt-5 inline-flex items-center gap-2 rounded-xl border border-emerald-400/10 bg-emerald-400/5 px-3 py-2">
                <span className="h-1.5 w-1.5 rounded-full bg-emerald-300 shadow-[0_0_8px_rgba(110,231,183,.7)]" />

                <span className="text-[10px] font-bold uppercase tracking-[0.14em] text-emerald-300">
                  Active account
                </span>
              </div>
            </div>

            <div className="mt-7 border-t border-white/5 pt-5">
              <button
                type="button"
                onClick={logout}
                className="flex w-full items-center justify-center gap-2 rounded-xl border border-rose-400/15 bg-rose-400/5 px-4 py-3 text-sm font-bold text-rose-300 transition hover:border-rose-400/25 hover:bg-rose-400/10"
              >
                <Icon name="logout" size={15} />
                Log out
              </button>

              <p className="mt-3 text-center text-[10px] leading-5 text-slate-700">
                You will need to authenticate again to access
                your QuantumInsight workspace.
              </p>
            </div>
          </div>
        </div>

        {/* Account information */}
        <div className="card overflow-hidden">
          <div className="border-b border-white/5 px-5 py-4 sm:px-6">
            <div className="flex items-center gap-2">
              <span className="grid h-7 w-7 place-items-center rounded-lg bg-violet-400/10 text-violet-300">
                <Icon name="shield" size={14} />
              </span>

              <div>
                <p className="text-sm font-bold text-slate-200">
                  Account information
                </p>

                <p className="mt-1 text-[11px] text-slate-600">
                  Details associated with your workspace account.
                </p>
              </div>
            </div>
          </div>

          <div className="p-5 sm:p-6">
            <div className="grid gap-3 sm:grid-cols-2">
              <Info
                label="Full name"
                value={user.name}
                icon="user"
              />

              <Info
                label="Email address"
                value={user.email}
                icon="mail"
              />

              <Info
                label="User ID"
                value={`QI-${String(user.id).padStart(5, "0")}`}
                icon="shield"
              />

              <Info
                label="Account created"
                value={new Date(
                  user.created_at
                ).toLocaleDateString()}
                icon="history"
              />
            </div>

            {/* Security */}
            <div className="mt-6 rounded-2xl border border-cyan-400/10 bg-cyan-400/[.03] p-4 sm:p-5">
              <div className="flex gap-3">
                <span className="grid h-8 w-8 shrink-0 place-items-center rounded-lg bg-cyan-400/10 text-cyan-300">
                  <Icon name="shield" size={15} />
                </span>

                <div>
                  <p className="text-sm font-bold text-slate-200">
                    Authentication protected
                  </p>

                  <p className="mt-1 text-xs leading-5 text-slate-500">
                    Your account uses authenticated sessions,
                    while passwords are hashed server-side.
                    The frontend stores a signed session token
                    rather than your password.
                  </p>
                </div>
              </div>
            </div>

            {/* Security indicators */}
            <div className="mt-4 grid gap-3 sm:grid-cols-2">
              <SecurityItem
                title="Session authentication"
                description="Protected workspace access"
              />

              <SecurityItem
                title="Password protection"
                description="Server-side password hashing"
              />
            </div>
          </div>
        </div>
      </section>

      {/* Footer note */}
      <div className="rounded-2xl border border-dashed border-white/5 bg-white/[.01] px-5 py-5 text-center">
        <div className="mx-auto grid h-9 w-9 place-items-center rounded-xl bg-cyan-400/5 text-cyan-300">
          <Icon name="lock" size={16} />
        </div>

        <p className="mt-3 text-xs font-semibold text-slate-500">
          Your QuantumInsight account is secured by
          authenticated access.
        </p>

        <p className="mx-auto mt-1 max-w-lg text-[10px] leading-5 text-slate-700">
          Keep your account credentials private and sign out
          when using QuantumInsight on a shared device.
        </p>
      </div>
    </div>
  );
}

function Info({
  label,
  value,
  icon,
}: {
  label: string;
  value: string;
  icon: string;
}) {
  return (
    <div className="group rounded-xl border border-white/5 bg-white/[.02] p-4 transition hover:border-cyan-400/10 hover:bg-cyan-400/[.015]">
      <div className="flex items-center justify-between gap-3">
        <p className="text-[10px] font-bold uppercase tracking-widest text-slate-600">
          {label}
        </p>

        <Icon
          name={icon}
          size={12}
          className="text-slate-700 transition group-hover:text-cyan-300"
        />
      </div>

      <p className="mt-2 break-all text-sm font-semibold text-slate-200">
        {value}
      </p>
    </div>
  );
}

function SecurityItem({
  title,
  description,
}: {
  title: string;
  description: string;
}) {
  return (
    <div className="rounded-xl border border-white/5 bg-white/[.015] p-4">
      <div className="flex items-center gap-2">
        <span className="h-1.5 w-1.5 rounded-full bg-emerald-300" />

        <p className="text-xs font-bold text-slate-300">
          {title}
        </p>
      </div>

      <p className="mt-1 pl-3.5 text-[10px] leading-5 text-slate-700">
        {description}
      </p>
    </div>
  );
}
