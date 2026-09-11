# Frontend bugs — audit & fixes

Audit date: 2026-05-21
Scope: `frontend/` — React 19 + react-router-dom 7 + CRA + Redux Toolkit + axios.
Status legend: ✅ fixed (originally commits `1766039`/`6f4c762`; HIGH/MEDIUM items fixed 2026-09-11 in the Phase 4 bug-fix pass), 🟡 partial / mitigation only, ⬜ not yet fixed.

---

## CRITICAL

### ✅ XSS via teacher-authored lesson HTML
- **Where:**
  - `src/views/student/courses/LessonPage/StudentLessonPage.js:534`
  - `src/views/teacher/courses/LessonPage/LessonPage.js:267`
- **What:** `section.html` came from a `contentEditable` rich-text editor, stored in the DB, then injected via `dangerouslySetInnerHTML` with no sanitization. A compromised teacher account could inject `<script>` or `<img onerror=...>` that executes in every student's browser.
- **Fix:** added `src/utils/sanitize.js` (DOMPurify wrapper). Both views now run `section.html` through `sanitizeHtml()` before injection. `dompurify@^3.4.5` added to `package.json`.
- **Regressed when render moved to LessonContentBlocks.js; re-fixed + test added.** `StudentLessonPage.js` was later refactored to delegate section rendering to `src/views/student/courses/LessonPage/LessonContentBlocks.js`, which reintroduced the raw, unsanitized `dangerouslySetInnerHTML={{__html: section.html}}` call — the original fix's line reference above no longer matches where the render actually happens. Re-fixed by importing `sanitizeHtml` into `LessonContentBlocks.js` and wrapping `section.html` the same way `LessonPage.js` already does; regression test added at `frontend/src/__tests__/LessonContentBlocks.test.js`. Every other `dangerouslySetInnerHTML` site in the frontend was audited at the same time: `BugHuntArena.js` and `ExercsieFileUpload.js` render output from `src/utils/highlight.js`, which HTML-escapes its input before tokenizing and calls `sanitizeHtml()` on its own return value — already safe by construction, no change needed.

### ✅ Refresh-token interceptor was dead code
- **Where:** `src/api/axiosInstance.js` (the interceptor itself was fine — nothing imported it).
- **What:** Every component used `useHttp().request` from `src/api/search/base.js`, which used raw `fetch()`. The interceptor in `axiosInstance.js` was never invoked, so on 401 nothing refreshed and the user was silently dropped into a broken-session state.
- **Fix:** `useHttp.request` now routes through `axiosInstance.request(config)`. The 401 → refresh-token flow now actually fires.

### ✅ axiosInstance ↔ base.js circular import (introduced by the fix above)
- **Where:** `src/api/axiosInstance.js:2`, `src/api/search/base.js:2`
- **What:** After wiring `base.js` to import `axiosInstance`, the existing `import { API_URL } from './search/base'` in `axiosInstance.js` created a cycle. ESM TDZ error at startup: `Cannot access 'API_URL' before initialization` (minified to `'si'` in prod build).
- **Fix:** compute `API_URL` inline inside `axiosInstance.js` (kept in sync with the version in `base.js` via comment).

---

## HIGH

### ✅ `isAuthenticated` not reactive
- **Where:** `src/context/AuthContext.js:16`
- **What:** `const isAuthenticated = !!user && !!localStorage.getItem('token')` was computed during render by reading `localStorage` synchronously. If the interceptor cleared the token, or another tab logged out, the value stayed stale until an unrelated re-render fired.
- **Fix:** token now lives in React state; `isAuthenticated` is memoized off `user + token`. Added `storage` event listener for cross-tab sync.

### ✅ TeacherProfile updated via student endpoint
- **Where:** `src/views/teacher/profile/TeacherProfile.js:49`
- **What:** Profile fetch hit `v1/auth/me` (correct) but save sent `PUT v1/student/${profile.id}` — wrong resource. Teachers got 403 or silently mutated the wrong record.
- **Fix:** save now hits `v1/auth/me`. Added a guard so saves abort if `profile.id` is somehow missing.

### ✅ Raw `fetch()` calls bypass axiosInstance entirely
- **Where (original):**
  - `TeacherCourses.js:228,233,235,274,327`
  - `Teachercertificates.js:513`
  - `DegreeCard.js:55,61`
  - `StudentLessonPage.js:391,445`
  - `MyProjects.js:181`
  - `TeacherStatistics.js:103`
- **What:** These call `fetch(...)` directly with manual `headers()` — they never trigger the refresh interceptor and silently fail after token expiry.
- **Fixed (2026-09-11), actual locations (all line numbers above had drifted; real count was higher):**
  - `TeacherCourses.js` — 4 sites (`syncExercises` ×3, `doDeleteCourse`) → `useHttp().request(...)`.
  - `Teachercertificates.js` — `handleDelete` → `useHttp().request(...)`.
  - `DegreeCard.js` — check-and-earn POST → `useHttp().request(...)`; PDF download needs a `Blob` response, which `useHttp()`'s wrapper has no option for, so it now calls `axiosInstance.get(url, {responseType:'blob', ...})` directly instead — still crosses the shared interceptor, just not via the `request()` helper. Mirrors the existing pattern in `TeacherTeamGame.js`'s CSV export.
  - `StudentLessonPage.js` — 4 of 5 raw sites converted (`uploadZip`, both certificate-check calls, the explanation-modal PATCH). `handleDownloadFile`'s file download deliberately stays on `fetch()` — same blob-response limitation as DegreeCard's PDF above — with an inline comment; a 401 there still fails outright instead of refreshing (documented, known gap).
  - `MyProjects.js` — 2 sites (`uploadZipForProject`, `handleZipUpload`), not 1 as originally recorded.
  - `TeacherStatistics.js` — 1 site, confirmed as described (just at a different line, ~189 not ~103).
- **Remaining known gap:** the blob-response endpoints (file/PDF downloads) still don't get the refresh-interceptor treatment — `useHttp()`'s `request()` helper would need a `responseType` option to close this fully. Not done here; low frequency (only hit on an expired-token file download) and each site is now at least going through `axiosInstance` directly where practical.

### ✅ Login / Register double-write tokens to localStorage
- **Where:**
  - `src/views/auth/login/Login.js:39-44`
  - `src/views/auth/register/Register.js:57-64`
- **What:** Both components manually `localStorage.setItem('token', ...)` and *also* call `onLogin(res)` which goes through `AuthContext.login()` (which sets the same keys). Two code paths to keep in sync.
- **Fixed (2026-09-11):** `Login.js` turned out already correct — no manual `setItem` calls exist there (doc drift). `Register.js` had the real bug (manually wrote `token`/`refresh_token`/`user` to `localStorage` in addition to calling `onLogin`); the three manual `setItem` calls were removed. `AuthContext.login(response, remember)` is a strict superset of what was removed — it also respects `remember` (localStorage vs sessionStorage) and clears the other storage, which the manual writes didn't.

---

## MEDIUM

### ✅ `TeacherStatistics` crashed on null backend fields
- **Where:** `src/views/teacher/statistics/TeacherStatistics.js:143,158`
- **What:** `data.average_points.toFixed(1)` and `data.dynamics.map(...)` threw a `TypeError` when the backend returned `null` / undefined.
- **Fix:** `(data.average_points ?? 0).toFixed(1)` and `(data.dynamics || []).map(...)`.

### ✅ Mock initial Redux state had plaintext password
- **Where:** `src/store/studentsSlice.js:11,20,28`
- **What:** `initialStudents` shipped `password: 'student123'` in the production bundle.
- **Fix:** initial state set to empty arrays. Real data still comes from the API.

### ✅ Debug `console.log` calls in production paths
- **Where:** `src/views/student/courses/LessonPage/StudentLessonPage.js:396,450`
- **Fix:** removed both. `console.warn` calls in `.catch` arms were kept as legitimate fallback signals.

### ✅ Silent error swallowing (`.catch(() => {})`)
- **Where:**
  - `LeaderBoard.js:30-33` — `fetchMyRank` failure leaves `myRank` null forever, "Mening o'rnim" card never appears.
  - `DegreeCard.js:22-25` — `Promise.all` failure shows empty state with no message or retry.
  - `Teachercertificates.js:481-487` — initial-load failure leaves an empty list silently.
- **Fixed (2026-09-11):** all three now set an error state on catch, show an inline error message, and offer a retry button that re-runs the fetch. `LeaderBoard.js` and its `rating.loadError`/`rating.retry` i18n keys were reused as the structural + textual model for the other two.
- **🟡 Follow-up needed:** `Teachercertificates.js` and `DegreeCard.js` had no i18n mechanism in use at all before this fix, and `translations.js` has no generic "failed to load" key outside the `rating.*` namespace (reusing `rating.loadError` there would literally say "failed to load the **rating**", wrong context). Their new error *messages* use a hardcoded English fallback string, clearly commented in the code as a placeholder — needs a real UZ/RU translated key added to `translations.js` and swapped in. The retry *buttons* in both already reuse the existing `rating.retry` key correctly (domain-neutral, exact fit).

### ✅ Unguarded `setTimeout` → setState-after-unmount
- **Where:**
  - `Profile.js:51` — `setSuccess`
  - `TeacherProfile.js:17, 58` — `setEditMode`/`setEditClose`/`setSuccess`
  - `Teachercertificates.js:478` — `setToast`
  - `TeacherReview.js:90` — `setDetail`
- **Fixed (2026-09-11):** each timer id is now stored in a `useRef` and cleared in an unmount cleanup `useEffect` (or before starting a replacement timer, for the ones that can restart). `Profile.js` had 4 separate `setTimeout(() => setSuccess(''), 3000)` sites, not 1 as originally recorded — all fixed via one shared ref.

### ⬜ `useEffect` dep arrays disabled with `eslint-disable-line`
- **Where:** `StudentCourses.js:185,187,245`, `TeacherCourses.js:204`, `StudentLayout.js:38`, `Profile.js:36`, `TeacherProfile.js:42`, `TeacherStatistics.js:95`, `LeaderBoard.js:38`, `DegreeCard.js:25`, `Teachercertificates.js:156,487`, `MyProjects.js:95`, `LessonEditor.js:65`, `TeacherReview.js:49`
- **What:** `request` from `useHttp()` is stable (memoized with empty deps), so silencing the warning is *currently safe*. Removing the suppressions exposes the real intent and prevents a future refactor from quietly introducing stale-closure bugs.
- **Deliberately not touched in the Phase 4 correctness pass:** no live bug here per the doc's own note — this is a hygiene/clarity item, left for a hygiene pass rather than a correctness one.

### ✅ `key={index}` on reorderable lists
- **Where (original):** `StudentLessonPage.js:218` (drag-drop chips), `StudentCoursePage.js:301` (chapters).
- **What:** Index keys cause incorrect React reconciliation when items reorder.
- **Fixed (2026-09-11), both locations had drifted:**
  - The drag-drop chips moved out of `StudentLessonPage.js` entirely in an earlier refactor (`5854b70`, "split StudentLessonPage.js into focused modules") into `LessonExercise.js`'s `dragDropped`/`dragAvailable` lists — `StudentLessonPage.js` itself has no such list anymore. Keyed by `` `${word}__${index}` `` there instead of a bare index.
  - `StudentCoursePage.js`'s actual bug wasn't the lesson list (already keyed by `lesson.id`) but the chapter *groups* list — keyed by the group's own stable `g.key` (the lesson's `chapter` field, or a `'__none__'` sentinel) instead of its array index, so a chapter's collapsed/open state no longer follows the wrong group after a reorder/filter.

### ✅ `Loader` component defined inside another component
- **Where:** `TeacherCourses.js:338`
- **Fixed (2026-09-11):** extracted to its own `Loader.js`, matching the existing `ConfirmModal.js`/`CategoriesModal.js`/`SortableCourseCard.js`/`CategoryPicker.js` split-file convention already used in that directory. Text unchanged.

### ✅ `saveCourse` reads user from `localStorage` directly
- **Where:** `TeacherCourses.js:256`
- **Fixed (2026-09-11):** now uses `const { user } = useAuth()` (matching `LeaderBoard.js`'s existing usage), with a guard that aborts the save and surfaces an error if `user?.id` is missing instead of silently sending `instructor_id: undefined`.

### ✅ `LessonEditor` / `useTranslation` minor issues
- `useTranslation.js:5` doesn't listen for the `storage` event, only the custom `languageChange` event — multi-tab inconsistency. **Fixed:** added a `storage` listener (filtered to the `lang` key) alongside the existing one, with matching cleanup.
- `LessonEditor.js:65` has a missing `value` dep on a `useEffect`. **Fixed, but not in `LessonEditor.js`** — that file has no such effect; the real bug is in the sibling `RichTextEditor.js` (a `contentEditable` DOM-sync effect with an empty `[]` dep array, so external `value` prop changes after mount were silently ignored). A naive `[value]` dep would re-run on every keystroke (this component's own `onChange` round-trips through the parent as a new `value` prop) and reset the caret on every character typed. Fixed with a `lastEmitted` ref: the effect only resyncs the DOM when `value` differs from what this editor itself last emitted, i.e. a genuine external change.
- `MyProjects.js` uses `window.confirm` / `alert` for destructive actions — blocked in some embedded contexts; inconsistent with the modal pattern already used elsewhere. **Fixed:** only `window.confirm` was actually present (the `alert` claim was drift). Replaced with the existing `TeacherCourses/ConfirmModal.js`, reused across the teacher/student boundary (precedent for that already exists elsewhere in this codebase). The confirm text itself (`'Удалить проект?'`) is unchanged, just moved into the modal.

---

## LOW

- ⬜ `NO_STATS_PATHS` constant declared but never used (`StudentLayout.js:9`).
- ⬜ Several `'is assigned a value but never used'` lint warnings (see `npm run build` output).
- ⬜ `useHttp` header helpers (`headers`, `headersImg`, etc.) are mostly redundant now that axiosInstance auto-attaches the bearer. Keep for now for the raw-fetch callers; consolidate when those are migrated.

---

## Required action when deploying

- Hard refresh (Ctrl+Shift+R) after a deploy that ships a new bundle, otherwise the old `main.<hash>.js` stays cached.
- If you see `Cannot access 'si' before initialization` on first load, you're on the broken bundle from commit `1766039` — pull `6f4c762` (the circular-import fix) and redeploy.

---

## Quick verification after deploy

```bash
# 1. Bundle built successfully
ls frontend/build/static/js/main.*.js

# 2. Open devtools → Network → reload. Confirm:
#    - No 401 → broken UI; refresh interceptor kicks in.
#    - No "Cannot access X before initialization" in console.
#    - Lesson page text sections render plain text from a malicious teacher
#      input (e.g. <img src=x onerror=alert(1)>) without firing the alert.
```
