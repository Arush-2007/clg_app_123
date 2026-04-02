# College Application — Project Overview & Architecture Report

**Audience:** Senior developer / tech lead
**Purpose:** Full understanding of what this app is, current state, what works, what's partial, what's remaining.
**Last updated:** 2026-04-01

---

## 1. Executive Summary

A **three-application college platform** targeting NIT Agartala (extensible to other colleges).

| App | Stack | Location | Role |
|-----|-------|----------|------|
| **Student Client** | Flutter (Dart) | `app_frontend_app/` | Mobile/web: auth, profile, events, club registration, placeholder chat |
| **API Server** | FastAPI + SQLAlchemy 2 + Alembic | `app_backend/` | REST API, Firebase ID token verification, PostgreSQL persistence |
| **Admin Dashboard** | Next.js 16 + TypeScript + Tailwind | `app_admin/` | Web: pending club approvals, admin user management |

**Identity provider:** Firebase Authentication (project `college-app-835a2`). The backend never issues sessions — it trusts Firebase ID tokens on protected routes.

**Database:** PostgreSQL via `psycopg2-binary`. 23 entity tables managed through 10 Alembic migrations (`0001` → `0010`).

**Current state:** Core auth, profile, events, club registration + admin approval, and media upload are **fully wired end-to-end**. Social features (connections, follows, tags), feed system, chat/messaging, event registration, certificates, and work experience have **schema + migrations created** but **no API routes or frontend UI yet**.

---

## 2. Tech Stack

### Backend (`app_backend/`)
| Category | Technology |
|----------|-----------|
| Framework | FastAPI 0.115, Uvicorn 0.35 |
| Language | Python 3.12+ |
| ORM | SQLAlchemy 2.0 (sync, `mapped_column` style) |
| Migrations | Alembic 1.16 (linear chain, 10 revisions) |
| Database | PostgreSQL (psycopg2-binary driver) |
| Auth | firebase-admin 6.9 (ID token verification) |
| Validation | Pydantic v2, pydantic-settings |
| File upload | python-multipart, local FS or Google Cloud Storage |
| Secrets | GCP Secret Manager (optional, env fallback) |
| Linting | Ruff 0.12 |
| Testing | pytest 8.4, httpx 0.28 |

### Flutter Client (`app_frontend_app/`)
| Category | Technology |
|----------|-----------|
| Framework | Flutter 3.24 / Dart |
| Auth | firebase_auth, google_sign_in |
| HTTP | http (dart), http_parser, mime |
| Media | image_picker |
| Location | geolocator, geocoding |
| UI | google_fonts, lottie, curved_navigation_bar |

### Admin Dashboard (`app_admin/`)
| Category | Technology |
|----------|-----------|
| Framework | Next.js 16 (App Router) |
| Language | TypeScript |
| Styling | Tailwind CSS v4 |
| Auth | firebase (npm) — email/password sign-in |
| API calls | Native fetch with Bearer token |

### Infrastructure
| Category | Technology |
|----------|-----------|
| Containerization | Docker (multi-stage, non-root `appuser`) |
| Orchestration | docker-compose (dev), Cloud Run (prod target) |
| CI | GitHub Actions (`ci.yml`: ruff, alembic, pytest, Flutter analyze/test) |
| Secrets (prod) | GCP Secret Manager (optional) |
| Storage (prod) | Google Cloud Storage (optional, local FS default) |

---

## 3. Architecture

### 3.1 High-Level Flow

```
┌──────────────┐     Firebase Auth      ┌──────────────────┐
│ Flutter App   │◄──────────────────────►│  Firebase Console │
│ (mobile/web)  │    ID tokens           └──────────────────┘
└──────┬───────┘                                │
       │ REST + Bearer token                    │ ID token verify
       ▼                                        ▼
┌──────────────┐                        ┌──────────────────┐
│  FastAPI      │◄─────────────────────►│  PostgreSQL       │
│  Backend      │   SQLAlchemy ORM      │  (23 tables)      │
└──────┬───────┘                        └──────────────────┘
       │ REST + Bearer token
       ▼
┌──────────────┐
│  Next.js      │
│  Admin Panel  │
└──────────────┘
```

### 3.2 Backend Architecture

**Entry point:** `src/main.py`

**Middleware stack** (outermost → innermost):
1. `SecurityHeadersMiddleware` — X-Content-Type-Options, X-Frame-Options, Referrer-Policy, Permissions-Policy
2. `RateLimitMiddleware` — per-IP sliding window, configurable RPM (default 120)
3. `RequestContextMiddleware` — request ID, logging, metrics recording
4. `CORSMiddleware` — environment-aware: regex match for any localhost in dev, strict origins in prod

**Lifespan:**
- Startup: optional `Base.metadata.create_all()` if `AUTO_CREATE_SCHEMA=true`
- Shutdown: no-op

**Static files:** `/uploads` mount when `STORAGE_PROVIDER=local`

**Config:** `pydantic-settings` with env vars, optional GCP Secret Manager fallback for `DATABASE_URL` and `FIREBASE_CREDENTIALS_JSON`.

### 3.3 Authentication & Authorization

| Dependency | What it does |
|-----------|-------------|
| `verify_firebase_token` | Reads `Authorization: Bearer <token>`, verifies via Firebase Admin SDK; `check_revoked=True` in prod, `False` in dev; returns decoded token dict |
| `verify_admin` | Wraps `verify_firebase_token` + checks `admins` table for UID; raises 403 if not admin |

**Bootstrap:** `POST /api/v1/admins/seed` with a shared secret (`ADMIN_SEED_SECRET`) creates the first admin. Subsequent admins are added by existing admins via `POST /api/v1/admins/add`.

### 3.4 Flutter Client Architecture

**Navigation flow:**
```
App start → AuthGate
  ├── No user → LoginScreen
  │     ├── Email/password → LoginPostScreen (if email unverified)
  │     ├── Google Sign-In → AuthGate
  │     └── Sign Up → SignUpScreen → LoginPostScreen
  └── User exists
        ├── Email unverified → LoginPostScreen
        └── Token valid
              ├── hasProfile() → Bottombar (Home | Chat | Clubs)
              └── !hasProfile() → ProfileSetupScreen → Bottombar
```

**Bottom navigation tabs:**
1. **Home** — events feed (ongoing/upcoming), 5-min in-memory cache, debug bar (dev)
2. **Chat** — "Chippo AI coming soon" placeholder
3. **Clubs** — placeholder hub + "Register a Club" button → ClubRegistrationScreen

---

## 4. Database Schema — All 23 Tables

### Migration chain
```
0001_initial → 0002_hardening → 0003_club_registration → 0004_admins
→ 0005_club_account_manager → 0006_colleges → 0007_connections_tags
→ 0008_feed → 0009_profile_extensions → 0010_chat
```
**Current head:** `0010_chat`

### 4.1 Core Identity & Profile

| Table | Key columns | Notes |
|-------|------------|-------|
| `users` | id, firebase_uid (unique), email (unique), source, is_active, created/updated_at | Created on first backend sync after Firebase auth |
| `profiles` | profile_id, firebase_uid (unique), name, college, year_of_graduation, branch, avatar_url, latitude, longitude, bio, skills, social_links, is_premium, is_alumni, college_id FK | Upserted via `POST /profiles/me` |
| `admins` | id, firebase_uid (unique), added_by_uid, created_at | Platform-level administrators |

### 4.2 College System

| Table | Key columns | Notes |
|-------|------------|-------|
| `colleges` | id, name (unique), college_code (unique), city, state, is_active | Seeded with NIT Agartala in migration 0006 |
| `college_admins` | id, college_id FK→colleges, firebase_uid, added_by_uid | Per-college admin role; UQ(college_id, firebase_uid) |

### 4.3 Club System

| Table | Key columns | Notes |
|-------|------------|-------|
| `clubs` | club_id, parent_college, club_name, club_admin, members (count), description, c_id (unique slug), status (pending/verified/rejected), document_url, account_manager_uid, college_id FK, rejection_reason, verified_at | Full registration→approval flow |
| `club_members` | id, club_id FK→clubs CASCADE, firebase_uid, position_name, hierarchy | UQ(club_id, firebase_uid) |
| `club_accounts` | id, club_id FK→clubs CASCADE (unique), managed_by_uid, club_avatar_url, club_bio, is_verified | Created on club approval; one account per club |
| `positions` | position_id, c_id FK→clubs CASCADE, hierarchy, hierarchy_holders, position_name | UQ(c_id, hierarchy) |

### 4.4 Events System

| Table | Key columns | Notes |
|-------|------------|-------|
| `events` | event_id, title, image_url, status, starts_at, creator_uid, event_type (online/offline), registration_url, max_registrations, college_id FK | Extended in migration 0008 |
| `event_registrations` | id, event_id FK→events CASCADE, firebase_uid, registered_at | UQ(event_id, firebase_uid); schema only |

### 4.5 Social / Networking (Schema Only — No Routes Yet)

| Table | Key columns | Notes |
|-------|------------|-------|
| `follows` | id, follower_uid, followee_id, followee_type (club/body) | UQ(follower_uid, followee_id, followee_type) |
| `connections` | id, requester_uid, receiver_uid, status (pending/accepted/rejected/blocked) | UQ(requester_uid, receiver_uid) |
| `tags` | id, name, tag_type, college_id FK | e.g. club_president, branch_topper |
| `user_tags` | id, firebase_uid, tag_id FK→tags CASCADE, granted_by_uid | UQ(firebase_uid, tag_id) |

### 4.6 Feed System (Schema Only — No Routes Yet)

| Table | Key columns | Notes |
|-------|------------|-------|
| `feed_items` | id, creator_uid, creator_type (user/club/admin), content_type (post/reel/event/notice), caption, media_url, media_type, college_id FK, likes_count, comments_count, is_flagged | Cached counters to avoid COUNT(*) |
| `feed_likes` | id, feed_item_id FK→feed_items CASCADE, firebase_uid | UQ(feed_item_id, firebase_uid) |
| `feed_reports` | id, feed_item_id FK→feed_items CASCADE, reported_by_uid, reason | Content moderation |

### 4.7 Profile Extensions (Schema Only — No Routes Yet)

| Table | Key columns | Notes |
|-------|------------|-------|
| `profile_certificates` | id, firebase_uid, title, issued_by, file_url, issued_at | Uploaded certificate records |
| `work_experiences` | id, firebase_uid, title, company, description, start_date, end_date, is_current | LinkedIn-style work history |

### 4.8 Chat / Messaging (Schema Only — No Routes Yet)

| Table | Key columns | Notes |
|-------|------------|-------|
| `conversations` | id, type (direct/group/official), name, avatar_url, college_id FK, club_id FK, created_by_uid | Official = tied to a club |
| `conversation_members` | id, conversation_id FK→conversations CASCADE, firebase_uid, role (admin/member), last_read_at | UQ(conversation_id, firebase_uid) |
| `messages` | id, conversation_id FK→conversations CASCADE, sender_uid, content, message_type (text/image/reel_share), is_deleted | Indexed on created_at for feed ordering |

---

## 5. API Endpoints

### 5.1 System (no prefix)

| Method | Path | Auth | Purpose |
|--------|------|------|---------|
| GET | `/healthz` | No | Liveness check |
| GET | `/readyz` | No | DB connectivity check |
| GET | `/metrics` | Token header | Request metrics |

### 5.2 Users — `/api/v1/users`

| Method | Path | Auth | Purpose |
|--------|------|------|---------|
| POST | `/` | Firebase token | Upsert user (backend sync) |
| GET | `/me` | Firebase token | Get current user |

### 5.3 Profiles — `/api/v1/profiles`

| Method | Path | Auth | Purpose |
|--------|------|------|---------|
| POST | `/me` | Firebase token | Create/update profile |
| GET | `/me` | Firebase token | Get own profile |

### 5.4 Events — `/api/v1/events`

| Method | Path | Auth | Purpose |
|--------|------|------|---------|
| POST | `/` | Firebase token | Create event |
| GET | `/` | No | List events (optional `?status=` filter) |

### 5.5 Clubs — `/api/v1/clubs`

| Method | Path | Auth | Purpose |
|--------|------|------|---------|
| POST | `/register` | Firebase token | Submit club registration (pending) |
| GET | `/pending` | Admin only | List pending clubs |
| POST | `/` | Firebase token | Direct club create (legacy) |
| GET | `/` | No | List all clubs |
| GET | `/{club_id}` | No | Get single club |
| PATCH | `/{club_id}` | Firebase token | Update club |
| DELETE | `/{club_id}` | Firebase token | Delete club |
| POST | `/{club_id}/verify` | Admin only | Approve or reject club |
| GET | `/{club_id}/members` | No | List club members |

### 5.6 Positions — `/api/v1/positions`

| Method | Path | Auth | Purpose |
|--------|------|------|---------|
| POST | `/` | Firebase token | Create position |
| GET | `/` | No | List positions (optional `?c_id=` filter) |
| GET | `/{position_id}` | No | Get position |
| PATCH | `/{position_id}` | Firebase token | Update position |
| DELETE | `/{position_id}` | Firebase token | Delete position |

### 5.7 Media — `/api/v1/media`

| Method | Path | Auth | Purpose |
|--------|------|------|---------|
| POST | `/upload` | Firebase token | Upload image (5MB, jpeg/png/webp) |

### 5.8 Admins — `/api/v1/admins`

| Method | Path | Auth | Purpose |
|--------|------|------|---------|
| POST | `/seed` | Shared secret | Bootstrap first admin |
| POST | `/add` | Admin only | Add another admin |
| GET | `/` | Admin only | List all admins |

---

## 6. Feature Status — Fully Implemented (End-to-End)

These features have backend routes, service logic, database tables, AND frontend/admin UI:

| Feature | Backend | Flutter | Admin |
|---------|---------|---------|-------|
| **Email/password signup** | `POST /users` sync | SignUpScreen → email verification → LoginPostScreen | — |
| **Email/password login** | Token verification | LoginScreen, LoginPostScreen | — |
| **Google sign-in** | Token verification | LoginScreen, SignUpScreen | — |
| **Password reset** | Firebase built-in | Forgot password dialog on both login screens | — |
| **Profile create/update** | `POST /profiles/me` | ProfileSetupScreen (name, college, branch, year, avatar, location) | — |
| **Profile fetch** | `GET /profiles/me` | AuthGate checks, Home greeting | — |
| **Events list** | `GET /events?status=` | HomeScreen with ongoing/upcoming, 5-min cache | — |
| **Event create** | `POST /events` | Debug bar only | — |
| **Club registration** | `POST /clubs/register` | ClubRegistrationScreen (form + members) | — |
| **Club approval/rejection** | `POST /clubs/{id}/verify` | — | Dashboard: approve/reject with reason |
| **Club CRUD** | Full REST | Debug bar for testing | — |
| **Positions CRUD** | Full REST | Debug bar for testing | — |
| **Image upload** | `POST /media/upload` (local or GCS) | ProfileSetupScreen, debug bar | — |
| **Admin management** | seed + add + list | — | Dashboard: add admin, list admins |
| **Admin auth gate** | `verify_admin` dependency | — | Firebase login → protected dashboard |

---

## 7. Feature Status — Schema Only (Tables Created, No API/UI)

These have database tables and migrations but **zero backend routes and zero frontend UI**:

| Feature | Tables | What's needed |
|---------|--------|---------------|
| **Social connections** | `connections` | Routes: send/accept/reject/block requests; Flutter: connections list, people discovery |
| **Follow system** | `follows` | Routes: follow/unfollow clubs/bodies; Flutter: follow button, following list |
| **Tags & badges** | `tags`, `user_tags` | Routes: admin grant tags, user view tags; Flutter: profile badges display |
| **Feed / posts** | `feed_items`, `feed_likes`, `feed_reports` | Routes: CRUD posts, like/unlike, report; Flutter: feed screen, post creation, like UI |
| **Event registration** | `event_registrations` | Routes: register/unregister for events; Flutter: register button, attendees list |
| **Profile certificates** | `profile_certificates` | Routes: CRUD certificates; Flutter: certificate upload/list in profile |
| **Work experience** | `work_experiences` | Routes: CRUD work history; Flutter: experience section in profile |
| **Chat / messaging** | `conversations`, `conversation_members`, `messages` | Routes: create conversation, send/receive messages, list conversations; Flutter: real chat UI (currently placeholder); likely needs WebSocket for real-time |
| **College system** | `colleges`, `college_admins` | Routes: CRUD colleges, assign college admins; Flutter: dynamic college dropdown; Admin: college management |
| **Profile extensions** | `bio`, `skills`, `social_links`, `is_premium`, `is_alumni` on profiles | Routes: update extended fields; Flutter: extended profile edit/view |
| **Event extensions** | `creator_uid`, `event_type`, `registration_url`, `max_registrations` on events | Routes: use new fields in create/update; Flutter: event detail screen with registration |

---

## 8. Feature Status — Partial / Placeholder

| Feature | Current state | What's missing |
|---------|--------------|----------------|
| **Chippo AI chat** | Flutter shows "coming soon" placeholder | Entire chat backend + AI integration |
| **Clubs tab** | Placeholder screen with "Register a Club" button | Club browser, club detail, member management |
| **Facebook login** | UI button commented out in login.dart | Facebook OAuth setup |
| **Multi-college support** | `colleges` table seeded with NIT Agartala only; profile/club forms hardcode "NIT Agartala" | Dynamic college selection, admin college CRUD |
| **Debug bar** | Embedded in HomeScreen for dev testing | Must be removed before production |
| **Club account switching** | `club_accounts` table exists, `managed_by_uid` stored | No "switch to club profile" UI or API logic |

---

## 9. Known Issues & Technical Debt

| Issue | Details |
|-------|---------|
| **docker-compose.yml mounts SQLite file** | `college_app.db` volume mount is leftover from pre-Postgres migration; harmless but confusing |
| **`__init__.py` router wiring unused** | `src/routes/__init__.py` builds `api_routes` but `main.py` wires routers directly; dead code |
| **Admin dashboard hardcoded API URL** | `app_admin/lib/api.ts` has `BASE = "http://127.0.0.1:8000/api/v1"` — needs env var for prod |
| **Flutter API base for Android** | Default `api_config.dart` uses `10.0.2.2:8000` (Android emulator); web requires `--dart-define=API_BASE_URL` override |
| **No test coverage** | `pytest` and Flutter test configured in CI but no actual test files exist |
| **`app_admin` not in CI** | GitHub Actions workflow only runs backend + Flutter checks |
| **Auth gate retry error state** | After 3 failed profile checks, shows "Sign Out and Retry" but sign-out doesn't navigate — user must restart app |
| **Event model incomplete** | `EventResponse` Pydantic model may not include the new fields (`creator_uid`, `event_type`, `registration_url`, `max_registrations`) added in migration 0008 |
| **Profile model incomplete** | `ProfileResponse` Pydantic model may not include new fields (`bio`, `skills`, `social_links`, `is_premium`, `is_alumni`) added in migration 0007 |

---

## 10. Infrastructure & Deployment

### Docker (Production)
- **Dockerfile:** Multi-stage build (`python:3.12-slim`), non-root `appuser` (UID 1001), `HEALTHCHECK` on `/healthz`, `CMD` runs `alembic upgrade head` then uvicorn on `$PORT` (default 8080).
- **`.dockerignore`:** Excludes `.env`, tests, uploads, caches, git.

### Environment Configuration (`.env.example`)
```
DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/college_app
FIREBASE_CREDENTIALS_JSON=            # inline JSON or file path
FIREBASE_PROJECT_ID=college-app-835a2
APP_ENV=production                    # development | production
CORS_ORIGINS=["https://your-app.web.app"]
CORS_ALLOW_ALL_LOCALHOST=false        # true for local dev
SECRETS_PROVIDER=env                  # env | gcp
STORAGE_PROVIDER=local                # local | gcs
GCS_BUCKET_NAME=
ADMIN_SEED_SECRET=change-me
```

### CI/CD (`.github/workflows/ci.yml`)
- **Backend job:** Python 3.12, ruff check, alembic upgrade head, pytest (coverage ≥50%)
- **Frontend job:** Flutter 3.24, pub get, dart format check, flutter analyze, flutter test
- **Missing:** No `app_admin` CI job

### Production Readiness Checklist
See `docs/release/production_rollout_checklist.md` for staging soak criteria and deployment steps.

---

## 11. Recommended Next Steps (Priority Order)

### Immediate (before any new features)
1. **Update Pydantic response models** — `ProfileResponse` and `EventResponse` need the new fields from migrations 0007/0008
2. **Remove debug bar** from HomeScreen (or gate it behind `APP_ENV=development`)
3. **Write basic tests** — at least smoke tests for auth flow and profile CRUD
4. **Fix admin dashboard API URL** — use environment variable instead of hardcoded localhost

### Short-term (complete partially-built features)
5. **Profile extensions API** — bio, skills, social_links editing in backend + Flutter
6. **Certificates & work experience CRUD** — routes + Flutter profile sections
7. **Event registration flow** — register/unregister + attendee count
8. **College management** — CRUD routes, dynamic college dropdown in Flutter
9. **Clubs browsing** — replace placeholder tab with club list, detail, and member views

### Medium-term (new features using existing schema)
10. **Feed system** — post creation, feed timeline, likes, reports
11. **Connections** — send/accept/reject requests, people discovery
12. **Follow system** — follow clubs, following feed
13. **Tags/badges** — admin-granted recognition badges on profiles

### Long-term
14. **Real-time chat** — WebSocket layer for conversations/messages (schema ready)
15. **Chippo AI assistant** — integrate LLM for campus Q&A
16. **Multi-college rollout** — full college onboarding, college-scoped data
17. **App store deployment** — iOS/Android builds, production Firebase, Cloud Run

---

## 12. File Structure Overview

```
Clg_Application/
├── app_backend/                    # FastAPI backend
│   ├── src/
│   │   ├── main.py                 # App entry, router registration, middleware
│   │   ├── core/
│   │   │   ├── config.py           # Pydantic Settings, secrets integration
│   │   │   ├── database.py         # Engine, SessionLocal, Base, get_db
│   │   │   ├── security.py         # Firebase token verify, admin verify
│   │   │   ├── middleware.py        # Request context, rate limit, security headers
│   │   │   ├── secrets.py          # GCP Secret Manager / env loader
│   │   │   └── debug_log.py        # Dev-only file logger (disabled in prod)
│   │   ├── db/
│   │   │   └── entities.py         # All 23 SQLAlchemy entity classes
│   │   ├── models/                 # Pydantic request/response models
│   │   │   ├── clubs.py
│   │   │   ├── events.py
│   │   │   ├── positions.py
│   │   │   ├── profiles.py
│   │   │   └── users.py
│   │   ├── routes/                 # FastAPI routers (8 files)
│   │   │   ├── system_routes.py
│   │   │   ├── users_routes.py
│   │   │   ├── profile_routes.py
│   │   │   ├── events_routes.py
│   │   │   ├── clubs_routes.py
│   │   │   ├── positions_routes.py
│   │   │   ├── media_routes.py
│   │   │   └── admins_routes.py
│   │   └── services/               # Business logic (7 files)
│   │       ├── user_service.py
│   │       ├── profile_service.py
│   │       ├── event_service.py
│   │       ├── clubs_service.py
│   │       ├── club_registration_service.py
│   │       ├── position_service.py
│   │       └── storage_service.py
│   ├── alembic/
│   │   ├── env.py
│   │   └── versions/              # 10 migration files (0001→0010)
│   ├── Dockerfile                  # Multi-stage, Cloud Run ready
│   ├── .dockerignore
│   ├── requirements.txt
│   ├── .env.example
│   └── .env                        # Local dev (gitignored)
│
├── app_frontend_app/               # Flutter client
│   └── lib/
│       ├── main.dart
│       ├── config/api_config.dart
│       ├── firebase_options.dart
│       ├── theme/                  # Light/dark themes, animated gradient
│       ├── services/
│       │   ├── auth_methods.dart    # All auth flows
│       │   ├── events_api.dart      # Events fetcher
│       │   ├── image_data_picker.dart
│       │   ├── location.dart
│       │   └── ui_services/
│       │       ├── bottomBar.dart   # 3-tab navigation
│       │       └── list_builder.dart
│       └── pages/
│           ├── auth/               # auth_gate, login, signup, profile_setup, home, chat
│           ├── home/debug_bar.dart  # Dev testing widget
│           └── clubs/club_registration_screen.dart
│
├── app_admin/                      # Next.js admin dashboard
│   ├── lib/
│   │   ├── firebase.ts
│   │   └── api.ts
│   ├── app/
│   │   ├── page.tsx                # Login
│   │   ├── layout.tsx
│   │   └── dashboard/page.tsx      # Protected admin panel
│   └── package.json
│
├── docs/
│   ├── project_overview_handover.md  # This file
│   └── release/production_rollout_checklist.md
│
├── docker-compose.yml
└── .github/workflows/ci.yml
```

---

## 13. How to Run Locally

### Backend
```bash
cd app_backend
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
# Start PostgreSQL (Docker or local), set DATABASE_URL in .env
alembic upgrade head
uvicorn src.main:app --reload --port 8000
```

### Flutter Client
```bash
cd app_frontend_app
flutter pub get
flutter run -d chrome --web-hostname localhost --web-port 3000 \
  --dart-define=API_BASE_URL=http://127.0.0.1:8000
```

### Admin Dashboard
```bash
cd app_admin
npm install
npm run dev    # http://localhost:3000
```

**Note:** Backend must be running. Admin login requires a seeded admin account (`POST /api/v1/admins/seed`).

---

*End of report. For questions, refer to the codebase or the previous conversation history.*
