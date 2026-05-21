# Backend bugs — audit & fixes

Audit date: 2026-05-21
Scope: `backend/` — FastAPI + SQLAlchemy 2.x async + asyncpg + alembic.
Status legend: ✅ fixed in commit `1766039`, 🟡 partial / mitigation only, ⬜ not yet fixed.

---

## CRITICAL

### ✅ Registration role escalation
- **Where:** `app/schemas/user.py:29`, `app/services/auth_service.py:65`
- **What:** `UserCreate.role` was caller-supplied — any anonymous client could POST `/api/v1/auth/register` with `"role": "teacher"` and receive a teacher JWT.
- **Fix:** removed `role` from `UserCreate`; `register_new_student` now hard-codes `UserRole.student` (defense in depth).

### ✅ Hardcoded JWT default secret
- **Where:** `app/config.py:12-13`
- **What:** `SECRET_KEY="your-secret-key-here"` shipped as default. If `.env` was ever missing the override (after a force-push, fresh deploy, etc.), every JWT became forgeable.
- **Fix:** `SECRET_KEY` is now `Field(..., min_length=16)` — startup fails loudly if not present. `DEBUG` default flipped to `False`. `ACCESS_TOKEN_EXPIRE_MINUTES` default cut from 1440 → 30 (production `.env` still overrides to 1440 — lower when ready).

### ✅ CORS wildcard + credentials
- **Where:** `app/main.py:64-65`
- **What:** `allow_origins=["*"]` with `allow_credentials=True` is forbidden by the CORS spec and FastAPI's CORSMiddleware silently reflects the request `Origin` — effectively letting any site make credentialed requests.
- **Fix:** explicit origins from `settings.BACKEND_CORS_ORIGINS` (supports both comma-separated and legacy JSON-list `.env` formats).

### ✅ Teacher statistics open to any authenticated user
- **Where:** `app/api/v1/endpoints/teacher/statistics.py:14-16`
- **What:** `Depends(get_current_user)` accepted students; aggregate platform data was leaking.
- **Fix:** `Depends(get_current_instructor)`. Also switched `datetime.utcnow()` → `datetime.now(timezone.utc)`.

### ✅ Exercise CRUD unauthenticated
- **Where:** `app/api/v1/endpoints/exercises.py:24-122`
- **What:** `POST`, `PUT`, `DELETE`, `PATCH /reorder` had no auth dependency. Anonymous users could wipe every exercise.
- **Fix:** `Depends(get_current_teacher)` on all four routes.

### ✅ Two endpoints crashed on every call
- **Where:** `app/api/v1/endpoints/students.py:51, 138`
- **What:**
  - `service.get_projects_by_student(...)` — method didn't exist (actual name `get_all_projects_by_student`).
  - `student.update_level_based_on_points()` — method didn't exist on the model; only a `@validates` hook did.
- **Fix:** corrected method call. Replaced the second call with `student.total_points = student.total_points` (re-triggers the validator that syncs level).

### ✅ `video_watches` and related tables not in alembic chain
- **Where:** `alembic/versions/` (missing); also affected by stale `app/db/base.py` imports.
- **What:** Models for `video_watches`, `lesson_completions`, `exercise_submissions`, `exercises`, `course_certificates`, `quizzes`, `questions`, `student_quiz_results` had no migration coverage. Fresh deploys would 500 with `UndefinedTableError`.
- **Mitigation:** `db/base.py` now explicitly imports `VideoWatch`, `LessonCompletion`, `CourseCertificate`. `init_db` runs `Base.metadata.create_all` (idempotent — only creates missing tables) so fresh deploys bootstrap cleanly without alembic.
- **⬜ Still pending:** the alembic chain has three duplicate "Initial migration" entries and gaps. Proper repair = squash to a single baseline and `alembic stamp` everywhere. Not done because Aziz force-pushes server.

---

## HIGH

### ✅ Public PII leak on student endpoints
- **Where:** `app/api/v1/endpoints/students.py:56-77`
- **What:** `GET /api/v1/student/` and `GET /api/v1/student/{id}` had no auth — anyone could enumerate email, phone, balance, full name.
- **Fix:** added `Depends(get_current_student)` to both.

### ✅ Project comment/file update without ownership check
- **Where:** `app/api/v1/endpoints/projects.py:234-252`, `app/services/project_service.py:147,168`
- **What:** Any authenticated student could overwrite any other student's project comment or file URL by sending the project id.
- **Fix:** service methods now require `student_id` and raise 403 if `project.student_id != student_id`. Endpoints pass `current_student.id`.

### 🟡 Project like spam / dedup
- **Where:** `app/services/project_service.py:177`
- **What:** `likes_count += 1` had no per-user dedup.
- **Mitigation:** self-likes blocked.
- **⬜ Still pending:** real dedup needs a `project_likes(student_id, project_id)` join table with unique constraint + migration.

### ✅ AI re-review point farming + prompt injection
- **Where:** `app/api/v1/endpoints/ai_review.py:17-60`
- **What:** Endpoint had no re-review guard — student could re-call to bump points and burn OpenAI credit. `github_url` was injected verbatim into the LLM prompt.
- **Fix:** rejects re-review when `status=="Approved"`; validates `github_url` against `^https://github\.com/owner/repo` regex. Switched to `datetime.now(timezone.utc)`.

### ✅ Upload-image DoS + path traversal
- **Where:** `app/api/v1/endpoints/courses.py:207-247`
- **What:** `await file.read()` had no size cap — teacher could OOM the server. Old-image cleanup used a relative path with no traversal guard.
- **Fix:** read capped at `settings.MAX_FILE_SIZE` with 413 on overflow. Old-image cleanup resolves to absolute path inside `UPLOAD_DIR` only and uses `unlink()` with `OSError` catch (no more bare `except: pass`).

### ✅ Debug `print()` leaking Authorization headers
- **Where:** `app/api/v1/endpoints/courses.py:107-108, 127`, `app/services/auth_service.py:90`
- **What:** Logged full request headers including bearer tokens on every course detail request; logged usernames on every login attempt (PII + potential password-in-username-field exposure).
- **Fix:** all debug prints removed.

### ✅ StaticFiles + makedirs on relative path
- **Where:** `app/main.py:45-47, 71`
- **What:** `os.makedirs("../uploads")` and `StaticFiles(directory="../uploads")` broke (or mounted the wrong dir) depending on the uvicorn working directory.
- **Fix:** anchored to `settings.UPLOAD_DIR` (absolute path computed from source file location).

### ✅ DB connection error leaked password in logs
- **Where:** `app/db/database.py:26`
- **What:** `print(f" Database connection failed: {e}")` — SQLAlchemy exceptions often embed the full DSN including password.
- **Fix:** `_safe_db_url()` strips the password before logging; the exception itself goes to the proper logger via `logger.exception` and stdout gets only a sanitized one-liner.

### ⬜ N+1 in lesson progress
- **Where:** `app/api/v1/endpoints/lessons.py:113-153`
- **What:** `_calc_course_progress` runs up to 3 DB queries per lesson — 60 round-trips for a 20-lesson course on every lesson list/detail/submit.
- **Not fixed:** invasive rewrite. Batch-fetch `VideoWatch`/`ExerciseSubmission`/`Submission` per course in 3 queries and compute in Python.

### ⬜ Ranking full-table sort
- **Where:** `app/services/ranking_service.py:283`
- **What:** `calculate_and_update_rankings()` loads every row into Python and sorts. Called on every point change.
- **Not fixed:** rewrite to a SQL `ROW_NUMBER() OVER (...)` window function (already used in `get_leaderboard`).

### ⬜ Points TOCTOU race
- **Where:** `app/services/ranking_service.py:150`
- **What:** `student.total_points += points` reads → modifies → writes without `SELECT ... FOR UPDATE`. Concurrent AI reviews + lesson completions lose updates.
- **Not fixed:** needs `.with_for_update()` on the `SELECT Student`/`SELECT Ranking` queries plus retry/lock-wait timeout policy.

### ⬜ No rate limiting on login / upload / AI review
- **Where:** `app/api/v1/endpoints/auth.py:16`, `courses.py:207`, `ai_review.py:17`
- **What:** Login is brute-force-able; upload has no rate cap (combine with the now-fixed size check); AI review costs money per call.
- **Not fixed:** add `slowapi` middleware with per-IP and per-user limits.

---

## MEDIUM

### ✅ `UserRead.achievements` schema mismatch
- **Where:** `app/schemas/user.py:98`
- **What:** Schema field was `achievements`, but `Student` ORM model exposes `student_achievements`. With `from_attributes=True`, Pydantic always returned `[]`.
- **Fix:** added `@model_validator(mode="before")` that maps `student_achievements → achievements`. Note: requires the relationship to be eagerly loaded (`selectinload(Student.student_achievements).selectinload(StudentAchievement.achievement)`) at the call site, else the fallback `[]` still applies.

### ✅ `JWT_SECRET_KEY` dead code
- **Where:** `app/config.py` + `app/core/security.py:45,52`
- **What:** `JWT_SECRET_KEY` was configured but JWTs were actually signed with `SECRET_KEY` — operators rotating the wrong one would be surprised nothing changed.
- **Fix:** dropped `JWT_SECRET_KEY` from `Settings` (config only has `SECRET_KEY` now; `extra="ignore"` keeps existing `.env` entries from erroring).

### ✅ Teacher can delete any student
- **Where:** `app/api/v1/endpoints/teacher/students.py:36`
- **What:** No check that the target student was in a group owned by the requesting teacher.
- **Fix:** `_student_is_in_teachers_group()` guard before `delete_student`.

### ✅ Gennis-synced accounts had literal `"external_auth"` as hash
- **Where:** `app/services/auth_service.py:128`
- **What:** Confusing audit value; bcrypt rejects it so it's safe today, but any future bug that decides to "set the password to the existing hash" would create a real vulnerability.
- **Fix:** unusable bcrypt hash from `os.urandom(32).hex()`.

### ✅ DEBUG=True default + docs always exposed
- **Where:** `app/config.py:11`, `app/main.py:55-56`
- **What:** SQL echo on in prod logs; Swagger/ReDoc always exposed regardless of DEBUG.
- **Fix:** `DEBUG=False` default; `/docs`, `/redoc`, `/openapi.json` gated by `settings.DEBUG`.

### ✅ Missing security headers
- **Where:** `app/main.py`
- **What:** No `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, `Permissions-Policy`.
- **Fix:** `security_headers_middleware` adds all four with sane defaults.

### ✅ Password min length 5
- **Where:** `app/schemas/user.py:42`
- **Fix:** raised to 8.

### ⬜ `datetime.utcnow()` deprecation throughout
- **Where:** `ranking_service.py`, `project_service.py`, `projects.py` (in many places).
- **What:** Returns naive datetime; clashes with `timestamptz` columns and is deprecated in Python 3.12+.
- **Partial fix:** updated in `ai_review.py` and `teacher/statistics.py`. **Pending elsewhere.**

### ⬜ Duplicate `get_db` definitions
- **Where:** `app/db/session.py:6` vs `app/dependencies.py:13`
- **What:** Two independent session factories; risk of one drifting from the other.
- **Not fixed:** consolidate to `app/dependencies.py` and update imports.

### ⬜ `requirements.txt` has only 3 unpinned packages
- **Where:** `backend/requirements.txt`
- **Not fixed:** `pip freeze > requirements.txt` and add `pip-audit` to CI.

---

## LOW / housekeeping

- ✅ `backend/.gitignore` added (second-line defense for `.env`, `debug_output.txt`, `debug_sync.txt`).
- ⬜ `backend/debug_output.txt` and `debug_sync.txt` are git-tracked — `git rm --cached` them and rely on the new ignore.
- ⬜ Stale `.py~` editor backups in `app/api/v1/endpoints/` (`achievements.py~`, `lessons.py~`). Delete or ignore.
- ⬜ Token revocation / blacklist — JWT logout is currently client-only. Pair with the access-token-TTL cut once a revocation store (Redis) exists.

---

## Quick sanity check after deploy

```bash
# Backend imports clean and finds all routes
cd backend && venv/bin/python -c "from app.main import app; print(len(app.routes), 'routes')"

# Confirm CORS, DEBUG, token TTL are what you expect
venv/bin/python -c "from app.config import settings; print(settings.cors_origins_list, settings.DEBUG, settings.ACCESS_TOKEN_EXPIRE_MINUTES)"

# Hit a previously-broken endpoint
curl -s -H "Authorization: Bearer <student_token>" http://host:8062/api/v1/student/me/projects | jq '.[0:1]'
```
