const BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000/api/v1";

async function request<T>(
  token: string,
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    ...options,
    headers: {
      "Authorization": `Bearer ${token}`,
      "Content-Type": "application/json",
      ...(options.headers ?? {}),
    },
  });
  if (res.status >= 400) {
    const text = await res.text();
    throw new Error(text || `HTTP ${res.status}`);
  }
  return res.json() as Promise<T>;
}

// ── Club types ──────────────────────────────────────────────────────────────

export interface PendingClub {
  club_id: number;
  club_name: string;
  parent_college: string;
  description: string;
  status: string;
  document_url: string | null;
  created_at: string;
  members?: number;
}

export interface ClubStatus {
  club_id: number;
  club_name: string;
  status: string;
  verified_at: string | null;
  rejection_reason: string | null;
}

// ── Admin types ─────────────────────────────────────────────────────────────

export interface Admin {
  id: number;
  firebase_uid: string;
  added_by_uid: string | null;
  created_at: string;
}

// ── API functions ───────────────────────────────────────────────────────────

export function getPendingClubs(token: string): Promise<PendingClub[]> {
  return request(token, "/clubs/pending");
}

export function verifyClub(
  token: string,
  clubId: number,
  action: string,
  reason?: string
): Promise<ClubStatus> {
  return request(token, `/clubs/${clubId}/verify`, {
    method: "POST",
    body: JSON.stringify({ action, rejection_reason: reason ?? null }),
  });
}

export function getAdmins(token: string): Promise<Admin[]> {
  return request(token, "/admins");
}

export function addAdmin(
  token: string,
  firebase_uid: string
): Promise<{ message: string; firebase_uid: string }> {
  return request(token, "/admins/add", {
    method: "POST",
    body: JSON.stringify({ firebase_uid }),
  });
}
