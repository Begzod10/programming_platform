# Harden the points system: enforce the total_points invariant at write-time

Points on `students.total_points` are supposed to obey:

```
total_points =
    Σ exercise.points        (per first-time correct submission)
  + Σ project.points_earned  (per Approved project)
  + Σ lesson.points_reward   (per LessonCompletion)
  + Σ achievement.points_reward (per StudentAchievement)
  ± Σ manual /rankings/add-points | /subtract-points calls
```

Correctness relied entirely on app-level guards, so totals drifted over time
(double-awards on concurrent submissions, orphaned lesson rewards after AI
re-grades, unaudited manual adjustments). This PR moves the invariant to the
DB layer where practical, extracts the LessonCompletion reconciliation to a
single shared helper called from all three review paths, adds a
PointAdjustment audit ledger for manual mutations, and ships a recalc script
that verifies (and can repair) the invariant across all students.

**Point amounts and thresholds are unchanged.** Only the correctness gaps are
closed.

## The 5 fixes

### 1. DB-level idempotency for exercise scoring awards

- New partial unique index `uq_exercise_submissions_scoring` on
  `exercise_submissions (student_id, exercise_id) WHERE score > 0`. Declared
  in the ORM model (`ExerciseSubmission.__table_args__`) via
  `postgresql_where`/`sqlite_where` so tests using `Base.metadata.create_all`
  against SQLite also see the invariant.
- `submit_exercise` still runs its in-code `already_solved` guard first, but
  now flushes the scoring insert BEFORE crediting points. On IntegrityError
  we roll back, rewrite as a non-scoring (`score=0`) duplicate submission,
  and return the standard "Ball bir marta beriladi" feedback. Never
  double-awards, never 500s.
- Alembic migration `de1a5b3f7c01_harden_points_add_scoring_uniq_index.py`
  dedupes pre-existing duplicates (keeps the earliest scoring row, zeroes
  out the rest) BEFORE creating the index.

**Files:** `backend/app/models/exercise.py`,
`backend/app/services/exercise_service.py`,
`backend/alembic/versions/de1a5b3f7c01_harden_points_add_scoring_uniq_index.py`

### 2. DB-level idempotency for lesson completions

- The model already declared `UniqueConstraint("student_id", "lesson_id",
  name="uq_student_lesson_completion")` but no migration existed. Added
  `de1a5b3f7c02_harden_points_lesson_completion_uniq.py` which dedupes
  historical duplicates then conditionally creates the constraint (uses a
  Postgres `DO $$ IF NOT EXISTS $$` block so a re-run is safe).
- `_maybe_auto_complete_lesson` in `exercise_service.py` now delegates to
  the shared `reconcile_lesson_completion` helper (see #3) which catches
  IntegrityError from a racing insert and no-ops.

**Files:** `backend/app/services/exercise_service.py`,
`backend/alembic/versions/de1a5b3f7c02_harden_points_lesson_completion_uniq.py`

### 3. Unwind LessonCompletion + reward on project demotion (biggest over-count source)

- New module `backend/app/services/completion_reconciler.py` with a single
  idempotent function `reconcile_lesson_completion(db, *, student_id,
  lesson_id, passing, ranking_service)` that:
  - `passing=True` and no completion → insert row + add `lesson.points_reward`
  - `passing=True` and completion exists → no-op (never double-award)
  - `passing=False` and completion exists → delete row + subtract
    `lesson.points_reward`
  - `passing=False` and no completion → no-op
- Wired into all three review paths, replacing hand-rolled logic:
  - **AI review**: `backend/app/services/ai_review_service.py`
    (`run_ai_review_for_project`) — an AI re-grade from 80 → 30 now unwinds
    the lesson reward instead of leaving it credited forever.
  - **Teacher endpoint**: `backend/app/api/v1/endpoints/projects.py`
    (`review_project`) — same behavior on teacher re-review.
  - **Legacy service method**: `backend/app/services/project_service.py`
    (`ProjectService.review_project`) — previously didn't touch
    LessonCompletion at all; now stays in lockstep with the other two paths.
- `passing` is `points >= PROJECT_PASS_THRESHOLD` (75, from
  `project_service.py`).

**Files:** `backend/app/services/completion_reconciler.py` (new),
`backend/app/services/ai_review_service.py`,
`backend/app/api/v1/endpoints/projects.py`,
`backend/app/services/project_service.py`

### 4. PointAdjustment audit ledger

- New model `backend/app/models/point_adjustment.py`:
  - `id`, `student_id` (FK → students, CASCADE), `delta` (signed int),
    `actor_id` (FK → students, SET NULL), `reason` (non-null String(500)),
    `related_entity_type` (nullable), `related_entity_id` (nullable),
    `created_at`.
- Exported from `backend/app/models/__init__.py` and `backend/app/db/base.py`
  so `Base.metadata` sees it in tests.
- Alembic migration `de1a5b3f7c03_harden_points_add_point_adjustments.py`
  creates the table + student_id index.
- The `/rankings/add-points` and `/rankings/subtract-points` endpoints now
  take a JSON body (`PointAdjustmentRequest` with `student_id`, `points`,
  `reason`) instead of query params. Every call writes a `PointAdjustment`
  row inside the same transaction as the `RankingService` mutation. We
  grepped the frontend on 2026-07-16 — no callers, so requiring a body is a
  safe change.
- Only the two manual endpoints write to this ledger. Exercise / project /
  lesson / achievement awards are already reconstructable from
  source-of-truth rows and stay unchanged.

**Files:** `backend/app/models/point_adjustment.py` (new),
`backend/app/models/__init__.py`, `backend/app/db/base.py`,
`backend/app/api/v1/endpoints/rankings.py`,
`backend/alembic/versions/de1a5b3f7c03_harden_points_add_point_adjustments.py`

### 5. Recalc / audit CLI

- New script `backend/scripts/recalc_points.py`, patterned after
  `scripts/normalize_misgraded_projects.py` (argparse, `--apply`, async
  main, `sys.path` insert, `AsyncSessionLocal`).
- Flags: `--student-id N` (single student, default: all),
  `--apply` (write corrections, default: report only).
- Identity used:
  ```
  total_points ==
      SUM(exercise.points where scoring)
    + SUM(project.points_earned where Approved)
    + SUM(lesson.points_reward where completed)
    + SUM(achievement.points_reward where earned)
    + SUM(point_adjustments.delta)
  ```
- On `--apply`, rewrites `students.total_points` and mirrors to
  `rankings.total_points` in one transaction, then calls
  `RankingService.calculate_and_update_rankings()` to re-derive ranks.
- Output columns: `sid, name, cur, exp, Δ, ex, proj, les, ach, man`.

**Files:** `backend/scripts/recalc_points.py` (new)

## Tests

New / extended coverage in `backend/tests/`:

- **`test_exercises.py`** — `test_concurrent_correct_submissions_award_points_once`:
  spawns two concurrent `submit_exercise` calls on the same (student,
  exercise). Asserts exactly one scoring row exists and
  `student.total_points` moved by exactly `exercise.points` (not 2x).
  Also `test_repeat_correct_submission_after_scoring_stays_at_one_award`
  for the sequential-repeat case.
- **`test_project_reconciler.py`** (new file) — 5 tests:
  - Passing → failing correctly unwinds completion + reward.
  - Double passing does not double-award.
  - Double failing does not double-subtract.
  - Legacy teacher path Rejected(50) → Approved(60) credits 60 net (documents
    the pre-existing subtract-clamp quirk in
    `RankingService.subtract_points_from_student` where subtracting a
    never-credited 50 clamps at 0) and does NOT create a LessonCompletion
    (60 < 75).
  - AI path Approved(80) → re-grade to 30 debits both project + lesson
    reward cleanly.
- **`test_rankings.py`** — 4 new tests:
  - `POST /rankings/add-points` writes a positive-delta `PointAdjustment`
    row with the supplied reason.
  - `POST /rankings/subtract-points` writes a NEGATIVE-delta row.
  - Missing `reason` returns 422.
  - Recalc identity computed via `_compute_for_student` reconciles to zero
    drift when only manual adjustments have been applied.

### Test run

```
$ cd backend && python -m pytest tests/ -q
........................................................................ [ 75%]
........................                                                 [100%]
96 passed in 34.64s
```

Baseline before this PR was 85 tests. All previously-passing tests still
pass; the 11 new tests all pass.

### Recalc script run against the test SQLite DB (report mode)

```
=== Points recalc (REPORT) ===

  sid  name                          cur    exp     Δ     ex  proj   les   ach   man
------------------------------------------------------------------------------------
   24  stud_0dbba4e0                  17     17     0     17     0     0     0     0
   26  stud_95e4d5ec                  17     17     0     17     0     0     0     0
   40  s_3e7bea97                     25     25     0      0     0    25     0     0
   44  s_4bd02981                     60     60     0      0    60     0     0     0
   48  stud_9432c290                  42     42     0      0     0     0     0    42
   50  stud_77d3f26b                  80     80     0      0     0     0     0    80
   54  stud_0b0071c7                  30     30     0      0     0     0     0    30

Checked 46 students; drift on 0 (sum |Δ| = 0).
```

Zero drift across all 46 test-generated students. The columns line up as
expected: concurrent-submit test students show `ex=17` (award happened once,
not twice); reconciler test students show either `les=25` or `proj=60`;
manual-adjustment test students show correctly-signed `man` totals.

## Explicitly out of scope (per the task spec)

Noted here so the coordinator can decide whether to open follow-ups:

1. **Teacher-review can award any 0–100 score, but the AI review has a hard
   ≥75 gate.** A teacher-Approved project at 50 still credits 50 points to
   the student total but does NOT unlock the next lesson (the reconciler
   correctly does not create a LessonCompletion when `points < 75`). This
   asymmetry is preserved here — the PR just makes sure that whichever
   direction the score moves, both the project points AND the lesson reward
   stay in sync via the shared reconciler.
2. **Grok's `partial_score` is computed but never wired into the scoring
   path.** Left as-is.

## Migration order

Chain: `cc1122334455` → `de1a5b3f7c01` → `de1a5b3f7c02` → `de1a5b3f7c03`.

Each migration has a working `downgrade()`. None were applied to any real
DB — following project convention (migrations are user-owned), only the
alembic files were written. The `de1a5b3f7c02` migration's constraint-add is
guarded by `IF NOT EXISTS` so it's a no-op if the constraint already exists
in production.

Model-level constraints (partial unique index, unique constraint,
PointAdjustment table) are declared on the SQLAlchemy models so
`Base.metadata.create_all` in the test suite sees them without running
migrations.
