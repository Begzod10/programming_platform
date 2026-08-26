# Project Knowledge Base — Student Platform

Read this file first, cold, before touching anything else in this repo. It exists so a
fresh agent session doesn't have to re-derive architecture and history from scratch by
reading 274 commits and 24 model files one at a time. Everything here was extracted from
the actual code, migrations, and git history as of 2026-08-19 — file:line references are
given wherever they help navigation, but the code is the ground truth if this doc drifts.

Companion docs, already in this directory, catalogued separately because they're audit
artifacts with their own status legend (✅/🟡/⬜) rather than narrative:
- `docs/BACKEND_BUGS.md` — security/correctness audit of the FastAPI backend (2026-05-21)
- `docs/FRONTEND_BUGS.md` — same for the React frontend (2026-05-21)

This file folds their still-relevant findings in by category (see "Known bug patterns"
below) but does not repeat every entry verbatim — read those two directly for the full
list including items marked ⬜ (not yet fixed) that aren't called out here.

---

## 1. What this is

A coding-education platform (Uzbek-first, Russian as second language throughout) built
for Gennis/Turon education centers. Two roles: **student** and **teacher**. Students
enroll in courses made of ordered lessons; lessons carry rich HTML content, code samples,
practice exercises, and (for capstone-style lessons) a project submission that gets
AI-graded. Students earn points for completing lessons/exercises/projects, compete on a
leaderboard, build vocabulary through a spaced-repetition dictionary tool, play a live
Kahoot-style "team game" quiz in class, and spend earned points on a cosmetics store.
Teachers author courses/lessons, review submissions, run team-game sessions, and see
per-student/per-group analytics. Student and teacher identity/rosters sync from **Gennis**
(the school's separate CRM/attendance system) on login — this is not a standalone user
base.

**Stack**
- Backend: FastAPI, SQLAlchemy 2.x (async, `Mapped`/`mapped_column` style), asyncpg,
  Alembic, Pydantic v2 (`pydantic-settings`), python-jose-style JWT via `python-jose`,
  httpx for outbound calls, pytest for tests.
- Frontend: React 19, react-router-dom 7, Redux Toolkit, axios, react-i18next (uz/ru),
  `@dnd-kit` for drag-and-drop exercises, `mermaid` for in-lesson diagrams, `dompurify`
  for sanitizing teacher-authored HTML, Create React App (`react-scripts`) as the build
  tool — not Vite.
- AI providers: OpenAI (primary, `gpt-4.1-mini`), with Gemini and Groq wired as
  fallback chain members but **currently OpenAI-only in practice** (see §7).
- DB: PostgreSQL, database name historically `Student_Platform` locally but the actual
  server DB is `tech_platform` on the shared Postgres host (see `management-v2`'s
  `.env` — `DATABASE_URL` points at `5.129.242.151:5432/tech_platform`).

---

## 2. Repository layout

```
student_platform/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app, CORS, security headers, static mounts
│   │   ├── config.py            # Settings — see §12 for every env var
│   │   ├── dependencies.py      # get_current_user / get_current_student / _teacher / _instructor
│   │   ├── db/                  # session.py, database.py, base.py (model imports), base_class.py
│   │   ├── models/               # 24 files, one SQLAlchemy model group per file — see §3
│   │   ├── schemas/              # Pydantic request/response DTOs
│   │   ├── api/v1/endpoints/     # one router file per domain — see §4
│   │   ├── services/              # business logic, one file per domain — see §5
│   │   ├── core/                 # security.py (JWT/password hashing)
│   │   ├── ws/                   # WebSocket handling (team-game live updates)
│   │   ├── utils/
│   │   ├── static/
│   │   └── tests/                 # a second, thinner test dir exists here too
│   ├── alembic/                  # migration chain — see §3.1 for its known issues
│   ├── scripts/                  # 239 files — course-authoring pipeline + one-off ops scripts, see §6
│   │   ├── course_builder/       # the reusable spec→DB pipeline library
│   │   └── course_specs/         # per-course content specs (data only, no DB code)
│   ├── tests/                    # pytest suite, 14 files — see §11
│   ├── create_template/          # currently empty directory (present but unused)
│   ├── uploads/                  # user-uploaded files, served from UPLOAD_DIR
│   └── frontend/                 # STALE/untracked leftover dir — NOT the real frontend, see below
├── frontend/                     # the REAL React app (top-level, tracked in git)
│   └── src/
│       ├── AppRouter.js          # all routes, 156 lines
│       ├── api/                  # axiosInstance.js (interceptor-based client), search/base.js (useHttp hook)
│       ├── context/               # AuthContext.js
│       ├── views/
│       │   ├── auth/              # login/register
│       │   ├── student/           # courses, projects, store, dictionary, roadmap, dashboard,
│       │   │                      # profile, teamgame, achievements, degrees, stats, rankings
│       │   ├── teacher/           # courses, statistics, activityanalytics, TeacherCertificates,
│       │   │                      # TeacherAchievements, StudentRankings, profile, teamgame,
│       │   │                      # mystudents, teacherreview
│       │   ├── public/, shared/
│       ├── hooks/                 # includes useSessionSocket.js (shared team-game WS hook)
│       ├── store/                 # Redux slices
│       └── utils/sanitize.js      # DOMPurify wrapper — see §10 XSS fix
├── .github/workflows/            # deploy-backend.yml, deploy-frontend.yml, test.yml — see §13
└── docs/                         # this file + BACKEND_BUGS.md + FRONTEND_BUGS.md
```

**`backend/frontend/`** exists on disk (`backend/frontend/src/views`) but is **not
tracked by git** (`git ls-files backend/frontend` returns nothing) — it's a stray/stale
directory, likely a leftover from an earlier restructure. The real, deployed frontend is
the top-level `frontend/` directory; `deploy-frontend.yml` builds from `frontend/` only.
Don't edit anything under `backend/frontend/`.

---

## 3. Database schema

24 model files under `backend/app/models/`, registered in `app/models/__init__.py`
(imported explicitly — SQLAlchemy needs every model imported somewhere before
`Base.metadata.create_all` or Alembic autogenerate will see it; this has bitten the
project before, see §3.1).

### Core identity & structure
- **`Student`** (`user.py`) — despite the name, this is the single user table for BOTH
  roles (`role: student|teacher`). Auth fields (`username`, `email`, `hashed_password`),
  profile, and **two separate point counters** that must never be confused:
  - `total_points` — spendable wallet balance. Goes up on earn, down on store purchase.
  - `lifetime_points` — monotonic career total. Drives `current_level` via a
    `@validates` hook (`sync_level_with_points`, user.py:1933) and is what the
    leaderboard/ranking reads. **Never decreases.** See §8 for the bug this distinction
    exists to prevent.
  - Gennis-sync fields: `phone`, `balance`, `surname`, `gennis_token`, `gennis_id`.
  - Streak fields (`current_streak`, `longest_streak`, `last_activity_date`) bumped by
    `streak_service.bump_streak()` on meaningful activity.
- **`Group`** (`group.py`) — a class/cohort, linked to a `gennis_id`. `teacher_id` FK.
  Many-to-many with `Student` via `student_groups` table.
- **`Category`** (`category.py`) — global course categories, auto-created by teachers
  typing a new name (case-insensitive dedup) — no separate "manage categories" UI.

### Courses & lessons
- **`Course`** (`course.py`) — `instructor_id`, `difficulty_level`, `max_points`,
  optional `prerequisite_course_id` (self-referential — course sequencing),
  `category_id`, `display_order` (teacher-controlled manual sort), `source_lang`
  (drives translation direction), `is_published` (drafts stay unpublished).
- **`Lesson`** (`lesson.py`) — belongs to a course, `order`, `points_reward`. Content
  can be `text_content`/`code_content`/`video_url`/`sections_json` (structured blocks).
  `source_lang` per-lesson (most content authored in `uz`). Optional `task_*` fields
  (title/description/requirements/technologies/deadline_days) turn a lesson into a
  project-submission lesson — see `has_project` property (lesson.py:770): true if either
  `project_id` is set OR `task_title` is non-empty. This property is the gate that
  decides whether lesson completion requires a `Submission` (project path) or all
  exercises answered correctly (exercise path) — see `lessons.py` progress logic.
  - **`LessonVocabulary`** — teacher-defined key terms per lesson (prep-check feature).
  - **`LessonCompletion`** — one row per (student, lesson), unique constraint. This is
    the actual "did they finish it" record; created either on passing AI review
    (project lessons) or on exercise completion (exercise lessons).
- **`LessonFile`** (`lesson_file.py`) — downloadable/attached files per lesson, with
  `code_content` for inline-viewable snippets and `preview_image_url`.
- **`LessonSample`** (`lesson_sample.py`) — the "namuna" (example) shown alongside a
  lesson. `sample_type`: `web` (HTML/CSS/JS live iframe preview), `python`, `sql`, or
  **`code`** (a JSON array of `{filename, language, code}` — a *read-only tabbed source
  viewer*, added specifically because React/TypeScript/anything needing a build step
  can't run in the web/python/sql iframe preview; see feedback memory
  "Namuna Must Teach Lesson" — samples must demonstrate the ACTUAL taught tech, not a
  same-looking substitute in a different language).
- **`LessonFeedback`** — 1-5 star rating + optional comment, one per (student, lesson),
  used by teachers to spot confusing/broken lessons.

### Exercises
- **`Exercise`** (`exercise.py`) — belongs to a lesson. `exercise_type` enum:
  `fill_in_blank`, `drag_and_drop`, `multiple_choice`, `text_input`. Type-specific
  columns (`correct_answers`, `drag_items`/`correct_order`, `options`, `expected_answer`)
  are all stored as JSON-in-Text or comma strings, not normalized tables.
  - **IMPORTANT — dead columns**: `title_ru`, `description_ru`, `hint_ru`,
    `explanation_ru`, `expected_answer_ru` on this model are **dead** — nothing in the
    serving code reads them (exercise.py:366 comment). Live RU translation for exercises
    goes exclusively through the `translation_cache` table via
    `translation_store.py` + `_translate_exercise_dto` in `exercises.py`. Writing a
    translation into one of these columns has zero effect on what a Russian-language
    student sees. Use `scripts/write_ru_translations.py::translate_exercises()` and
    verify with `scripts/check_ru_coverage.py`. A platform-wide audit found 1,371
    exercises missing this because earlier scripts silently skipped it — this is why
    `course_builder` (§6) now makes it structurally hard to skip.
  - **`ExerciseSubmission`** — one row per attempt, `student_answer` (JSON string),
    `is_correct`, `score`, `ai_feedback`, anti-cheat `time_spent_ms`.

### Projects & submissions (capstone/AI-graded work)
- **`Project`** (`project.py`) — a student's submitted work: `github_url` OR
  `project_files` (ZIP), `technologies_used`, `status` (`Draft`/`Submitted`/
  `Approved`/`Rejected`), `points_earned`, `grade`, AI feedback fields
  (`instructor_feedback`, `ai_strengths`, `ai_improvements`, `ai_bugs` — all JSON
  strings). Anti-cheat metrics captured at submission: `time_spent_seconds`,
  `keystroke_count`, `paste_count`, `code_explanation`.
- **`Submission`** (`submission.py`) — links a `Project` to a specific `Lesson`
  (nullable — standalone/portfolio projects have no lesson). Unique constraint on
  `(student_id, lesson_id)` where `lesson_id IS NOT NULL` — a student can only have
  one submission per lesson.

### Points, ranking, achievements
- **`Ranking`** (`ranking.py`) — one row per student, denormalized point/rank totals
  for daily/weekly/monthly/all-time windows plus `projects_completed`,
  `average_grade`. Recalculated by `ranking_service.calculate_and_update_rankings()`
  — **known perf issue**: loads every row into Python and sorts instead of using a SQL
  window function (BACKEND_BUGS.md, unfixed as of the audit).
- **`Achievement`** / **`StudentAchievement`** — badge system, `criteria_type` +
  `criteria_value` define unlock conditions, monitored by
  `achievement_monitoring_service.py`.
- **`Degree`** / **`StudentDegree`** — higher-level "you finished N courses at this
  tier" certificates, separate from per-course `CourseCertificate`.
- **`CourseCertificate`** — one per (student, course), issued on course completion.

### Store / points-spending economy (Phase 1 of a multi-phase design — `store.py`)
Four tables, deliberately minimal for Phase 1 (cosmetics only — themes, fonts, sound
packs). Cases, subscriptions, boosts, and real-value rewards are *intentionally not yet
modeled* — the enums (`StoreItemKind`, `PurchaseStatus`) already have placeholder values
for phases 2-3 so adding them later is a data change, not a migration to a new enum.
- **`StoreItem`** — catalogue row. `asset_ref` JSON holds kind-specific payload (theme
  token map, font URL, sound URLs) so new kinds don't need new columns.
- **`WalletLedgerEntry`** — **append-only**, never updated/deleted. Balance = sum of
  `delta_coins` for a student; `balance_after` is snapshotted per-row so hot reads don't
  need to re-sum. `idempotency_key` (unique) is the anti-double-spend mechanism — a
  retried purchase with the same key fails cleanly on the unique constraint.
  `LedgerReason` enum enforces earn reasons have positive delta, spend reasons negative
  — enforced in `wallet_service.py`, not just convention.
- **`StudentPurchase`** — one row per purchase, price snapshotted at purchase time
  (catalogue price is mutable; a receipt isn't). Status machine:
  `completed` (cosmetics, immediate) or `requested → approved → fulfilled/rejected`
  (Phase 3 real-value items).
- **`StudentInventoryItem`** — what a student owns. `is_equipped` boolean, enforced
  at most one per `kind` per student by the service layer. Unique on
  `(student_id, store_item_id)`.

### Team-game (live quiz) — `team_game.py`
- **`GameSession`** — `game_type` (`team`/`individual`), `status`
  (`pending`/`active`/`completed`), `auto_mode` (self-paced vs teacher-driven),
  `language`, `course_id` (optional — question source), `team_count`.
- **`GameTeam`** / **`GameTeamMember`** — teams within a session; individual-mode
  sessions still use one-member "teams" internally (see §9 for the bug this caused).
- **`GameQuestion`** — `question_kind`: `quiz` (default, 4-option multiple choice) or
  **`bug_hunt`** (added later — `code_snippet` + `bug_line` (1-indexed) + candidate
  line numbers stored in the *same* `options` column as strings, so the existing
  answer-checking pipeline needed zero changes to support the new kind). Bilingual via
  `question_text_ru`/`options_ru` (paired uz/ru row for quiz; a translated prompt field
  for bug_hunt since code stays the single source of truth for option text).
- **`StudentQuestionOrder`** — per-(session, student) shuffled question order for
  auto-mode, unique constraint added after a race condition let a double-click/retry
  500 mid-game (see §9).
- **`GameAnswer`** — one row per (question, student), unique constraint prevents
  double-answering.
- **`GameSessionSnapshot`** (`game_session_snapshot.py`) — **immutable**, written once
  at `complete_session()` time. Exists because every live team-game table cascades on
  delete (deleting a student, editing a question, reshaping a team wipes history) — the
  snapshot is a JSON blob (not normalized) so the teacher's post-game summary, CSV
  export, and parent-bot notification all read one atomic, tamper-proof source instead
  of live tables that could have already mutated.
- **`LessonQuestion`** (`lesson_question.py`) — the reusable **question bank** attached
  to a lesson (separate from `GameQuestion`, which is per-session). `import_questions_
  from_lesson` (in `team_game_questions.py`) copies+reshuffles bank questions into a
  live session's `GameQuestion` rows.

### Dictionary / spaced repetition — `dictionary.py`
- **`UserDictionary`** — one entry per (student, word, lang). Full SM-2 spaced-
  repetition state (`ease_factor`, `interval_days`, `reps`, `lapses`,
  `next_review_at`) — ported from a sibling project (`life_tracker`), see
  `srs.py` for the algorithm. `part_of_speech` is AI-extracted, nullable for legacy
  rows. `lang` distinguishes uz/ru definitions of the same word.
- **`PracticeSession`** — a "Mashq" (practice) session; `progress` JSON is an opaque
  blob the frontend owns the shape of (chunk index, answered word ids, sub-mode state)
  so a student can close the tab and resume.
- **`QuizSession`** / **`QuizAnswer`** — the daily 5-word quiz mode specifically.

### Legacy quiz system — `quiz.py`
`Quiz`/`Question`/`StudentQuizResult` is a **separate, older** quiz system (plain
A/B/C/D questions with `passing_score`/`points_reward`) distinct from both the
dictionary `QuizSession` and the team-game `GameQuestion`. Check which one an endpoint
actually touches before assuming they're related — three different "quiz" concepts
coexist in this codebase.

### Translation cache — `translation_cache.py`
Single shared table for on-demand AI-translated text across lessons/courses/exercises.
Cache key: `(entity_type, entity_id, lang, field_name)`. `source_text_hash` (SHA-256)
lets a read path detect a teacher's edit invalidated the cached translation without an
explicit delete-on-edit code path anywhere. `provider` is always `"groq"` today but
kept for future swaps. This is the mechanism that actually serves lesson/exercise/course
translations at request time — NOT the dead `*_ru` columns described above.

### 3.1 Alembic — known chain issues
Per BACKEND_BUGS.md: the alembic chain has **three duplicate "Initial migration"
entries and gaps**. Several tables (`video_watches`, `lesson_completions`,
`exercise_submissions`, `exercises`, `course_certificates`, `quizzes`, `questions`,
`student_quiz_results`) had **no migration coverage at all** at audit time — a fresh
deploy would 500 with `UndefinedTableError`. Current mitigation (not a real fix):
`app/db/base.py` explicitly imports the affected models, and `init_db.py` runs
`Base.metadata.create_all()` (idempotent, only creates missing tables) so fresh deploys
bootstrap without relying on alembic for those tables. **This was never properly
repaired** — proper fix is squashing to a single baseline + `alembic stamp` on the live
server, deliberately not done because the person operating the server (per the audit
note) force-pushes directly, making an alembic reset risky to coordinate. Before adding
a new migration, check `alembic/versions/` for the actual current head rather than
assuming linear history.

---

## 4. API layer (`backend/app/api/v1/endpoints/`)

All routes mounted under `/api/v1` (`API_V1_PREFIX`). One file per domain, wired
together in `app/api/v1/router.py`. Auth dependencies (`get_current_user`,
`get_current_student`, `get_current_teacher`/`get_current_instructor`) live in
`app/dependencies.py` — **every mutating endpoint must declare one explicitly**; there
have been multiple incidents of routes shipping with no auth dependency at all (see §10).

| File | Domain |
|---|---|
| `auth.py` | register/login/refresh, also the Gennis-login pass-through |
| `students.py`, `teacher/students.py` | student CRUD, teacher's view of their own students |
| `courses.py` | course CRUD, image upload, RU translation serving (`_translate_course_dto`) |
| `lessons.py`, `lesson_helpers.py` | lesson CRUD, **progress calculation** (`_calc_course_progress` — N+1 hotspot, see §10), sections_json hydration |
| `lesson_files.py`, `lesson_vocabulary.py`, `lesson_feedback.py`, `lesson_questions.py` | lesson sub-resources |
| `exercises.py` | exercise CRUD + grading dispatch (`_translate_exercise_dto` lives here too) |
| `projects.py` | project submission, listing, comments/likes |
| `ai_review.py` | manual "review my project" trigger — thin wrapper over `ai_review_service` |
| `groups.py` | group CRUD, Gennis-linked |
| `rankings.py` | leaderboard reads |
| `achievements.py` | achievement listing/award |
| `degrees.py` | degree listing/award |
| `store.py` | catalogue, purchase, inventory, equip |
| `dictionary.py`, `practice.py`, `practice_session.py`, `practice_stats.py`, `practice_words.py` | vocabulary/SRS subsystem |
| `quizzes.py` | the legacy A/B/C/D quiz system |
| `team_game.py`, `team_game_common.py`, `team_game_questions.py`, `team_game_session.py` | live quiz game — session lifecycle, question bank import, WS-adjacent REST endpoints |
| `categories.py` | course category CRUD (mostly auto-create-on-write) |
| `parent.py` | endpoints the Telegram parent bot calls (secret-authenticated, not JWT) |
| `bot_stats.py` | stats endpoints for bot integrations |
| `teacher/statistics.py`, `teacher/activity_analytics.py` | teacher-facing aggregate dashboards |
| `teacher/course_access.py` | which teacher can touch which course |

---

## 5. Services layer (`backend/app/services/`)

Business logic lives here; endpoints should stay thin. Notable ones:

- **`ai_review_service.py`** — the core AI-grading pipeline for project submissions.
  Read it directly (it's short, 312 lines, and heavily commented) rather than
  paraphrasing — but the key structural facts: two callers share it (`ai_review.py`
  manual endpoint, `projects.py` auto-trigger on submit) via a `raise_on_error` flag
  that decides HTTPException-vs-swallow-and-return-dict behavior. See §7 for the
  grading pipeline narrative and §8 for the points-reversal fix it depends on
  (`RankingService.revoke_earned_points`).
- **`grok_service.py`**, **`grok_ai_client.py`**, **`grok_review.py`**,
  **`grok_translation.py`**, **`grok_dictionary.py`** — despite the "grok" naming
  (historical — Groq was the original/primary provider), these now route through
  whatever's in `AI_PROVIDER_CHAIN` (currently OpenAI-only, see §7 and §12).
  `grok_ai_client.py::call_chain()` is the actual multi-provider iterator.
- **`github_repo_service.py`** — fetches a GitHub repo or ZIP snapshot for AI review.
  `capstone` parameter widens the file/byte budget and does directory-aware selection
  for multi-service capstone repos (backend/frontend/bot as separate top-level dirs) —
  see `CAPSTONE_COURSE_IDS = {86, 88, 90, 92}` in `ai_review_service.py:44`.
- **`ranking_service.py`** — `add_points_to_student` (bumps both `total_points` AND
  `lifetime_points`), `subtract_points_from_student` (spend-only — wallet purchases,
  NEVER use to reverse an award), `revoke_earned_points` (the correct inverse of
  `add_points_to_student` — added specifically to fix the bug in §8). Also computes
  leaderboard rankings (known perf issue — full-table Python sort, see §3 Ranking
  model note).
- **`wallet_service.py`** — enforces the ledger's earn/spend sign invariant, equip
  exclusivity (one equipped item per kind), idempotency-key dedup on purchase.
- **`exercise_service.py`** — per-type grading. `check_answer_locally` handles
  fill_in_blank/drag_and_drop/multiple_choice without an AI call; checks
  `translation_store` for a language-appropriate correct answer before falling back to
  the raw column (see §8 — this is where the RU grading fix landed for both
  drag_and_drop and fill_in_blank).
- **`gennis_service.py`** — student/teacher identity sync from the Gennis CRM. Read
  §9 in full before touching this file; it has been the single most bug-prone service
  in the project's history (id-remapping, add-only sync drift, stale rosters).
- **`streak_service.py`** — daily activity streak bump, called from exercise
  submission, lesson completion, project submission, and dictionary quiz completion.
- **`achievement_service.py`**, **`achievement_monitoring_service.py`** — badge
  criteria evaluation and awarding.
- **`translation_service.py`**, **`translation_store.py`** — the AI-translation
  cache read/write path described in §3 (`translation_cache` table).
- **`srs.py`** — SM-2 spaced-repetition scheduling algorithm for the dictionary.
- **`course_service.py`**, **`lesson_service.py`**, **`student_service.py`**,
  **`degree_service.py`**, **`quiz_service.py`**, **`dictionary_service.py`**,
  **`group_service.py`**, **`project_service.py`** — standard CRUD/orchestration
  per domain; `project_service.py` also owns the like/comment/resubmission logic
  (and the resubmission points-reversal bug fixed in §8).
- **`lesson_context_resolver.py`** — resolves the lesson/course context for a project
  so the AI grader gets a real rubric instead of falling back to a generic persona
  (see §7).
- **`points_scale.py`** — tiny helper, team-game question points scaled 0-10 by
  course difficulty.
- **`storage_service.py`** — currently empty (0 lines) — placeholder, not yet used.

---

## 6. Course/lesson authoring pipeline — how content actually gets built

This is the subsystem the user specifically wants documented in depth. It lives under
`backend/scripts/` and is genuinely a differentiator: courses are **not** authored
through an admin UI form-by-form — they're written as Python "spec" modules and run
through a shared pipeline that guarantees every required piece (RU translation, exercise
integrity, image checks) actually happens, because skipping a step used to be silent and
cheap.

### 6.1 Why it exists (read `course_builder/__init__.py:1-18` for the full rationale)
Every earlier course-building script (`seed_python_algorithms.py`,
`seed_sql_database_design.py`, ...) mixed two unrelated things in one 2,000+ line file:
the DB-writing mechanism and the course's actual content. Copy-pasting the mechanism for
each new course made it easy to silently skip a step — **a platform-wide audit found
1,371 exercises missing RU translation** because of exactly this. `course_builder/` is
the mechanism, extracted once; a "spec" module is pure data (dicts/lists, zero DB code).

### 6.2 The three-file library (`backend/scripts/course_builder/`)
- **`spec_loader.py`** (23 lines) — `load_spec(path_or_name)` imports a spec module
  either by dotted name or file path; `require(module, name)` fails loudly if a
  required top-level attribute (`COURSE`, `LESSONS`) is missing.
- **`db_helpers.py`** (296 lines) — the actual DB-writing functions (create course,
  create lessons, create exercises, write samples, set submission tasks).
- **`translations.py`** (157 lines) — RU translation helpers, including
  `derive_correct_order_ru()` (auto-derives a drag-and-drop's RU correct-order from
  the UZ order + item translations, so an author never hand-maps indices — a source of
  past bugs) and `is_natural_language_answer()` (heuristic to warn if a fill-in-blank/
  text-input answer looks like it needs RU translation but doesn't have one, or vice
  versa — a code/SQL/API token like `print` should NOT be "translated").

### 6.3 Spec module contract (full detail in `course_builder/__init__.py` docstring)
A spec file (e.g. `course_specs/sql_advanced_queries.py`) defines two top-level names:

- **`COURSE: dict`** — required: `title`, `description`, `instructor_id`,
  `difficulty_level`, `duration_weeks`, `max_points`. Optional: `category_id`,
  `prerequisite_course_id`, `display_order`, `image_url`, `thumbnail_url`,
  `is_active` (default True), `is_published` (**default False** — courses stay
  unpublished until a human reviews them), `title_ru`, `description_ru`.
  **`title_ru`/`description_ru` are NOT actually optional** — `_translate_course_dto()`
  in `courses.py` reads them at request time exactly like a lesson's RU translation. An
  earlier build shipped 6 courses missing these on the wrong assumption nothing read
  them; `check_ru_coverage.py` now flags a missing `course_ru` too.

- **`LESSONS: list[dict]`** — one dict per lesson, in order. Each carries `order`,
  `title`(+`_ru`), `points_reward`, `text_content`(+`_ru`), `code_content`(+`_ru`),
  `code_language`, `video_url`, an optional `task` dict (only for project/capstone
  lessons: `task_title`, `task_description`, `task_requirements`,
  `task_technologies`, `task_deadline_days` — the `_ru` siblings exist for the first
  three but not the last two), an optional `sample` dict (namuna — see §3 LessonSample),
  and an `exercises: list[dict]`.

- **Exercise dict** — `title`/`description`(+`_ru`), `exercise_type`, and
  type-specific fields matching the `Exercise` model (§3), with strict rules on what
  gets an `_ru` sibling and what doesn't:
  - `multiple_choice`: `options`/`options_ru` must be same length/order;
    `correct_answers` (letter, e.g. `"A"` or `"A,C"`) indexes the **untranslated**
    options and is never re-derived from `options_ru`.
  - `fill_in_blank`/`text_input`: `correct_answers_ru` should ONLY be set when the
    answer is genuine natural language, never a code/SQL/API token — checked by
    `is_natural_language_answer()`.
  - `drag_and_drop`: `drag_items`/`drag_items_ru` same length/order; `correct_order`
    must be a permutation of `drag_items` (checked by `check_exercise_integrity.py`);
    `correct_order_ru` is **never hand-written** — derived automatically by
    `derive_correct_order_ru()`.

### 6.4 Diagrams (Mermaid) — a documented near-miss
Not a schema field at all — a plain HTML authoring convention. The frontend generically
auto-detects any `<pre class="mermaid">` block in rendered lesson HTML and runs
mermaid.js on it (`StudentLessonPage.js`), and `LessonContentBlocks.js` renders text
sections via `dangerouslySetInnerHTML` (post-sanitization), so it "just works" with zero
backend/schema changes — but that also means **nothing catches a lesson with zero
diagrams**, because there's no field to be missing. Course 109 shipped with ZERO
diagrams across all 14 lessons for exactly this reason, caught only when a user compared
it to an older course. Rule going forward, per the docstring: for EVERY lesson, ask
whether a diagram would clarify the content (schema/ER shape, decomposition,
relationship, multi-step flow, before/after) — author it directly in `text_content`
using the exact `<h3>...</h3><pre class="mermaid">flowchart TB...</pre><p>caption</p>`
markup, grounded in that lesson's own real content (never an invented generic example).
Skipping a lesson that's genuinely not diagram-worthy (pure recap) is fine —
`check_diagram_coverage.py` reports the ratio but never fails the build; it's
informational so the decision is visible, not enforced blindly.

RU translation rule for diagrams (confirmed against course 98's hand-built original):
table/column/schema/code identifiers inside node/edge labels (`courses`,
`lessons.course_id`, `student_courses`, `id PK`, `FK`) stay **exactly as-is** in both
languages. Only natural-language edge-label text and the caption `<p>` get translated.

### 6.5 Pipeline order (each script independently re-runnable)
```
check_course_images.py --set <id> --image <url> --thumbnail <url>
create_course.py <spec_module>
create_lessons.py <spec_module>
create_exercises.py <spec_module>
check_exercise_integrity.py <course_id>       # fix before translating
translate_exercises_ru.py <spec_module>
create_samples.py <spec_module>
set_submission_tasks.py <spec_module>         # BEFORE translate_lessons_ru — that
                                               # script reads lesson.task_* off the ORM
                                               # row to build its section_translations map
translate_lessons_ru.py <spec_module>
check_ru_coverage.py <course_id>              # must pass clean
check_diagram_coverage.py <course_id>         # informational only, never blocks
check_course_images.py <course_id>            # must pass clean
```
Or run `build_course.py <spec_module>` to do the whole sequence in one process (calls
the same underlying functions — not a separate implementation).

### 6.6 Other authoring/ops scripts of note (`backend/scripts/`, 239 files total)
- `check_ru_coverage.py`, `check_exercise_integrity.py`, `check_course_images.py`,
  `check_diagram_coverage.py`, `check_schema_drift.py`, `check_duplicate.py`,
  `check_achievements.py`, `check_promote_teacher.py` — the audit/verification
  scripts referenced above.
- `write_ru_translations.py` — the actual writer for exercise RU translations into
  `translation_cache` (the live-serving mechanism — not the dead `*_ru` columns).
- `sync_turon_teacher_salary.py`-style one-off ops scripts and 171 course-authoring
  scripts (RU lesson content, capstone tracks, seeds for Node/Django/TypeScript/
  testing/SQL courses) were bulk-committed in `34d5214` — they were previously
  untracked despite `backend/scripts/` being a tracked directory.
- `course_specs/` currently holds ~13 real spec files (`ai_api_integration.py`,
  `github_actions_cicd.py`, `git_internals_workflow.py`, `nextjs_ssr.py`,
  `rag_vector_search.py`, `react_performance.py`, `sql_advanced_queries.py`,
  `sql_orm_migrations.py`, `team_collaboration_workflow.py`,
  `telegram_bot_advanced.py`, `telegram_bot_pyrogram.py`,
  `telethon_userbot_mtproto.py`) plus `_example.py` (a documented template, explicitly
  marked "NOT meant to be seeded for real — run this only with `--dry-run`").
  Copy `_example.py` as the starting point for a new course spec (drop the leading
  underscore for real files).
- **Security note on two of these files**: `ru_node_lesson_11.py` and
  `seed_nodejs_express.py` contain a literal `const JWT_SECRET = 'mening-maxfiy-
  kalitim-123'` — this trips secret scanners but is **intentional teaching material**
  demonstrating the anti-pattern, annotated in the lesson text itself as "❌ записан в
  коде!" / "❌ kodga yozilgan!" (❌ written in the code!). Not a real credential.

---

## 7. AI review / grading pipeline

`ai_review_service.py::run_ai_review_for_project()` is the single entry point, called
from two places (manual button `POST /ai/{project_id}/ai-review`, and
auto-trigger on `POST /project/{project_id}/submit`) via a shared function with a
`raise_on_error` flag controlling whether failures raise `HTTPException` (manual — user
sees a clean error) or return `{success: False, reason, http_status}` (auto-trigger — a
flaky AI provider must never block lesson submission itself).

**Flow**: validate AI is enabled (`MAX_AI_REVIEWS_PER_DAY > 0`) → block re-review if
`project.reviewed_at` is already set (not just `status == "Approved"` — this closes a
bypass via resubmission cycles that changed status but left the original review
timestamp) → validate GitHub URL format or presence of ZIP → enforce daily quota
(`count_reviews_today`, backstop against both manual and auto-trigger abuse) → resolve
lesson/course context via `lesson_context_resolver` (**without this the AI grader uses
a generic persona and an HTML/CSS submission gets reviewed against an invented
Python/Flask rubric** — standalone projects with no `Submission` row fall back to a
generic "dasturlash o'qituvchisi" persona) → fetch a real code snapshot (GitHub API or
ZIP; capstone courses `{86, 88, 90, 92}` get a wider file/byte budget and
directory-aware file selection for multi-service repos) → refuse the AI call entirely
if the snapshot is empty/unreadable (no point spending tokens to hallucinate) → call
`analyze_project_with_grok()` → on provider failure, **do not write to DB** — leave
`status="Submitted"` for manual teacher review, with a friendly rate-limit-specific
message if detected → clamp returned points to `[0, 100]`, defaulting to 0 (never 60)
on a malformed response so a broken AI response can never grant free points → reverse
any previously-earned points via `revoke_earned_points` (only if the project was
previously `Approved` — reversing a Rejected project's points would deduct points never
actually granted) → award new points only if `new_points >= 75` (this threshold is also
what flips `status` to `Approved` vs `Rejected`) → on passing, also create the
`LessonCompletion` row (the actual unlock gate for the next lesson) and award the
lesson's own `points_reward` on top of the project points, but only if a
`LessonCompletion` doesn't already exist for that (student, lesson) pair.

### 7.1 The production outage (`b724929`, 2026-07-31) — read this before touching AI config
Four compounding issues fixed in one commit:
1. `submitted_at` was **never being written** on lesson/ZIP project submissions —
   broke teacher activity views and ranking windows for **~39% of projects**.
2. `AI_PROVIDER_CHAIN` forced to `openai`-only. Gemini had no key configured (dead
   fallback link); Groq's free-tier rate limit was surfacing as user-facing
   "AI unavailable" failures under real classroom load.
3. `submit_project()` was marking a project `"Rejected"` on ANY AI failure, including
   transient ones (provider down, rate-limited, daily cap hit) — only genuine content
   problems (bad URL, unreadable repo) should reject; transient failures now leave
   `status="Submitted"` so the student/teacher can retry instead of the submission
   being permanently mislabeled as a real rejection.
4. `LessonContentBlocks.js` had Russian-only strings in several spots, leaking through
   regardless of the student's selected language.

If AI review appears broken again in production, check (in this order): is
`OPENAI_API_KEY` actually set on the server `.env` (not just locally)? Is
`AI_PROVIDER_CHAIN` still `openai` (someone re-adding `groq`/`gemini` without a
configured key reintroduces the exact outage this commit fixed)? Is `submitted_at`
still being set on submission (regression here silently breaks downstream analytics,
not the review itself, so it's easy to miss). The deploy workflow (`deploy-backend.yml`)
now runs a base64-encoded diagnostic Python one-liner on every deploy specifically to
verify the OpenAI chain reaches prod correctly — see §13.

### 7.2 Self-contradictory grading guard (`54845dc`)
The AI review response is validated against itself — e.g. a review that says "Approved"
in prose but returns points below the passing threshold (or vice versa) is caught rather
than trusted blindly. Check `grok_review.py`/`grok_ai_client.py` for the current
validation logic if extending the grading prompt.

---

## 8. Points / leaderboard economy — the reversal-inflation bug class

**The invariant to protect**: `Student.total_points` (spendable wallet) and
`Student.lifetime_points` (career total, drives level + leaderboard) are separate
counters. `RankingService.add_points_to_student()` bumps **both** on any award.
`subtract_points_from_student()` is **spend-only** (store purchases) and must reduce
**only** `total_points`.

**The bug (`211cd33`)**: three call sites — project re-review, achievement revocation,
project resubmission/manual re-grade — were using `subtract_points_from_student` to
*reverse* a previously-earned award. Since the original award bumped both counters,
using the spend-only subtract to reverse it left `lifetime_points` (and the leaderboard,
which mirrors it) **permanently inflated by the reversed amount on every reversal
cycle** — a student re-reviewed multiple times would accumulate leaderboard rank they
never actually earned.

**The fix**: `RankingService.revoke_earned_points()` is the proper inverse of
`add_points_to_student` — decrements both counters symmetrically. `ai_review_service`,
`achievement_service`, and `project_service` were switched to use it wherever an award
is being reversed (not spent).

**A second, independent bug fixed in the same commit**: `project_service.create_project`'s
resubmission path reversed `old_points` unconditionally, including for a
previously-**Rejected** project whose `points_earned` was stored for display purposes
but never actually credited to the wallet — silently draining points a student never
received. Fixed by gating the reversal on `old_status == "Approved"`, matching the
pattern already used in `ai_review_service`.

**Rule for any future code that reverses an award**: check whether the original grant
went through `add_points_to_student` (→ reverse with `revoke_earned_points`) or was a
pure spend (→ `subtract_points_from_student` is correct). Never assume; check the
award's origin. `backend/tests/test_points_reversal.py` covers both historical bugs plus
a guard-rail test that `subtract_points_from_student` stays spend-only — extend this
test file rather than writing a parallel one if you touch this area again.

Same commit also extended `exercise_service.check_answer_locally`'s `fill_in_blank`
grading to check `translation_store` for an RU correct answer before falling back to
the raw column (mirroring an earlier `drag_and_drop` fix) — a natural-language
fill-in-the-blank answer previously had no language-aware grading path at all, so a
correct Russian answer could be marked wrong.

---

## 9. Team-game (live quiz) subsystem

A Kahoot-style live quiz: a teacher creates a `GameSession` (team or individual mode),
imports questions from a lesson's `LessonQuestion` bank (or hand-authors bug-hunt
questions), and runs it either **manually** (advances questions themselves, live WS
push) or in **auto-mode** (`StudentQuestionOrder` gives each student their own shuffled
question order, self-paced with a timer). `GameAnswer` scores per-question with
`points_scale.py` scaling points 0-10 by course difficulty. On completion, a
`GameSessionSnapshot` freezes the result (see §3) and the parent Telegram bot is
notified (fire-and-forget, see §12 `PARENT_BOT_URL`).

### 9.1 The big security/correctness pass (`9284218`)
A security review found the feature was **fully unauthenticated** on list/get session
endpoints (leaked every session's full student roster to anyone with no login at all),
the WebSocket accepted connections with **no membership check**, and auto-mode answers
had **no active-session guard** (a student could keep scoring after the teacher marked
the session completed). All closed in this commit, alongside CSV formula-injection
sanitization (exported CSVs could carry a formula payload opened in Excel), cross-teacher
question-bank exfiltration via the import endpoint, and switching an internal-secret
comparison to constant-time (timing-attack hardening).

Same commit fixed a real **race condition**: `StudentQuestionOrder` was missing its
unique constraint, so a double-click/retry on session start could 500 mid-game — fixed
with the `uq_student_question_order` constraint now on the model (§3). Also fixed a
silent network-failure bug in the manual quiz submit path, a permanently-broken
"Вопросы (0)" teacher badge, and extracted the drifted duplicate WS-handling logic
between student/teacher pages into a single shared `src/hooks/useSessionSocket.js`.

### 9.2 Individual-mode team bug (`424e822`)
Individual game sessions were incorrectly splitting students into multiple teams
internally (a leftover from the team-mode code path being reused without a branch for
`game_type == "individual"`) — fixed by not creating placeholder teams for individual
sessions (`ca49f63` is the related "don't create placeholder teams" follow-up).

### 9.3 Bug-hunt question kind (`d887934`, `e1859a8`, `16bf2b0`)
Added as a second `question_kind` alongside the original `quiz` kind, deliberately
reusing the existing `options`/`correct_option` pipeline (candidate line numbers as
strings) rather than adding new columns/branches — see the model comment in
`team_game.py` (§3). `import_questions_from_lesson` filters by kind so a teacher can
mix quiz and bug-hunt questions when building a session from a lesson's bank.

### 9.4 Auto-mode edge cases fixed over time
- `2ef962c` — student stuck on a quiz question after a 409 (already-answered) response
  wasn't handled client-side, leaving the UI frozen instead of advancing.
- `d80ea34` — newly-added questions weren't synced into already-generated auto-mode
  orders (a teacher adding a question mid-session wouldn't reach students who'd already
  had their order generated).
- `81888bf` — auto-mode quiz replay bug + missing RU answer-option translations.
- `9a4a54e` — auto quiz question index wasn't persisted in `sessionStorage`, so a page
  refresh lost progress.
- `7849e79` — auto-advance-after-answering had a race between the advance timer and the
  manual-advance path; fixed by splitting into separate refs so they can't cancel each
  other.

---

## 10. Gennis integration — identity linking

**This has been the single most bug-prone subsystem historically.** Read
`gennis_service.py` in full (it's well-commented, ~300 lines) before making any change
here — the patterns below are not obvious from a partial read.

### 10.1 The core id-mapping trap (documented directly in code)
From `apps/backend/app/api/v1/integrations/student_platform.py:120-135` (the gennis-v2
side of the integration, in the sibling `gennis-v2` repo, but the trap applies
symmetrically here): **old Gennis did NOT send the same id for both roles.**
- For **teachers**, the payload's `id` is the Gennis **user** id.
- For **students**, the payload's `id` must be the Gennis **student** id (a different
  number from the user id for the same underlying account).

Sending the user id where the student id is expected makes `student_platform`'s
username lookup (`gennis_{id}`) miss the existing account and **silently create a
second, empty one** — stranding the real account's entire history. This exact bug
happened to a real student, Afruzbek Abdujjaborov, who ended up with two accounts:
`gennis_13807` (the real one, with all his points/projects/submissions) and
`gennis_14084` (an empty duplicate created by the mismatch). The fix on the gennis-v2
side overrides the id sent for the student branch specifically; on this side, the
lookup key is always `gennis_{s_id}` from `students[].id` in the login response's
`student.group[]` data — never derive it from the user-level id.

### 10.2 GENNIS v2 cutover — id renumbering (`ce06525`, 2026-08-13)
The GENNIS v2 cutover **re-issued every student id**, so the `gennis_{id}` username
lookup in `_sync_student` missed for every student already on the platform under their
old id. Each miss minted a fresh zero-point account, and the stale-member-prune logic
that runs right after (§10.3) then evicted the real account from its group — stranding
points, projects, and enrollments on an orphaned row nothing points at anymore. **A
single teacher login on 2026-08-13 did this to 43 students** in one shot (this is
exactly what the `restore_student_usernames.sql` repair script in `management-v2`
exists to undo).

**Fix**: `_find_renumbered_student()` (`gennis_service.py:200-240`) — before minting a
new student, search the *target group's current members* for someone with the same
normalized (case/whitespace-insensitive) full name but a *different* `gennis_id`. If
exactly one match, re-link that existing row to the new id instead of creating a new
one. If zero or more-than-one matches, fall through to creating a new row rather than
guessing — **scoping the search to the group is what makes this safe**: a candidate
must already be a member of the very group Gennis is currently placing the student
into, so two different people with the same name in different groups can never be
collapsed into one account.

### 10.3 Add-only sync drift (two related fixes)
`sync_teacher_data`/`_sync_student` originally only ever **added** rows — a group or
student membership that changed or ended on the Gennis side was never removed locally,
so local rosters only ever grew, permanently drifting from the source of truth.
- **`c7be43f`** — unlink teacher groups no longer returned by Gennis on login
  (`teacher_id = NULL` for any group previously linked but now missing from the
  response).
- **`1251c68`** — remove stale `student_groups` rows for students Gennis's current
  roster for that group no longer includes (caught a case where a local group showed
  22 students vs 14 in Gennis).

**Both fixes share the same critical guard**: if Gennis's response for that
group/teacher comes back **empty**, treat it as a transient API issue and remove
**nothing** — an empty response is far more likely to be a flaky API call than "this
teacher/group now has zero students," and treating it as real deletion would be
actively destructive. Any future change to this sync logic must preserve that
empty-response guard.

### 10.4 v2 endpoint migration (`de069d7`)
`admin.gennis.uz` (old Gennis) was switched off at the cutover — its `/base/login`
stopped answering entirely, so every login fell through to local auth, and students
synced from Gennis carried `hashed_password="external_auth"` (a placeholder, not a real
hash) so they **could not log in at all** post-cutover. `gennis-v2` now exposes a
compatibility endpoint returning the same nested shape this service already parses, so
only the URLs changed:
```
POST {base}/base/login          →  POST {base}/login
GET  {base}/group/students/{id} →  GET  {base}/group/{id}/students
```
`sync_teacher_data`, `sync_student_data`, `_sync_group`, `_sync_student` themselves were
**untouched** — only the URL construction changed. One behavior worth knowing: v2
answers `409` for an account it cannot trace to a Gennis teacher/student; `login()` only
treats `200` as success, so a `409` falls through to local auth exactly like a network
error would (i.e., it fails silently rather than surfacing a clear "not found in Gennis"
error — worth improving if this becomes a support burden).

### 10.5 Password placeholder security note
`_sync_student` creates new Gennis-synced accounts with a literal
`hashed_password="external_auth"` string (still true as of this doc — see
`gennis_service.py:277`). `BACKEND_BUGS.md` documents a related fix (an unusable bcrypt
hash from `os.urandom(32).hex()`, in `auth_service.py`) to close the theoretical risk of
a future bug that "sets the password to the existing hash" — **verify at the point of
use whether that fix actually replaced this literal or lives alongside it**; the two
files were not cross-checked against each other while writing this doc.

### 10.6 Repointed to management-v2, `GENNIS_API_URL` renamed (2026-08-26)
management-v2 grew its own copy of gennis-v2's `/integrations/student-platform`
shim (`POST /login`, `GET /group/{id}/students`, `GET /flow/{id}/students`) — same
contract, but reads the shared `user`/`gennis_*`/`turon_*_v2` tables directly
instead of gennis-v2's read-only mirror. The setting was renamed
`GENNIS_API_URL` → `MGMT_INTEGRATION_URL` and repointed at
`https://office.gennis.uz/...` to reflect that this now goes straight to the
DB owner, not gennis-v2. There is **no fallback to gennis-v2's copy** — if
management-v2 is unreachable, `GennisService.login()` returns `None` and
`auth_service.login()` falls through to local auth exactly as it always has
on any other failure; it does not retry a second URL. Live-verified against
one real account per (system, role) combination at cutover time: gennis
student, gennis teacher, turon student, turon teacher.

---

## 11. Testing

`backend/tests/` — 14 files, pytest, with `conftest.py` providing fixtures.
Notable test files and what they guard against regressions in:
- `test_points_reversal.py` — the wallet/leaderboard reversal bugs (§8).
- `test_ai_review.py` — AI review pipeline behavior.
- `test_bug_hunt.py`, `test_team_game.py` — team-game mechanics.
- `test_fill_in_blank_grading.py`, `test_exercises.py` — per-type exercise grading.
- `test_lesson_bug_import.py` — question-bank import into a game session.
- `test_dictionary.py`, `test_practice_utils.py` — SRS/dictionary logic.
- `test_rankings.py` — leaderboard calculation.
- `test_auth.py`, `test_lessons.py` — auth flow, lesson progress gating.

A second, thinner test area also exists at `backend/app/tests/` — check both locations
before assuming test coverage for a given area doesn't exist.

`.github/workflows/test.yml` runs CI checks on push (see its contents directly for the
current gate — not reproduced here since it's simple and self-explanatory).

Frontend has minimal test coverage (`App.test.js`, `setupTests.js` are CRA defaults);
no evidence of a substantial React test suite as of this doc.

---

## 12. Configuration / environment variables

All settings load via `pydantic-settings` from `backend/.env` (`app/config.py`). Names
only below — **never put actual values from `.env` into this file or any commit.**

| Variable | Purpose |
|---|---|
| `DATABASE_URL` | asyncpg connection string |
| `APP_NAME`, `APP_VERSION` | cosmetic |
| `DEBUG` | gates `/docs`/`/redoc`/`/openapi.json` exposure and SQL echo; **must be False in prod** |
| `SECRET_KEY` | JWT signing — **required, no default**, startup fails loudly if missing (intentional — see §10 of BACKEND_BUGS.md) |
| `JWT_ALGORITHM` | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | default 30 (short-lived; refresh flow handles long sessions) |
| `REFRESH_TOKEN_EXPIRE_DAYS` | default 7 |
| `UPLOAD_DIR`, `MAX_FILE_SIZE`, `ALLOWED_EXTENSIONS` | file upload limits |
| `BACKEND_CORS_ORIGINS` | comma-separated (also tolerates legacy JSON-list `.env` syntax) — **wildcard forbidden**, see §10 |
| `MGMT_INTEGRATION_URL` | points at management-v2's compatibility shim, not old admin.gennis.uz or gennis-v2's own copy (§10.4, §10.6) |
| `AI_PROVIDER_CHAIN` | comma-separated `groq,gemini,openai` — **currently forced to `openai` only** in practice (§7.1); re-adding a fallback without a configured key reintroduces a past outage |
| `OPENAI_BASE_URL`, `OPENAI_API_URL`, `OPENAI_API_KEY`, `OPENAI_MODEL` | `OPENAI_BASE_URL` optionally points at a relay/proxy to bypass geo-blocks |
| `GEMINI_API_KEY`, `GEMINI_MODEL`, `GEMINI_API_URL` | configured in code but currently unused (no key set) |
| `GROK_API_URL`, `GROK_API_KEY` (aliases `GROK_API_KEY`/`GROQ_API_KEY`), `GROK_MODEL` | Groq provider — accepts both env var spellings since deployed `.env` files use both |
| `HTTP_PROXY` | outbound proxy for AI calls (geo-block bypass) |
| `GITHUB_TOKEN` | read-only public scope; unauthenticated GitHub API is capped at 60/hr/IP |
| `MAX_AI_REVIEWS_PER_DAY` | default 20; set to 0 to disable AI review entirely |
| `PARENT_BOT_URL`, `PARENT_BOT_SECRET` | Telegram parent-bot notification on game-session completion; empty `PARENT_BOT_URL` cleanly disables the integration (no error) |

---

## 13. Deployment

**Git-push-triggered, not manual SSH deploy.** Two GitHub Actions workflows, both
triggered on push to the **`server`** branch (not `master`/`main`):

- **`deploy-backend.yml`** — SSHes into prod, `git pull origin server` inside
  `BACKEND_DIR`, reinstalls `requirements.txt`, restarts the systemd service
  (`SERVICE_NAME`). Runs extensive diagnostics on every deploy (branch/HEAD before and
  after pull, `AI_PROVIDER_CHAIN` value in `.env`, systemd unit's actual
  `WorkingDirectory`/`ExecStart`, and a base64-encoded live OpenAI-chain smoke test run
  directly on the prod host) — added (`a087fa9`) specifically because a prior deploy
  reported success and "Already up to date" while prod kept showing the exact
  AI-chain failure the code fix was supposed to resolve; the diagnostics exist to catch
  "deploy claims success but nothing actually changed" class of failures early.
- **`deploy-frontend.yml`** — builds the React bundle **in CI**, not on the prod box.
  Explicitly documented reason: earlier deploys ran `npm run build` directly on the
  production server and **OOM-killed mid-build**, leaving a half-written `build/`
  directory and a broken site. CI runners have more headroom (7GB/4-core). Sets
  `CI=false` (CRA treats warnings as build-failing errors when `CI=true`, and runners
  default that on), `NODE_OPTIONS=--max-old-space-size=4096`, and
  `GENERATE_SOURCEMAP=false` (halves bundle size, source maps are useless in prod).
  Verifies `frontend/build/index.html` exists before rsyncing — catches a build that
  exits 0 but produces nothing (silent-failure guard). Rsyncs with `--delete` to
  `/var/www/tech_gennis/frontend/build/` — the trailing slash on the source path is
  load-bearing (without it rsync nests an extra `build/` inside the target).

Required GitHub repo secrets for both workflows: `SSH_HOST`, `SSH_USER`,
`SSH_PRIVATE_KEY`, `SSH_PORT` (optional, defaults 22); backend additionally needs
`BACKEND_DIR`, `SERVICE_NAME`.

**Practical implication for anyone making a change here**: committing to `master`
(where this file lives) does **not** deploy anything. A change only reaches prod once
merged/pushed to `server`. After a frontend deploy, a hard refresh (Ctrl+Shift+R) is
required client-side or the old cached bundle hash stays active (documented in
`FRONTEND_BUGS.md`).

---

## 14. Known bug patterns / lessons learned

Distilled from `BACKEND_BUGS.md`, `FRONTEND_BUGS.md`, and git history — organized by
*pattern*, not by individual bug, so the same mistake isn't repeated in a new location.
Consult the two audit docs directly for the full itemized list including unresolved
(⬜) items not summarized here.

**Auth/authorization gaps ship easily in this codebase — always check.** Multiple
endpoints have shipped with zero auth dependency at all: exercise CRUD (anyone could
wipe every exercise), student read endpoints (PII enumeration — email/phone/balance/
full name with no login), teacher statistics (any authenticated user, not just
teachers, saw platform-wide aggregates), and the entire team-game list/get/WS surface
(§9.1). **Pattern**: when adding any new endpoint, explicitly state which
`Depends(get_current_*)` it uses — "I'll add auth later" has repeatedly become "shipped
with none."

**Ownership checks are separate from authentication.** Being logged in as *a* student
is not being logged in as *the* student who owns a resource. Project comment/file
updates were exploitable by any authenticated student against any other student's
project until an explicit `project.student_id != student_id` check was added. Apply the
same scrutiny to any new per-student-owned resource.

**The two-points-counter split (`total_points` vs `lifetime_points`) is the platform's
sharpest footgun.** Any code that awards points must use `add_points_to_student`
(bumps both); any code that *reverses* a previous award must use
`revoke_earned_points` (also both); any code that *spends* points must use
`subtract_points_from_student` (total_points only). Mixing these up doesn't error — it
silently drifts the leaderboard. See §8 in full before writing point-adjusting code.

**RU translation has two competing storage mechanisms and only one is live.** The
`Exercise` model has `*_ru` columns that are **completely dead** — nothing serves them.
The actual live translation path is `translation_cache` + `translation_store.py`. This
has caused real content gaps (1,371 exercises, 6 courses) because it's not obvious from
the model alone which mechanism is authoritative. Before adding any bilingual field to
a new model, decide explicitly which mechanism it uses and say so in a comment on the
column, the way `exercise.py:366` now does.

**Gennis sync bugs are almost always "add-only, never remove" or "id assumed stable
across systems."** See §10 in full. Any new Gennis-sync code must (a) handle removal/
staleness symmetrically with addition, (b) guard against an empty API response being
misread as "everything was deleted," and (c) never assume a Gennis id is stable across
a cutover — always have a name-based (or similarly robust) re-linking fallback scoped
tightly enough not to merge different people.

**Raw `fetch()` bypasses the auth-refresh interceptor (frontend).** `useHttp().request`
routes through `axiosInstance`, which has the 401→refresh-token interceptor wired up.
Several older components call `fetch()` directly instead and silently break on token
expiry (`FRONTEND_BUGS.md` lists the exact files, as of the audit: `TeacherCourses.js`,
`Teachercertificates.js`, `DegreeCard.js`, `StudentLessonPage.js`, `MyProjects.js`,
`TeacherStatistics.js`). When touching any of these, migrate the call to `useHttp`
rather than leaving it as-is — do not add new raw `fetch()` calls anywhere.

**Teacher-authored HTML is a stored-XSS surface, sanitize on every render path.**
`section.html` comes from a `contentEditable` editor and is injected via
`dangerouslySetInnerHTML`. Both known render sites now run it through
`src/utils/sanitize.js` (DOMPurify) — if a new component renders lesson/course HTML,
it must do the same; this is not automatic just because the data passed through
sanitization once elsewhere.

**AI review failures must never masquerade as content rejections.** A transient
provider failure (rate limit, no key, timeout) must leave `status="Submitted"`, never
flip to `"Rejected"` — only a genuine content problem (bad URL, unreadable repo)
earns `"Rejected"`. Conflating these was the core of the `b724929` outage (§7.1) and
is easy to accidentally reintroduce in new AI-adjacent code.

**Debug output that includes headers, tokens, or DSNs must never reach logs.** Two
separate historical incidents: full request headers (including bearer tokens) printed
on every course-detail request, and a raw exception string that could embed a full
Postgres DSN (with password) on DB connection failure. Use the sanitizing helpers
already in place (`_safe_db_url()` in `database.py`) rather than printing exceptions
raw.

**A missing model import silently breaks schema creation, not just Alembic.** Because
`init_db.py` relies on `Base.metadata.create_all()` as a safety net for the broken
Alembic chain (§3.1), a new model that isn't imported in `app/db/base.py` /
`app/models/__init__.py` won't get its table created on a fresh deploy, and the
failure mode is a runtime `UndefinedTableError` on first use, not a startup error.
Always add new models to both files.

---

## 15. Quick orientation checklist for a fresh session

1. Read this file fully before editing anything.
2. If touching points/rankings — re-read §8 first, always.
3. If touching Gennis sync — re-read §10 first, always.
4. If touching AI review — re-read §7 first, check `AI_PROVIDER_CHAIN` assumptions.
5. If authoring/editing course content — use `course_builder` + a `course_specs/`
   module, never hand-write DB inserts; run the full pipeline in §6.5, not a subset.
6. If adding an endpoint — explicitly choose an auth dependency; do not ship one
   without deciding this consciously.
7. Real frontend is top-level `frontend/`; ignore `backend/frontend/` (stale, untracked).
8. Deploys happen on push to the `server` branch, not `master`.
9. For anything not covered here in enough depth, `docs/BACKEND_BUGS.md` and
   `docs/FRONTEND_BUGS.md` have the full itemized audit this file draws from.
