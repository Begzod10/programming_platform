"""Shared, reusable library for building courses from a spec module.

## Why this exists

Every earlier course-building script (seed_python_algorithms.py,
seed_sql_database_design.py, ...) mixed two unrelated things in one 2,000+
line file: the DB-writing mechanism (create course/lesson/exercise rows,
build sections_json, write translation_cache) and the course's actual
content (titles, HTML, exercises). That made each new course a fresh
copy-paste of the mechanism, and — critically — made it easy to silently
skip a step (like RU exercise translation) because nothing forced the
same shape every time. A platform-wide audit found 1,371 exercises with
exactly that gap.

This package is the mechanism, extracted once, reused by every course.
Course content lives in a separate "spec" module (see course_specs/) that
contains ONLY data — dicts and lists, no DB code — so writing a new course
means writing a spec, not rewriting the pipeline.

## Spec module contract

A spec module (e.g. course_specs/my_course.py) must define:

  COURSE: dict — Course model fields. Required keys: title, description,
    instructor_id, difficulty_level, duration_weeks, max_points. Optional:
    category_id, prerequisite_course_id, display_order, image_url,
    thumbnail_url, is_active (default True), is_published (default False —
    leave False until a human reviews the course), title_ru, description_ru.

    title_ru/description_ru are NOT optional in practice — GET /courses
    reads them at request time via _translate_course_dto() (courses.py),
    exactly like it reads a lesson's RU translation. A round of course
    builds shipped 6 courses missing these on the wrong assumption that no
    serving code read a course-level translation; it does, so treat this
    the same as any other required bilingual field. check_ru_coverage.py
    now checks for it too.

  LESSONS: list[dict] — one dict per lesson, in course order. Each lesson
    dict:
      order: int (required, matches Lesson.order)
      title: str (required) / title_ru: str | None
      points_reward: int (default 10)
      text_content: str | None / text_content_ru: str | None
      code_content: str | None / code_content_ru: str | None
      code_language: str | None
      video_url: str | None
      task: dict | None — only for review/capstone lessons. Keys:
        task_title, task_title_ru, task_description, task_description_ru,
        task_requirements, task_requirements_ru, task_technologies,
        task_deadline_days (task_technologies/task_deadline_days have no
        _ru sibling — the former is a tech-stack string, the latter a
        plain int).
      sample: dict | None — namuna. Keys: title, description, sample_type
        ("web"|"python"|"sql"|"code"), html_code, css_code, js_code,
        code_files (list[{"filename","language","code"}], used when
        sample_type="code").
      exercises: list[dict] — see EXERCISE SPEC below.

  EXERCISE SPEC (each dict in a lesson's "exercises" list):
    title: str / title_ru: str | None
    description: str / description_ru: str | None
    exercise_type: "multiple_choice" | "fill_in_blank" | "drag_and_drop" | "text_input"
    options: list[str] | None / options_ru: list[str] | None
      (multiple_choice — options_ru must be the SAME length/order as
      options; correct_answers below indexes into the UNTRANSLATED
      options via letter, so it is never re-derived from options_ru)
    correct_answers: str | None (e.g. "A" or "A,C" for multiple_choice;
      a literal answer word for fill_in_blank/text_input)
    correct_answers_ru: str | None — ONLY set this for fill_in_blank/
      text_input when the source answer is genuine natural language (not
      a code/SQL/API token) — see is_natural_language_answer() below,
      which the translate step uses to warn if this looks like it was
      skipped when it shouldn't have been, or set when it shouldn't.
    drag_items: list[str] | None / drag_items_ru: list[str] | None
      (drag_and_drop — SAME length/order as drag_items; do NOT hand-derive
      correct_order_ru, see derive_correct_order_ru() below — the create/
      translate scripts do this automatically so a human/agent author
      never has to get the index-mapping right by hand)
    correct_order: list[str] | None (drag_and_drop — must be a permutation
      of drag_items; check_exercise_integrity.py verifies this)
    is_multiple_select: bool (default False)
    expected_answer: str | None (text_input — AI-graded rubric hint, never
      translated, never read as a strict-match key)
    hint: str | None / hint_ru: str | None
    explanation: str | None (never translated — dead field for RU per
      _translate_exercise_dto, kept UZ-only intentionally)
    difficulty_level: "Easy" | "Medium" | "Hard" (default "Medium")
    points: int (default 10)

## Diagrams (Mermaid)

Not a schema field — a plain HTML authoring convention the frontend
generically supports (StudentLessonPage.js auto-detects any
`<pre class="mermaid">` block anywhere in rendered lesson HTML and runs
mermaid.js on it; LessonContentBlocks.js renders text sections via
dangerouslySetInnerHTML, so this just works with zero backend/schema
changes). Course 109 was originally built with ZERO diagrams across all 14
lessons — nothing in the pipeline catches this because there's no field to
be "missing", so it silently shipped that way until a user noticed by
comparing to an older course. Do not repeat that: for EVERY lesson, ask
whether a diagram would genuinely clarify the content (a schema/ER shape, a
decomposition, a relationship, a multi-step flow/pipeline, a
before/after comparison) — and if yes, author one directly into that
lesson's `text_content` / `text_content_ru` strings (and, once
build_sections_json runs, it will automatically be present in
sections_json too, since that's built FROM text_content — no separate
step needed). It is equally correct to skip a lesson that has nothing
diagram-worthy (e.g. a pure recap/review lesson) — do not add one as
filler just for coverage. `check_diagram_coverage.py` reports the ratio
after a build so this is a visible, reviewed decision, not a silent one —
it is informational only and never fails the build.

Exact markup (ground every diagram in THAT lesson's own real content —
tables/columns/code the lesson already discusses, never an invented
generic example):

    <h3>Some heading</h3>
    <pre class="mermaid">
    flowchart TB
      A["node label
    line two"]
      A -->|"edge label"| B["other node"]
    </pre>
    <p>Caption paragraph explaining what the diagram shows.</p>

RU translation rule (confirmed against course 98's original hand-built
diagram and its own RU translation): table names, column names, and any
other real schema/code identifiers inside node/edge labels stay EXACTLY
as-is in both languages — never translate `courses`, `lessons.course_id`,
`student_courses`, `id PK`, `FK`, etc. Only the natural-language parts of
edge labels (the "why"/"what" descriptions) and the caption `<p>` get
translated, same as any other prose.

## Pipeline (run in this order; each script is independently re-runnable)

    check_course_images.py --set <id> --image <url> --thumbnail <url>
    create_course.py <spec_module>
    create_lessons.py <spec_module>
    create_exercises.py <spec_module>
    check_exercise_integrity.py <course_id>       # fix before translating
    translate_exercises_ru.py <spec_module>
    create_samples.py <spec_module>
    set_submission_tasks.py <spec_module>         # BEFORE translate_lessons_ru —
                                                   # that reads lesson.task_* off
                                                   # the ORM row to build its
                                                   # section_translations map
    translate_lessons_ru.py <spec_module>
    check_ru_coverage.py <course_id>              # must pass clean
    check_diagram_coverage.py <course_id>          # informational only
    check_course_images.py <course_id>             # must pass clean

Or run build_course.py <spec_module> to do all of the above in order in
one process (still calling the same underlying functions).
"""
