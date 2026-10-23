# PC Guard: student PC blocking tied to the daily quota

Date: 2026-10-23
Status: draft for review

## 1. Goal

Student PCs at the center run a Windows agent that blocks every app except an
allowlist until the student has met their daily quota on the programming platform.
Once the quota is met, the PC unlocks. The teacher controls PCs remotely and reads a
progress report, both from a phone or a Mac.

## 2. Decisions taken in brainstorming

| Topic | Decision |
|---|---|
| Student OS | Windows only |
| Blocking mode | Allowlist (only listed apps run while locked) |
| Agent stack | C# .NET 8: Windows Service plus a shell app |
| Teacher console | Responsive page in the existing React teacher UI (phone and Mac browsers), no native apps |
| Teacher powers | Lock/unlock now, edit allowlist, live status, send message |
| Report | Teacher dashboard in the platform (no Telegram digest in this version) |
| Monitoring depth | App name and duration, plus lock/unlock events. No screenshots, keystrokes or page contents |
| Student identity | Student signs in on the PC with their platform account (assumption, confirm in review) |

## 3. Existing code this builds on

- `backend/app/models/daily_quota.py`: `StudentDailyProgress.unlocked` per student per
  Tashkent day, `QuotaConfig` (rest days Sat/Sun, enabled flag).
- `backend/app/services/daily_quota_service.py`: `get_today`, `on_lesson_completed`,
  `_emit_unlocked`. The unlock event is the hook for pushing a PC unlock.
- `backend/app/ws/`: existing WebSocket handling, used as the pattern for the PC channel.
- `backend/app/dependencies.py`: `get_current_teacher` for the console endpoints.
- Frontend teacher views under `frontend/src/views/teacher/`.

Lock state is NOT redefined. The PC reads the platform's own quota result.

## 4. Architecture

### 4.1 Windows agent (new repo directory `pc-agent/`)

- **Guard service** (Windows Service, SYSTEM)
  - Watches running processes; closes any process not on the active allowlist while locked.
  - Holds the WebSocket to the backend; applies lock state, allowlist and commands.
  - Caches the last rules; after 10 minutes without the server it falls back to locked.
  - Records app-usage intervals and sends them in batches.
  - Heartbeat every 30 seconds.
  - Restarts itself through service recovery options; a second watchdog task re-launches it.
- **Shell app** (runs in the student's session)
  - Sign-in screen, lock overlay showing remaining lessons, teacher message pop-ups.
  - Talks to the guard service over a local named pipe.
  - Shows a notice of what is recorded (app names and durations only).

### 4.2 Backend (new module `pc_control`)

Tables (new Alembic migration):
- `pc_devices`: id, hostname, machine_key hash, group_id (nullable), last_seen_at, online flag.
- `pc_allowlists`: id, scope (global or group_id), entries (executable name, publisher
  signature, optional note), updated_by, updated_at.
- `pc_sessions`: id, device_id, student_id, signed_in_at, signed_out_at.
- `pc_usage_events`: id, session_id, app_name, started_at, ended_at, was_locked.
- `pc_commands`: id, device_id or group scope, type (lock, unlock, message), payload,
  created_by, created_at, delivered_at.

Endpoints:
- `POST /pc/login`: platform credentials in, device-scoped token out (valid only on `/pc/*`).
- `GET /pc/state`: lock state, remaining quota, effective allowlist.
- `WS /pc/ws`: pushes lock changes, allowlist changes and commands.
- `POST /pc/usage`: batched usage events.
- Teacher endpoints (teacher auth): list devices, send commands, edit allowlists, report queries.

Lock decision, computed on the server only:
1. Active teacher "lock now" override means locked.
2. Else active teacher "unlock now" override means unlocked.
3. Else locked if not `StudentDailyProgress.unlocked`; unlocked on rest days per `QuotaConfig`.
4. No signed-in student means locked.

Hook: in `daily_quota_service._emit_unlocked`, also notify the student's PC channel so
the PC unlocks within seconds.

### 4.3 Teacher console (React, responsive)

New route under the teacher views with:
- Device list: online/offline, signed-in student, locked/unlocked, active app.
- Per device, per group and all-PCs buttons: lock now, unlock now, send message.
- Allowlist editor (global and per group).
- Report tab (section 6).

## 5. Browser handling

Chrome and Edge are on the default allowlist, but while locked a browser rule limits them
to the platform domain. The guard reads the address bar of the active browser window
through Windows UI Automation and closes the window when the host is not the platform.
The URL is checked locally and never stored or uploaded. This is best-effort: it keeps
the browser from becoming a loophole without needing an extension, but a determined
student could find gaps. If it proves unreliable, the fallback is to remove browsers from
the locked-state allowlist.

## 6. Report

Per student and day: quota met or not and unlock time; minutes locked versus unlocked;
top apps by minutes; seven-day trend. Per group: summary table. Source tables are
`pc_sessions`, `pc_usage_events` and `student_daily_progress`.

## 7. Security and tamper resistance

- Requirement: students use standard (non-admin) Windows accounts. Documented in the install guide.
- Signed binaries; service recovery on failure.
- The agent applies only what the server says; it never decides an unlock itself.
- The device token is scoped to `/pc/*` and cannot call student or teacher APIs.
- A device that stops sending heartbeats while a session is open is shown to the teacher as offline/suspicious.
- Student passwords are never stored on the PC.

## 8. Privacy

Recorded: app name, start and end time, lock state, sign-in and out times. Not recorded:
screenshots, keystrokes, window titles, page contents. A notice is shown at sign-in
because many students are minors; the center should inform parents.

## 9. Error handling

- Server unreachable: keep cached rules for 10 minutes, then lock.
- Sign-in failure: stay locked, show the reason.
- Allowlist empty or malformed: keep the previous valid list.
- Usage upload failure: keep events on disk and retry.
- A killed service: restarted by Windows recovery and the watchdog.

## 10. Testing

- Backend: pytest for the lock-decision function (all precedence cases, rest days, no
  student), device-token scoping, command delivery.
- Agent: unit tests for the allowlist matcher and rule cache, plus a manual test script
  on a Windows VM (sign-in, block, unlock on quota, kill-service recovery).
- Frontend: component tests for the device list and command buttons.

## 11. Delivery order

1. Backend `pc_control` module, migration, lock decision and tests.
2. Windows agent (guard service, then shell app).
3. Teacher console page and report.

Each step is separately usable: step 1 plus 2 already gives working blocking.

## 12. Out of scope (this version)

macOS or Linux agents, native phone apps, Telegram digests, screenshots, remote desktop
view, per-student allowlists (only global and per group), installer auto-update (manual
reinstall first).

## 13. Open question for review

- Student identity is assumed to be platform sign-in on a shared PC. If each PC is instead
  permanently assigned to one student, sign-in can be replaced by an install-time binding.
