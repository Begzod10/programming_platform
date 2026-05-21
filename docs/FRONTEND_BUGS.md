# Frontend bugs — audit & fixes

Audit date: 2026-05-21
Scope: `frontend/` — React 19 + react-router-dom 7 + CRA + Redux Toolkit + axios.
Status legend: ✅ fixed in commits `1766039` / `6f4c762`, 🟡 partial / mitigation only, ⬜ not yet fixed.

---

## CRITICAL

### ✅ XSS via teacher-authored lesson HTML
- **Where:**
  - `src/views/student/courses/LessonPage/StudentLessonPage.js:534`
  - `src/views/teacher/courses/LessonPage/LessonPage.js:267`
- **What:** `section.html` came from a `contentEditable` rich-text editor, stored in the DB, then injected via `dangerouslySetInnerHTML` with no sanitization. A compromised teacher account could inject `<script>` or `<img onerror=...>` that executes in every student's browser.
- **Fix:** added `src/utils/sanitize.js` (DOMPurify wrapper). Both views now run `section.html` through `sanitizeHtml()` before injection. `dompurify@^3.4.5` added to `package.json`.

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

### ⬜ Raw `fetch()` calls bypass axiosInstance entirely
- **Where:**
  - `TeacherCourses.js:228,233,235,274,327`
  - `Teachercertificates.js:513`
  - `DegreeCard.js:55,61`
  - `StudentLessonPage.js:391,445`
  - `MyProjects.js:181`
  - `TeacherStatistics.js:103`
- **What:** These call `fetch(...)` directly with manual `headers()` — they never trigger the refresh interceptor and silently fail after token expiry.
- **Not fixed:** noisy refactor across many files. The fixed `useHttp` covers the bulk of API calls; convert these one file at a time when touching them.

### ⬜ Login / Register double-write tokens to localStorage
- **Where:**
  - `src/views/auth/login/Login.js:39-44`
  - `src/views/auth/register/Register.js:57-64`
- **What:** Both components manually `localStorage.setItem('token', ...)` and *also* call `onLogin(res)` which goes through `AuthContext.login()` (which sets the same keys). Two code paths to keep in sync.
- **Not fixed:** delete the manual `setItem` calls and let `AuthContext.login()` be the single source of truth.

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

### ⬜ Silent error swallowing (`.catch(() => {})`)
- **Where:**
  - `LeaderBoard.js:30-33` — `fetchMyRank` failure leaves `myRank` null forever, "Mening o'rnim" card never appears.
  - `DegreeCard.js:22-25` — `Promise.all` failure shows empty state with no message or retry.
  - `Teachercertificates.js:481-487` — initial-load failure leaves an empty list silently.
- **Not fixed:** set an error state on catch and surface a retry affordance.

### ⬜ Unguarded `setTimeout` → setState-after-unmount
- **Where:**
  - `Profile.js:51` — `setSuccess`
  - `TeacherProfile.js:17, 58` — `setEditMode`/`setEditClose`/`setSuccess`
  - `Teachercertificates.js:478` — `setToast`
  - `TeacherReview.js:90` — `setDetail`
- **Not fixed:** store timer ids and clear in cleanup, or move into `useEffect` with a teardown.

### ⬜ `useEffect` dep arrays disabled with `eslint-disable-line`
- **Where:** `StudentCourses.js:185,187,245`, `TeacherCourses.js:204`, `StudentLayout.js:38`, `Profile.js:36`, `TeacherProfile.js:42`, `TeacherStatistics.js:95`, `LeaderBoard.js:38`, `DegreeCard.js:25`, `Teachercertificates.js:156,487`, `MyProjects.js:95`, `LessonEditor.js:65`, `TeacherReview.js:49`
- **What:** `request` from `useHttp()` is stable (memoized with empty deps), so silencing the warning is *currently safe*. Removing the suppressions exposes the real intent and prevents a future refactor from quietly introducing stale-closure bugs.

### ⬜ `key={index}` on reorderable lists
- **Where:** `StudentLessonPage.js:218` (drag-drop chips), `StudentCoursePage.js:301` (chapters).
- **What:** Index keys cause incorrect React reconciliation when items reorder.
- **Not fixed:** use item content / id as key.

### ⬜ `Loader` component defined inside another component
- **Where:** `TeacherCourses.js:338`
- **What:** Redeclared on every render → React treats it as a new component type → DOM subtree torn down + rebuilt each render.
- **Not fixed:** move outside the parent component body.

### ⬜ `saveCourse` reads user from `localStorage` directly
- **Where:** `TeacherCourses.js:256`
- **What:** Bypasses `AuthContext`; if `user` is null in state, sends `instructor_id: undefined`.
- **Not fixed:** use `const { user } = useAuth()`.

### ⬜ `LessonEditor` / `useTranslation` minor issues
- `useTranslation.js:5` doesn't listen for the `storage` event, only the custom `languageChange` event — multi-tab inconsistency.
- `LessonEditor.js:65` has a missing `value` dep on a `useEffect`.
- `MyProjects.js` uses `window.confirm` / `alert` for destructive actions — blocked in some embedded contexts; inconsistent with the modal pattern already used elsewhere.

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
