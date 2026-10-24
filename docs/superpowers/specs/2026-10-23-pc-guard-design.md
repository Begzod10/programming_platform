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

### 4.1 Windows agent (`pc-agent/`)

Two processes, split by Windows session. A SYSTEM service in session 0 cannot see the
student's desktop, so the service is the authority and the shell is its eyes.

- **Guard service** (Windows Service, LocalSystem): the only authority on the PC.
  - Signs in against the backend, holds the device token in memory only, holds the
    WebSocket, applies lock state, allowlist and commands, and kills violating processes
    (SYSTEM can kill across sessions). Enforcement tick every 2 seconds.
  - Heartbeat every 30 seconds. Rule cache: after 10 minutes without the server the PC
    falls back to locked (a negative cache age, i.e. a clock rollback, counts as expired).
  - Restarts through Windows service recovery: restart after 5 s on every failure. There is
    no second watchdog task.
  - Enables SeDebugPrivilege at start.
  - Usage tracker: gaps over 30 s end the open interval at the last observation; intervals
    are chunked below 12 h. Events carry the session they belong to, each session keeps its
    own token in memory, and the queue (capped at 20,000 events) uploads in batches of at
    most 500. After a service restart, queued usage whose token is gone is dropped, never
    filed under another student.
- **Shell** (WPF, runs as the student in the console session): sign-in screen with a
  privacy notice in Uzbek and Russian, lock banner (always visible while signed in; shows
  remaining lessons while locked), teacher message pop-ups. Every 2 seconds it sends a
  `snapshot` to the service: pids and exe names of windowed processes (UWP apps resolved
  through their CoreWindow), the foreground app, and Chrome/Edge windows with a bare host
  (or `readable: false`). It closes browser windows on the service's `close_window` request
  (WM_CLOSE) and sends `alive` frames. It skips snapshots while the input desktop is not
  "Default".
- **Pipe**: the named pipe `PcGuard.Pipe`. The service launches the shell itself (suspended,
  pins its pid and creation time, then resumes) and accepts only that instance. There is no
  Run key, scheduled task or Startup shortcut for the shell; if the shell dies the service
  relaunches it (at most once per 15 s; a hung shell is killed after about 30 s).
- **Shell protection**: deny-terminate process DACL, restricted token default DACL with an
  OWNER RIGHTS ACE, environment variables `DOTNET_`, `COMPlus_`, `CORECLR_`, `COR_` stripped
  from its environment, and `StartupHookSupport=false` in the published build. The install
  folder is writable only by SYSTEM and Administrators.
- **Fallback**: if no fresh snapshot arrived for 6 seconds (shell missing, hung, other
  desktop or session), the service enforces by process name only. This is stricter for
  third-party apps (background and autostart apps are killed too) and also closes allowlisted
  browsers when a browser host list is active. It is weaker for Windows inbox apps: Notepad
  and similar survive until the shell is back (about 6 to 15 s).
- **Ownership rule**: while locked, a console-session process is never killed if its exe name
  is in the protected set (explorer, dwm, shell hosts such as SearchHost/SearchApp/
  StartMenuExperienceHost/ShellHost/Widgets/LockApp, ApplicationFrameHost, the PC Guard
  binaries), if it is allowlisted, or if it is service-owned (token owner SYSTEM, LOCAL
  SERVICE or NETWORK SERVICE; an unreadable owner counts as service-owned only for a system
  image or an unreadable path). A student's own Notepad or Paint is killed in normal mode.
  In fallback mode system images are spared too.
- **Allowlist matching**: by exe name. An entry with a publisher also compares the exe's
  `CompanyName` file metadata, which is NOT a signature check and can be forged; the default
  allowlist has no publishers.
- **Other desktops**: while the student is on a second desktop, UAC or the lock screen, no
  snapshots arrive and the service uses fallback enforcement without relaunching the shell.
- **Safe Mode**: the installer registers the service for Safe Mode (Minimal and Network),
  best effort and untested.

### 4.2 Backend (module `pc_control`)

Tables (one Alembic migration):
- `pc_devices`: id, hostname, machine_key_hash (unique), group_id (nullable), last_seen_at,
  last_app, created_at. There is no stored online flag: `online` is derived as `last_seen_at`
  within the last 90 seconds.
- `pc_allowlists`: id, group_id (NULL = the global row), entries (exe name, optional
  publisher), updated_by, updated_at.
- `pc_sessions`: id, device_id, student_id, signed_in_at, signed_out_at.
- `pc_usage_events`: id, session_id, app_name, started_at, ended_at, was_locked.
- `pc_commands`: id, scope_type (device, group, all), scope_id, type (lock, unlock, clear,
  message), payload, created_by, created_at. There is no `delivered_at`: message commands
  are pushed to sockets that are connected at that moment and are not queued for offline PCs.

Endpoints:
- `POST /pc/login`: platform credentials plus machine key in, device token and initial state
  out. Students only. Rate limit 120 calls per 60 s per IP (a class shares one NAT address).
  A new login closes the machine's previous open sessions and its sockets (WS code 4001).
- `POST /pc/logout`: ends the session, closes the sockets (4001).
- `GET /pc/state`: current state (also refreshes `last_seen_at`).
- `WS /pc/ws?token=`: first frame is `state`; the agent sends `{type: hb, app}` every 30 s;
  the server stores `last_seen_at` and `last_app`, answers `pong`, then recomputes the state
  and sends a `state` frame whenever it differs from the last one sent on that socket. This
  covers midnight rollover, quota-config changes and missed pushes. Every heartbeat re-checks
  that the token's session is still open, otherwise the socket closes with 4001.
  Server pushes `state` and `message` frames.
- `POST /pc/usage`: batched usage events, all-or-nothing: at most 500 events per batch, each
  event shorter than 12 h with `ended_at` after `started_at`, and no event ending more than
  5 minutes in the future (else 422). Events are attributed to the token's own session. A
  token whose session was closed within the last 24 h is still accepted here (offline-buffered
  usage), and nowhere else.
- Device token: JWT with `sub=pc:<device_id>`, `stu`, `ses`, `typ=pc`, expiry 14 h. It is
  rejected by every student and teacher API, and the `/pc/*` endpoints require it. It dies
  when its session ends (logout or a new login on that machine).
- Teacher endpoints under `/teacher/pc` (teacher auth): `GET /devices`, `PATCH /devices/{id}`
  (set group), `POST /commands`, `GET`/`PUT /allowlist`, `GET /report`.
  Scoping: report access and group-level actions (group commands, group allowlist, assigning a
  device to a group) are limited to the teacher's own groups (403 otherwise). The device list,
  scope `all` and `device` commands and the global allowlist are open to any teacher, because
  lab PCs are shared hardware. A signed-in student is named in the device list only to a
  teacher who teaches that student. Message text is limited to 500 characters. An empty
  allowlist is rejected (422); a group list cannot be cleared back to "global only" through
  the API.
- Report: `GET /teacher/pc/report?from&to&group_id`, at most 31 days. One row per student and
  Tashkent day: `quota_met`, `unlocked_at`, `minutes_locked`, `minutes_unlocked`, top 5 apps
  by minutes. Days are bucketed in Asia/Tashkent; usage events crossing midnight are split.

Lock decision, computed on the server only (`pc_lock_service.compute_state`):
1. No signed-in student means locked (`no_student`), always first.
2. Otherwise the NEWEST applicable `lock`, `unlock` or `clear` command wins, regardless of
   scope (device, the device's group, or all). `clear` ("Resume") removes the override.
   Overrides expire at the end of the Tashkent day in which they were created. A device-scope
   command applies only to the current session (a sign-out/in ends it); group and all
   commands are not session-bound, so a "lock all" sent before class still holds.
3. Else locked unless `StudentDailyProgress.unlocked`; rest days follow `QuotaConfig`.

State frame: `locked`, `reason`, `remaining`, `completed`, `required`, `student`,
`allowlist` (global merged with the device's group list), `browser_hosts`, `server_time`.
`browser_hosts` comes from the setting `PC_PLATFORM_HOSTS` (comma-separated hosts); if it is
empty the browser host rule is disabled and browsers run unrestricted while locked.

Hook: `daily_quota_service._emit_unlocked` also pushes a state frame to the student's PC
channel, so the PC unlocks within seconds. Allowlist and command changes are pushed the same
way.

### 4.3 Teacher console (React, responsive)

Page `frontend/src/views/teacher/pccontrol/` with three tabs, strings in Uzbek and Russian:
- **Devices**: online/offline, signed-in student, locked/unlocked with reason, active app,
  last seen. Per device a group selector (own groups only), and lock, unlock, resume and
  message buttons. A scope picker (one device, one of the teacher's groups, or all PCs);
  lock/unlock for all PCs needs a second confirmation. Students the teacher does not teach
  show as "-". The list refreshes every 5 s and pauses while the browser tab is hidden.
- **Allowlist**: global and per-group editor.
- **Report**: date range and group filter, per-student per-day table, a per-student summary
  (quota days met, 7-day trend), and a note that days and times are Tashkent time.

## 5. Browser handling

Chrome and Edge are on the default allowlist, but while locked and while `PC_PLATFORM_HOSTS`
is non-empty, a browser rule limits them to the platform hosts. The shell reads the address
bar of each Chrome/Edge window through Windows UI Automation (omnibox class
`OmniboxViewViews`) and reports only the bare host; the service compares it to the host list
and has the shell close the window (WM_CLOSE) when it is not allowed. The URL host is checked
locally and never stored or uploaded. Details:
- Empty host list means the rule is disabled (browsers unrestricted while locked).
- A window with no address bar at all (app-mode, PWA, popup) is reported `readable: false`
  after 2 consecutive snapshots (about 4 s; Chrome builds its UI tree lazily) and is closed
  while a host list is active. If the bar exists but cannot be read, the last host for that
  window is reused; internal pages (`chrome://`, new tab) are allowed.
- Only Chrome and Edge are covered by the host rule. Other allowlisted browsers are not.
- This is best-effort and depends on browser UI internals that can change with an update. If
  it proves unreliable, the fallback is to remove browsers from the locked-state allowlist.

## 6. Report

Per student and day: quota met or not and unlock time; minutes locked versus unlocked; top
five apps by minutes; per-student summary in the console. Days are Tashkent days. Source
tables are `pc_sessions`, `pc_usage_events` and `student_daily_progress`. Open usage events
(no end time) are not counted; a session spanning midnight with no events adds no row for the
second day. The report is limited to the calling teacher's students and 31 days.

## 7. Security and tamper resistance

- Requirement: students use standard (non-admin) Windows accounts. An administrator can stop
  the service and bypass everything. The installer prints a best-effort warning when the
  signed-in user looks like an administrator; it can miss domain, Azure AD and nested-group
  administrators, so verify the accounts yourself.
- The service runs as SYSTEM, is restarted by Windows recovery, and its folder is writable
  only by SYSTEM and Administrators. The build scripts have no code-signing step.
- The agent applies only what the server says; it never decides an unlock itself.
- The device token is scoped to `/pc/*` (see 4.2), lives 14 h, is kept in memory only, and is
  revoked by logout or a new login on the machine.
- The shell is launched only by the service and protected as described in 4.1; the pipe
  accepts only that instance.
- A device that stops sending heartbeats is shown as offline within 90 s.
- Student passwords are never stored on the PC or in the backend by this feature. The
  password travels from the shell to the service as a .NET string and cannot be zeroed in
  memory.
- Publisher entries in the allowlist are metadata matches and spoofable (see section 14).

## 8. Privacy

Recorded and sent to the backend: app (exe) names, start and end times, lock state, sign-in
and sign-out times. Not recorded: screenshots, keystrokes, window titles, page contents,
URLs. The browser host is read in the shell, checked by the service, and never stored or
sent. Logs: the shell log (per student, about 512 KB, rotated) holds exception type names and
stack traces only, never messages, titles, URLs or passwords. Local data in
`%ProgramData%\PcGuard` (machine key, rule cache, usage queue) is readable only by SYSTEM and
Administrators. A notice in Uzbek and Russian is shown at sign-in because many students are
minors; the center should inform parents. These claims are enforced by design, but the
privacy search (checklist tests 87 and 88) has not been run.

## 9. Error handling

- Server unreachable: keep cached rules for 10 minutes, then lock. Reconnect backoff 1, 2, 5,
  10, 30 s; a silent socket is dropped after about 75 s.
- Sign-in failure: stay locked, show the reason in Uzbek and Russian (wrong password, not a
  student, too many attempts, backend unreachable).
- Allowlist empty or malformed: the server rejects an empty list (422) and the agent keeps
  the previous valid list.
- Usage upload failure: a 422 drops the batch; 5xx or offline keeps events and retries.
- A dead or revoked token (403, or 4001 on the socket) signs the student out on the PC.
- A killed service: restarted by Windows recovery after 5 s. A killed or hung shell: relaunched
  by the service, with name-only enforcement in between.
- The data folder cannot be secured: the service runs locked with the default allowlist and
  writes nothing to disk.

## 10. Testing

- Backend: pytest for lock decision (precedence, rest days, no student, expiry, session
  binding), device-token scoping, WebSocket flow, usage rules, allowlist, commands, scoping
  and report.
- Agent: unit tests of the pure logic in `PcGuard.Core` (matcher, rule cache, usage tracker
  and queue, planner, pipe protocol, browser rule, ownership, shell security, UI strings).
  The Windows service, shell and scripts are only compile-checked.
- Frontend: component tests for the console tabs, in `frontend/src/__tests__/`.
- Manual: the 93-test Windows VM checklist in `pc-agent/README.md`.

## 11. Delivery order

1. Backend `pc_control` module, migration, lock decision and tests.
2. Windows agent (guard service, then shell app) and installer scripts.
3. Teacher console page and report.

Steps 1 and 2 together give working blocking; the console makes it usable by teachers.

## 12. Out of scope (this version)

macOS or Linux agents, native phone apps, Telegram digests, screenshots, remote desktop view,
per-student allowlists (only global and per group), installer auto-update (manual
reinstall), Authenticode signature checks, graceful close of violating apps (they are killed
at once), queued delivery of messages to offline PCs, clearing a group allowlist back to
"global only", restricting browsers other than Chrome and Edge.

## 13. Resolved question

Student identity: students sign in on the PC with their platform account, and this is how it
is built. A PC permanently bound to one student (install-time binding) was not implemented.

## 14. Verification status and known limitations

Tested: backend pytest (105 PC Guard tests; the whole backend suite had one failure,
`test_auth.py::test_synced_student_username_upgrades_from_synthetic_on_relogin`, a pre-existing
shared-test-DB collision unrelated to this feature); agent Core unit tests (386); frontend
(49 suites, 292 tests, also under other time zones).

Never run: the Windows service, the shell and the installer scripts (`install.ps1`,
`uninstall.ps1`, `publish.ps1`). They compile (0-warning build) but nothing has executed on
Windows. The 93-test VM checklist in `pc-agent/README.md` must be run before any rollout;
treat enforcement, shell protection, the Safe Mode registration, browser address-bar reading
and the installer rollback as unverified until then.

Accepted or parked risks:
- A renamed copy of an allowlisted exe name passes the name match (no signature check); a
  publisher entry is a spoofable metadata match.
- Allowlisted interpreters (`python.exe`, `node.exe`) own any windows they open (pygame,
  Electron), so those windows are not closed.
- WSL, Docker and VM guests are not seen; only the host-side window is checked.
- Same-user code injection into the shell is only partly mitigated; a compromised shell could
  under-report windows.
- An administrator can stop the service; Safe Mode behaviour is untested.
- Violators are killed with no chance to save work.
- Fallback mode is stricter for third-party apps (can kill autostart apps right after
  sign-in) and weaker for inbox apps.
- Parked pending a Windows VM: an unreadable token owner on a non-system image is treated as
  student-owned, which depends on SeDebugPrivilege working (an enable failure is logged as an
  error); some user-token inbox hosts (werfault, smartscreen, openwith, dllhost,
  credentialuibroker, pickerhost, systemsettings) are not protected and could be closed when
  windowed; `widgets.exe` outside %SystemRoot% may be killed.
- Backend minors: a first-login race on a new machine key can return 500; the token is valid
  up to 14 h without re-checking that the student is still active; a socket on a replaced
  session lives up to about 30 s until its next heartbeat; pushed state frames are not tracked
  per socket, so a state that flips back within one heartbeat window can show stale until the
  next change; the device list computes state per device (fine at lab scale); moving a device to another group does not clear
  the old group's commands; the report loads
  events in memory.
- Console minors: a hung poll request can suppress later polls until a manual refresh or
  command (no request timeout); no retry button after a load error.

Deploy warning: pushing branch `server` auto-deploys the backend to production
(`.github/workflows/deploy-backend.yml`), which exposes `/pc/*` and `/teacher/pc/*`. Set
`PC_PLATFORM_HOSTS` in the server's own `.env` first; the deploy does not touch `.env`, and an
empty value silently disables the browser rule. Nothing has been pushed.
