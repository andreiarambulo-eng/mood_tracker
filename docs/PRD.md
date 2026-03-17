# Product Requirements Document (PRD)
## Mood Tracker — Personal Wellbeing & Sentiment Analytics Platform

| Field | Value |
|---|---|
| **Document Version** | 1.0 |
| **Status** | Draft for Stakeholder Review |
| **Date** | 2026-03-17 |
| **Product** | Mood Tracker |
| **Tech Stack** | FastAPI · MongoDB · Next.js 14 · TypeScript · Docker |

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Problem Statement](#2-problem-statement)
3. [Product Vision & Goals](#3-product-vision--goals)
4. [Target Audience / User Personas](#4-target-audience--user-personas)
5. [User Stories](#5-user-stories)
6. [Feature Requirements](#6-feature-requirements)
7. [Non-Functional Requirements](#7-non-functional-requirements)
8. [Technical Architecture Overview](#8-technical-architecture-overview)
9. [Data Model](#9-data-model)
10. [API Endpoints Summary](#10-api-endpoints-summary)
11. [Security & Privacy Considerations](#11-security--privacy-considerations)
12. [Success Metrics / KPIs](#12-success-metrics--kpis)
13. [Future Roadmap](#13-future-roadmap)
14. [Appendix](#14-appendix)

---

## 1. Executive Summary

Mood Tracker is a full-stack web application that enables individuals to log their daily emotional state, annotate it with free-text remarks, and gain insight into their wellbeing trends over time through rich data visualisations. The application combines a Python FastAPI backend with a Next.js 14 frontend, persisted to MongoDB, and is deployed entirely via Docker.

The platform offers two roles: **Users** who privately track and visualise their own mood data, and **Admins** who manage the user base and monitor aggregated, anonymised platform health metrics. All personal remarks are encrypted at rest using HMAC-SHA256, and sentiment is automatically derived from each entry using TextBlob's natural language processing.

Key differentiators include privacy-first data design, automatic sentiment analysis without user effort, a GitHub-style annual calendar heatmap, and ISO-week navigable summary reports — making the product suitable for individual self-monitoring as well as organisational wellbeing programmes.

---

## 2. Problem Statement

### 2.1 Mental Health Awareness Gap

Mental health conditions affect approximately 1 in 5 adults globally, yet the gap between experiencing emotional distress and seeking professional support remains large. Many people lack awareness of their own emotional patterns until problems become acute. Regular, low-friction mood logging has been shown in clinical studies to increase emotional self-awareness, improve cognitive-behavioural therapy (CBT) outcomes, and reduce anxiety by externalising feelings.

### 2.2 Lack of Private, Self-Hosted Monitoring Tools

Existing mood-tracking tools on the market suffer from one or more of the following drawbacks:

- **Privacy concerns**: Consumer apps monetise user health data through advertising or third-party data sharing.
- **No self-hosting option**: Users cannot run the tool on their own infrastructure, leaving sensitive emotional records in external hands.
- **Complexity or friction**: Many tools require extensive daily questionnaires, reducing long-term adherence.
- **No actionable analytics**: Logging without trend visualisation provides no insight.
- **No organisational tier**: Consumer apps are not suitable for team wellbeing monitoring, where a manager or HR lead needs aggregated, anonymised signals rather than individual records.

### 2.3 Insight Without Effort

People who do manage to track their mood manually (notebooks, spreadsheets) rarely have the tools to surface patterns. Detecting correlations between sentiment expressed in writing and subjective mood score, identifying weekly dips, or visualising annual mood rhythms requires analytical capability most individuals do not have.

Mood Tracker addresses all three gaps: it is privacy-first (remarks encrypted at rest, fully self-hostable), requires only a single daily interaction (one score + optional remark), and surfaces analytics automatically.

---

## 3. Product Vision & Goals

### 3.1 Vision Statement

> To give every person a simple, private daily ritual that turns their emotional experience into self-knowledge — and to give organisations a compassionate, anonymised window into collective wellbeing.

### 3.2 Strategic Goals

| # | Goal | Metric |
|---|---|---|
| G1 | Maximise daily logging adherence | ≥ 5-day average logging streak per active user |
| G2 | Provide actionable personal insight | ≥ 80% of users access analytics at least once per week |
| G3 | Protect user privacy absolutely | Zero incidents of unencrypted remark exposure in production |
| G4 | Enable organisational use | Admin panel supports ≥ 100 concurrent users without degradation |
| G5 | Minimise time-to-log | Daily mood entry completes in under 30 seconds |

### 3.3 Product Principles

- **Privacy by design**: The most sensitive field (remark text) is always encrypted at rest.
- **Low friction first**: The daily log is a single-screen interaction.
- **Insight as a by-product**: Analytics are computed automatically; users do not need to configure reports.
- **Role separation**: Admins see only anonymised aggregate data; they cannot read individual remarks.
- **Self-hostable**: The entire stack runs with a single `docker compose up`.

---

## 4. Target Audience / User Personas

### 4.1 Persona 1 — Individual User (Primary)

| Attribute | Detail |
|---|---|
| **Name** | Alex, 29 |
| **Role** | Software Engineer |
| **Goal** | Understand patterns in personal wellbeing and identify what triggers low-mood days |
| **Context** | Logs mood at the end of each working day; reviews the calendar heatmap weekly |
| **Pain Points** | Forgetting to log; not knowing whether things are getting better or worse over time |
| **Motivation** | Therapist recommended mood journalling; wants data to bring to sessions |
| **Tech Comfort** | High — comfortable self-hosting via Docker |

### 4.2 Persona 2 — Team Lead / People Manager (Secondary)

| Attribute | Detail |
|---|---|
| **Name** | Jordan, 42 |
| **Role** | Engineering Manager at a 30-person company |
| **Goal** | Monitor team morale trends without invading privacy; identify if collective mood drops after organisational changes |
| **Context** | Reviews admin analytics dashboard weekly; never reads individual remarks |
| **Pain Points** | Pulse surveys are infrequent and don't capture daily signals; employee assistance programmes are reactive |
| **Motivation** | Wants to be a data-informed, empathetic leader |
| **Tech Comfort** | Medium — relies on IT team to deploy and manage the instance |

### 4.3 Persona 3 — Therapist / Mental Health Practitioner (Secondary)

| Attribute | Detail |
|---|---|
| **Name** | Dr. Sam, 38 |
| **Role** | Clinical psychologist in private practice |
| **Goal** | Recommend a journalling tool to clients that respects their privacy and produces shareable weekly summaries |
| **Context** | Asks clients to share weekly summary reports during sessions; uses sentiment trends to guide discussion |
| **Pain Points** | Consumer apps send data to third parties; clients are reluctant to use them |
| **Motivation** | Needs a trustworthy, privacy-respecting tool they can recommend without reservation |
| **Tech Comfort** | Low — relies on a self-hosted instance set up by a technically capable client or their own IT provider |

---

## 5. User Stories

### 5.1 User Role Stories

#### Authentication & Account Management

| ID | Story | Acceptance Criteria |
|---|---|---|
| US-001 | As a User, I want to register with my email, full name, and a password so that I can create a private account. | Registration succeeds with a valid email and password ≥ 8 characters; duplicate email is rejected with a clear error. |
| US-002 | As a User, I want to log in with my email and password so that I can access my dashboard. | Login returns a JWT token valid for 24 hours; inactive accounts are rejected with a specific message. |
| US-003 | As a User, I want to log out so that my session is invalidated. | Token is cleared from client storage; subsequent requests with that token are rejected. |
| US-004 | As a User, I want to view my own profile information (name, email, role) so that I can verify my account details. | GET /auth/me returns current user data; no other user's data is accessible. |
| US-005 | As a User, I want to change my password so that I can maintain account security. | Current password must be verified before new password is accepted; new password must meet minimum length requirements. |

#### Daily Mood Logging

| ID | Story | Acceptance Criteria |
|---|---|---|
| US-006 | As a User, I want to log today's mood with a score from 1 to 5 so that I can record how I feel. | Entry is created with the correct score, label, and today's date; only one entry per day is allowed. |
| US-007 | As a User, I want to optionally add a free-text remark (up to 500 characters) alongside my mood score so that I can add context. | Remark is stored encrypted; sentiment is automatically computed and stored; remark is decrypted on retrieval. |
| US-008 | As a User, I want to see whether I have already logged today's mood so that I don't accidentally try to log twice. | Dashboard surface shows today's entry if it exists, and a prompt to log if it does not. |
| US-009 | As a User, I want to edit today's mood entry so that I can correct a mistake or update how I feel later in the day. | Mood score and remark can both be updated; sentiment is recalculated on remark change; updated_at timestamp is refreshed. |
| US-010 | As a User, I want to delete a mood entry so that I can remove an entry I logged by mistake. | Entry is permanently removed; it no longer appears in history or analytics. |

#### Mood History

| ID | Story | Acceptance Criteria |
|---|---|---|
| US-011 | As a User, I want to browse my full mood history in a paginated table so that I can review past entries. | History is sorted by date descending; pagination works correctly; each entry shows date, score, label, sentiment, and decrypted remark. |
| US-012 | As a User, I want to filter my mood history by date range so that I can focus on a specific period. | Filtering by start and/or end date returns only entries within that range. |
| US-013 | As a User, I want to view a single mood entry by its ID so that I can see its full details. | Returns the correct entry; returns 404 if the entry does not exist or belongs to another user. |

#### Analytics & Visualisations

| ID | Story | Acceptance Criteria |
|---|---|---|
| US-014 | As a User, I want to see a calendar heatmap of my mood over the past 12 months so that I can identify seasonal or recurring patterns. | Heatmap shows all 365 days of the selected year; each day is colour-coded by mood score; days with no entry are shown in a neutral colour. |
| US-015 | As a User, I want to see a dual-axis sentiment trend chart so that I can compare my reported mood score against the computed sentiment of my remarks over time. | Chart shows up to the last 30 days by default; both mood score and sentiment score are plotted on appropriate axes. |
| US-016 | As a User, I want to see a word cloud generated from my recent remarks so that I can see which themes appear most in my writing. | Word cloud is derived from the last 90 days of remarks; common stop words are excluded; up to 80 unique words are shown weighted by frequency. |
| US-017 | As a User, I want to see a mood distribution pie/donut chart so that I can understand the proportion of each mood score over a time period. | Chart shows counts and percentages for each mood label (Terrible through Great) for the last 90 days by default. |
| US-018 | As a User, I want to see my current logging streak so that I can be motivated to maintain a daily habit. | Streak is defined as consecutive calendar days with a logged entry, counting backwards from today. |

#### Weekly Reports

| ID | Story | Acceptance Criteria |
|---|---|---|
| US-019 | As a User, I want to see a weekly summary report showing my average mood, average sentiment, most common mood, and a day-by-day breakdown for the current ISO week. | Summary correctly computes averages; most common mood is the modal mood label; day breakdown includes a truncated remark preview (max 80 characters). |
| US-020 | As a User, I want to navigate to previous and future ISO weeks so that I can review historical weekly summaries. | Navigation correctly identifies the Monday-to-Sunday boundaries of each ISO week; weeks with no data show a clear empty state. |

### 5.2 Admin Role Stories

#### User Management

| ID | Story | Acceptance Criteria |
|---|---|---|
| AS-001 | As an Admin, I want to view a paginated list of all registered users so that I can manage the user base. | Returns all users (excluding password hashes); sorted by registration date descending. |
| AS-002 | As an Admin, I want to view a single user's profile by their ID so that I can inspect their account details. | Returns the user's profile; 404 if user does not exist. |
| AS-003 | As an Admin, I want to update a user's name, role, or active status so that I can manage access and permissions. | Changes are persisted; an Admin can promote a User to Admin or deactivate an account. |
| AS-004 | As an Admin, I want to delete a user account so that I can remove inactive or inappropriate accounts. | User record is permanently deleted. |

#### Platform Analytics

| ID | Story | Acceptance Criteria |
|---|---|---|
| AS-005 | As an Admin, I want to see a platform-wide overview showing total active users, total mood entries, this week's average mood, and this week's entry count so that I can monitor platform health. | Overview aggregates data across all users; no personally identifiable mood data or remarks are exposed. |
| AS-006 | As an Admin, I want to see a list of users who have logged this week with their entry count and average mood so that I can identify active engagement. | List is sorted by entry count descending; includes full name and entries/average mood only — no remarks or individual entry details. |

---

## 6. Feature Requirements

### 6.1 Priority Definitions

| Priority | Definition |
|---|---|
| **P0** | Must ship for v1 launch; the product does not function without these |
| **P1** | High value for v1; should ship but does not block launch |
| **P2** | Nice-to-have for v1; can be deferred to v1.x patch |

### 6.2 P0 — Core (Launch Blockers)

#### F-001: User Authentication System

- User registration with email, full name, and password (bcrypt-hashed)
- Email uniqueness enforced at the database index level
- JWT-based login returning a signed HS256 token (24-hour expiry)
- Role-based route protection: `User` and `Admin` tiers
- Token verified on every protected request via `Authorization: Bearer <token>` header
- Account deactivation support (deactivated users cannot log in)
- Password change endpoint with current-password verification

#### F-002: Daily Mood Logging

- Single mood entry per user per calendar day (enforced at both service and database index levels)
- Mood score: integer 1–5 with automatic label assignment
- Optional free-text remark: max 500 characters
- Remark encrypted at rest using HMAC-SHA256 with a server-side key
- Automatic sentiment analysis (TextBlob polarity, -1.0 to +1.0) on remark at write time
- Sentiment label: Positive (>0.1), Neutral (-0.1 to 0.1), Negative (<-0.1)
- Full CRUD: create, read (by ID and paginated list), update (today's entry), delete

#### F-003: Data Isolation

- All mood queries are scoped to the authenticated user's `user_id`
- Cross-user access is blocked at the service layer; an entry belonging to user A cannot be retrieved, modified, or deleted by user B
- Admins do not have read access to individual mood entries; admin analytics are aggregate-only

#### F-004: Docker Deployment

- Three-container deployment: `backend` (FastAPI, port 8000), `frontend` (Next.js, port 3000), `mongo` (MongoDB 7, port 27017)
- MongoDB initialised with collections and indexes on first start via `init_mongodb.js`
- Health check on backend via `/healthz` endpoint
- Production and development compose configurations provided

### 6.3 P1 — High Value (Target v1)

#### F-005: Calendar Heatmap

- GitHub-style 12-month calendar view coloured by mood score
- Full-year data retrieved in a single API call (`/analytics/heatmap?year=YYYY`)
- Colour scale maps score 1 (deep red) through 5 (deep green); no-entry days neutral grey
- Year selector to browse historical data

#### F-006: Sentiment Trend Chart

- Dual-axis line chart (recharts) over configurable day window (default: 30 days)
- Left Y-axis: mood score (1–5); right Y-axis: sentiment polarity (-1.0 to +1.0)
- Helps users see whether their stated mood and the emotional tone of their writing align

#### F-007: Word Cloud

- Derived from the last 90 days of decrypted remarks
- Stop words filtered server-side (80+ common English words excluded)
- Top 80 words by frequency returned; rendered with size proportional to count
- Words with fewer than 3 characters excluded

#### F-008: Mood Distribution Chart

- Pie/donut chart showing the count and percentage of each mood label
- Configurable time window via `days` query parameter (default: 90)

#### F-009: Logging Streak

- Counter of consecutive calendar days with a logged entry counting back from today
- Displayed prominently on the dashboard to encourage habit formation

#### F-010: Weekly Summary Report

- ISO week-aligned report: Monday through Sunday
- Metrics: total entries, average mood score, average sentiment score, modal mood label
- Day-by-day breakdown with remark preview (first 80 characters)
- ISO week navigation (previous / next week) with year rollover handling

#### F-011: Admin Panel

- Paginated user list with full name, email, role, active status, and last login
- Per-user profile view and inline editing (name, role, active status)
- User deletion
- Platform overview: total active users, total entries, current-week average mood, current-week entry count
- Active users this week: list sorted by entry count with per-user average mood

### 6.4 P2 — Enhancements (v1.x)

#### F-012: Mood History Table

- Paginated, date-sorted table of all past entries
- Date-range filter for targeted review
- Displays: date, mood score, mood label, sentiment score, sentiment label, remark (decrypted)

#### F-013: Today's Entry Quick View

- Dashboard surface showing today's entry if logged, or a contextual prompt + entry form if not
- Reduces daily friction to a single-screen interaction

#### F-014: Responsive Mobile Layout

- Full functionality accessible on mobile viewports (≥ 320px width)
- Sidebar collapses to a hamburger menu on small screens

---

## 7. Non-Functional Requirements

### 7.1 Security

| Requirement | Detail |
|---|---|
| NFR-SEC-01 | Passwords are hashed with bcrypt (work factor ≥ 12) before storage; plaintext passwords are never stored or logged |
| NFR-SEC-02 | JWT tokens are signed with HS256 using a secret of at least 32 characters configured via environment variable |
| NFR-SEC-03 | Remark text is encrypted at rest using HMAC-SHA256 with a separate `ENCRYPTION_KEY` environment variable |
| NFR-SEC-04 | All authenticated endpoints require a valid, non-expired JWT in the `Authorization` header |
| NFR-SEC-05 | Role checks are enforced at the FastAPI dependency layer, not only in controller logic |
| NFR-SEC-06 | Secrets (`JWT_SECRET`, `ENCRYPTION_KEY`) are injected via environment variables; no secrets are committed to version control |
| NFR-SEC-07 | CORS policy is configured explicitly; wildcard origins are not permitted in production |
| NFR-SEC-08 | Database password hashes are excluded from all API responses |

### 7.2 Performance

| Requirement | Detail |
|---|---|
| NFR-PERF-01 | Mood list and analytics queries must complete within 500ms for datasets up to 10,000 entries per user |
| NFR-PERF-02 | MongoDB indexes are defined on `users.email` (unique), `moods.(user_id, logged_date)` (unique compound), `moods.user_id`, and `moods.logged_date` |
| NFR-PERF-03 | The heatmap query retrieves at most 366 documents (one per day per year); no aggregation pipeline required |
| NFR-PERF-04 | Word cloud computation is performed server-side and limited to 90 days of entries; results are capped at 80 words |
| NFR-PERF-05 | Next.js pages are server-side rendered (SSR) with client-side data fetching for analytics components to ensure fast initial load |

### 7.3 Scalability

| Requirement | Detail |
|---|---|
| NFR-SCALE-01 | The backend is stateless; horizontal scaling is supported by adding additional backend container replicas behind a load balancer |
| NFR-SCALE-02 | MongoDB is used as the primary data store; sharding can be enabled for large deployments without application changes |
| NFR-SCALE-03 | Docker Compose is used for single-host deployments; the architecture is compatible with Kubernetes orchestration for larger deployments |
| NFR-SCALE-04 | Pagination is implemented on all list endpoints (users, mood history) to bound query cost at any scale |

### 7.4 Availability & Reliability

| Requirement | Detail |
|---|---|
| NFR-AVAIL-01 | Backend container restarts automatically on crash (`restart: unless-stopped`) |
| NFR-AVAIL-02 | MongoDB has a health check; the backend container will not start until MongoDB reports healthy |
| NFR-AVAIL-03 | The `/healthz` endpoint returns HTTP 200 and a status payload; it is used by Docker and any upstream load balancer |
| NFR-AVAIL-04 | MongoDB data is persisted to a named Docker volume (`mongo_data`) to survive container restarts |

### 7.5 Privacy

| Requirement | Detail |
|---|---|
| NFR-PRIV-01 | Remark text is encrypted before writing to MongoDB; the database never contains plaintext remarks |
| NFR-PRIV-02 | Admins cannot access individual mood entries, remarks, or sentiment for any user |
| NFR-PRIV-03 | Admin active-user analytics expose only: `full_name`, `entries_this_week`, and `avg_mood` — no remark data |
| NFR-PRIV-04 | The application can be deployed entirely on private infrastructure with no external network dependencies at runtime |
| NFR-PRIV-05 | No third-party analytics, tracking scripts, or telemetry libraries are included in the frontend |

### 7.6 Maintainability

| Requirement | Detail |
|---|---|
| NFR-MAINT-01 | Backend follows a layered architecture: routes → controllers → services → database; business logic lives exclusively in services |
| NFR-MAINT-02 | All API models are defined with Pydantic; validation errors return structured HTTP 422 responses |
| NFR-MAINT-03 | Frontend components are co-located by feature under `src/components/`; shared UI primitives use shadcn/ui |
| NFR-MAINT-04 | Environment-specific configuration (dev vs. production) is managed via separate Docker Compose files |

---

## 8. Technical Architecture Overview

### 8.1 System Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    Docker Network                         │
│                                                           │
│  ┌──────────────────┐      ┌──────────────────────────┐  │
│  │   Frontend       │      │      Backend             │  │
│  │   Next.js 14     │─────▶│   Python FastAPI         │  │
│  │   TypeScript     │      │   Uvicorn ASGI           │  │
│  │   Tailwind CSS   │      │   Port 8000              │  │
│  │   shadcn/ui      │      └────────────┬─────────────┘  │
│  │   recharts       │                   │                  │
│  │   Port 3000      │      ┌────────────▼─────────────┐  │
│  └──────────────────┘      │      MongoDB 7            │  │
│                             │   Collections:           │  │
│                             │   - users                │  │
│                             │   - moods                │  │
│                             │   Volume: mongo_data     │  │
│                             │   Port 27017             │  │
│                             └──────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### 8.2 Backend Architecture

The backend follows a **layered architecture** pattern:

| Layer | Responsibility | Example |
|---|---|---|
| **Routes** (`routes/api.py`) | Route registration, authentication dependency injection | `APIRouter`, `Depends(get_authenticated_user)` |
| **Controllers** (`app/controllers/`) | HTTP request/response handling, input validation | `MoodController`, `AnalyticsController` |
| **Services** (`app/services/`) | Business logic, data access, encryption, analytics computation | `MoodService`, `AnalyticsService` |
| **Models** (`app/models/`) | Pydantic request/response schemas, enums | `MoodCreate`, `UserCreate`, `MoodScore` |
| **Helpers** (`app/helpers/`) | Cross-cutting concerns: JWT, encryption, sentiment, password hashing, HTTP responses | `JWTHelper`, `EncryptionHelper`, `SentimentHelper` |
| **Modules** (`modules/`) | Infrastructure abstraction | `MongoDBManager` (singleton connection pool) |

#### Authentication Flow

```
Client ──POST /auth/login──▶ UserController
                                  │
                             UserService.login()
                                  │
                        PasswordHelper.verify_password()  ←── bcrypt comparison
                                  │
                          JWTHelper.create_token()  ←── HS256, 24h TTL
                                  │
                         Return { token, user }
                                  │
Client stores token ◀─────────────┘

Subsequent requests:
Client ──GET /moods/get──▶ Depends(get_authenticated_user)
                                  │
                          JWTHelper.verify_token()
                                  │
                         Fetch user from MongoDB
                                  │
                        Inject current_user into handler
```

### 8.3 Frontend Architecture

| Directory | Content |
|---|---|
| `src/app/` | Next.js App Router pages |
| `src/app/dashboard/` | Protected dashboard area (auth-gated via `AuthGuard`) |
| `src/app/dashboard/analytics/` | Analytics page (heatmap, charts, word cloud) |
| `src/app/dashboard/reports/` | Weekly summary reports with ISO week navigation |
| `src/app/dashboard/history/` | Mood history table with date filtering |
| `src/app/dashboard/admin/` | Admin panel (user management + platform analytics) |
| `src/app/login/` | Login page |
| `src/app/register/` | Registration page |
| `src/components/` | Shared feature components |
| `src/hooks/` | Custom React hooks for data fetching |
| `src/lib/` | Utility functions, API client configuration |

### 8.4 Key Technology Choices

| Technology | Rationale |
|---|---|
| **FastAPI** | High-performance async Python web framework; automatic OpenAPI documentation; Pydantic integration for request validation |
| **MongoDB** | Schema flexibility suits evolving analytics queries; compound indexes provide fast user-scoped lookups; document model maps naturally to mood entries |
| **Next.js 14 (App Router)** | Server-side rendering for fast initial loads; TypeScript support; built-in API route proxying possible |
| **Tailwind CSS + shadcn/ui** | Utility-first styling with a pre-built accessible component library; rapid iteration without custom CSS overhead |
| **recharts** | Composable, React-native charting library; supports dual-axis charts out of the box |
| **TextBlob** | Lightweight NLP library for polarity-based sentiment scoring; no external API dependencies; runs entirely server-side |
| **Docker Compose** | Single-command orchestration for all three services; reproducible environments across development and production |

---

## 9. Data Model

### 9.1 Users Collection

**Collection name:** `users`

| Field | Type | Constraints | Description |
|---|---|---|---|
| `_id` | ObjectId | PK | MongoDB auto-generated document ID |
| `email` | String | Unique index, required | User's email address (used for login) |
| `full_name` | String | 1–100 chars, required | User's display name |
| `password_hash` | String | Required | bcrypt hash of the user's password |
| `role` | String | Enum: `"Admin"`, `"User"` | Determines access level |
| `is_active` | Boolean | Default: `true` | Soft-disable access without deleting the account |
| `created_at` | DateTime | UTC, auto-set on create | Account creation timestamp |
| `updated_at` | DateTime | UTC, auto-set on update | Last modification timestamp |
| `last_login` | DateTime | UTC, nullable | Timestamp of most recent successful login |

**Indexes:**
- `{ email: 1 }` — unique index, supports login lookup

**Example document:**
```json
{
  "_id": "64b7f1a2c3d4e5f6a7b8c9d0",
  "email": "alex@example.com",
  "full_name": "Alex Johnson",
  "password_hash": "$2b$12$...",
  "role": "User",
  "is_active": true,
  "created_at": "2026-01-15T09:00:00Z",
  "updated_at": "2026-03-10T14:22:00Z",
  "last_login": "2026-03-17T08:45:00Z"
}
```

---

### 9.2 Moods Collection

**Collection name:** `moods`

| Field | Type | Constraints | Description |
|---|---|---|---|
| `_id` | ObjectId | PK | MongoDB auto-generated document ID |
| `user_id` | String | Required, ref: users._id | Owner of this entry (stored as string) |
| `mood_score` | Integer | 1–5, required | Subjective mood score |
| `mood_label` | String | Derived from score | Human-readable label (see Appendix) |
| `remark` | String | Nullable, max 500 chars (pre-encryption) | Encrypted remark text (HMAC-SHA256 + base64) |
| `sentiment_score` | Float | -1.0 to +1.0, default 0.0 | TextBlob polarity score |
| `sentiment_label` | String | Enum: Positive, Neutral, Negative | Derived from sentiment_score thresholds |
| `logged_date` | DateTime | UTC midnight, required | The calendar date of the entry (time component is always 00:00:00) |
| `created_at` | DateTime | UTC | Record creation timestamp |
| `updated_at` | DateTime | UTC | Last modification timestamp |

**Indexes:**
- `{ user_id: 1, logged_date: 1 }` — unique compound index (one entry per user per day)
- `{ user_id: 1 }` — supports user-scoped queries
- `{ logged_date: 1 }` — supports admin analytics date range queries

**Example document:**
```json
{
  "_id": "64c8a2b3d4e5f6a7b8c9d0e1",
  "user_id": "64b7f1a2c3d4e5f6a7b8c9d0",
  "mood_score": 4,
  "mood_label": "Good",
  "remark": "R29vZCBkYXk6OjxobWFjLXNpZ25hdHVyZT4=",
  "sentiment_score": 0.3625,
  "sentiment_label": "Positive",
  "logged_date": "2026-03-17T00:00:00Z",
  "created_at": "2026-03-17T18:30:00Z",
  "updated_at": "2026-03-17T18:30:00Z"
}
```

**Note on remark encryption:** The remark field stores a base64-encoded string containing `<plaintext_bytes>::<hmac_sha256_signature>`. The HMAC acts as both an integrity check and an obfuscation layer. Decryption verifies the signature before returning the plaintext. If the `ENCRYPTION_KEY` is rotated, stored remarks become unreadable — key management is therefore a deployment responsibility.

---

## 10. API Endpoints Summary

**Base URL:** `http://<host>:8000`

**Authentication:** All protected endpoints require `Authorization: Bearer <jwt_token>` header.

### 10.1 Public Endpoints (No Authentication)

| Method | Path | Description |
|---|---|---|
| `GET` | `/healthz` | Health check; returns `{ status: "healthy" }` |
| `GET` | `/v1` | API version and status |
| `POST` | `/auth/register` | Register a new user account |
| `POST` | `/auth/login` | Authenticate and receive a JWT token |

### 10.2 Authenticated User Endpoints

#### Authentication

| Method | Path | Description |
|---|---|---|
| `POST` | `/auth/logout` | Log out (client-side token invalidation) |
| `GET` | `/auth/me` | Get the current authenticated user's profile |
| `POST` | `/auth/change-password` | Change the authenticated user's password |

#### Mood CRUD

| Method | Path | Description | Query Params |
|---|---|---|---|
| `GET` | `/moods/get` | Get paginated mood history for the current user | `page`, `limit`, `start_date`, `end_date` |
| `GET` | `/moods/today` | Get today's mood entry (or null) | — |
| `GET` | `/moods/get/{mood_id}` | Get a single mood entry by ID | — |
| `POST` | `/moods/create` | Create today's mood entry | — |
| `PATCH` | `/moods/edit/{mood_id}` | Update a mood entry | — |
| `DELETE` | `/moods/{mood_id}` | Delete a mood entry | — |

#### Analytics

| Method | Path | Description | Query Params |
|---|---|---|---|
| `GET` | `/analytics/heatmap` | 12-month calendar heatmap data | `year` |
| `GET` | `/analytics/sentiment-trend` | Sentiment and mood over time | `days` (default 30) |
| `GET` | `/analytics/word-cloud` | Word frequency data from recent remarks | `days` (default 90) |
| `GET` | `/analytics/mood-distribution` | Mood score distribution | `days` (default 90) |
| `GET` | `/analytics/weekly-summary` | Current ISO week summary | — |
| `GET` | `/analytics/weekly-summary/{year}/{week}` | Specific ISO week summary | — |
| `GET` | `/analytics/streak` | Current logging streak | — |

### 10.3 Admin-Only Endpoints

| Method | Path | Description | Query Params |
|---|---|---|---|
| `GET` | `/users/get` | Paginated list of all users | `page`, `limit` |
| `GET` | `/users/get/{user_id}` | Get a user by ID | — |
| `PATCH` | `/users/edit` | Update a user's name, role, or active status | — |
| `DELETE` | `/users/{user_id}` | Delete a user account | — |
| `GET` | `/admin/analytics/overview` | Platform-wide mood and engagement summary | — |
| `GET` | `/admin/analytics/active-users` | Users who logged this week with stats | — |

### 10.4 Standard Response Format

**Success:**
```json
{
  "success": true,
  "message": "Operation description",
  "data": { ... }
}
```

**Error:**
```json
{
  "success": false,
  "message": "Human-readable error description"
}
```

**Pagination:**
```json
{
  "data": [ ... ],
  "total_count": 142
}
```

---

## 11. Security & Privacy Considerations

### 11.1 Authentication Security

- **Password storage:** bcrypt with a work factor of 12+. Plaintext passwords are never logged, cached, or returned in any API response.
- **JWT implementation:** Custom HS256 implementation. Tokens carry `user_id`, `email`, and `role` claims plus standard `exp` and `iat` claims. Tokens expire after 24 hours.
- **Token transmission:** Tokens should be transmitted only over HTTPS in production. The frontend stores the token in browser memory or an httpOnly cookie (not `localStorage` in production deployments to reduce XSS risk).
- **Account lockout:** v1 does not implement rate limiting or account lockout on failed login attempts. This is a known v1 limitation and is tracked in the future roadmap (see Section 13).

### 11.2 Data Encryption

| Data | At Rest | In Transit |
|---|---|---|
| Passwords | bcrypt hash | HTTPS (TLS) |
| Mood remarks | HMAC-SHA256 + base64 | HTTPS (TLS) |
| Mood scores, dates, sentiment | Plaintext in MongoDB | HTTPS (TLS) |
| JWT tokens | N/A (stateless) | HTTPS (TLS) |

**Remark encryption detail:** The `EncryptionHelper` computes an HMAC-SHA256 signature over the plaintext remark using the server's `ENCRYPTION_KEY`. The plaintext and its signature are concatenated (`plaintext::signature`) and base64-encoded before storage. On retrieval, the stored value is decoded, the signature recomputed, and compared in constant time. Tampering with stored data is detectable. Note that this scheme provides **integrity and obfuscation** but is not equivalent to symmetric encryption (e.g., AES-GCM). Anyone with access to the `ENCRYPTION_KEY` and the database can recover all remarks.

### 11.3 Authorisation Model

```
Role    │ Own mood entries │ All users' mood entries │ User management │ Admin analytics
────────┼──────────────────┼─────────────────────────┼─────────────────┼────────────────
User    │ Full CRUD        │ No access               │ No access       │ No access
Admin   │ Full CRUD        │ No access               │ Full CRUD       │ Read-only
```

The key design decision is that **Admins cannot read individual mood entries**. Admin analytics endpoints expose only aggregate statistics (counts and averages), preserving the privacy of individual users even from platform administrators.

### 11.4 Input Validation

- All request bodies are validated by Pydantic models; malformed requests receive HTTP 422 before reaching business logic.
- Mood scores are constrained to the range 1–5 at the model level (`ge=1, le=5`).
- Password minimum length is enforced at 8 characters; maximum at 128 characters.
- Remark maximum length is 500 characters.
- Email addresses are validated as valid email format using `pydantic.EmailStr`.

### 11.5 Infrastructure Security

- No secrets are hardcoded in source code; all sensitive values are injected via environment variables (`JWT_SECRET`, `ENCRYPTION_KEY`).
- The Docker Compose configuration explicitly warns that default placeholder values must be replaced before production deployment.
- MongoDB is not exposed with authentication in the default Compose configuration; production deployments must configure MongoDB access controls and bind to localhost or a private network only.
- CORS policy must be explicitly configured for production; the default FastAPI CORS middleware setting should restrict `allow_origins` to the frontend domain.

---

## 12. Success Metrics / KPIs

### 12.1 User Engagement

| KPI | Definition | Target (90 days post-launch) |
|---|---|---|
| Daily Active Users (DAU) | Users who log at least one mood entry on a given day | ≥ 60% of registered active users |
| Average Logging Streak | Mean consecutive-day streak across all active users | ≥ 5 days |
| Weekly Report Views | Count of `/analytics/weekly-summary` requests per user per week | ≥ 1 per active user per week |
| Analytics Page Views | Count of `/analytics/heatmap` or `/analytics/sentiment-trend` requests | ≥ 2 per active user per week |
| Entry Retention Rate | % of users who are still logging 30 days after registration | ≥ 40% |

### 12.2 Platform Health

| KPI | Definition | Target |
|---|---|---|
| API Latency (p95) | 95th percentile response time for all endpoints | < 500ms |
| API Availability | Uptime of the backend container | ≥ 99.5% monthly |
| Error Rate | % of non-4xx HTTP responses that are 5xx | < 0.5% |
| Data Integrity Incidents | Number of incidents where plaintext remarks were exposed | 0 |

### 12.3 Admin Observability

| KPI | Definition | Target |
|---|---|---|
| Platform Average Mood | Weekly rolling average mood score across all users | Monitored; no fixed target |
| Weekly Logging Rate | % of registered users who log at least once per week | Monitored; baseline to be established |
| User Growth | New registrations per week | Monitored |

### 12.4 Technical Quality

| KPI | Definition | Target |
|---|---|---|
| Test Coverage | Unit test coverage of service layer | ≥ 80% |
| Docker Build Time | Time to build and start all containers from clean | < 3 minutes |
| First Contentful Paint (FCP) | Frontend FCP on dashboard page | < 2 seconds on standard broadband |

---

## 13. Future Roadmap

### 13.1 v1.1 — Security Hardening

| Feature | Description |
|---|---|
| Login rate limiting | Implement per-IP and per-email rate limiting on `/auth/login` to prevent brute-force attacks |
| Refresh token rotation | Replace long-lived access tokens with short-lived access tokens + long-lived refresh tokens |
| AES-GCM encryption | Upgrade remark encryption from HMAC-SHA256 obfuscation to authenticated symmetric encryption (AES-256-GCM) for stronger at-rest security |
| MongoDB authentication | Enable MongoDB username/password authentication and TLS in the default Compose configuration |
| Audit log | Immutable log of admin actions (user updates, deletions) |

### 13.2 v1.2 — User Experience Improvements

| Feature | Description |
|---|---|
| Mobile-first redesign | Fully optimised mobile experience with native-feel touch interactions |
| Push / email reminders | Optional daily reminder notification (configurable time) to prompt mood logging |
| Mood entry streak badges | Visual milestone badges (7-day, 30-day, 100-day streaks) to gamify habit formation |
| Customisable analytics window | User-configurable date range selector across all analytics views instead of fixed presets |
| Dark mode | System-preference-aware dark mode toggle |

### 13.3 v2.0 — Platform Expansion

| Feature | Description |
|---|---|
| Multi-factor authentication (MFA) | TOTP-based MFA as an optional security layer for all accounts |
| Export & portability | Allow users to export their full mood history as CSV or JSON |
| Mood triggers / tags | User-defined categorical tags (work, sleep, exercise, etc.) associated with entries to enable correlation analysis |
| Advanced analytics | Correlation matrix between mood score, sentiment, day-of-week, and user-defined tags |
| Team organisations | Group users into organisations; team leads see aggregated team analytics, not the platform-wide view |
| API rate limiting | Token bucket rate limiting on all API endpoints |
| Webhook integrations | Outbound webhooks on low-mood events for integration with HR systems or alerting platforms |
| Therapist sharing mode | Time-limited, read-only share links allowing a therapist to view a user's weekly summaries |
| Native mobile app | React Native or Flutter companion app for faster daily logging |
| Self-registration controls | Admin configurable: open registration vs. invite-only vs. closed |

---

## 14. Appendix

### Appendix A: Mood Score Scale

| Score | Label | Colour (UI) | Description |
|---|---|---|---|
| 1 | Terrible | Deep red (`#ef4444`) | Significant distress; very difficult day |
| 2 | Bad | Orange-red (`#f97316`) | Below average; struggling |
| 3 | Neutral | Amber (`#eab308`) | Neither good nor bad; baseline |
| 4 | Good | Light green (`#84cc16`) | Above average; positive day |
| 5 | Great | Deep green (`#22c55e`) | Excellent; high wellbeing |

**One entry per calendar day** is enforced. The score represents the user's holistic assessment of the day and is set at the time of logging. It may be updated at any point during the same day but cannot be backdated.

---

### Appendix B: Sentiment Score Scale

Sentiment is computed automatically by TextBlob's `sentiment.polarity` method on the remark text. It does not require any user input.

| Range | Label | Description |
|---|---|---|
| `> 0.1` | Positive | The remark contains net positive emotional language |
| `-0.1` to `0.1` | Neutral | The remark is emotionally balanced or contains insufficient signal |
| `< -0.1` | Negative | The remark contains net negative emotional language |

**Score range:** -1.0 (maximally negative) to +1.0 (maximally positive), with 0.0 representing perfect neutrality.

**Relationship to mood score:** Sentiment is computed independently from the mood score. A user may report a mood score of 5 (Great) while writing a remark with negative sentiment (e.g., "Not as terrible as yesterday, finally getting better"), or vice versa. The dual-axis sentiment trend chart is designed to surface these divergences as meaningful signals.

**Absence of remark:** If no remark is provided, `sentiment_score` defaults to `0.0` and `sentiment_label` to `"Neutral"`. These entries are still counted in mood analytics but excluded from word cloud computation.

---

### Appendix C: Environment Variables Reference

| Variable | Required | Description | Example |
|---|---|---|---|
| `JWT_SECRET` | Yes | Secret key for JWT signing (min 32 chars) | `your-very-long-random-secret-here` |
| `ENCRYPTION_KEY` | Yes | Key for remark HMAC-SHA256 encryption | `another-very-long-random-key-here` |
| `CONNECTION_STRING` | Yes | MongoDB connection URI | `mongodb://mongo:27017/` |
| `DATABASE_NAME` | Yes | MongoDB database name | `mood_tracker` |
| `APP_NAME` | No | Application display name | `Mood Tracker API` |
| `APP_HOST` | No | Uvicorn bind host | `0.0.0.0` |
| `APP_PORT` | No | Uvicorn bind port | `8000` |
| `APP_ENVIRONMENT` | No | Runtime environment label | `production` |
| `NEXT_PUBLIC_API_URL` | Yes (frontend) | Backend API base URL for client-side requests | `http://localhost:8000` |

---

*Document prepared by the Mood Tracker development team. For questions or feedback, contact the product owner.*
