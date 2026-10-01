"use client";

import { FormEvent, useState } from "react";
import { useAuth, useRequireAuth } from "../../lib/auth";

const API =
  process.env.NEXT_PUBLIC_API_URL ||
  "https://quantuminsight-backend.onrender.com";

export default function SettingsPage() {
  useRequireAuth();

  const { user, token, logout } = useAuth();

  const [name, setName] = useState(user?.name || "");
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const [nameLoading, setNameLoading] = useState(false);
  const [passwordLoading, setPasswordLoading] = useState(false);

  const [nameMessage, setNameMessage] = useState("");
  const [nameError, setNameError] = useState("");

  const [passwordMessage, setPasswordMessage] = useState("");
  const [passwordError, setPasswordError] = useState("");

  async function handleNameChange(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    setNameMessage("");
    setNameError("");

    const trimmedName = name.trim();

    if (trimmedName.length < 2) {
      setNameError("Name must contain at least 2 characters.");
      return;
    }

    setNameLoading(true);

    try {
      const response = await fetch(
        `${API}/api/auth/profile/name`,
        {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            name: trimmedName,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data?.detail || "Unable to update your name."
        );
      }

      setNameMessage("Name updated successfully.");
      setName(data.user?.name || trimmedName);

      window.location.reload();
    } catch (error) {
      setNameError(
        error instanceof Error
          ? error.message
          : "Unable to update your name."
      );
    } finally {
      setNameLoading(false);
    }
  }

  async function handlePasswordChange(
    event: FormEvent<HTMLFormElement>
  ) {
    event.preventDefault();

    setPasswordMessage("");
    setPasswordError("");

    if (newPassword.length < 8) {
      setPasswordError(
        "New password must contain at least 8 characters."
      );
      return;
    }

    if (newPassword !== confirmPassword) {
      setPasswordError("New passwords do not match.");
      return;
    }

    setPasswordLoading(true);

    try {
      const response = await fetch(
        `${API}/api/auth/profile/password`,
        {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            current_password: currentPassword,
            new_password: newPassword,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data?.detail || "Unable to change password."
        );
      }

      setPasswordMessage("Password changed successfully.");
      setCurrentPassword("");
      setNewPassword("");
      setConfirmPassword("");
    } catch (error) {
      setPasswordError(
        error instanceof Error
          ? error.message
          : "Unable to change password."
      );
    } finally {
      setPasswordLoading(false);
    }
  }

  if (!user) {
    return null;
  }

  return (
    <main className="mx-auto w-full max-w-5xl space-y-6">
      {/* Header */}
      <section>
        <div className="text-sm uppercase tracking-[0.25em] text-cyan-400">
          Account
        </div>

        <h1 className="mt-2 text-3xl font-semibold text-white">
          Settings
        </h1>

        <p className="mt-2 text-slate-400">
          Manage your QuantumInsight profile and account security.
        </p>
      </section>

      {/* Profile */}
      <section className="card">
        <div className="flex flex-col gap-5 sm:flex-row sm:items-center">
          <div className="flex h-16 w-16 shrink-0 items-center justify-center rounded-full bg-cyan-500/15 text-2xl font-semibold text-cyan-300 ring-1 ring-cyan-400/20">
            {user.name?.charAt(0)?.toUpperCase() || "U"}
          </div>

          <div>
            <h2 className="text-xl font-semibold text-white">
              {user.name}
            </h2>

            <p className="mt-1 text-sm text-slate-400">
              {user.email}
            </p>
          </div>
        </div>
      </section>

      {/* Change name */}
      <section className="card">
        <div className="mb-6">
          <h2 className="text-xl font-semibold text-white">
            Profile Information
          </h2>

          <p className="mt-1 text-sm text-slate-400">
            Update the name displayed across QuantumInsight.
          </p>
        </div>

        <form
          onSubmit={handleNameChange}
          className="space-y-5"
        >
          <div>
            <label
              htmlFor="name"
              className="mb-2 block text-sm font-medium text-slate-300"
            >
              Name
            </label>

            <input
              id="name"
              type="text"
              value={name}
              onChange={(event) =>
                setName(event.target.value)
              }
              maxLength={80}
              className="w-full rounded-xl border border-white/10 bg-slate-950/70 px-4 py-3 text-white outline-none transition focus:border-cyan-400/50 focus:ring-2 focus:ring-cyan-400/10"
              placeholder="Enter your name"
            />
          </div>

          {nameError && (
            <div className="rounded-xl border border-red-400/20 bg-red-400/10 px-4 py-3 text-sm text-red-300">
              {nameError}
            </div>
          )}

          {nameMessage && (
            <div className="rounded-xl border border-emerald-400/20 bg-emerald-400/10 px-4 py-3 text-sm text-emerald-300">
              {nameMessage}
            </div>
          )}

          <button
            type="submit"
            disabled={nameLoading}
            className="rounded-xl bg-cyan-500 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-400 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {nameLoading ? "Saving..." : "Save Name"}
          </button>
        </form>
      </section>

      {/* Change password */}
      <section className="card">
        <div className="mb-6">
          <h2 className="text-xl font-semibold text-white">
            Change Password
          </h2>

          <p className="mt-1 text-sm text-slate-400">
            Update your password to keep your account secure.
          </p>
        </div>

        <form
          onSubmit={handlePasswordChange}
          className="space-y-5"
        >
          <div>
            <label
              htmlFor="current-password"
              className="mb-2 block text-sm font-medium text-slate-300"
            >
              Current Password
            </label>

            <input
              id="current-password"
              type="password"
              value={currentPassword}
              onChange={(event) =>
                setCurrentPassword(event.target.value)
              }
              maxLength={128}
              className="w-full rounded-xl border border-white/10 bg-slate-950/70 px-4 py-3 text-white outline-none transition focus:border-cyan-400/50 focus:ring-2 focus:ring-cyan-400/10"
              placeholder="Enter current password"
            />
          </div>

          <div>
            <label
              htmlFor="new-password"
              className="mb-2 block text-sm font-medium text-slate-300"
            >
              New Password
            </label>

            <input
              id="new-password"
              type="password"
              value={newPassword}
              onChange={(event) =>
                setNewPassword(event.target.value)
              }
              minLength={8}
              maxLength={128}
              className="w-full rounded-xl border border-white/10 bg-slate-950/70 px-4 py-3 text-white outline-none transition focus:border-cyan-400/50 focus:ring-2 focus:ring-cyan-400/10"
              placeholder="Enter new password"
            />
          </div>

          <div>
            <label
              htmlFor="confirm-password"
              className="mb-2 block text-sm font-medium text-slate-300"
            >
              Confirm New Password
            </label>

            <input
              id="confirm-password"
              type="password"
              value={confirmPassword}
              onChange={(event) =>
                setConfirmPassword(event.target.value)
              }
              minLength={8}
              maxLength={128}
              className="w-full rounded-xl border border-white/10 bg-slate-950/70 px-4 py-3 text-white outline-none transition focus:border-cyan-400/50 focus:ring-2 focus:ring-cyan-400/10"
              placeholder="Confirm new password"
            />
          </div>

          {passwordError && (
            <div className="rounded-xl border border-red-400/20 bg-red-400/10 px-4 py-3 text-sm text-red-300">
              {passwordError}
            </div>
          )}

          {passwordMessage && (
            <div className="rounded-xl border border-emerald-400/20 bg-emerald-400/10 px-4 py-3 text-sm text-emerald-300">
              {passwordMessage}
            </div>
          )}

          <button
            type="submit"
            disabled={passwordLoading}
            className="rounded-xl bg-cyan-500 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-400 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {passwordLoading
              ? "Changing..."
              : "Change Password"}
          </button>
        </form>
      </section>

      {/* Logout */}
      <section className="card border-red-400/10">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h2 className="text-lg font-semibold text-white">
              Sign Out
            </h2>

            <p className="mt-1 text-sm text-slate-400">
              Sign out of your QuantumInsight account on this device.
            </p>
          </div>

          <button
            type="button"
            onClick={logout}
            className="rounded-xl border border-red-400/20 bg-red-400/10 px-5 py-3 text-sm font-semibold text-red-300 transition hover:bg-red-400/20"
          >
            Log out
          </button>
        </div>
      </section>
    </main>
  );
}
