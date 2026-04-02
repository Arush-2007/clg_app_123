"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { onAuthStateChanged, signOut, User } from "firebase/auth";
import { auth } from "@/lib/firebase";
import {
  getPendingClubs,
  verifyClub,
  getAdmins,
  addAdmin,
  PendingClub,
  Admin,
} from "@/lib/api";

export default function DashboardPage() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [authChecking, setAuthChecking] = useState(true);

  // ── Pending clubs state ──────────────────────────────────────────────────
  const [clubs, setClubs] = useState<PendingClub[]>([]);
  const [clubsError, setClubsError] = useState("");
  const [clubAction, setClubAction] = useState<Record<number, boolean>>({});
  const [clubMessage, setClubMessage] = useState("");

  // ── Admins state ─────────────────────────────────────────────────────────
  const [admins, setAdmins] = useState<Admin[]>([]);
  const [adminsError, setAdminsError] = useState("");
  const [newUid, setNewUid] = useState("");
  const [addingAdmin, setAddingAdmin] = useState(false);
  const [adminMessage, setAdminMessage] = useState("");

  // ── Auth guard ───────────────────────────────────────────────────────────
  useEffect(() => {
    const unsub = onAuthStateChanged(auth, (u) => {
      if (!u) {
        router.replace("/");
      } else {
        setUser(u);
        setAuthChecking(false);
      }
    });
    return unsub;
  }, [router]);

  // ── Data fetchers ────────────────────────────────────────────────────────
  const fetchClubs = useCallback(async (token: string) => {
    setClubsError("");
    try {
      const data = await getPendingClubs(token);
      setClubs(data);
    } catch (err: unknown) {
      setClubsError(err instanceof Error ? err.message : "Failed to load clubs");
    }
  }, []);

  const fetchAdmins = useCallback(async (token: string) => {
    setAdminsError("");
    try {
      const data = await getAdmins(token);
      setAdmins(data);
    } catch (err: unknown) {
      setAdminsError(err instanceof Error ? err.message : "Failed to load admins");
    }
  }, []);

  useEffect(() => {
    if (!user) return;
    user.getIdToken().then((token) => {
      fetchClubs(token);
      fetchAdmins(token);
    });
  }, [user, fetchClubs, fetchAdmins]);

  // ── Club actions ─────────────────────────────────────────────────────────
  async function handleClubAction(
    clubId: number,
    action: "approve" | "reject"
  ) {
    if (!user) return;
    let reason: string | undefined;
    if (action === "reject") {
      const input = window.prompt("Enter rejection reason:");
      if (input === null) return; // cancelled
      reason = input.trim() || undefined;
    }

    setClubAction((prev) => ({ ...prev, [clubId]: true }));
    setClubMessage("");
    try {
      const token = await user.getIdToken();
      await verifyClub(token, clubId, action, reason);
      setClubMessage(
        `Club #${clubId} ${action === "approve" ? "approved" : "rejected"} successfully.`
      );
      await fetchClubs(token);
    } catch (err: unknown) {
      setClubMessage(
        `Error: ${err instanceof Error ? err.message : "Action failed"}`
      );
    } finally {
      setClubAction((prev) => ({ ...prev, [clubId]: false }));
    }
  }

  // ── Add admin ────────────────────────────────────────────────────────────
  async function handleAddAdmin() {
    if (!user || !newUid.trim()) return;
    setAddingAdmin(true);
    setAdminMessage("");
    try {
      const token = await user.getIdToken();
      await addAdmin(token, newUid.trim());
      setAdminMessage("Admin added successfully.");
      setNewUid("");
      await fetchAdmins(token);
    } catch (err: unknown) {
      setAdminMessage(
        `Error: ${err instanceof Error ? err.message : "Failed to add admin"}`
      );
    } finally {
      setAddingAdmin(false);
    }
  }

  // ── Logout ───────────────────────────────────────────────────────────────
  async function handleLogout() {
    await signOut(auth);
    router.replace("/");
  }

  if (authChecking) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <p className="text-gray-500">Loading…</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* ── Header ────────────────────────────────────────────────────── */}
      <header className="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
        <h1 className="text-xl font-bold text-gray-800">Admin Dashboard</h1>
        <div className="flex items-center gap-4">
          <span className="text-sm text-gray-600">{user?.email}</span>
          <button
            onClick={handleLogout}
            className="text-sm bg-red-600 text-white px-3 py-1 rounded hover:bg-red-700"
          >
            Logout
          </button>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-6 py-8 flex flex-col gap-10">
        {/* ── Section 1: Pending Clubs ─────────────────────────────────── */}
        <section>
          <h2 className="text-lg font-semibold text-gray-700 mb-4">
            Pending Club Registrations
          </h2>

          {clubMessage && (
            <p
              className={`text-sm mb-3 ${
                clubMessage.startsWith("Error") ? "text-red-600" : "text-green-600"
              }`}
            >
              {clubMessage}
            </p>
          )}

          {clubsError && (
            <p className="text-red-600 text-sm mb-3">{clubsError}</p>
          )}

          {clubs.length === 0 && !clubsError && (
            <p className="text-gray-500 text-sm">No pending clubs.</p>
          )}

          <div className="flex flex-col gap-4">
            {clubs.map((club) => {
              const busy = !!clubAction[club.club_id];
              return (
                <div
                  key={club.club_id}
                  className="bg-white rounded border border-gray-200 p-5"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1">
                      <p className="font-semibold text-gray-800">
                        {club.club_name}
                      </p>
                      <p className="text-sm text-gray-500">
                        {club.parent_college} · Status:{" "}
                        <span className="font-medium">{club.status}</span>
                        {club.members !== undefined &&
                          ` · Members: ${club.members}`}
                      </p>
                      <p className="text-sm text-gray-600 mt-1">
                        {club.description}
                      </p>
                      {club.document_url && (
                        <a
                          href={club.document_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-blue-600 text-sm underline mt-1 inline-block"
                        >
                          View Document ↗
                        </a>
                      )}
                      <p className="text-xs text-gray-400 mt-1">
                        Submitted:{" "}
                        {new Date(club.created_at).toLocaleString()}
                      </p>
                    </div>

                    <div className="flex gap-2 shrink-0">
                      <button
                        disabled={busy}
                        onClick={() =>
                          handleClubAction(club.club_id, "approve")
                        }
                        className="bg-green-600 text-white text-sm px-3 py-1 rounded hover:bg-green-700 disabled:opacity-50"
                      >
                        Approve
                      </button>
                      <button
                        disabled={busy}
                        onClick={() =>
                          handleClubAction(club.club_id, "reject")
                        }
                        className="bg-red-500 text-white text-sm px-3 py-1 rounded hover:bg-red-600 disabled:opacity-50"
                      >
                        Reject
                      </button>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </section>

        {/* ── Section 2: Admins ────────────────────────────────────────── */}
        <section>
          <h2 className="text-lg font-semibold text-gray-700 mb-4">Admins</h2>

          {adminsError && (
            <p className="text-red-600 text-sm mb-3">{adminsError}</p>
          )}

          {admins.length > 0 && (
            <div className="overflow-x-auto mb-5">
              <table className="w-full text-sm border border-gray-200 rounded">
                <thead className="bg-gray-100 text-gray-600">
                  <tr>
                    <th className="text-left px-3 py-2 border-b">ID</th>
                    <th className="text-left px-3 py-2 border-b">
                      Firebase UID
                    </th>
                    <th className="text-left px-3 py-2 border-b">Added By</th>
                    <th className="text-left px-3 py-2 border-b">
                      Created At
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {admins.map((a) => (
                    <tr key={a.id} className="border-b last:border-0">
                      <td className="px-3 py-2">{a.id}</td>
                      <td className="px-3 py-2 font-mono text-xs">
                        {a.firebase_uid}
                      </td>
                      <td className="px-3 py-2 font-mono text-xs">
                        {a.added_by_uid ?? "—"}
                      </td>
                      <td className="px-3 py-2 text-gray-500">
                        {new Date(a.created_at).toLocaleString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {adminMessage && (
            <p
              className={`text-sm mb-3 ${
                adminMessage.startsWith("Error") ? "text-red-600" : "text-green-600"
              }`}
            >
              {adminMessage}
            </p>
          )}

          <div className="flex gap-2 items-center">
            <input
              type="text"
              placeholder="Firebase UID to add as admin"
              value={newUid}
              onChange={(e) => setNewUid(e.target.value)}
              className="border border-gray-300 rounded px-3 py-2 text-sm flex-1 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              onClick={handleAddAdmin}
              disabled={addingAdmin || !newUid.trim()}
              className="bg-blue-600 text-white text-sm px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
            >
              {addingAdmin ? "Adding…" : "Add Admin"}
            </button>
          </div>
        </section>
      </main>
    </div>
  );
}
