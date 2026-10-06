# AI Workspace Copilot — Notion Lite

A multi-tenant workspace collaboration API built with **FastAPI**, **SQLAlchemy 2.0 (async)**, and **PostgreSQL** — a lightweight, Notion-style workspace system with JWT auth, refresh-token rotation, roles, and membership management.

## Features

- **Authentication**
  - Register / login with email + password
  - **Argon2id** password hashing (`pwdlib`)
  - JWT access tokens (HS256, configurable expiry) + opaque, DB-backed refresh tokens (7-day expiry, rotated on each login)
- **Workspaces**
  - Create, read, update, and list workspaces
  - Creator is automatically assigned the `owner` role
  - Offset pagination (`page`, `page_size`) and `ILIKE` search by name
- **Membership**
  - Join / leave workspaces
  - List your workspaces and a workspace's members (filtered by `owner` / `member` role)
  - Composite unique constraint `uq_workspace_user` prevents duplicate memberships
- **Fully async stack** — FastAPI + `AsyncSession` + `asyncpg` + async Alembic migrations
- **Pydantic v2** request/response schemas with typed `UUID` path params and `EmailStr`

## Tech Stack

| Layer | Tech |
|---|---|
| Framework | FastAPI |
| ORM | SQLAlchemy 2.0 (async) |
| Database | PostgreSQL (asyncpg) |
| Migrations | Alembic (async) |
| Auth | PyJWT (HS256) + Argon2id |
| Config | pydantic-settings |
| Package mgmt | uv |
| Server | Uvicorn |

## Project Structure

```
.
├── alembic/                  # Async migrations (versions/)
│   ├── env.py                # DB URL sourced from .env settings
│   └── versions/
├── src/
│   └── ai_workspace_copilot_notion_lite/
│       ├── main.py           # FastAPI app + router registration
│       ├── core/
│       │   ├── config.py     # pydantic-settings Settings
│       │   ├── db.py         # async engine, session factory, get_db
│       │   └── security.py   # hashing, JWT, get_user dependency
│       ├── models/           # SQLAlchemy models (users, refresh_token, workspaces, workspace_members)
│       ├── routers/          # auth, workspace, workspace-members endpoints
│       └── schemas/          # Pydantic request/response schemas
├── alembic.ini
├── pyproject.toml
└── requirements.txt
```

## Getting Started

### Prerequisites

- Python **3.12+**
- [uv](https://docs.astral.sh/uv/) (recommended) or pip
- PostgreSQL running locally (or a connection string to any Postgres instance)

### 1. Clone & install

```bash
git clone https://github.com/pushphans/AI-Workspace-Copilot-Notion-Lite.git
cd AI-Workspace-Copilot-Notion-Lite
uv sync
```

### 2. Configure environment

Create a `.env` in the project root (gitignored — never commit it):

```bash
DATABASE_URL=postgresql+asyncpg://postgres:<password>@localhost:5432/workspace_copilot
JWT_SECRET_KEY=<random-secret>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRY_IN_MINUTES=30
REFRESH_TOKEN_EXPIRY_IN_DAYS=7
```

Generate a strong secret, e.g.:

```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

### 3. Run migrations

```bash
uv run alembic upgrade head
```

### 4. Start the server

```bash
uv run uvicorn ai_workspace_copilot_notion_lite.main:app --reload
```

The API is served at `http://localhost:8000`:

- Swagger UI → `http://localhost:8000/docs`
- ReDoc → `http://localhost:8000/redoc`

## API Reference

> All endpoints below marked **🔒** require an `Authorization: Bearer <access_token>` header.

### Auth (`/auth`)

| Method | Endpoint | Description | Status |
|---|---|---|---|
| POST | `/auth/register` | Create an account `{name, email, password}` | 201 |
| POST | `/auth/login` | Login → returns `access_token` + `refresh_token` | 200 |
| POST | `/auth/refresh-token` 🔒 | Exchange refresh token for a new access token | 200 |

### Workspace (`/workspace`)

| Method | Endpoint | Description | Status |
|---|---|---|---|
| POST | `/workspace/create-workspace` 🔒 | Create workspace; creator becomes `owner` | 201 |
| GET | `/workspace/get-workspace/{id}` 🔒 | Fetch a workspace by ID | 200 |
| GET | `/workspace/workspaces` 🔒 | List workspaces (paginated + `search_term`) | 200 |
| PUT | `/workspace/update-workspace/{id}` 🔒 | Update name/description | 200 |

**List query params:** `page` (≥1, default 1), `page_size` (1–100, default 10), `search_term` (optional, `ILIKE` match on name).

### Workspace Members (`/workspace-members`)

| Method | Endpoint | Description | Status |
|---|---|---|---|
| POST | `/workspace-members/join-workspace` 🔒 | Join a workspace as `member` | 201 |
| DELETE | `/workspace-members/leave-workspace/{id}` 🔒 | Leave workspace `{id}` | 200 |
| GET | `/workspace-members/member/workspaces` 🔒 | Workspaces you belong to (with your role) | 200 |
| GET | `/workspace-members/workspace/members` 🔒 | Members of a workspace (`owner=true/false` filter) | 200 |

### Quick example

```bash
# Register
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name":"Pushp","email":"pushp@example.com","password":"secret123"}'

# Login → save access_token
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"pushp@example.com","password":"secret123"}'

# Create a workspace
curl -X POST http://localhost:8000/workspace/create-workspace \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access_token>" \
  -d '{"name":"My Workspace","description":"First one"}'
```

## Database Schema

| Table | Purpose |
|---|---|
| `users` | Accounts (unique `email`, Argon2id `password_hash`) |
| `refresh_token` | One refresh token per user with `expires_at` |
| `workspaces` | Workspace records (`name`, nullable `description`) |
| `workspace_members` | Membership with `workspace_role` enum (`owner` / `member`), unique per `(workspace_id, user_id)` |

Migrations live in `alembic/versions/`; generate new ones with:

```bash
uv run alembic revision --autogenerate -m "description"
```

## Development Notes

- Config is loaded from `.env` at import time — the app fails fast if any required variable is missing.
- `alembic.ini` holds a placeholder `sqlalchemy.url`; the real URL comes from `settings.DATABASE_URL`.
- Workspace membership/role authorization on read/update endpoints is not yet enforced (auth-only) — see roadmap.

## License

[MIT](LICENSE) © 2026 Pushp Hans
