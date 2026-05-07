# Implementation Plan - Production Readiness (PostgreSQL & Vercel)

This plan outlines the transition from a local SQLite setup to a professional production architecture using PostgreSQL and Vercel.

## User Review Required

> [!IMPORTANT]
> **PostgreSQL Migration**: We will switch from `aiosqlite` to `postgresql+asyncpg`. Local testing will require a Postgres instance or we can keep a hybrid config for local development.
> **Environment Variables**: All sensitive data (Bot Token, DB URL) will move to a `.env` file. You must never share this file publicly.
> **Vercel Webhooks**: To run the bot on Vercel, we must switch from "Polling" to "Webhooks". This means the bot will only respond when the API is live on the internet.

## Proposed Changes

### 1. Database & Config
Centralize all settings and switch to Postgres.

#### [MODIFY] [database.py](file:///c:/Users/sunna/.antigravity/Nanomed/database/database.py)
- Use `os.getenv("DATABASE_URL")` with a fallback to SQLite for local development.
- Ensure `async_engine` handles Postgres connection strings.

#### [NEW] [.env](file:///c:/Users/sunna/.antigravity/Nanomed/.env)
- `BOT_TOKEN=865735...`
- `DATABASE_URL=postgresql+asyncpg://user:pass@host/db`
- `WEBAPP_URL=https://your-app.vercel.app`

### 2. Backend (FastAPI on Vercel)
Prepare the backend to run as Vercel Serverless Functions.

#### [NEW] [api/index.py](file:///c:/Users/sunna/.antigravity/Nanomed/api/index.py)
- Special entry point for Vercel that exports the FastAPI `app` from `tma_server.py`.

#### [NEW] [vercel.json](file:///c:/Users/sunna/.antigravity/Nanomed/vercel.json)
- Routing for `/api/*` to the Python backend.
- Routing for `/*` to the React frontend build.

### 3. Frontend Production Build
Configure React to talk to the same domain in production.

#### [MODIFY] [api.js](file:///c:/Users/sunna/.antigravity/Nanomed/frontend/src/utils/api.js)
- Detect if running on Vercel to automatically use relative paths for API calls instead of `localhost:8000`.

## Verification Plan

### Automated Tests
- Test database connection with a mock Postgres URL.
- Verify that environment variables are correctly loaded using `python-dotenv`.

### Manual Verification
- Run the app locally with `.env` and verify it still works.
- Perform a test build of the React app.
