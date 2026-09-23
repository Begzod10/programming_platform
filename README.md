# Student Programming Platform

An education platform for teaching programming to students, built for **Gennis IT** (deployed at [tech.gennis.uz](https://tech.gennis.uz)). Students take courses, solve interactive coding exercises, submit AI-graded projects, work in AI-formed teams on shared projects, and earn points/ranks/certificates along the way. Teachers manage groups, review student work, and run their own courses.

## What it does

- **Courses & lessons** — structured courses (`Course` → `Lesson`), each lesson pairing video/content with hands-on exercises.
- **Interactive exercises** — drag-and-drop code ordering, matching, fill-in-the-blank, multiple choice, quizzes, and "bug hunt" challenges, each graded locally (no AI round-trip needed for correctness checks).
- **AI-graded projects** — students submit a GitHub repo or a ZIP; an AI review pipeline (`ai_review_service.py`) fetches the real code, grades it against the assignment, and returns a score/feedback.
- **Team projects** — a teacher forms skill-balanced teams (a snake-draft algorithm spreads strong/weak students evenly), an AI planner assigns each member one piece of a shared project sized to their level, students submit and get AI-reviewed per-task, peer-rate each other, and the team lead finalizes into a graded final project.
- **Team games** — live, teacher-run quiz/question games for a whole group.
- **Early learning** — a separate, simplified game track (tap-to-select, drag-to-assemble, shape-tracing, maze navigation) for younger students not yet ready for text-based courses.
- **Gamification** — points (daily/weekly/monthly + lifetime), global/level rankings, achievements, a spendable-points store, streaks, and downloadable course-completion certificates.
- **Teacher tools** — group/flow management, student rosters, work review queues, statistics/activity analytics, and an error log for triaging student-reported issues.
- **External sync** — student/teacher rosters, groups, and identities are synced from Gennis's own back-office systems ("gennis" and "turon"/management-v2) rather than managed as a separate source of truth; local accounts link to those external identities.

## Tech stack

**Backend** — FastAPI + SQLAlchemy 2.0 (async) + PostgreSQL, Alembic migrations, APScheduler for background jobs (points resets, translation backfill, stuck-AI-review sweeps), JWT auth.

**Frontend** — React 19 (Create React App), React Router 7, Axios, `@dnd-kit` for drag-and-drop exercises.

## Project layout

```
backend/
  app/
    api/v1/endpoints/   REST endpoints (courses, exercises, projects, team_project,
                         rankings, store, teacher/*, early_learning, ...)
    models/              SQLAlchemy models (one file per domain area)
    schemas/             Pydantic request/response schemas
    services/             business logic (AI review, points, sync with gennis/turon,
                          team-project planning, ...)
    ws/                  WebSocket managers (realtime team/project updates)
    scheduler.py         background jobs
  alembic/               DB migrations
  scripts/                one-off/maintenance scripts
  tests/                 pytest suite

frontend/
  src/
    views/student/       student-facing pages (courses, projects, team projects,
                          rankings, store, early-learning, ...)
    views/teacher/        teacher-facing pages (groups, review, statistics, ...)
    api/, hooks/          shared API client and hooks
    __tests__/            Jest/RTL tests
```

## Development

**Backend**
```bash
cd backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

**Frontend**
```bash
cd frontend
npm install
npm start
```

**Tests**
```bash
cd backend && pytest
cd frontend && npm test
```

## Deployment

Deploys happen via CI/CD on push to the `server` branch — there is no manual SSH deploy step. Pushing to `server` triggers GitHub Actions to run the test suite and deploy the backend/frontend independently.
