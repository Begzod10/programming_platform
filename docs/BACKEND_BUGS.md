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
- **Regressed, re-fixed (2026-09-11):** `allow_credentials` was correctly `False`, but `allow_origins` had drifted back to a hardcoded `["*"]` — `settings.cors_origins_list` existed in `config.py` but was never actually passed to `CORSMiddleware`. Wired it in; added `backend/tests/test_config.py` covering both the comma-separated and legacy JSON-list `.env` formats; added `backend/.env.example` and a `BACKEND_CORS_ORIGINS` diagnostic line to `deploy-backend.yml` (matching the existing `AI_PROVIDER_CHAIN` check) so a missing production origin surfaces on deploy instead of failing silently in the browser.

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

### ✅ Project like spam / dedup
- **Where:** `app/services/project_service.py`
- **What:** `likes_count += 1` had no per-user dedup — the same other student could like a project unlimited times (only self-likes were blocked).
- **Fix (2026-09-11):** new `ProjectLike` model (`project_likes` table, unique on `(student_id, project_id)` — the real dedup mechanism), migration `cc44dd55ee66`. `like_project` now does an existence pre-check + insert with an `IntegrityError` fallback for a genuine concurrent race (never a 500 on a double-click); added `unlike_project` + `DELETE /project/{id}/like`. `likes_count` is recomputed from `project_likes` on every like/unlike rather than incremented in place, so it can never drift. Tests: `backend/tests/test_project_likes.py`.

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

### ✅ N+1 in lesson progress
- **Where:** `app/api/v1/endpoints/lesson_helpers.py` (the function actually lives here, not `lessons.py` which only imports it — corrected from the original audit's file reference)
- **What:** `_calc_course_progress` called `_calc_lesson_progress` per lesson, and that function issued up to 3 of its own DB queries (`VideoWatch`, `ExerciseSubmission`, `Submission`+`Project`) — ~60 round-trips for a 20-lesson course on every lesson list/detail/submit.
- **Fix (2026-09-11):** `_calc_course_progress` now batch-fetches `VideoWatch`/`ExerciseSubmission`/`Submission`+`Project`/`LessonCompletion` for the WHOLE course in 4 queries (5 total with the lessons query), computing each lesson's progress in Python via new `_calc_lesson_progress_from_batch` — a pure port of the exact same per-lesson math. `_calc_lesson_progress` itself is untouched (still used by single-lesson reads). Measured: 21 queries → 5 for a 20-lesson course. Tests: `backend/tests/test_lesson_progress_batching.py` (correctness against hand-derived values + a query-count assertion).

### ✅ Ranking full-table sort
- **Where:** `app/services/ranking_service.py::calculate_and_update_rankings`
- **What:** Loaded every `Ranking` row into Python and sorted, one `UPDATE` per row. Called on every point change.
- **Fix (2026-09-11):** rewritten to SQL `ROW_NUMBER() OVER (...)` windows (same technique `get_leaderboard` already used for reads), one `UPDATE` per period via a correlated scalar subquery — standard SQL, runs unmodified on Postgres and SQLite, no dialect branch needed. Tests: `backend/tests/test_rankings.py::test_calculate_and_update_rankings_ranks_are_dense_and_ordered`.

### ✅ Points TOCTOU race
- **Where:** `app/services/ranking_service.py` — `add_points_to_student`, `subtract_points_from_student`, `revoke_earned_points`
- **What:** `student.total_points += points` reads → modifies → writes without `SELECT ... FOR UPDATE`. Concurrent AI reviews + lesson completions could lose updates.
- **Fix (2026-09-11):** `.with_for_update()` added to the `SELECT Student`/`SELECT Ranking` queries in all three methods. No-ops on SQLite (documented SQLAlchemy behavior, harmless — SQLite has no concurrent writers to protect against anyway); actually locks on Postgres. The `total_points`/`lifetime_points` invariant (§ below) is unchanged — only the read-then-write is now atomic. Tests: `backend/tests/test_points_reversal.py::test_sequential_award_revoke_award_ends_at_correct_total`. **Not independently verified against real concurrent Postgres connections in this environment** — the fix follows the standard SQLAlchemy pattern and the sequential test proves transactional soundness, but true lock contention under concurrent load wasn't directly observed; worth a sanity check against real Postgres if it matters for a given deploy.
- **Not fixed:** needs `.with_for_update()` on the `SELECT Student`/`SELECT Ranking` queries plus retry/lock-wait timeout policy.

### ✅ No rate limiting on login / upload / AI review
- **Where:** `app/api/v1/endpoints/auth.py`, `courses.py`, `ai_review.py`
- **What:** Login is brute-force-able; upload has no rate cap (combine with the now-fixed size check); AI review costs money per call.
- **Fix:** `app/core/rate_limit.py`'s in-memory sliding-window `rate_limit()` dependency (already applied to `/auth/register`, `/auth/login`, `/auth/sso`) added to `courses.py`'s `upload-image` endpoint (30/min/IP) and `ai_review.py`'s `ai-review` endpoint (5/min/IP — the real anti-farming control stays `count_reviews_today`'s daily quota; this is just a burst throttle). **Known limitation, documented in the module docstring, not fixed here**: per-process (multi-worker deploy multiplies the effective limit by worker count) and resets on every restart — migrating to Redis fixes both, left as a follow-up.

### ✅ Startup blocked on OpenAI reachability
- **Where:** `app/main.py`'s `lifespan()` (previously ~lines 30-66)
- **What:** On every startup, before accepting a single request, the app looped over every active course and called `translate_text_with_ai()` (an OpenAI request) for any title/description not yet cached. A slow/rate-limited/unreachable OpenAI, or a missing `OPENAI_API_KEY`, delayed the whole server's boot — a course-translation backfill should never be able to block the platform from coming up.
- **Fix (2026-09-11):** extracted the loop into `app/services/translation_backfill.py::backfill_course_translations()`, scheduled via `app/scheduler.py` — runs once ~30s after startup (`DateTrigger`) and then daily at 03:00 (`CronTrigger`), off the request path entirely. `lifespan()` now only keeps `translation_store.load(db)` (a local-DB-only read, fast, genuinely needed before serving translated content). Verified: startup completes in milliseconds with `OPENAI_API_KEY` empty.

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

### ✅ `datetime.utcnow()` deprecation throughout
- **Where:** was in 12 files, 39 call sites (`ranking_service.py` ×15, `project_service.py` ×8, plus `lessons.py`, `practice_session.py`, `practice_stats.py`, `practice_words.py`, `projects.py`, `core/security.py`, `achievement_service.py`, `degree_service.py`, `gennis_service.py`, `srs.py`).
- **What:** Returns a naive datetime; deprecated in Python 3.12+, and silently wrong when compared against/assigned to a `DateTime(timezone=True)` column (most of this codebase's timestamp columns).
- **Fix (2026-09-11):** new `app/utils/datetime_utils.py::utcnow()` — the single source of truth, always aware UTC — used everywhere `datetime.utcnow()` was. 5 model files (`project.py`, `team_game.py`, `lesson_file.py`, `lesson_question.py`, `translation_cache.py`) each had their own identical local `utcnow()`/`_utcnow()` helper predating this; consolidated to import from the shared one instead. Checked every call site's target column before choosing aware vs naive: most columns are `DateTime(timezone=True)` and got plain `utcnow()`; a few genuinely naive columns (`UserDictionary`/`PracticeSession`/`QuizSession` in `dictionary.py`, `StudentDegree.earned_at`) got `utcnow().replace(tzinfo=None)` with a comment explaining why. `project_service.py::is_orphaned_submission` had its own naive/aware-mismatch workaround (stripping tzinfo off an aware DB value to compare against a naive `datetime.utcnow()`) — simplified to compare aware-to-aware directly, with a defensive fallback for any still-naive legacy row. Also fixes a latent, previously-masked bug in `core/security.py::create_access_token`: passing a naive `datetime.utcnow()`-derived value as a JWT `exp` claim is only correct if the server's system timezone happens to be UTC; an aware value is correct regardless.
- Full backend test suite (238 tests) passes; verified zero remaining `datetime.utcnow()` call sites via `grep -rn` across `app/`.

### ✅ Duplicate `get_db` definitions
- **Where:** `app/db/session.py:6` vs `app/dependencies.py:13`
- **What:** Two independent session factories; risk of one drifting from the other.
- **Fix (2026-09-11):** kept `app/db/session.py` as canonical (not `app/dependencies.py` — tracing the import chain showed the other direction creates a cycle: `core/security.py` imports `get_db` from `db.session`, and `dependencies.py` imports from `core.security`, so `db.session` importing from `dependencies` would cycle back on itself; `db.session` itself only depends on `db.database`, so `dependencies.py` importing from `db.session` is cycle-free). `app/dependencies.py` now re-exports it instead of re-implementing. All ~30 consumers of `from app.dependencies import get_db` get the same function object transparently; the handful of files already importing from `app.db.session` needed no change.

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
