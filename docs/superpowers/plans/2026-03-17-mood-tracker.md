# Mood Tracker Application — Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a full-stack mood tracking application with daily mood logging, sentiment analysis, calendar heatmap visualization, word cloud, and weekly summary reports — supporting multi-user authenticated access.

**Architecture:** Two-service architecture mirroring `recruitment_tracker_api` patterns — a Python FastAPI backend (Controller → Service → MongoDB, custom JWT auth, HMAC encryption, role-based access) and a Next.js 14 App Router frontend. Each service runs in its own Docker container orchestrated via docker-compose. The backend owns all business logic, auth, and data; the frontend is a thin client that calls the API.

**Tech Stack:**
- **Backend:** Python 3.12, FastAPI 0.103, PyMongo 4.5, Pydantic v2, NLTK/TextBlob (sentiment), python-decouple
- **Frontend:** Next.js 14 (App Router), TypeScript, Tailwind CSS, shadcn/ui, recharts (heatmap/charts), d3-cloud (word cloud)
- **Infrastructure:** Docker, docker-compose, MongoDB, Nginx (optional reverse proxy)

---

## Project Structure

```
mood_tracker/
├── backend/
│   ├── app/
│   │   ├── controllers/
│   │   │   ├── __init__.py
│   │   │   ├── HealthController.py
│   │   │   ├── UserController.py
│   │   │   ├── MoodController.py
│   │   │   └── AnalyticsController.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── UserModel.py
│   │   │   └── MoodModel.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── UserService.py
│   │   │   ├── MoodService.py
│   │   │   └── AnalyticsService.py
│   │   ├── helpers/
│   │   │   ├── __init__.py
│   │   │   ├── JWTHelper.py
│   │   │   ├── PasswordHelper.py
│   │   │   ├── EncryptionHelper.py
│   │   │   ├── RouteAuth.py
│   │   │   ├── HttpResponse.py
│   │   │   ├── PaginationHelper.py
│   │   │   └── SentimentHelper.py
│   │   └── __init__.py
│   ├── modules/
│   │   └── mongodb/
│   │       ├── __init__.py
│   │       └── MongoDBManager.py
│   ├── routes/
│   │   ├── __init__.py
│   │   └── api.py
│   ├── config/
│   │   └── app.py
│   ├── main.py
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── Dockerfile.dev
│   ├── init_mongodb.js
│   └── dev.env
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx                    (redirect to /dashboard or /login)
│   │   │   ├── login/
│   │   │   │   └── page.tsx
│   │   │   ├── register/
│   │   │   │   └── page.tsx
│   │   │   └── dashboard/
│   │   │       ├── layout.tsx              (auth-guarded shell)
│   │   │       ├── page.tsx                (main dashboard: heatmap + today's mood)
│   │   │       ├── history/
│   │   │       │   └── page.tsx            (mood history list)
│   │   │       ├── analytics/
│   │   │       │   └── page.tsx            (word cloud + sentiment trends)
│   │   │       ├── reports/
│   │   │       │   └── page.tsx            (weekly summary report)
│   │   │       └── admin/
│   │   │           └── page.tsx            (user management — Admin only)
│   │   ├── components/
│   │   │   ├── ui/                         (shadcn/ui primitives)
│   │   │   ├── MoodCalendarHeatmap.tsx
│   │   │   ├── MoodEntryForm.tsx
│   │   │   ├── WordCloud.tsx
│   │   │   ├── SentimentTrendChart.tsx
│   │   │   ├── WeeklySummaryCard.tsx
│   │   │   ├── MoodHistoryTable.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   └── AuthGuard.tsx
│   │   ├── lib/
│   │   │   ├── api.ts                      (fetch wrapper with auth)
│   │   │   ├── auth.ts                     (token storage, login/logout)
│   │   │   └── types.ts                    (shared TypeScript interfaces)
│   │   └── hooks/
│   │       ├── useAuth.ts
│   │       └── useMood.ts
│   ├── public/
│   ├── tailwind.config.ts
│   ├── next.config.js
│   ├── tsconfig.json
│   ├── package.json
│   ├── Dockerfile
│   └── Dockerfile.dev
├── docker-compose.yml
├── docker-compose.dev.yml
└── docs/
    └── superpowers/
        └── plans/
            └── 2026-03-17-mood-tracker.md  (this file)
```

---

## Database Schema (MongoDB)

### Collection: `users`
```json
{
  "_id": "ObjectId",
  "email": "string (unique)",
  "full_name": "string",
  "password_hash": "string (salt$hash)",
  "role": "Admin | User",
  "is_active": true,
  "created_at": "datetime",
  "updated_at": "datetime",
  "last_login": "datetime"
}
```

### Collection: `moods`
```json
{
  "_id": "ObjectId",
  "user_id": "string (ref: users._id)",
  "mood_score": "int (1-5)",
  "mood_label": "string (Terrible|Bad|Neutral|Good|Great)",
  "remark": "string (short text, encrypted at rest)",
  "sentiment_score": "float (-1.0 to 1.0, computed by backend)",
  "sentiment_label": "string (Negative|Neutral|Positive)",
  "logged_date": "date (one entry per user per day)",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```
- **Unique compound index:** `(user_id, logged_date)` — one mood per user per day
- **Index:** `user_id`
- **Index:** `logged_date`

---

## Authentication & Security Design

Mirrors `recruitment_tracker_api` exactly:

| Concern | Implementation | Reference File |
|---|---|---|
| JWT tokens | Custom HMAC-SHA256, 24h expiry | `JWTHelper.py` (same pattern) |
| Password hashing | SHA-256 + random 64-char salt | `PasswordHelper.py` (same pattern) |
| Field encryption | HMAC-SHA256 + base64 for remarks | `EncryptionHelper.py` (same pattern) |
| Route auth | `Depends()` injection, cookie + Bearer header | `RouteAuth.py` (same pattern) |
| Roles | `Admin` (manage users), `User` (own moods only) | Simplified from 4-role to 2-role |

### Auth Levels

| Level | Who | What |
|---|---|---|
| **unauth** | Anyone | `GET /healthz`, `POST /auth/login`, `POST /auth/register` |
| **user_auth** | Any authenticated user | CRUD own moods, view own analytics, change password |
| **admin_auth** | Admin only | Manage users, view all users' analytics |

### Data Isolation
- Users can **only** read/write **their own** mood entries
- Admin can view **aggregated** analytics across all users but **not** read individual remarks (encrypted)
- Remarks are encrypted at rest using `EncryptionHelper.encrypt_field()` — only the owning user's session decrypts them for display

---

## API Endpoints

### Unauth (Public)
| Method | Path | Description |
|---|---|---|
| `GET` | `/healthz` | Health check (MongoDB ping) |
| `GET` | `/v1` | API version info |
| `POST` | `/auth/login` | Login → returns JWT |
| `POST` | `/auth/register` | Self-registration (creates User role) |

### User Auth (Any Authenticated User — Own Data Only)
| Method | Path | Description |
|---|---|---|
| `POST` | `/auth/logout` | Logout (clear cookie) |
| `GET` | `/auth/me` | Current user info |
| `POST` | `/auth/change-password` | Change own password |
| `GET` | `/moods/get` | List own moods (paginated, date-filtered) |
| `GET` | `/moods/get/{mood_id}` | Get single mood entry |
| `GET` | `/moods/today` | Get today's mood (or 404) |
| `POST` | `/moods/create` | Log mood for today (enforces 1/day) |
| `PATCH` | `/moods/edit/{mood_id}` | Update today's mood |
| `DELETE` | `/moods/{mood_id}` | Delete a mood entry |
| `GET` | `/analytics/heatmap` | Calendar heatmap data (12 months) |
| `GET` | `/analytics/sentiment-trend` | Sentiment scores over time |
| `GET` | `/analytics/word-cloud` | Word frequency from remarks |
| `GET` | `/analytics/weekly-summary` | Current week summary report |
| `GET` | `/analytics/weekly-summary/{year}/{week}` | Specific week summary |
| `GET` | `/analytics/mood-distribution` | Mood score distribution |
| `GET` | `/analytics/streak` | Current logging streak |

### Admin Auth (Admin Only)
| Method | Path | Description |
|---|---|---|
| `GET` | `/users/get` | List all users |
| `GET` | `/users/get/{user_id}` | Get user details |
| `PATCH` | `/users/edit` | Update user (role, active) |
| `DELETE` | `/users/{user_id}` | Delete user |
| `GET` | `/admin/analytics/overview` | Platform-wide mood averages |
| `GET` | `/admin/analytics/active-users` | User engagement stats |

---

## Frontend Pages

### `/login` — Login Page
- Email + password form
- Calls `POST /auth/login`, stores JWT in httpOnly cookie via API response
- Redirects to `/dashboard`

### `/register` — Registration Page
- Full name + email + password + confirm password
- Calls `POST /auth/register`
- Redirects to `/login` with success message

### `/dashboard` — Main Dashboard (Auth Required)
- **Today's Mood Card:** If not logged today → mood entry form (emoji picker for 1-5 score + remark textarea). If already logged → show today's entry with edit option
- **Calendar Heatmap:** 12-month GitHub-style heatmap colored by mood score (1=red → 5=green). Clicking a day shows that day's mood details in a popover
- **Quick Stats:** Current streak, average mood this week, total entries

### `/dashboard/history` — Mood History
- Paginated table of all mood entries (date, mood emoji, remark excerpt, sentiment badge)
- Date range filter
- Click to expand full remark

### `/dashboard/analytics` — Analytics
- **Sentiment Trend Chart:** Line chart of `sentiment_score` over time (recharts)
- **Word Cloud:** Most frequent words from remarks (d3-cloud)
- **Mood Distribution:** Pie/donut chart of mood score counts

### `/dashboard/reports` — Weekly Summary
- Select week (defaults to current)
- Summary card: average mood, most common mood, total entries, sentiment average
- Day-by-day breakdown with sparkline
- Key words of the week

### `/dashboard/admin` — Admin Panel (Admin Only)
- User management table (name, email, role, active, last login)
- Toggle active status
- Platform overview stats

---

## Docker Configuration

### `docker-compose.yml` (Production)
```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: mood_tracker_api
    restart: unless-stopped
    environment:
      APP_NAME: Mood Tracker API
      APP_HOST: 0.0.0.0
      APP_PORT: 8000
      APP_ENVIRONMENT: production
      CONNECTION_STRING: mongodb://mongo:27017/
      DATABASE_NAME: mood_tracker
      JWT_SECRET: ${JWT_SECRET}
      ENCRYPTION_KEY: ${ENCRYPTION_KEY}
    ports:
      - "8000:8000"
    depends_on:
      mongo:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/healthz"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: mood_tracker_ui
    restart: unless-stopped
    environment:
      NEXT_PUBLIC_API_URL: http://backend:8000
    ports:
      - "3000:3000"
    depends_on:
      - backend

  mongo:
    image: mongo:7
    container_name: mood_tracker_mongo
    restart: unless-stopped
    volumes:
      - mongo_data:/data/db
      - ./backend/init_mongodb.js:/docker-entrypoint-initdb.d/init.js:ro
    ports:
      - "27017:27017"
    healthcheck:
      test: ["CMD", "mongosh", "--eval", "db.adminCommand('ping')"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  mongo_data:
```

### `docker-compose.dev.yml` (Development)
```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.dev
    container_name: mood_tracker_api_dev
    restart: unless-stopped
    environment:
      APP_NAME: Mood Tracker API (Dev)
      APP_HOST: 0.0.0.0
      APP_PORT: 8000
      APP_ENVIRONMENT: development
      CONNECTION_STRING: mongodb://mongo:27017/
      DATABASE_NAME: mood_tracker_dev
      JWT_SECRET: dev_secret_change_in_prod
      ENCRYPTION_KEY: dev_encryption_key_change_in_prod
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
      - /app/__pycache__
    depends_on:
      - mongo
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.dev
    container_name: mood_tracker_ui_dev
    restart: unless-stopped
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:8000
    ports:
      - "3000:3000"
    volumes:
      - ./frontend:/app
      - /app/node_modules
      - /app/.next
    command: npm run dev

  mongo:
    image: mongo:7
    container_name: mood_tracker_mongo_dev
    restart: unless-stopped
    volumes:
      - mongo_dev_data:/data/db
      - ./backend/init_mongodb.js:/docker-entrypoint-initdb.d/init.js:ro
    ports:
      - "27017:27017"

volumes:
  mongo_dev_data:
```

---

## Git Branching Strategy

Each task (or logical group of tasks) gets its own **feature branch** off `main`, and is **PR'd back into main** before the next dependent branch starts.

| Branch Name | Tasks | PR Into |
|---|---|---|
| `feat/backend-scaffold` | 1, 2 | `main` |
| `feat/backend-helpers` | 3, 4 | `main` |
| `feat/backend-user-service` | 5 | `main` |
| `feat/backend-mood-service` | 6 | `main` |
| `feat/backend-analytics` | 7 | `main` |
| `feat/backend-routes-docker` | 8, 9 | `main` |
| `feat/docker-compose` | 10 | `main` |
| `feat/frontend-scaffold` | 11, 12 | `main` |
| `feat/frontend-auth-pages` | 13, 14 | `main` |
| `feat/frontend-dashboard` | 15, 16 | `main` |
| `feat/frontend-history-analytics` | 17, 18 | `main` |
| `feat/frontend-reports-admin` | 19, 20 | `main` |
| `feat/integration-tests` | 21 | `main` |
| `feat/final-polish` | 22 | `main` |

**Workflow per branch:**
1. `git checkout main && git pull`
2. `git checkout -b feat/<branch-name>`
3. Implement tasks, commit incrementally
4. `git push -u origin feat/<branch-name>`
5. `gh pr create` → merge into `main`
6. Next branch starts from updated `main`

---

## Implementation Tasks

---

### Task 1: Backend — Project Scaffolding & Configuration

**Files:**
- Create: `backend/main.py`
- Create: `backend/config/app.py`
- Create: `backend/requirements.txt`
- Create: `backend/dev.env`
- Create: `backend/app/__init__.py`
- Create: `backend/app/controllers/__init__.py`
- Create: `backend/app/models/__init__.py`
- Create: `backend/app/services/__init__.py`
- Create: `backend/app/helpers/__init__.py`
- Create: `backend/modules/__init__.py`
- Create: `backend/modules/mongodb/__init__.py`
- Create: `backend/routes/__init__.py`

- [ ] **Step 1: Create `backend/requirements.txt`**

```
fastapi==0.103.0
uvicorn==0.23.2
pymongo==4.5.0
python-decouple==3.8
pydantic==2.3.0
pydantic_core==2.6.3
python-dateutil==2.9.0.post0
httptools==0.6.0
python-multipart==0.0.6
requests==2.31.0
email-validator==2.1.0
textblob==0.18.0
nltk==3.9.1
```

- [ ] **Step 2: Create `backend/dev.env`**

```
APP_NAME=Mood Tracker API
APP_HOST=0.0.0.0
APP_PORT=8000
APP_ENVIRONMENT=development
CONNECTION_STRING=mongodb://localhost:27017/
DATABASE_NAME=mood_tracker_dev
JWT_SECRET=dev_secret_change_in_prod
ENCRYPTION_KEY=dev_encryption_key_change_in_prod
```

- [ ] **Step 3: Create `backend/config/app.py`** (mirrors `recruitment_tracker_api/config/app.py`)

```python
from decouple import config

APP_NAME = config('APP_NAME')
APP_HOST = config('APP_HOST')
APP_PORT = config('APP_PORT')
APP_ENVIRONMENT = config('APP_ENVIRONMENT')
CONNECTION_STRING = config('CONNECTION_STRING')
DATABASE_NAME = config('DATABASE_NAME')
```

- [ ] **Step 4: Create all `__init__.py` files** (empty files for package recognition)

- [ ] **Step 5: Create `backend/main.py`** (mirrors recruitment_tracker_api pattern)

```python
from routes.api import API
from fastapi.middleware.cors import CORSMiddleware

app = API().app

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

- [ ] **Step 6: Commit**

```bash
git add backend/
git commit -m "feat: scaffold backend project structure and configuration"
```

---

### Task 2: Backend — MongoDB Manager

**Files:**
- Create: `backend/modules/mongodb/MongoDBManager.py`

- [ ] **Step 1: Create `MongoDBManager.py`** (singleton pattern, same as recruitment_tracker_api)

```python
"""MongoDB connection manager with singleton pattern."""
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from config.app import CONNECTION_STRING, DATABASE_NAME
import time


class MongoDBManager:
    """Singleton MongoDB connection manager."""

    _instance = None
    _client = None
    _db = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._connect()
        return cls._instance

    @classmethod
    def _connect(cls, max_retries=5, retry_delay=5):
        """Establish MongoDB connection with retry logic."""
        for attempt in range(max_retries):
            try:
                cls._client = MongoClient(
                    CONNECTION_STRING,
                    serverSelectionTimeoutMS=5000
                )
                cls._client.admin.command('ping')
                cls._db = cls._client[DATABASE_NAME]
                print(f"Connected to MongoDB: {DATABASE_NAME}")
                return
            except ConnectionFailure:
                if attempt < max_retries - 1:
                    print(f"MongoDB connection attempt {attempt + 1} failed. Retrying in {retry_delay}s...")
                    time.sleep(retry_delay)
                else:
                    raise

    @classmethod
    def get_db(cls):
        """Get database instance."""
        if cls._db is None:
            cls()
        return cls._db

    @classmethod
    def get_collection(cls, collection_name: str):
        """Get a collection by name."""
        db = cls.get_db()
        return db[collection_name]

    @classmethod
    def ping(cls) -> bool:
        """Check MongoDB connectivity."""
        try:
            if cls._client is None:
                cls()
            cls._client.admin.command('ping')
            return True
        except Exception:
            return False
```

- [ ] **Step 2: Commit**

```bash
git add backend/modules/
git commit -m "feat: add MongoDB connection manager with singleton and retry"
```

---

### Task 3: Backend — Helper Modules (Auth, Encryption, Utilities)

**Files:**
- Create: `backend/app/helpers/JWTHelper.py`
- Create: `backend/app/helpers/PasswordHelper.py`
- Create: `backend/app/helpers/EncryptionHelper.py`
- Create: `backend/app/helpers/RouteAuth.py`
- Create: `backend/app/helpers/HttpResponse.py`
- Create: `backend/app/helpers/PaginationHelper.py`
- Create: `backend/app/helpers/SentimentHelper.py`

- [ ] **Step 1: Create `JWTHelper.py`** — Copy exact pattern from `recruitment_tracker_api/app/helpers/JWTHelper.py`

Same custom HMAC-SHA256 JWT implementation. No changes needed — it reads `JWT_SECRET` from env.

- [ ] **Step 2: Create `PasswordHelper.py`** — Copy exact pattern from `recruitment_tracker_api/app/helpers/PasswordHelper.py`

SHA-256 + random salt hashing. Identical implementation.

- [ ] **Step 3: Create `EncryptionHelper.py`** — Copy exact pattern from `recruitment_tracker_api/app/helpers/EncryptionHelper.py`

HMAC-SHA256 + base64 field encryption. Used to encrypt mood remarks at rest.

- [ ] **Step 4: Create `HttpResponse.py`**

```python
"""Standardized HTTP response helpers."""
from fastapi.responses import JSONResponse


class HttpResponse:
    """Helper for consistent API responses."""

    @staticmethod
    def success(data=None, message="Success", status_code=200):
        return JSONResponse(
            status_code=status_code,
            content={"success": True, "message": message, "data": data}
        )

    @staticmethod
    def error(message="Error", status_code=400):
        return JSONResponse(
            status_code=status_code,
            content={"success": False, "message": message}
        )

    @staticmethod
    def paginated(data, pagination, message="Success"):
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": message,
                "data": {"data": data, "pagination": pagination}
            }
        )
```

- [ ] **Step 5: Create `PaginationHelper.py`**

```python
"""Pagination calculation helper."""
import math


class PaginationHelper:
    """Helper for pagination calculations."""

    @staticmethod
    def get_pagination(page: int, limit: int, total_count: int) -> dict:
        total_pages = math.ceil(total_count / limit) if limit > 0 else 0
        return {
            "page": page,
            "limit": limit,
            "total_count": total_count,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1
        }

    @staticmethod
    def get_skip(page: int, limit: int) -> int:
        return (page - 1) * limit
```

- [ ] **Step 6: Create `SentimentHelper.py`**

```python
"""Sentiment analysis helper using TextBlob."""
from textblob import TextBlob


class SentimentHelper:
    """Analyzes sentiment from mood remarks."""

    @staticmethod
    def analyze(text: str) -> dict:
        """
        Analyze sentiment of a text string.

        Returns:
            dict with sentiment_score (-1.0 to 1.0) and sentiment_label
        """
        if not text or not text.strip():
            return {"sentiment_score": 0.0, "sentiment_label": "Neutral"}

        blob = TextBlob(text)
        score = round(blob.sentiment.polarity, 4)

        if score > 0.1:
            label = "Positive"
        elif score < -0.1:
            label = "Negative"
        else:
            label = "Neutral"

        return {"sentiment_score": score, "sentiment_label": label}
```

- [ ] **Step 7: Create `RouteAuth.py`** — Adapted from recruitment_tracker_api pattern

```python
"""
Route-level authentication helpers.

Two authentication levels:
1. unauth - No authentication required
2. user_auth - Any authenticated user (own data only)
3. admin_auth - Admin role only
"""
from fastapi import Header, HTTPException, Depends, Request, Cookie
from typing import Optional, Annotated
from app.services.UserService import UserService
from app.models.UserModel import UserRole


async def get_authenticated_user(
    request: Request,
    authorization: Annotated[Optional[str], Header()] = None,
    auth_token: Annotated[Optional[str], Cookie(name="auth_token")] = None
):
    """Authenticate any user via cookie or Bearer token."""
    token = None

    if auth_token:
        token = auth_token
    elif request.cookies.get("auth_token"):
        token = request.cookies.get("auth_token")
    elif authorization:
        parts = authorization.split()
        if len(parts) == 2 and parts[0].lower() == "bearer":
            token = parts[1]

    if not token:
        raise HTTPException(
            status_code=401,
            detail={"success": False, "message": "Authentication required."}
        )

    user_service = UserService()
    user = user_service.verify_token(token)

    if not user:
        raise HTTPException(
            status_code=401,
            detail={"success": False, "message": "Invalid or expired token"}
        )

    return user


async def get_admin_user(
    request: Request,
    authorization: Annotated[Optional[str], Header()] = None,
    auth_token: Annotated[Optional[str], Cookie(name="auth_token")] = None
):
    """Authenticate admin users only."""
    user = await get_authenticated_user(request, authorization, auth_token)

    if user.get('role') != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=403,
            detail={"success": False, "message": "Admin access required."}
        )

    return user


user_auth = Depends(get_authenticated_user)
admin_auth = Depends(get_admin_user)
```

- [ ] **Step 8: Commit**

```bash
git add backend/app/helpers/
git commit -m "feat: add auth, encryption, pagination, sentiment, and response helpers"
```

---

### Task 4: Backend — Pydantic Models

**Files:**
- Create: `backend/app/models/UserModel.py`
- Create: `backend/app/models/MoodModel.py`

- [ ] **Step 1: Create `UserModel.py`**

```python
"""User data models."""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from enum import Enum


class UserRole(str, Enum):
    ADMIN = "Admin"
    USER = "User"


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=8, max_length=128)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    user_id: str
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class ChangePassword(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=128)
```

- [ ] **Step 2: Create `MoodModel.py`**

```python
"""Mood entry data models."""
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class MoodScore(int, Enum):
    TERRIBLE = 1
    BAD = 2
    NEUTRAL = 3
    GOOD = 4
    GREAT = 5


MOOD_LABELS = {
    1: "Terrible",
    2: "Bad",
    3: "Neutral",
    4: "Good",
    5: "Great"
}


class MoodCreate(BaseModel):
    mood_score: int = Field(..., ge=1, le=5)
    remark: Optional[str] = Field(None, max_length=500)


class MoodUpdate(BaseModel):
    mood_score: Optional[int] = Field(None, ge=1, le=5)
    remark: Optional[str] = Field(None, max_length=500)
```

- [ ] **Step 3: Commit**

```bash
git add backend/app/models/
git commit -m "feat: add User and Mood Pydantic models with validation"
```

---

### Task 5: Backend — User Service & Controller

**Files:**
- Create: `backend/app/services/UserService.py`
- Create: `backend/app/controllers/UserController.py`

- [ ] **Step 1: Create `UserService.py`**

```python
"""User business logic service."""
from datetime import datetime
from bson import ObjectId
from modules.mongodb.MongoDBManager import MongoDBManager
from app.helpers.JWTHelper import JWTHelper
from app.helpers.PasswordHelper import PasswordHelper


class UserService:
    """Handles user CRUD and authentication."""

    def __init__(self):
        self.collection = MongoDBManager.get_collection('users')

    def register(self, email: str, full_name: str, password: str, role: str = "User") -> dict:
        """Register a new user."""
        if self.collection.find_one({"email": email}):
            return {"success": False, "message": "Email already registered"}

        password_hash = PasswordHelper.hash_password(password)
        now = datetime.utcnow()

        user_doc = {
            "email": email,
            "full_name": full_name,
            "password_hash": password_hash,
            "role": role,
            "is_active": True,
            "created_at": now,
            "updated_at": now,
            "last_login": None
        }

        result = self.collection.insert_one(user_doc)
        return {
            "success": True,
            "message": "User registered successfully",
            "data": {"user_id": str(result.inserted_id)}
        }

    def login(self, email: str, password: str) -> dict:
        """Authenticate user and return JWT token."""
        user = self.collection.find_one({"email": email})

        if not user:
            return {"success": False, "message": "Invalid credentials"}

        if not user.get("is_active", True):
            return {"success": False, "message": "Account is deactivated"}

        if not PasswordHelper.verify_password(password, user["password_hash"]):
            return {"success": False, "message": "Invalid credentials"}

        token = JWTHelper.create_token({
            "user_id": str(user["_id"]),
            "email": user["email"],
            "role": user["role"]
        })

        self.collection.update_one(
            {"_id": user["_id"]},
            {"$set": {"last_login": datetime.utcnow()}}
        )

        return {
            "success": True,
            "message": "Login successful",
            "data": {
                "token": token,
                "user": {
                    "user_id": str(user["_id"]),
                    "email": user["email"],
                    "full_name": user["full_name"],
                    "role": user["role"]
                }
            }
        }

    def verify_token(self, token: str) -> dict:
        """Verify JWT token and return user data."""
        payload = JWTHelper.verify_token(token)
        if not payload:
            return None

        user = self.collection.find_one({"_id": ObjectId(payload["user_id"])})
        if not user or not user.get("is_active", True):
            return None

        return {
            "user_id": str(user["_id"]),
            "email": user["email"],
            "full_name": user["full_name"],
            "role": user["role"]
        }

    def get_all_users(self, page: int = 1, limit: int = 10) -> dict:
        """Get all users (admin only)."""
        skip = (page - 1) * limit
        total = self.collection.count_documents({})
        cursor = self.collection.find({}, {"password_hash": 0}).skip(skip).limit(limit).sort("created_at", -1)

        users = []
        for u in cursor:
            u["_id"] = str(u["_id"])
            users.append(u)

        return {"data": users, "total_count": total}

    def get_user_by_id(self, user_id: str) -> dict:
        """Get a single user."""
        user = self.collection.find_one({"_id": ObjectId(user_id)}, {"password_hash": 0})
        if not user:
            return None
        user["_id"] = str(user["_id"])
        return user

    def update_user(self, user_id: str, updates: dict) -> dict:
        """Update user fields."""
        updates["updated_at"] = datetime.utcnow()
        result = self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": updates}
        )
        return {"success": result.modified_count > 0}

    def delete_user(self, user_id: str) -> dict:
        """Delete a user."""
        result = self.collection.delete_one({"_id": ObjectId(user_id)})
        return {"success": result.deleted_count > 0}

    def change_password(self, user_id: str, current_password: str, new_password: str) -> dict:
        """Change user password."""
        user = self.collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            return {"success": False, "message": "User not found"}

        if not PasswordHelper.verify_password(current_password, user["password_hash"]):
            return {"success": False, "message": "Current password is incorrect"}

        new_hash = PasswordHelper.hash_password(new_password)
        self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"password_hash": new_hash, "updated_at": datetime.utcnow()}}
        )
        return {"success": True, "message": "Password changed successfully"}
```

- [ ] **Step 2: Create `UserController.py`**

```python
"""User controller — thin layer delegating to UserService."""
from app.services.UserService import UserService
from app.models.UserModel import UserCreate, UserLogin, UserUpdate, ChangePassword
from app.helpers.HttpResponse import HttpResponse
from app.helpers.PaginationHelper import PaginationHelper
from fastapi import Depends
from app.helpers.RouteAuth import get_authenticated_user


class UserController:
    def __init__(self):
        self.service = UserService()

    async def register(self, body: UserCreate):
        result = self.service.register(body.email, body.full_name, body.password)
        if not result["success"]:
            return HttpResponse.error(result["message"], 409)
        return HttpResponse.success(result["data"], result["message"], 201)

    async def login(self, body: UserLogin):
        result = self.service.login(body.email, body.password)
        if not result["success"]:
            return HttpResponse.error(result["message"], 401)
        return HttpResponse.success(result["data"], result["message"])

    async def logout(self):
        return HttpResponse.success(message="Logged out successfully")

    async def get_current_user_info(self, current_user=Depends(get_authenticated_user)):
        return HttpResponse.success(current_user)

    async def change_password(self, body: ChangePassword, current_user=Depends(get_authenticated_user)):
        result = self.service.change_password(
            current_user["user_id"], body.current_password, body.new_password
        )
        if not result["success"]:
            return HttpResponse.error(result["message"])
        return HttpResponse.success(message=result["message"])

    async def get_all_users(self, page: int = 1, limit: int = 10):
        result = self.service.get_all_users(page, limit)
        pagination = PaginationHelper.get_pagination(page, limit, result["total_count"])
        return HttpResponse.paginated(result["data"], pagination)

    async def get_user_by_id(self, user_id: str):
        user = self.service.get_user_by_id(user_id)
        if not user:
            return HttpResponse.error("User not found", 404)
        return HttpResponse.success(user)

    async def update_user(self, body: UserUpdate):
        updates = body.model_dump(exclude_unset=True, exclude={"user_id"})
        result = self.service.update_user(body.user_id, updates)
        if not result["success"]:
            return HttpResponse.error("Update failed")
        return HttpResponse.success(message="User updated")

    async def delete_user(self, user_id: str):
        result = self.service.delete_user(user_id)
        if not result["success"]:
            return HttpResponse.error("Delete failed", 404)
        return HttpResponse.success(message="User deleted")
```

- [ ] **Step 3: Commit**

```bash
git add backend/app/services/UserService.py backend/app/controllers/UserController.py
git commit -m "feat: add user service and controller with auth, CRUD, password change"
```

---

### Task 6: Backend — Mood Service & Controller

**Files:**
- Create: `backend/app/services/MoodService.py`
- Create: `backend/app/controllers/MoodController.py`

- [ ] **Step 1: Create `MoodService.py`**

```python
"""Mood entry business logic service."""
from datetime import datetime, date
from bson import ObjectId
from modules.mongodb.MongoDBManager import MongoDBManager
from app.helpers.EncryptionHelper import EncryptionHelper
from app.helpers.SentimentHelper import SentimentHelper
from app.models.MoodModel import MOOD_LABELS


class MoodService:
    """Handles mood CRUD with encryption and sentiment analysis."""

    def __init__(self):
        self.collection = MongoDBManager.get_collection('moods')

    def _serialize(self, doc: dict, decrypt: bool = True) -> dict:
        """Convert MongoDB doc to API-friendly dict."""
        doc["_id"] = str(doc["_id"])
        if decrypt and doc.get("remark"):
            doc["remark"] = EncryptionHelper.decrypt_field(doc["remark"]) or ""
        if doc.get("logged_date"):
            doc["logged_date"] = doc["logged_date"].isoformat() if isinstance(doc["logged_date"], (date, datetime)) else doc["logged_date"]
        if doc.get("created_at"):
            doc["created_at"] = doc["created_at"].isoformat()
        if doc.get("updated_at"):
            doc["updated_at"] = doc["updated_at"].isoformat()
        return doc

    def create_mood(self, user_id: str, mood_score: int, remark: str = None) -> dict:
        """Create a mood entry for today (one per day enforced)."""
        today = date.today()
        today_dt = datetime.combine(today, datetime.min.time())

        existing = self.collection.find_one({
            "user_id": user_id,
            "logged_date": today_dt
        })
        if existing:
            return {"success": False, "message": "Mood already logged for today. Use edit instead."}

        # Analyze sentiment
        sentiment = SentimentHelper.analyze(remark) if remark else {"sentiment_score": 0.0, "sentiment_label": "Neutral"}

        # Encrypt remark
        encrypted_remark = EncryptionHelper.encrypt_field(remark) if remark else None

        now = datetime.utcnow()
        mood_doc = {
            "user_id": user_id,
            "mood_score": mood_score,
            "mood_label": MOOD_LABELS.get(mood_score, "Unknown"),
            "remark": encrypted_remark,
            "sentiment_score": sentiment["sentiment_score"],
            "sentiment_label": sentiment["sentiment_label"],
            "logged_date": today_dt,
            "created_at": now,
            "updated_at": now
        }

        result = self.collection.insert_one(mood_doc)
        mood_doc["_id"] = result.inserted_id
        return {"success": True, "message": "Mood logged", "data": self._serialize(mood_doc)}

    def get_today(self, user_id: str) -> dict:
        """Get today's mood entry."""
        today = date.today()
        today_dt = datetime.combine(today, datetime.min.time())
        doc = self.collection.find_one({"user_id": user_id, "logged_date": today_dt})
        if not doc:
            return None
        return self._serialize(doc)

    def get_mood_by_id(self, mood_id: str, user_id: str) -> dict:
        """Get a single mood entry (must belong to user)."""
        doc = self.collection.find_one({"_id": ObjectId(mood_id), "user_id": user_id})
        if not doc:
            return None
        return self._serialize(doc)

    def get_moods(self, user_id: str, page: int = 1, limit: int = 10,
                  start_date: str = None, end_date: str = None) -> dict:
        """Get paginated mood entries for a user."""
        query = {"user_id": user_id}

        if start_date or end_date:
            date_filter = {}
            if start_date:
                date_filter["$gte"] = datetime.fromisoformat(start_date)
            if end_date:
                date_filter["$lte"] = datetime.fromisoformat(end_date)
            query["logged_date"] = date_filter

        total = self.collection.count_documents(query)
        skip = (page - 1) * limit
        cursor = self.collection.find(query).sort("logged_date", -1).skip(skip).limit(limit)

        moods = [self._serialize(doc) for doc in cursor]
        return {"data": moods, "total_count": total}

    def update_mood(self, mood_id: str, user_id: str, updates: dict) -> dict:
        """Update a mood entry (must belong to user)."""
        existing = self.collection.find_one({"_id": ObjectId(mood_id), "user_id": user_id})
        if not existing:
            return {"success": False, "message": "Mood entry not found"}

        set_fields = {"updated_at": datetime.utcnow()}

        if "mood_score" in updates and updates["mood_score"] is not None:
            set_fields["mood_score"] = updates["mood_score"]
            set_fields["mood_label"] = MOOD_LABELS.get(updates["mood_score"], "Unknown")

        if "remark" in updates:
            remark = updates["remark"]
            if remark:
                set_fields["remark"] = EncryptionHelper.encrypt_field(remark)
                sentiment = SentimentHelper.analyze(remark)
                set_fields["sentiment_score"] = sentiment["sentiment_score"]
                set_fields["sentiment_label"] = sentiment["sentiment_label"]
            else:
                set_fields["remark"] = None
                set_fields["sentiment_score"] = 0.0
                set_fields["sentiment_label"] = "Neutral"

        self.collection.update_one({"_id": ObjectId(mood_id)}, {"$set": set_fields})

        updated = self.collection.find_one({"_id": ObjectId(mood_id)})
        return {"success": True, "data": self._serialize(updated)}

    def delete_mood(self, mood_id: str, user_id: str) -> dict:
        """Delete a mood entry (must belong to user)."""
        result = self.collection.delete_one({"_id": ObjectId(mood_id), "user_id": user_id})
        return {"success": result.deleted_count > 0}
```

- [ ] **Step 2: Create `MoodController.py`**

```python
"""Mood controller — thin layer delegating to MoodService."""
from app.services.MoodService import MoodService
from app.models.MoodModel import MoodCreate, MoodUpdate
from app.helpers.HttpResponse import HttpResponse
from app.helpers.PaginationHelper import PaginationHelper
from fastapi import Depends
from app.helpers.RouteAuth import get_authenticated_user


class MoodController:
    def __init__(self):
        self.service = MoodService()

    async def create_mood(self, body: MoodCreate, current_user=Depends(get_authenticated_user)):
        result = self.service.create_mood(current_user["user_id"], body.mood_score, body.remark)
        if not result["success"]:
            return HttpResponse.error(result["message"], 409)
        return HttpResponse.success(result["data"], result["message"], 201)

    async def get_today(self, current_user=Depends(get_authenticated_user)):
        mood = self.service.get_today(current_user["user_id"])
        if not mood:
            return HttpResponse.error("No mood logged today", 404)
        return HttpResponse.success(mood)

    async def get_mood_by_id(self, mood_id: str, current_user=Depends(get_authenticated_user)):
        mood = self.service.get_mood_by_id(mood_id, current_user["user_id"])
        if not mood:
            return HttpResponse.error("Mood entry not found", 404)
        return HttpResponse.success(mood)

    async def get_moods(self, page: int = 1, limit: int = 10,
                        start_date: str = None, end_date: str = None,
                        current_user=Depends(get_authenticated_user)):
        result = self.service.get_moods(current_user["user_id"], page, limit, start_date, end_date)
        pagination = PaginationHelper.get_pagination(page, limit, result["total_count"])
        return HttpResponse.paginated(result["data"], pagination)

    async def update_mood(self, mood_id: str, body: MoodUpdate,
                          current_user=Depends(get_authenticated_user)):
        updates = body.model_dump(exclude_unset=True)
        result = self.service.update_mood(mood_id, current_user["user_id"], updates)
        if not result["success"]:
            return HttpResponse.error(result["message"], 404)
        return HttpResponse.success(result["data"], "Mood updated")

    async def delete_mood(self, mood_id: str, current_user=Depends(get_authenticated_user)):
        result = self.service.delete_mood(mood_id, current_user["user_id"])
        if not result["success"]:
            return HttpResponse.error("Mood entry not found", 404)
        return HttpResponse.success(message="Mood deleted")
```

- [ ] **Step 3: Commit**

```bash
git add backend/app/services/MoodService.py backend/app/controllers/MoodController.py
git commit -m "feat: add mood service with encryption, sentiment analysis, and controller"
```

---

### Task 7: Backend — Analytics Service & Controller

**Files:**
- Create: `backend/app/services/AnalyticsService.py`
- Create: `backend/app/controllers/AnalyticsController.py`

- [ ] **Step 1: Create `AnalyticsService.py`**

```python
"""Analytics service for mood data aggregation."""
from datetime import datetime, date, timedelta
from collections import Counter
import re
from modules.mongodb.MongoDBManager import MongoDBManager
from app.helpers.EncryptionHelper import EncryptionHelper


class AnalyticsService:
    """Computes mood analytics and aggregations."""

    # Common stop words to exclude from word cloud
    STOP_WORDS = {
        "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
        "have", "has", "had", "do", "does", "did", "will", "would", "could",
        "should", "may", "might", "shall", "can", "need", "dare", "ought",
        "used", "to", "of", "in", "for", "on", "with", "at", "by", "from",
        "as", "into", "through", "during", "before", "after", "above",
        "below", "between", "out", "off", "over", "under", "again",
        "further", "then", "once", "here", "there", "when", "where", "why",
        "how", "all", "each", "every", "both", "few", "more", "most",
        "other", "some", "such", "no", "nor", "not", "only", "own", "same",
        "so", "than", "too", "very", "just", "because", "but", "and", "or",
        "if", "while", "about", "up", "it", "i", "me", "my", "myself",
        "we", "our", "you", "your", "he", "him", "she", "her", "they",
        "them", "what", "which", "who", "this", "that", "these", "those",
        "am", "its", "let", "got", "get", "go", "going", "went", "really",
        "feel", "feeling", "felt", "today", "day", "much", "like", "also",
        "still", "even", "well", "back", "thing", "things", "lot", "bit"
    }

    def __init__(self):
        self.collection = MongoDBManager.get_collection('moods')

    def get_heatmap(self, user_id: str, year: int = None) -> list:
        """
        Get 12-month heatmap data: [{date: "2026-01-15", mood_score: 4}, ...]
        """
        if not year:
            year = date.today().year

        start = datetime(year, 1, 1)
        end = datetime(year, 12, 31, 23, 59, 59)

        cursor = self.collection.find(
            {"user_id": user_id, "logged_date": {"$gte": start, "$lte": end}},
            {"logged_date": 1, "mood_score": 1, "mood_label": 1}
        ).sort("logged_date", 1)

        return [
            {
                "date": doc["logged_date"].strftime("%Y-%m-%d"),
                "mood_score": doc["mood_score"],
                "mood_label": doc.get("mood_label", "")
            }
            for doc in cursor
        ]

    def get_sentiment_trend(self, user_id: str, days: int = 30) -> list:
        """Get sentiment scores over time."""
        start = datetime.combine(date.today() - timedelta(days=days), datetime.min.time())

        cursor = self.collection.find(
            {"user_id": user_id, "logged_date": {"$gte": start}},
            {"logged_date": 1, "sentiment_score": 1, "sentiment_label": 1, "mood_score": 1}
        ).sort("logged_date", 1)

        return [
            {
                "date": doc["logged_date"].strftime("%Y-%m-%d"),
                "sentiment_score": doc.get("sentiment_score", 0),
                "sentiment_label": doc.get("sentiment_label", "Neutral"),
                "mood_score": doc["mood_score"]
            }
            for doc in cursor
        ]

    def get_word_cloud(self, user_id: str, days: int = 90) -> list:
        """
        Get word frequencies from remarks for word cloud.
        Returns: [{"word": "happy", "count": 12}, ...]
        """
        start = datetime.combine(date.today() - timedelta(days=days), datetime.min.time())

        cursor = self.collection.find(
            {"user_id": user_id, "logged_date": {"$gte": start}, "remark": {"$ne": None}},
            {"remark": 1}
        )

        word_counter = Counter()
        for doc in cursor:
            decrypted = EncryptionHelper.decrypt_field(doc["remark"])
            if decrypted:
                words = re.findall(r'[a-zA-Z]{3,}', decrypted.lower())
                filtered = [w for w in words if w not in self.STOP_WORDS]
                word_counter.update(filtered)

        return [
            {"word": word, "count": count}
            for word, count in word_counter.most_common(80)
        ]

    def get_weekly_summary(self, user_id: str, year: int = None, week: int = None) -> dict:
        """Get summary for a specific ISO week."""
        if not year or not week:
            today = date.today()
            year, week, _ = today.isocalendar()

        # Calculate week boundaries
        jan4 = date(year, 1, 4)
        start_of_week1 = jan4 - timedelta(days=jan4.isoweekday() - 1)
        week_start = start_of_week1 + timedelta(weeks=week - 1)
        week_end = week_start + timedelta(days=6)

        start_dt = datetime.combine(week_start, datetime.min.time())
        end_dt = datetime.combine(week_end, datetime.max.time())

        cursor = self.collection.find(
            {"user_id": user_id, "logged_date": {"$gte": start_dt, "$lte": end_dt}}
        ).sort("logged_date", 1)

        entries = list(cursor)

        if not entries:
            return {
                "year": year, "week": week,
                "week_start": week_start.isoformat(),
                "week_end": week_end.isoformat(),
                "total_entries": 0,
                "average_mood": None,
                "average_sentiment": None,
                "most_common_mood": None,
                "days": []
            }

        mood_scores = [e["mood_score"] for e in entries]
        sentiment_scores = [e.get("sentiment_score", 0) for e in entries]
        mood_counter = Counter([e.get("mood_label", "") for e in entries])

        days = []
        for e in entries:
            remark = EncryptionHelper.decrypt_field(e.get("remark")) if e.get("remark") else None
            days.append({
                "date": e["logged_date"].strftime("%Y-%m-%d"),
                "mood_score": e["mood_score"],
                "mood_label": e.get("mood_label", ""),
                "sentiment_score": e.get("sentiment_score", 0),
                "remark_preview": (remark[:80] + "...") if remark and len(remark) > 80 else remark
            })

        return {
            "year": year,
            "week": week,
            "week_start": week_start.isoformat(),
            "week_end": week_end.isoformat(),
            "total_entries": len(entries),
            "average_mood": round(sum(mood_scores) / len(mood_scores), 2),
            "average_sentiment": round(sum(sentiment_scores) / len(sentiment_scores), 4),
            "most_common_mood": mood_counter.most_common(1)[0][0] if mood_counter else None,
            "days": days
        }

    def get_mood_distribution(self, user_id: str, days: int = 90) -> list:
        """Get mood score distribution."""
        start = datetime.combine(date.today() - timedelta(days=days), datetime.min.time())

        pipeline = [
            {"$match": {"user_id": user_id, "logged_date": {"$gte": start}}},
            {"$group": {"_id": "$mood_score", "count": {"$sum": 1}}},
            {"$sort": {"_id": 1}}
        ]

        results = list(self.collection.aggregate(pipeline))

        from app.models.MoodModel import MOOD_LABELS
        return [
            {
                "mood_score": r["_id"],
                "mood_label": MOOD_LABELS.get(r["_id"], "Unknown"),
                "count": r["count"]
            }
            for r in results
        ]

    def get_streak(self, user_id: str) -> dict:
        """Calculate current consecutive logging streak."""
        today = date.today()
        streak = 0
        check_date = today

        while True:
            check_dt = datetime.combine(check_date, datetime.min.time())
            exists = self.collection.find_one({"user_id": user_id, "logged_date": check_dt})
            if exists:
                streak += 1
                check_date -= timedelta(days=1)
            else:
                break

        return {"current_streak": streak, "as_of": today.isoformat()}

    def get_admin_overview(self) -> dict:
        """Platform-wide mood averages (admin only, no PII)."""
        users_col = MongoDBManager.get_collection('users')
        total_users = users_col.count_documents({"is_active": True})
        total_entries = self.collection.count_documents({})

        # Average mood this week
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        week_start_dt = datetime.combine(week_start, datetime.min.time())

        pipeline = [
            {"$match": {"logged_date": {"$gte": week_start_dt}}},
            {"$group": {"_id": None, "avg_mood": {"$avg": "$mood_score"}, "count": {"$sum": 1}}}
        ]
        result = list(self.collection.aggregate(pipeline))

        return {
            "total_users": total_users,
            "total_entries": total_entries,
            "this_week_avg_mood": round(result[0]["avg_mood"], 2) if result else None,
            "this_week_entries": result[0]["count"] if result else 0
        }

    def get_active_users_stats(self) -> list:
        """User engagement stats (admin only, no remarks)."""
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        week_start_dt = datetime.combine(week_start, datetime.min.time())

        pipeline = [
            {"$match": {"logged_date": {"$gte": week_start_dt}}},
            {"$group": {
                "_id": "$user_id",
                "entries_this_week": {"$sum": 1},
                "avg_mood": {"$avg": "$mood_score"}
            }},
            {"$sort": {"entries_this_week": -1}}
        ]

        results = list(self.collection.aggregate(pipeline))

        users_col = MongoDBManager.get_collection('users')
        output = []
        for r in results:
            user = users_col.find_one({"_id": __import__('bson').ObjectId(r["_id"])}, {"full_name": 1, "email": 1})
            output.append({
                "user_id": r["_id"],
                "full_name": user["full_name"] if user else "Unknown",
                "entries_this_week": r["entries_this_week"],
                "avg_mood": round(r["avg_mood"], 2)
            })

        return output
```

- [ ] **Step 2: Create `AnalyticsController.py`**

```python
"""Analytics controller."""
from app.services.AnalyticsService import AnalyticsService
from app.helpers.HttpResponse import HttpResponse
from fastapi import Depends
from app.helpers.RouteAuth import get_authenticated_user


class AnalyticsController:
    def __init__(self):
        self.service = AnalyticsService()

    async def get_heatmap(self, year: int = None, current_user=Depends(get_authenticated_user)):
        data = self.service.get_heatmap(current_user["user_id"], year)
        return HttpResponse.success(data)

    async def get_sentiment_trend(self, days: int = 30, current_user=Depends(get_authenticated_user)):
        data = self.service.get_sentiment_trend(current_user["user_id"], days)
        return HttpResponse.success(data)

    async def get_word_cloud(self, days: int = 90, current_user=Depends(get_authenticated_user)):
        data = self.service.get_word_cloud(current_user["user_id"], days)
        return HttpResponse.success(data)

    async def get_weekly_summary(self, current_user=Depends(get_authenticated_user)):
        data = self.service.get_weekly_summary(current_user["user_id"])
        return HttpResponse.success(data)

    async def get_weekly_summary_by_week(self, year: int, week: int,
                                          current_user=Depends(get_authenticated_user)):
        data = self.service.get_weekly_summary(current_user["user_id"], year, week)
        return HttpResponse.success(data)

    async def get_mood_distribution(self, days: int = 90, current_user=Depends(get_authenticated_user)):
        data = self.service.get_mood_distribution(current_user["user_id"], days)
        return HttpResponse.success(data)

    async def get_streak(self, current_user=Depends(get_authenticated_user)):
        data = self.service.get_streak(current_user["user_id"])
        return HttpResponse.success(data)

    async def get_admin_overview(self):
        data = self.service.get_admin_overview()
        return HttpResponse.success(data)

    async def get_active_users(self):
        data = self.service.get_active_users_stats()
        return HttpResponse.success(data)
```

- [ ] **Step 3: Commit**

```bash
git add backend/app/services/AnalyticsService.py backend/app/controllers/AnalyticsController.py
git commit -m "feat: add analytics service with heatmap, sentiment, word cloud, weekly summary"
```

---

### Task 8: Backend — Health Controller & Route Registration

**Files:**
- Create: `backend/app/controllers/HealthController.py`
- Create: `backend/routes/api.py`

- [ ] **Step 1: Create `HealthController.py`**

```python
"""Health check controller."""
from modules.mongodb.MongoDBManager import MongoDBManager
from app.helpers.HttpResponse import HttpResponse


class HealthController:
    async def healthz(self):
        is_healthy = MongoDBManager.ping()
        if is_healthy:
            return HttpResponse.success(message="Healthy")
        return HttpResponse.error("MongoDB unreachable", 503)
```

- [ ] **Step 2: Create `routes/api.py`** (mirrors recruitment_tracker_api pattern)

```python
"""Main API route registration."""
from fastapi import FastAPI, APIRouter, Depends
from app.controllers.HealthController import HealthController
from app.controllers.UserController import UserController
from app.controllers.MoodController import MoodController
from app.controllers.AnalyticsController import AnalyticsController
from app.helpers.RouteAuth import get_authenticated_user, get_admin_user
from config.app import APP_NAME


class API:
    """
    Main API class with route-based authentication.

    Three levels:
    1. unauth - Public endpoints
    2. user_auth - Any authenticated user (own data)
    3. admin_auth - Admin only
    """

    def __init__(self):
        self.app = FastAPI(
            title="Mood Tracker API",
            description="Daily mood tracking with sentiment analysis",
            version="1.0.0"
        )
        self.setup_routes()

    def setup_routes(self):
        health = HealthController()
        user = UserController()
        mood = MoodController()
        analytics = AnalyticsController()

        # ========== UNAUTH (Public) ==========
        self.app.get('/healthz')(health.healthz)
        self.app.get('/v1')(self.api_version)

        unauth = APIRouter()
        unauth.post('/auth/login')(user.login)
        unauth.post('/auth/register')(user.register)

        # ========== USER AUTH (Any Authenticated User) ==========
        user_router = APIRouter(dependencies=[Depends(get_authenticated_user)])

        # Auth
        user_router.post('/auth/logout')(user.logout)
        user_router.get('/auth/me')(user.get_current_user_info)
        user_router.post('/auth/change-password')(user.change_password)

        # Mood CRUD (own data only — enforced in service layer)
        user_router.get('/moods/get')(mood.get_moods)
        user_router.get('/moods/today')(mood.get_today)
        user_router.get('/moods/get/{mood_id}')(mood.get_mood_by_id)
        user_router.post('/moods/create')(mood.create_mood)
        user_router.patch('/moods/edit/{mood_id}')(mood.update_mood)
        user_router.delete('/moods/{mood_id}')(mood.delete_mood)

        # Analytics (own data only)
        user_router.get('/analytics/heatmap')(analytics.get_heatmap)
        user_router.get('/analytics/sentiment-trend')(analytics.get_sentiment_trend)
        user_router.get('/analytics/word-cloud')(analytics.get_word_cloud)
        user_router.get('/analytics/weekly-summary')(analytics.get_weekly_summary)
        user_router.get('/analytics/weekly-summary/{year}/{week}')(analytics.get_weekly_summary_by_week)
        user_router.get('/analytics/mood-distribution')(analytics.get_mood_distribution)
        user_router.get('/analytics/streak')(analytics.get_streak)

        # ========== ADMIN AUTH (Admin Only) ==========
        admin_router = APIRouter(dependencies=[Depends(get_admin_user)])

        admin_router.get('/users/get')(user.get_all_users)
        admin_router.get('/users/get/{user_id}')(user.get_user_by_id)
        admin_router.patch('/users/edit')(user.update_user)
        admin_router.delete('/users/{user_id}')(user.delete_user)
        admin_router.get('/admin/analytics/overview')(analytics.get_admin_overview)
        admin_router.get('/admin/analytics/active-users')(analytics.get_active_users)

        # Include routers
        self.app.include_router(unauth)
        self.app.include_router(user_router)
        self.app.include_router(admin_router)

    async def api_version(self):
        return {
            "application": APP_NAME,
            "version": "1.0.0",
            "status": "active"
        }
```

- [ ] **Step 3: Commit**

```bash
git add backend/app/controllers/HealthController.py backend/routes/api.py
git commit -m "feat: add health controller and route registration with 3 auth levels"
```

---

### Task 9: Backend — MongoDB Init Script & Dockerfiles

**Files:**
- Create: `backend/init_mongodb.js`
- Create: `backend/Dockerfile`
- Create: `backend/Dockerfile.dev`

- [ ] **Step 1: Create `init_mongodb.js`**

```javascript
// MongoDB initialization for mood_tracker
db = db.getSiblingDB('mood_tracker');

// Users collection
db.createCollection('users');
db.users.createIndex({ "email": 1 }, { unique: true });

// Moods collection
db.createCollection('moods');
db.moods.createIndex({ "user_id": 1, "logged_date": 1 }, { unique: true });
db.moods.createIndex({ "user_id": 1 });
db.moods.createIndex({ "logged_date": 1 });

// Seed admin user (password: admin123 — change in production)
// Salt: fixed for seed only — real users get random salts
db.users.insertOne({
    email: "admin@moodtracker.com",
    full_name: "Admin User",
    password_hash: "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2$SEED_HASH_REPLACE_ME",
    role: "Admin",
    is_active: true,
    created_at: new Date(),
    updated_at: new Date(),
    last_login: null
});

print("mood_tracker database initialized");
```

*Note: The seed admin password hash will need to be generated at first run via a setup script or the register endpoint.*

- [ ] **Step 2: Create `backend/Dockerfile`** (mirrors recruitment_tracker_api)

```dockerfile
FROM python:3.12.7-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ libc6-dev curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download NLTK data for TextBlob
RUN python -c "import nltk; nltk.download('punkt_tab'); nltk.download('averaged_perceptron_tagger_eng')"

COPY . .

RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/healthz || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

- [ ] **Step 3: Create `backend/Dockerfile.dev`**

```dockerfile
FROM python:3.12.7-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ libc6-dev curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN python -c "import nltk; nltk.download('punkt_tab'); nltk.download('averaged_perceptron_tagger_eng')"

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

- [ ] **Step 4: Commit**

```bash
git add backend/init_mongodb.js backend/Dockerfile backend/Dockerfile.dev
git commit -m "feat: add MongoDB init script and production/dev Dockerfiles"
```

---

### Task 10: Root Docker Compose Files

**Files:**
- Create: `docker-compose.yml`
- Create: `docker-compose.dev.yml`

- [ ] **Step 1: Create `docker-compose.yml`** (as defined in Docker Configuration section above)

- [ ] **Step 2: Create `docker-compose.dev.yml`** (as defined in Docker Configuration section above)

- [ ] **Step 3: Commit**

```bash
git add docker-compose.yml docker-compose.dev.yml
git commit -m "feat: add root docker-compose for production and development"
```

---

### Task 11: Frontend — Project Scaffolding

**Files:**
- Create: `frontend/` (via `npx create-next-app@14`)
- Create: `frontend/Dockerfile`
- Create: `frontend/Dockerfile.dev`

- [ ] **Step 1: Initialize Next.js project**

```bash
cd mood_tracker/frontend
npx create-next-app@14 . --typescript --tailwind --eslint --app --src-dir --import-alias "@/*"
```

- [ ] **Step 2: Install dependencies**

```bash
npm install recharts d3-cloud @types/d3-cloud axios js-cookie @types/js-cookie
npx shadcn@latest init
npx shadcn@latest add button card input label textarea badge dialog popover select tabs avatar dropdown-menu separator calendar toast
```

- [ ] **Step 3: Create `frontend/Dockerfile`**

```dockerfile
FROM node:20-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production

RUN addgroup --system --gid 1001 nodejs && adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs
EXPOSE 3000
ENV PORT=3000

CMD ["node", "server.js"]
```

- [ ] **Step 4: Create `frontend/Dockerfile.dev`**

```dockerfile
FROM node:20-alpine

WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev"]
```

- [ ] **Step 5: Update `next.config.js` for standalone output**

```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
}

module.exports = nextConfig
```

- [ ] **Step 6: Commit**

```bash
git add frontend/
git commit -m "feat: scaffold Next.js 14 frontend with Tailwind, shadcn/ui, and Docker"
```

---

### Task 12: Frontend — API Client & Auth Utilities

**Files:**
- Create: `frontend/src/lib/types.ts`
- Create: `frontend/src/lib/api.ts`
- Create: `frontend/src/lib/auth.ts`
- Create: `frontend/src/hooks/useAuth.ts`

- [ ] **Step 1: Create `types.ts`**

```typescript
export interface User {
  user_id: string;
  email: string;
  full_name: string;
  role: "Admin" | "User";
}

export interface MoodEntry {
  _id: string;
  user_id: string;
  mood_score: number;
  mood_label: string;
  remark: string | null;
  sentiment_score: number;
  sentiment_label: string;
  logged_date: string;
  created_at: string;
  updated_at: string;
}

export interface HeatmapEntry {
  date: string;
  mood_score: number;
  mood_label: string;
}

export interface WordCloudEntry {
  word: string;
  count: number;
}

export interface SentimentTrendEntry {
  date: string;
  sentiment_score: number;
  sentiment_label: string;
  mood_score: number;
}

export interface WeeklySummary {
  year: number;
  week: number;
  week_start: string;
  week_end: string;
  total_entries: number;
  average_mood: number | null;
  average_sentiment: number | null;
  most_common_mood: string | null;
  days: {
    date: string;
    mood_score: number;
    mood_label: string;
    sentiment_score: number;
    remark_preview: string | null;
  }[];
}

export interface MoodDistribution {
  mood_score: number;
  mood_label: string;
  count: number;
}

export interface ApiResponse<T = any> {
  success: boolean;
  message: string;
  data: T;
}

export interface PaginatedResponse<T = any> {
  success: boolean;
  message: string;
  data: {
    data: T[];
    pagination: {
      page: number;
      limit: number;
      total_count: number;
      total_pages: number;
      has_next: boolean;
      has_prev: boolean;
    };
  };
}
```

- [ ] **Step 2: Create `api.ts`**

```typescript
import Cookies from "js-cookie";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = Cookies.get("auth_token");

  const res = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
  });

  const data = await res.json();

  if (!res.ok) {
    throw new Error(data.message || data.detail?.message || "Request failed");
  }

  return data;
}

export const api = {
  get: <T>(path: string) => request<T>(path),
  post: <T>(path: string, body?: unknown) =>
    request<T>(path, { method: "POST", body: body ? JSON.stringify(body) : undefined }),
  patch: <T>(path: string, body?: unknown) =>
    request<T>(path, { method: "PATCH", body: body ? JSON.stringify(body) : undefined }),
  delete: <T>(path: string) => request<T>(path, { method: "DELETE" }),
};
```

- [ ] **Step 3: Create `auth.ts`**

```typescript
import Cookies from "js-cookie";
import { api } from "./api";
import type { ApiResponse, User } from "./types";

export async function login(email: string, password: string): Promise<User> {
  const res = await api.post<ApiResponse<{ token: string; user: User }>>("/auth/login", {
    email,
    password,
  });

  if (res.success && res.data.token) {
    Cookies.set("auth_token", res.data.token, { expires: 1, sameSite: "lax" });
    return res.data.user;
  }

  throw new Error(res.message);
}

export async function register(email: string, full_name: string, password: string): Promise<void> {
  const res = await api.post<ApiResponse>("/auth/register", {
    email,
    full_name,
    password,
  });

  if (!res.success) {
    throw new Error(res.message);
  }
}

export function logout(): void {
  Cookies.remove("auth_token");
  window.location.href = "/login";
}

export function getToken(): string | undefined {
  return Cookies.get("auth_token");
}

export function isAuthenticated(): boolean {
  return !!getToken();
}
```

- [ ] **Step 4: Create `useAuth.ts`**

```typescript
"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { isAuthenticated, logout } from "@/lib/auth";
import type { User, ApiResponse } from "@/lib/types";

export function useAuth(requireAuth = true) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    async function check() {
      if (!isAuthenticated()) {
        if (requireAuth) router.replace("/login");
        setLoading(false);
        return;
      }

      try {
        const res = await api.get<ApiResponse<User>>("/auth/me");
        setUser(res.data);
      } catch {
        logout();
      } finally {
        setLoading(false);
      }
    }
    check();
  }, [requireAuth, router]);

  return { user, loading, logout };
}
```

- [ ] **Step 5: Commit**

```bash
git add frontend/src/lib/ frontend/src/hooks/
git commit -m "feat: add API client, auth utilities, TypeScript types, and useAuth hook"
```

---

### Task 13: Frontend — Auth Pages (Login & Register)

**Files:**
- Create: `frontend/src/app/login/page.tsx`
- Create: `frontend/src/app/register/page.tsx`
- Modify: `frontend/src/app/page.tsx`

- [ ] **Step 1: Create login page** — Form with email + password, calls `login()`, redirects to `/dashboard`

- [ ] **Step 2: Create register page** — Form with full name + email + password + confirm, calls `register()`, redirects to `/login`

- [ ] **Step 3: Update root `page.tsx`** — Redirect to `/dashboard` if authenticated, `/login` if not

- [ ] **Step 4: Commit**

```bash
git add frontend/src/app/
git commit -m "feat: add login and register pages with auth flow"
```

---

### Task 14: Frontend — Dashboard Layout & Sidebar

**Files:**
- Create: `frontend/src/components/Sidebar.tsx`
- Create: `frontend/src/components/AuthGuard.tsx`
- Create: `frontend/src/app/dashboard/layout.tsx`

- [ ] **Step 1: Create `AuthGuard.tsx`** — Wraps children, shows loading spinner while checking auth, redirects to `/login` if unauthenticated

- [ ] **Step 2: Create `Sidebar.tsx`** — Navigation links: Dashboard, History, Analytics, Reports, Admin (if admin role). Shows user name, logout button.

- [ ] **Step 3: Create `dashboard/layout.tsx`** — AuthGuard wrapper + Sidebar + main content area

- [ ] **Step 4: Commit**

```bash
git add frontend/src/components/Sidebar.tsx frontend/src/components/AuthGuard.tsx frontend/src/app/dashboard/layout.tsx
git commit -m "feat: add dashboard layout with sidebar and auth guard"
```

---

### Task 15: Frontend — Mood Entry Form & Dashboard Page

**Files:**
- Create: `frontend/src/components/MoodEntryForm.tsx`
- Create: `frontend/src/app/dashboard/page.tsx`
- Create: `frontend/src/hooks/useMood.ts`

- [ ] **Step 1: Create `useMood.ts`** — Hook for mood CRUD operations (create, get today, update)

- [ ] **Step 2: Create `MoodEntryForm.tsx`** — Emoji picker (5 faces for scores 1-5), textarea for remark, submit button. Shows edit mode if mood already logged today.

- [ ] **Step 3: Create `dashboard/page.tsx`** — Today's mood card (form or display), quick stats (streak, week avg), calendar heatmap placeholder

- [ ] **Step 4: Commit**

```bash
git add frontend/src/components/MoodEntryForm.tsx frontend/src/app/dashboard/page.tsx frontend/src/hooks/useMood.ts
git commit -m "feat: add mood entry form and main dashboard page"
```

---

### Task 16: Frontend — Calendar Heatmap Component

**Files:**
- Create: `frontend/src/components/MoodCalendarHeatmap.tsx`
- Modify: `frontend/src/app/dashboard/page.tsx` (integrate heatmap)

- [ ] **Step 1: Create `MoodCalendarHeatmap.tsx`**

GitHub-style contribution graph:
- 12 months of cells, one cell per day
- Color scale: empty (gray) → 1 (red) → 2 (orange) → 3 (yellow) → 4 (lime) → 5 (green)
- Hover popover shows date, mood label, mood score
- Uses SVG rendering with recharts or custom SVG
- Fetches data from `GET /analytics/heatmap?year=YYYY`

- [ ] **Step 2: Integrate into dashboard page**

- [ ] **Step 3: Commit**

```bash
git add frontend/src/components/MoodCalendarHeatmap.tsx frontend/src/app/dashboard/page.tsx
git commit -m "feat: add mood calendar heatmap with color-coded days"
```

---

### Task 17: Frontend — History Page

**Files:**
- Create: `frontend/src/components/MoodHistoryTable.tsx`
- Create: `frontend/src/app/dashboard/history/page.tsx`

- [ ] **Step 1: Create `MoodHistoryTable.tsx`** — Paginated table with columns: Date, Mood (emoji + label), Remark (truncated), Sentiment badge. Date range filter.

- [ ] **Step 2: Create history page** — Uses MoodHistoryTable, connects to `GET /moods/get`

- [ ] **Step 3: Commit**

```bash
git add frontend/src/components/MoodHistoryTable.tsx frontend/src/app/dashboard/history/page.tsx
git commit -m "feat: add mood history page with paginated table and date filter"
```

---

### Task 18: Frontend — Analytics Page (Sentiment Trend + Word Cloud + Distribution)

**Files:**
- Create: `frontend/src/components/SentimentTrendChart.tsx`
- Create: `frontend/src/components/WordCloud.tsx`
- Create: `frontend/src/app/dashboard/analytics/page.tsx`

- [ ] **Step 1: Create `SentimentTrendChart.tsx`** — Line chart (recharts) showing sentiment_score and mood_score over time with dual Y-axis

- [ ] **Step 2: Create `WordCloud.tsx`** — Word cloud using d3-cloud, sized by frequency, colored by sentiment association

- [ ] **Step 3: Create analytics page** — Grid layout: Sentiment trend chart, word cloud, mood distribution donut chart

- [ ] **Step 4: Commit**

```bash
git add frontend/src/components/SentimentTrendChart.tsx frontend/src/components/WordCloud.tsx frontend/src/app/dashboard/analytics/page.tsx
git commit -m "feat: add analytics page with sentiment chart, word cloud, mood distribution"
```

---

### Task 19: Frontend — Weekly Summary Report Page

**Files:**
- Create: `frontend/src/components/WeeklySummaryCard.tsx`
- Create: `frontend/src/app/dashboard/reports/page.tsx`

- [ ] **Step 1: Create `WeeklySummaryCard.tsx`** — Displays: week range, average mood (with emoji), average sentiment, most common mood, day-by-day breakdown with small colored bars, remark previews

- [ ] **Step 2: Create reports page** — Week selector (prev/next arrows), renders WeeklySummaryCard for selected week

- [ ] **Step 3: Commit**

```bash
git add frontend/src/components/WeeklySummaryCard.tsx frontend/src/app/dashboard/reports/page.tsx
git commit -m "feat: add weekly summary report page with week navigation"
```

---

### Task 20: Frontend — Admin Page

**Files:**
- Create: `frontend/src/app/dashboard/admin/page.tsx`

- [ ] **Step 1: Create admin page** — User management table (from `GET /users/get`), toggle active status, platform overview stats from `GET /admin/analytics/overview`. Only visible to Admin role (guarded in Sidebar + page-level check).

- [ ] **Step 2: Commit**

```bash
git add frontend/src/app/dashboard/admin/page.tsx
git commit -m "feat: add admin page with user management and platform stats"
```

---

### Task 21: Integration Testing & Smoke Test

- [ ] **Step 1: Start dev environment**

```bash
cd mood_tracker
docker-compose -f docker-compose.dev.yml up --build
```

- [ ] **Step 2: Test backend health**

```bash
curl http://localhost:8000/healthz
curl http://localhost:8000/v1
```
Expected: `{"success": true, "message": "Healthy"}` and version info

- [ ] **Step 3: Test registration and login**

```bash
# Register
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","full_name":"Test User","password":"testpass123"}'

# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123"}'
```

- [ ] **Step 4: Test mood creation and retrieval**

```bash
TOKEN="<token from login>"

# Create mood
curl -X POST http://localhost:8000/moods/create \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"mood_score": 4, "remark": "Feeling good today, productive morning!"}'

# Get today's mood
curl http://localhost:8000/moods/today -H "Authorization: Bearer $TOKEN"

# Get heatmap
curl http://localhost:8000/analytics/heatmap -H "Authorization: Bearer $TOKEN"
```

- [ ] **Step 5: Verify frontend loads at `http://localhost:3000`** — Login page should render, login flow should work, dashboard should show

- [ ] **Step 6: Commit any fixes**

```bash
git add -A
git commit -m "fix: integration testing fixes"
```

---

### Task 22: Final Polish & Production Readiness

- [ ] **Step 1: Add `.gitignore`** at project root

```
# Python
__pycache__/
*.pyc
*.env
.env
venv/

# Node
node_modules/
.next/
.env.local

# Docker
mongo_data/

# OS
.DS_Store
Thumbs.db
```

- [ ] **Step 2: Add `.env.example`** at project root with all required env vars (no secrets)

- [ ] **Step 3: Verify CORS is restricted** — `main.py` should use `allow_origins=["http://localhost:3000"]` in dev, configured per environment in production

- [ ] **Step 4: Verify all sensitive data is encrypted** — Remarks encrypted at rest, passwords hashed with salt, JWT secret from env

- [ ] **Step 5: Final commit**

```bash
git add -A
git commit -m "feat: finalize mood tracker with security hardening and production config"
```

---

## Security Checklist

| Item | Status | Implementation |
|---|---|---|
| Passwords hashed with salt | Planned | SHA-256 + 64-char random salt (PasswordHelper) |
| JWT signed with HMAC-SHA256 | Planned | Custom JWT with env-based secret (JWTHelper) |
| Remarks encrypted at rest | Planned | HMAC-SHA256 + base64 (EncryptionHelper) |
| Data isolation per user | Planned | All mood queries filter by `user_id` from JWT |
| Role-based access control | Planned | Admin vs User, enforced in RouteAuth + service layer |
| Non-root Docker user | Planned | `appuser:1000` in production Dockerfile |
| CORS restricted | Planned | Explicit origin whitelist, not `*` |
| Input validation | Planned | Pydantic v2 models with field constraints |
| No secrets in code | Planned | All secrets via env vars / python-decouple |
| Health checks | Planned | Docker HEALTHCHECK + `/healthz` endpoint |

---

## Dependency Graph

```
Task 1  → Task 2  → Task 3  → Task 4  → Task 5  → Task 6  → Task 7  → Task 8  → Task 9  → Task 10
                                                                                                  ↓
Task 11 → Task 12 → Task 13 → Task 14 → Task 15 → Task 16 → Task 17 → Task 18 → Task 19 → Task 20
                                                                                                  ↓
                                                                                          Task 21 → Task 22
```

**Parallelizable:** Tasks 1-10 (backend) and Task 11 (frontend scaffold) can start in parallel. Tasks 12+ depend on Task 11 completing. Task 21 requires both backend and frontend complete.
