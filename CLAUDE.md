# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Mood Tracker is a full-stack mood logging and sentiment analytics platform. Users log daily mood (1-5 score + optional remark), and the system auto-computes sentiment via TextBlob NLP. Features include calendar heatmap, sentiment trend charts, word cloud, mood distribution, weekly reports, and an admin panel with aggregated analytics.

## Architecture

**Monorepo with two independently deployed apps:**

- `backend/` — Python FastAPI API with MongoDB (via pymongo), deployed to Vercel as a serverless Python function via `backend/api/index.py`
- `frontend/` — Next.js 14 (App Router) with TypeScript, Tailwind CSS, shadcn/ui, deployed to Vercel as a standard Next.js app

**Backend layered architecture** (routes → controllers → services → database):
- `routes/api.py` — Route registration with three auth tiers: unauth, user_auth (Depends), admin_auth (Depends)
- `app/controllers/` — HTTP handling, delegates to services
- `app/services/` — All business logic (MoodService, UserService, AnalyticsService)
- `app/models/` — Pydantic request/response schemas
- `app/helpers/` — Cross-cutting: custom JWT (HS256), HMAC-SHA256 remark encryption, TextBlob sentiment, password hashing, HTTP response formatting
- `modules/database/DatabaseManager.py` — Singleton MongoDB connection manager (pymongo)

**Frontend structure:**
- `src/app/` — Next.js App Router pages (login, register, dashboard/*)
- `src/components/` — Feature components (MoodEntryForm, MoodCalendarHeatmap, SentimentTrendChart, WordCloud, WeeklySummaryCard, Sidebar, AuthGuard)
- `src/hooks/` — `useAuth` (auth state + redirect) and `useMood` (CRUD operations)
- `src/lib/api.ts` — Central fetch wrapper that attaches Bearer token from `js-cookie`; auto-redirects to `/login` on 401
- `src/lib/auth.ts` — Login/register/logout with cookie-based token storage (1-day expiry)
- `src/lib/types.ts` — All TypeScript interfaces + mood emoji/color mappings

**Auth flow:** Custom JWT (24h TTL, includes user_id/email/full_name/role) → stored in `auth_token` cookie → sent as `Authorization: Bearer` header → verified statelessly by `RouteAuth.py` (signature + expiry only, no DB lookup).

**Data:** MongoDB with `users` and `moods` collections. Unique compound index on `(user_id, logged_date)` enforces one mood per day. Remarks are HMAC-SHA256 encrypted at rest.

## Commands

### Backend (from `backend/` directory)
```bash
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

python -m pytest tests/
python -m pytest tests/test_helpers.py -v
```

### Frontend (from `frontend/` directory)
```bash
npm install
npm run dev          # Dev server on :3000
npm run build        # Production build
npm run lint         # ESLint
```

### Docker (from project root)
```bash
docker compose -f docker-compose.dev.yml up    # Dev with hot-reload (includes MongoDB)
docker compose up --build                       # Production
```

## Environment Variables

### Backend
| Variable | Purpose |
|---|---|
| `JWT_SECRET` | HS256 signing key (min 32 chars) |
| `ENCRYPTION_KEY` | HMAC-SHA256 key for remark encryption |
| `CONNECTION_STRING` | MongoDB connection URI (e.g. `mongodb+srv://...`) |
| `DATABASE_NAME` | MongoDB database name (default: `mood_tracker`) |
| `ALLOWED_ORIGINS` | Comma-separated CORS origins (Vercel entry point only) |

### Frontend
| Variable | Purpose |
|---|---|
| `NEXT_PUBLIC_API_URL` | Backend API base URL |

## Deployment

Both apps deploy independently to Vercel:
- **Backend:** Python serverless function. Entry point: `backend/api/index.py`. Config: `backend/vercel.json`. Requires `CONNECTION_STRING` env var pointing to a MongoDB Atlas (or similar) instance.
- **Frontend:** Standard Next.js with `output: "standalone"` in `next.config.mjs`.

## Key Patterns

- **One mood per user per day** enforced at both service and DB (unique compound index)
- **Mood scores 1-5** map to labels: Terrible, Bad, Neutral, Good, Great
- **Sentiment** auto-computed from remark text via TextBlob polarity (-1.0 to +1.0)
- **API responses** always use `{"success": bool, "message": str, "data": ...}` format
- **CORS** is configured in `main.py` (Docker) and `api/index.py` (Vercel) separately
- **Frontend `api.ts`** is the single point for all HTTP calls — never use raw `fetch`
- **Auth is stateless** — JWT payload is trusted without DB lookup (required for serverless)
