"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

type User = {
  id: number;
  name: string;
  email: string;
  created_at: string;
};

export default function AdminUsersPage() {
  const router = useRouter();

  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [deletingId, setDeletingId] = useState<number | null>(null);
  const [error, setError] = useState("");

  const API_URL =
    process.env.NEXT_PUBLIC_API_URL ||
    "https://quantuminsight-backend.onrender.com";

  async function loadUsers() {
    try {
      setLoading(true);
      setError("");

      const token = window.localStorage.getItem("qi_token");

      if (!token) {
        router.push("/login");
        return;
      }

      const response = await fetch(`${API_URL}/api/admin/users`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.status === 401) {
        router.push("/login");
        return;
      }

      if (response.status === 403) {
        setError("Administrator access required.");
        return;
      }

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data?.detail || "Unable to load users."
        );
      }

      setUsers(data.users || []);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to load users."
      );
    } finally {
      setLoading(false);
    }
  }

  async function deleteUser(user: User) {
    const confirmed = window.confirm(
      `Are you sure you want to permanently delete the account for ${user.name} (${user.email})?\n\nThis action cannot be undone.`
    );

    if (!confirmed) {
      return;
    }

    try {
      setDeletingId(user.id);
      setError("");

      const token = window.localStorage.getItem("qi_token");

      if (!token) {
        router.push("/login");
        return;
      }

      const response = await fetch(
        `${API_URL}/api/admin/users/${user.id}`,
        {
          method: "DELETE",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data?.detail || "Unable to delete user."
        );
      }

      setUsers((currentUsers) =>
        currentUsers.filter(
          (currentUser) => currentUser.id !== user.id
        )
      );
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to delete user."
      );
    } finally {
      setDeletingId(null);
    }
  }

  useEffect(() => {
    loadUsers();
  }, []);

  return (
    <main className="min-h-screen px-6 py-10">
      <div className="mx-auto max-w-6xl">
        {/* Header */}
        <div className="mb-8 flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div>
            <div className="mb-2 text-xs font-semibold uppercase tracking-[0.25em] text-cyan-400">
              Administration
            </div>

            <h1 className="text-3xl font-bold text-white">
              User Management
            </h1>

            <p className="mt-2 text-sm text-slate-400">
              Manage registered QuantumInsight accounts.
            </p>
          </div>

          <button
            type="button"
            onClick={loadUsers}
            disabled={loading}
            className="rounded-xl border border-slate-700 bg-slate-900 px-4 py-2 text-sm font-medium text-slate-200 transition hover:border-cyan-500 hover:text-cyan-300 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {loading ? "Refreshing..." : "Refresh"}
          </button>
        </div>

        {/* Error */}
        {error && (
          <div className="mb-6 rounded-xl border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-300">
            {error}
          </div>
        )}

        {/* Statistics */}
        <div className="mb-6 grid gap-4 md:grid-cols-3">
          <div className="rounded-2xl border border-slate-800 bg-slate-900/70 p-5">
            <div className="text-xs uppercase tracking-widest text-slate-500">
              Total Users
            </div>

            <div className="mt-2 text-3xl font-bold text-white">
              {users.length}
            </div>
          </div>

          <div className="rounded-2xl border border-slate-800 bg-slate-900/70 p-5">
            <div className="text-xs uppercase tracking-widest text-slate-500">
              Access Level
            </div>

            <div className="mt-2 text-xl font-semibold text-cyan-300">
              Administrator
            </div>
          </div>

          <div className="rounded-2xl border border-slate-800 bg-slate-900/70 p-5">
            <div className="text-xs uppercase tracking-widest text-slate-500">
              Account Actions
            </div>

            <div className="mt-2 text-xl font-semibold text-slate-200">
              Delete Users
            </div>
          </div>
        </div>

        {/* Users table */}
        <div className="overflow-hidden rounded-2xl border border-slate-800 bg-slate-900/70 shadow-xl">
          <div className="border-b border-slate-800 px-6 py-4">
            <h2 className="text-lg font-semibold text-white">
              Registered Users
            </h2>

            <p className="mt-1 text-sm text-slate-500">
              Accounts registered in QuantumInsight.
            </p>
          </div>

          {loading ? (
            <div className="px-6 py-12 text-center text-sm text-slate-400">
              Loading users...
            </div>
          ) : users.length === 0 ? (
            <div className="px-6 py-12 text-center text-sm text-slate-400">
              No users found.
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full min-w-[760px]">
                <thead>
                  <tr className="border-b border-slate-800 text-left text-xs uppercase tracking-wider text-slate-500">
                    <th className="px-6 py-4">User</th>
                    <th className="px-6 py-4">Email</th>
                    <th className="px-6 py-4">Created</th>
                    <th className="px-6 py-4 text-right">
                      Action
                    </th>
                  </tr>
                </thead>

                <tbody>
                  {users.map((user) => (
                    <tr
                      key={user.id}
                      className="border-b border-slate-800/70 last:border-0 hover:bg-slate-800/30"
                    >
                      <td className="px-6 py-5">
                        <div className="font-medium text-white">
                          {user.name}
                        </div>

                        <div className="mt-1 text-xs text-slate-500">
                          User ID: {user.id}
                        </div>
                      </td>

                      <td className="px-6 py-5 text-sm text-slate-300">
                        {user.email}
                      </td>

                      <td className="px-6 py-5 text-sm text-slate-400">
                        {user.created_at
                          ? new Date(
                              user.created_at
                            ).toLocaleDateString()
                          : "—"}
                      </td>

                      <td className="px-6 py-5 text-right">
                        <button
                          type="button"
                          onClick={() => deleteUser(user)}
                          disabled={deletingId === user.id}
                          className="rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-2 text-sm font-medium text-red-300 transition hover:border-red-400 hover:bg-red-500/20 hover:text-red-200 disabled:cursor-not-allowed disabled:opacity-50"
                        >
                          {deletingId === user.id
                            ? "Deleting..."
                            : "Delete"}
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Security notice */}
        <div className="mt-6 rounded-xl border border-amber-500/20 bg-amber-500/5 px-5 py-4">
          <div className="text-sm font-semibold text-amber-300">
            Administrator Security
          </div>

          <p className="mt-1 text-sm leading-6 text-slate-400">
            User deletion is protected by the backend administrator
            authorization system. Your administrator account cannot
            be deleted from this page.
          </p>
        </div>
      </div>
    </main>
  );
}
