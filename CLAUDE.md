# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Mood Tracker is a full-stack mood logging and sentiment analytics platform. Users log daily mood (1-5 score + optional remark), and the system auto-computes sentiment via TextBlob NLP. Features include calendar heatmap, sentiment trend charts, word cloud, mood distribution, weekly reports, and an admin panel with aggregated analytics.

## Architecture

**Monorepo with two independently deployed apps:**

- `backend/` — Python FastAPI API with SQLite (migrated from MongoDB), deployed to Vercel as a serverless Python function via `backend/api/index.py`
- `frontend/` — Next.js 14 (App Router) with TypeScript, Tailwind CSS, shadcn/ui, deployed to Vercel as a standard Next.js app

**Backend layered architecture** (routes → controllers → services → database):
- `routes/api.py` — Route registration with three auth tiers: unauth, user_auth (Depends), admin_auth (Depends)
- `app/controllers/` — HTTP handling, delegates to services
- `app/services/` — All business logic (MoodService, UserService, AnalyticsService)
- `app/models/` — Pydantic request/response schemas
- `app/helpers/` — Cross-cutting: custom JWT (HS256), HMAC-SHA256 remark encryption, TextBlob sentiment, bcrypt passwords, HTTP response formatting
- `modules/database/DatabaseManager.py` — Thread-safe singleton SQLite manager with WAL mode

**Frontend structure:**
- `src/app/` — Next.js App Router pages (login, register, dashboard/*)
- `src/components/` — Feature components (MoodEntryForm, MoodCalendarHeatmap, SentimentTrendChart, WordCloud, WeeklySummaryCard, Sidebar, AuthGuard)
- `src/hooks/` — `useAuth` (auth state + redirect) and `useMood` (CRUD operations)
- `src/lib/api.ts` — Central fetch wrapper that attaches Bearer token from `js-cookie`; skips auth header for `/auth/login` and `/auth/register`
- `src/lib/auth.ts` — Login/register/logout with cookie-based token storage (1-day expiry)
- `src/lib/types.ts` — All TypeScript interfaces + mood emoji/color mappings

**Auth flow:** Custom JWT (24h TTL) → stored in `auth_token` cookie → sent as `Authorization: Bearer` header → verified by `RouteAuth.py` dependency → injects current_user dict into handlers.

**Data:** SQLite with `users` and `moods` tables. On Vercel, DB is stored at `/tmp` (ephemeral). Remarks are HMAC-SHA256 encrypted at rest.

## Commands

### Backend (from `backend/` directory)
```bash
# Install dependencies
pip install -r requirements.txt

# Run dev server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Run tests
python -m pytest tests/

# Run single test
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
docker compose -f docker-compose.dev.yml up    # Dev with hot-reload
docker compose up --build                       # Production
```

## Environment Variables

### Backend
| Variable | Purpose |
|---|---|
| `JWT_SECRET` | HS256 signing key (min 32 chars) |
| `ENCRYPTION_KEY` | HMAC-SHA256 key for remark encryption |
| `DATABASE_PATH` | SQLite file path (default: `./data/mood_tracker.db`, `/tmp` on Vercel) |
| `ALLOWED_ORIGINS` | Comma-separated CORS origins (Vercel entry point only) |

### Frontend
| Variable | Purpose |
|---|---|
| `NEXT_PUBLIC_API_URL` | Backend API base URL |

## Deployment

Both apps deploy independently to Vercel:
- **Backend:** Python serverless function. Entry point: `backend/api/index.py`. Config: `backend/vercel.json`. All routes go through the single function.
- **Frontend:** Standard Next.js with `output: "standalone"` in `next.config.mjs`.

**Important:** SQLite on Vercel uses `/tmp` which is ephemeral per function invocation — data does not persist across cold starts. This is a known limitation of the current Vercel deployment.

## Key Patterns

- **One mood per user per day** enforced at both service and DB (UNIQUE constraint on user_id + logged_date)
- **Mood scores 1-5** map to labels: Terrible, Bad, Neutral, Good, Great
- **Sentiment** auto-computed from remark text via TextBlob polarity (-1.0 to +1.0)
- **API responses** always use `{"success": bool, "message": str, "data": ...}` format
- **CORS** is configured in `main.py` (Docker) and `api/index.py` (Vercel) separately
- **Frontend `api.ts`** is the single point for all HTTP calls — never use raw `fetch`
