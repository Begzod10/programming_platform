# PC Guard: student PC blocking tied to the daily quota

Date: 2026-10-23
Status: implemented; Windows components untested (see section 14)

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
| Teacher powers | Lock/unlock now, resume, edit allowlist, live status, send message, one-time maintenance code for one PC |
| Report | Teacher dashboard in the platform (no Telegram digest in this version) |
| Monitoring depth | App name and duration (each usage row carries `was_locked`), plus session sign-in/out times; there is no lock/unlock event log. No screenshots, keystrokes or page contents |
| Student identity | Student signs in on the PC with their platform account (built that way) |

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

Implemented and unit-tested at the logic level; the Windows service, shell, ACLs and installer have not yet been run on Windows (see section 14). The agent requires an https backend URL (the installer allows http only for localhost); the password and token travel over it.

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
    most 500. Startup purges the whole queue (a token is memory-only), so usage buffered while
    offline or before a service restart or reboot is lost and reports undercount; it is
    never filed under another student.
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
- **Shell token (changed 2026-11-05, real-PC bug)**: the shell runs with the console user's
  ORDINARY token from WTSQueryUserToken. Nothing inside the token is changed (no custom default
  DACL, no privilege, integrity, group or session change, no restricted token) and the process and
  thread get default security (no deny-terminate/suspend/inject ACEs, no owner change, no OWNER
  RIGHTS entry). The token is duplicated only to give the token OBJECT an explicit descriptor
  (SYSTEM, Administrators, the user: `ShellTokenSecurity.TokenObjectSddl`) so the shell can open its
  own token like any normal process. Kept: environment variables `DOTNET_`, `COMPlus_`, `CORECLR_`,
  `COR_` stripped from its environment, `StartupHookSupport=false` in the published build, the
  suspended start and pin (the pipe accepts only that instance: pid + creation time + installed image
  path), and the install folder writable only by SYSTEM and Administrators.
  Why the earlier hardening was removed: it restricted the token's default DACL so the user got only
  query/synchronize/read-control on every object the shell created. For a UAC administrator (split
  token, Administrators deny-only) or a standard user, every NAMED object the shell or Windows created
  for it without an explicit descriptor became unusable: the single-instance mutex got ACCESS_DENIED
  and Windows text input (TSF, `TF_CreateInputProcessorProfiles`) failed with E_OUTOFMEMORY, which
  WPF raised as OutOfMemoryException in the TextBox constructor, so the sign-in window was never
  built (shell.log of 2026-11-05: `single-instance mutex AccessDenied (Win32 5)`, then the
  OutOfMemoryException stack, `Administrators enabled: unknown`). The built-in Administrator (BA
  enabled, BA had full control in that DACL) was not affected. Hardening the shell against
  termination is not required (see 7). The single-instance mutex
  `Local\PcGuard.Shell.SingleInstance` uses default security. If the name exists or cannot be
  opened, the shell exits (code 0) only when another process with this install's shell image runs in
  the same session; otherwise the name is squatted or stale and the shell runs anyway (a
  user-creatable name must never suppress the lock screen; the pipe pin still rejects any instance
  the service did not launch).
- **Shell UI fallback (defence in depth)**: if building or showing the sign-in window, overlay or
  banner throws during startup (OutOfMemoryException, COMException, anything), the shell logs the
  full exception (type, HRESULT, stack, inner exceptions; never messages), shows a minimal
  full-screen topmost lock window built in code from a Border and a TextBlock only (no text input,
  so no TSF; fixed uz/ru notice; nobody can sign in through it), or no window if even that fails,
  and in every case starts the pipe client, so the service sees a live shell and keeps
  window-aware enforcement. Not covered: uncatchable crashes (stack overflow, access violation,
  native fail-fast), failures before `OnStartup`, and dialogs opened later (logged by the dispatcher
  handler; the shell keeps running).
- **Shell startup failures**: an exception before the shell is fully initialised (pipe client
  started; a window failure is handled by the UI fallback above), or a startup that does not complete within 20 s (watchdog), ends the shell
  with exit code 3 or 4 after a shell.log line; it never stays alive without windows. After startup,
  UI exceptions are logged and the shell keeps running. shell.log carries a one-line startup trail
  (pid, session, whether Administrators is enabled, single-instance result with Win32 code, windows
  created, pipe connect attempts with Win32 codes, rate-limited) and no personal data.
- **Relaunch back-off**: a shell that ends or is killed as unresponsive without ever connecting
  counts as a failed start; the next launch waits 15, 30, 60, 120, then 300 s after the failure
  (reset by a connection, a console session change, or nobody signed in). One Warning per episode
  names `%LocalAppData%\PcGuard\shell.log`. Enforcement is unchanged: name-only fallback after the
  startup grace for as long as no shell reports. The pipe server logs the exact rejection reason
  (no pin, other pid, creation time unreadable or different, wrong session) with pids only.
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
- **Extra allowed apps (PC-local)**: `Allowlist:ExtraApps` in the installed `appsettings.json`
  (written by `install.ps1 -ExtraAllowedApps` / `Setup-PcGuard.exe --allow-app`, default empty,
  read at service start) lists exe names kept running on that PC. Each must be a bare name ending
  in `.exe`, 5-64 characters of ASCII letters, digits, `.`, `-`, `_`; at most 16; invalid or
  surplus entries are ignored with a warning (name only). The service merges them as
  publisher-free entries into the effective allowlist in every state (signed out, defaults,
  student rules, offline cache, fail-closed) where the effective rules are built, before the
  planner; they are never stored in the rule cache or sent to the backend. Protected-process and
  browser-host handling is unchanged. An upgrade without the parameter keeps them.
- **Other desktops**: while the student is on a second desktop, UAC or the lock screen, no
  snapshots arrive and the service uses fallback enforcement without relaunching the shell.
- **Safe Mode**: the installer registers the service for Safe Mode (Minimal and Network),
  best effort and untested.
- **Maintenance mode (teacher code)**: the only case in which enforcement is suspended without
  the server's lock decision, and it still needs the server (see 4.4). The shell's
  "Texnik kod" / "Код обслуживания" link sends a 6-digit code; the service checks it with the
  backend (https only) and, on success, treats the rules as unlocked for the 15, 60 or 240
  minutes the backend returned, measured on a monotonic clock. In memory only.
- **Recovery code (offline escape)**: see 4.5. Next to "Texnik kod", the link "Tiklash kodi" /
  "Код восстановления" sends an install-time, single-use code that the service checks locally;
  on success PC Guard stops enforcing, deletes the code's hash, sets its own start type to
  Disabled, ends every shell it launched and stops.

### 4.2 Backend (module `pc_control`)

Tables (one Alembic migration):
- `pc_devices`: id, hostname, machine_key_hash (unique), group_id (nullable), last_seen_at,
  last_app, created_at, maintenance_until (nullable; set on a successful maintenance redeem).
  There is no stored online flag: `online` is derived as `last_seen_at`
  within the last 90 seconds.
- `pc_allowlists`: id, group_id (NULL = the global row), entries (exe name, optional
  publisher), updated_by, updated_at.
- `pc_sessions`: id, device_id, student_id, signed_in_at, signed_out_at.
- `pc_usage_events`: id, session_id, app_name, started_at, ended_at, was_locked.
- `pc_commands`: id, scope_type (device, group, all), scope_id, type (lock, unlock, clear,
  message), payload, created_by, created_at. There is no `delivered_at`: message commands
  are pushed to sockets that are connected at that moment and are not queued for offline PCs.
- `pc_maintenance_codes` (separate migration; `maintenance_until` was added by a third one, `e4a9c1d7b250`): id, device_id, code_hash (HMAC-SHA256 with a
  per-code salt), salt, minutes, created_by_user_id, created_at, expires_at, used_at,
  failed_attempts. See 4.4.

Endpoints:
- `POST /pc/login`: platform credentials plus machine key in, device token and initial state
  out. Students only. Rate limit 120 calls per 60 s per IP (a class shares one NAT address).
  A new login closes the machine's previous open sessions and its sockets (WS code 4001).
- `POST /pc/logout`: ends the session, closes the sockets (4001).
- `GET /pc/state`: current state (also refreshes `last_seen_at`).
- `POST /pc/maintenance/redeem`: no token (a signed-out PC knows only its machine key);
  maintenance code check, contract in 4.4.
- `WS /pc/ws?token=`: first frame is `state`; the agent sends `{type: hb, app}` every 30 s;
  the server stores `last_seen_at` and `last_app`, answers `pong`, then recomputes the state
  and sends a `state` frame whenever it differs from the last one sent on that socket. This
  covers midnight rollover, quota-config changes and missed pushes. Every heartbeat re-checks
  that the token's session is still open, otherwise the socket closes with 4001.
  Server pushes `state` and `message` frames.
- `POST /pc/usage`: batched usage events, all-or-nothing: at most 500 events per batch, each
  event at most 12 h long with `ended_at` after `started_at`, and no event ending more than
  5 minutes in the future (else 422). Events are attributed to the token's own session. A
  token whose session was closed within the last 24 h is still accepted here (offline-buffered
  usage), and nowhere else.
- Device token: JWT with `sub=pc:<device_id>`, `stu`, `ses`, `typ=pc`, expiry 14 h. It is
  rejected by every student and teacher API, and the `/pc/*` endpoints require it. It dies
  when its session ends (logout or a new login on that machine).
- Teacher endpoints under `/teacher/pc` (teacher auth): `GET /devices` (includes `maintenance_until`, ISO, or null when unset or past), `PATCH /devices/{id}`
  (set group), `POST /commands`, `GET`/`PUT /allowlist`, `GET /report`,
  `POST /devices/{id}/maintenance-code` (4.4).
  Scoping: report access and group-level actions (group commands, group allowlist, assigning a
  device to a group) are limited to the teacher's own groups (403 otherwise). The device list,
  scope `all` and `device` commands and the global allowlist are open to any teacher, because
  lab PCs are shared hardware: any teacher may lock, unlock or message any device and may set
  a device's group to null or to one of their own groups, even if it is now in another
  teacher's group; only the target group is checked. For allowlist, command and device
  endpoints an unknown group is 404 and a foreign one 403; the report returns 403 for both.
  Flow-owned students count as the teacher's students for the report and device-list
  visibility, while group actions require `Group.teacher_id`. A signed-in student is named in the device list only to a
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
  last seen. Per device a group selector (own groups only) and Lock/Unlock/Resume (disabled
  while the PC is offline). An all-PCs bar and a group bar (own groups) offer the same three
  actions; lock/unlock for all PCs needs a second confirmation. Messages (max 500
  characters) are sent from a separate box with a target picker (one device, a group, or all).
  Students the teacher does not teach show as "-". The list refreshes every 5 s, pauses while
  the browser tab is hidden and reloads after a command or when the tab becomes visible;
  there is no manual refresh button.
- **Allowlist**: global and per-group editor.
- **Report**: date range and group filter, per-student per-day table, a per-student summary
  (`met/days`: quota days met out of the days with data in the range; the default range is
  the last 7 days ending today), and a note that days and times are Tashkent time.

### 4.4 Maintenance mode (teacher code)

Purpose: a way to use a locked PC (for example for repairs) without stopping PC Guard and
without any Windows account or password.

Precondition: the PC must already appear in the teacher console, i.e. a student has signed in
on it at least once with its current `machine.key` (a `pc_devices` row is created only by a
successful student sign-in, and redeem matches that row's machine key). A freshly installed PC,
a PC whose `machine.key` was regenerated (read error, quarantined data folder; the console may
still show the stale row with the same hostname) and a PC running fail-closed with a temporary
key can NOT be unlocked by code; the only recovery for them is the recovery code (4.5, if one
was set at install), Safe Mode or the Cleanup tool.

Flow:
1. A teacher creates a code for one device in the console:
   `POST /teacher/pc/devices/{id}/maintenance-code` body `{"minutes": 15|60|240}` (API default 60; the console preselects 15)
   -> 201 `{"code": "123456", "expires_at": ..., "minutes": ...}`. Recommended choice: 15 minutes
   (the teacher cannot end maintenance remotely yet, see 6). The code is 6 digits, lives
   5 minutes, is single use, supersedes older codes for that device (if a race leaves several active, redeem accepts any of them and retires all on success), and is stored only as an
   HMAC; at most 10 codes per hour per device (429). Any teacher may issue one (shared lab
   hardware). Nothing is pushed to the PC.
2. On the PC the "Texnik kod" / "Код обслуживания" link (sign-in screen, and the name banner
   while a student is signed in) opens a dialog with one 6-digit field (undo disabled, so a
   cleared code cannot be restored with Ctrl+Z). The shell sends
   `{"t":"maintenance_redeem","id":7,"code":"123456"}` over the pipe, `id` being a fresh request
   id; only the pinned shell instance is accepted (existing pipe gate), so a fake shell cannot
   send it. The service keeps only the latest pending request; one it replaces before checking
   it is answered `admin_result` ok=false, error `error`, with the replaced id.
3. The service, on its command loop (serialised with sign-in; the enforcement tick is not
   blocked), checks its local limiter (at least 1 s between attempts; 5 consecutive
   `invalid_code` failures lock code entry for 10 minutes), then the shape `^[0-9]{6}$` (anything
   else is `invalid_code` without a network call), then, only if the backend base URL is https
   (otherwise `error`, with a warning in the event log and no network call), calls the token-less
   `POST /pc/maintenance/redeem` body `{"machine_key": "<machine.key GUID>", "code": "123456"}`
   with a 10 s timeout. 200 `{"minutes": 15|60|240}` is success (any other value is treated as
   an error); every failure is 403 `{"detail":"invalid_code"}` (wrong, expired, used, other
   device); 429 means the backend's own block (5 failures per machine key -> 10 minutes, counted only for
   machine keys of known devices; unknown keys create no state) or the flood limit of 120
   requests per minute per client IP on this endpoint (first `X-Forwarded-For` entry as in login;
   shared by the lab or dodged by a spoofed header, so a coarse guard only). There is deliberately
   NO per-IP failure block, because the lab PCs share one public IP and one student could
   otherwise turn codes off for the whole lab; the per-code limit of 5 in the database bounds
   guessing); no answer means offline. The code is consumed on success. If the answer to a
   consumed code is lost (timeout, network drop), the PC shows offline, stays locked and the code
   is gone: the teacher issues a new one.
4. The service answers the shell
   `{"t":"admin_result","id":7,"ok":...,"error":...,"retry_seconds":n}` (the request's id)
   with `error` one of `invalid_code`, `locked_out` (with `retry_seconds`), `rate_limited`,
   `offline`, `error`, and on success sends `{"t":"maintenance","active":true,"until_utc":...}`
   (also to every newly connected shell and on every change). The shell ignores an
   `admin_result` whose id is not its current pending request (superseded, timed out after 15 s,
   or from a dialog that was closed), so a late answer never shows up in a later dialog.
5. While active the effective rules are the server's rules with `locked=false`, reason
   `maintenance`: no kills, no `close_window`, no name-only fallback kills. State frames (a
   teacher's "lock now" included) and usage keep arriving but cannot re-lock; when maintenance
   ends the current rules apply at once. The shell hides the sign-in screen and shows a banner
   "Texnik rejim HH:mm gacha" / "Режим обслуживания до HH:mm" (local time) with an End button.
   Sign-in does NOT work during maintenance: the sign-in screen is hidden. A student already
   signed in keeps working; a signed-out PC is simply open and nobody signs in until
   maintenance ends.
6. It ends at expiry, on `{"t":"admin_end"}` from the shell (no code needed: ending only
   re-locks), and when the service stops. The deadline is kept on a monotonic clock
   (`Environment.TickCount64`), so wall-clock steps (NTP, an administrator) neither end it early
   nor extend it; the wall clock only gives the displayed end time and the audit text. It is
   never persisted, so a restart or reboot re-locks. A window can last up to 4 hours and the
   teacher has no remote "end maintenance" action yet (deferred); the console keeps showing the
   server state and, from `maintenance_until`, a "Maintenance until HH:mm" badge. The badge is the
   granted window: it does not clear if the PC ends maintenance early.

Audit: log lines only. Windows Application event log entries for start (minutes, end time in
UTC), end (reason), rejected codes (n of 5), the local lockout and the refusal over http; the
backend writes log lines for issue (teacher, device, minutes) and redemption. There is no
durable audit table (code rows do not record why they were consumed and are deleted after
7 days). The code itself is never logged, stored or shown in an exception message on the PC.

Accepted limitation: the check needs the backend and a known device. With the backend
unreachable, or for a PC the console does not know with its current machine key (see the
precondition), the PC stays locked and the only way out is the recovery code (4.5, if one was
set at install; it switches PC Guard off on that PC), or Safe Mode or the Cleanup tool (both
need a Windows administrator). Because codes are often read out loud, a code should be issued only when the
person at that PC is ready to type it.

### 4.5 Recovery code (offline escape)

Purpose: the last way out when a PC is stuck on the full-screen lock and nothing else works
(backend down, so no teacher code; Task Manager hidden behind the topmost lock window). Found
during real-PC testing. It does not unlock temporarily: it switches PC Guard off on that PC,
and it works once.

- Set at install, interactive Setup only: typed hidden (Console.ReadKey with intercept,
  Backspace) and confirmed; 12-128 printable ASCII characters (inner spaces allowed, no
  leading/trailing space), at least 6 distinct characters, not 6 digits (teacher code shape),
  and at least 8 characters left after removing guessable parts (common uz/ru/en words such as
  maktab, kompyuter, admin, parol, password, school anywhere in the code; years 19xx/20xx;
  keyboard runs of 4+; alphabet/digit runs of 4+; a character 3+ times in a row; any repeated
  block of 3+). Mismatch or invalid: asked again, 3 failed tries abort the install with nothing
  changed; an empty answer after a failed try asks "Install without a recovery code? (y/N)".
  Silent installs set none (`--no-recovery-code` explicit, otherwise a warning). Never accepted
  on the command line or from environment variables.
- Optional default code file (one known code for many installs, never hardcoded): if
  `default-recovery-code.txt` is in the package root next to Setup-PcGuard.exe, Setup reads it
  (Core `DefaultRecoveryCode`) only when the package folder passed the admin-only ACL check and
  `--allow-writable-package` is NOT given (otherwise: ignored, said so, not read); the file must
  be a regular file (no reparse point), at most 130 bytes, with no allow ACE for Users,
  Authenticated Users, Everyone or INTERACTIVE that grants read or write-like rights; content
  plain printable ASCII on one line, exactly one trailing CR LF / LF / CR removed, no other
  trimming, then the normal code rules. Bytes and chars are read into buffers that are zeroed
  after hashing; the hash takes the same `recovery-hash.in` path. Interactive: "A default
  recovery code file was found (default-recovery-code.txt). Press Enter to use it, type another
  code, or type - (a single dash) to install without a recovery code:" (hidden; Enter = file,
  `-` = none, otherwise a typed code confirmed as usual). An invalid file prints the reason only
  and falls back to the normal question. Silent: `--default-recovery-code` (no value; exit code
  64 if missing/ignored/invalid; exclusive with `--no-recovery-code`); without it a silent
  install still sets none. Summary: "set (from default-recovery-code.txt)" / "set (typed)" /
  "NOT set". publish.ps1 and tools/package-zip.sh fail if the file is present; it is in
  .gitignore.
- Stored as `pbkdf2-sha256$<iterations>$<salt b64>$<hash b64>` (PBKDF2-HMAC-SHA256, 310000
  iterations, 16-byte random salt, 32-byte hash) computed by Setup (Core `RecoveryCode.Hash`,
  char buffers zeroed afterwards). The hash is never on a command line (Windows PowerShell 5.1
  logs its command line in events 400/600 of the "Windows PowerShell" log, which standard users
  can usually read): Setup writes it to `recovery-hash.in` in its admin-only temp folder and
  passes `install.ps1 -RecoveryCodeHashFile <path>`. install.ps1 requires a local absolute path
  with no reparse point in the chain, an admin-only folder and file (owner and ACL), at most
  136 bytes and a valid hash, before changing anything; it then wipes and deletes the file and
  writes `%ProgramData%\PcGuard\recovery.hash` (folder and file owner Administrators, SYSTEM
  and Administrators only, untrusted pre-existing folder moved aside FIRST, before any existing
  file is read). An existing recovery.hash is read only if trusted (admin-only, no link,
  <= 136 bytes, well formed), and kept on an upgrade only if the old service is not Disabled;
  `-ClearRecoveryCode` removes it; a failed install restores the previous one after validating
  it again (never one of a Disabled service). A new code resets recovery.attempts.
- Use: shell dialog (PasswordBox, cleared right after reading; text outside 0x20-0x7E is refused
  locally with a "switch the layout to EN" hint, not sent, not counted) -> pipe
  `recovery_release {id, code}` (code redacted in ToString) -> `recovery_result {id, ok, error:
  invalid_code | locked_out | not_configured | error, retry_seconds}`, same request-id
  convention as `admin_result`. Pinned shell only (existing pipe gate).
- Service: no trusted `recovery.hash` (missing, data folder not secured, link, other owner or
  ACL, malformed) -> not_configured (not counted). Otherwise the persistent
  `RecoveryAttemptLimiter` (Core, injectable store): 1 s spacing; 5 failures -> lockout of 10
  minutes, then 1 hour, then 24 hours each further time; state in `recovery.attempts` (admin-only
  data folder, same trust rules as recovery.hash), loaded at service start; every attempt is
  persisted as a failure BEFORE verification (power loss still counts; a failed write refuses
  the attempt); a success deletes the file and resets the escalation; an untrusted or corrupt
  file at start means a 24 h lockout (logged, written back); a file that disappears while
  running never shortens a lockout. Then `RecoveryCode.Verify` (constant-time compare, false
  for malformed values, never throws) on a worker thread, one verification at a time. On
  success: an internal flag stops enforcement and kills at once, the event log gets the
  acceptance, recovery.hash is overwritten and deleted (single use), ChangeServiceConfigW sets
  start=Disabled, the shell gets `recovery_result ok` and `released`, after 1.5 s the service
  terminates every PcGuard.Shell.exe it launched in any session (remembered pid + creation time,
  or this install's image), and the host stops cleanly. If ChangeServiceConfigW fails the service
  does NOT stop: it stays released (no enforcement), sends the shell a uz/ru notice (8 s before
  `released`), logs the error and retries every 30 s, stopping once it succeeds. Failures log
  the failure count only. The code and the hash are never logged.
- Shell: every pipe connection's server is checked (GetNamedPipeServerProcessId against the
  SCM's process id of PcGuard from QueryServiceStatusEx); a provably different server is
  disconnected and never heard; if the check cannot be made the connection is used but
  `released` is ignored. After a lost connection the shell exits when the SCM reports PcGuard
  stopped AND Disabled (read-only QueryServiceStatusEx / QueryServiceConfig).
- After a release the PC stays unprotected until Setup install / install.ps1 runs again with a
  new code (it deletes the Disabled service and creates a new Automatic one; the old code is
  gone) or an administrator sets the service back to Automatic (then without a code).
  uninstall.ps1 and Cleanup handle a Disabled service.

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
- A null host is allowed: `ExtractHost` returns null for every non-http(s) scheme (`file:`,
  `data:`, `view-source:`, `about:blank`, `javascript:`) and for dotless text, so such pages
  stay open while locked. Subdomains of a listed host are allowed.
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
- The agent applies only what the server says; it never decides an unlock itself. The one
  exception, maintenance mode (4.4), is also authorised by the server: a single-use 6-digit code
  that a teacher issued for this device, valid 5 minutes, checked by the backend; the PC adds a
  1 s spacing and a 10-minute lockout after 5 wrong codes, the backend blocks a machine key
  after 5 failures (no per-IP block: a lab shares one IP) and burns a code after 5 wrong
  guesses. The code is sent only over https. Maintenance is time-limited (15, 60 or 240
  minutes, set by the server, on a monotonic clock), memory-only (a service restart re-locks),
  cannot yet be ended remotely, and audited by log lines only. Its weak points: a code read aloud can be used by anyone at that PC within
  5 minutes, and a 6-digit code is guessable only within those limits.
- The device token is scoped to `/pc/*` (see 4.2), lives 14 h, is kept in memory only, and is
  revoked by logout or a new login on the machine.
- The shell is launched only by the service with the user's ordinary token (4.1); the pipe
  accepts only that instance. Threat model of the shell process: the student CAN end, suspend or
  inject into it like any of their own programs. That gains nothing that matters: the service
  relaunches it (MinLaunchInterval 15 s; back-off up to 5 min only for shells that never connect), a
  hung or suspended shell is killed after about 30 s, and while no shell reports the stricter
  name-only fallback closes every non-allowlisted third-party app (and allowlisted browsers while a
  host list is active); nobody can sign in meanwhile, so the PC stays locked. Residual, accepted: in
  fallback the Windows inbox apps under %SystemRoot% are spared, so a student who keeps ending the
  shell can keep such an app (Notepad) open; a shell under the student's control can under-report
  windows, which only pushes enforcement towards the same name-only rules. The earlier
  deny-terminate process DACL and restricted token default DACL were removed on 2026-11-05 because
  they broke the shell for UAC administrators and standard users (4.1).
- A device that stops sending heartbeats is shown as offline within 90 s.
- Student passwords are never stored on the PC or in the backend by this feature. The
  password travels from the shell to the service as a .NET string and cannot be zeroed in
  memory.
- Publisher entries in the allowlist are metadata matches and spoofable (see section 14).
- Recovery code (4.5), threat model: it is a deliberate offline kill switch. Anyone who knows
  the code can switch PC Guard off on that PC (no backend, no teacher involved), so it must be
  strong and unique per PC and never the Windows password. Online guessing is bounded by the
  persistent limiter (5 wrong codes -> 10 min, 1 h, then 24 h lockouts; kept in recovery.attempts,
  so neither a service restart nor a reboot, which a standard user CAN cause, resets it; at most
  about 15 guesses on the first day and 5 a day after that). The stored hash is readable only by
  SYSTEM and Administrators (an administrator can bypass PC Guard anyway) and never appears on a
  command line or in a PowerShell log (passed as an admin-only file); with the hash, guessing is
  offline and only PBKDF2 (310000 iterations) and the code rules slow it down. A fake shell
  cannot send a release (pipe pin); a student cannot plant a `recovery.hash` or
  `recovery.attempts` (admin-only folder; the service and install.ps1 refuse a file or folder
  with any other owner or ACL, install.ps1 quarantines an untrusted folder before reading it and
  never restores an unvalidated hash). The code is single use: the release deletes the hash and
  a reinstall over a Disabled service never keeps one. The typed code is exposed in the
  student's session (a low-level keyboard hook needs no rights; an allowed remote-control or
  screen-recording app; shoulder surfing), which is why it is single use. A pipe-name squatter
  (service down) is detected by the shell (server pid != the SCM's service pid) and cannot make
  it exit. The plain code is never on disk, on a command line, in a log or an exception
  message. Residual: a release is recorded only in the PC's event log (no console audit, no
  remote end), an administrator with physical access can still remove PC Guard other ways, and
  the code is a .NET string in the shell and service memory (and the hash in Setup's).
- Default recovery code file (4.5), accepted risk: the code sits in plain text on the
  administrator's media; anyone who can read the package folder (or a zip the administrator
  put it into) can switch PC Guard off on every PC installed with it. Mitigations are
  procedural (delete the file after installing or keep it on an admin-only drive; unique typed
  codes for student PCs, the default code only on test/admin PCs) plus: read only from a package
  folder that passed the admin-only check, never with --allow-writable-package, file ACL without
  standard-user read/write, no links, size cap, never echoed/logged/on a command line, never
  packaged (build guards, .gitignore). Single use still holds per PC (a release burns that PC's
  hash; a reinstall with the file re-applies the same code), so one use in front of students
  must be treated as exposing the code for every PC that has it.
  Packaging never includes the file unless the owner opts in with `tools/package-zip.sh --default-code-file` (separate `-WITH-DEFAULT-CODE` zip, confirmation prompt, file outside the repo); that zip is as sensitive as the code itself.
- Extra allowed apps (4.1) are local and administrator-configured (the install folder is
  admin-writable only) and bypass the lock for that PC only; the server and the teacher console
  do not see them. Adding remote-control software lets someone at the PC use it while the PC is
  locked (and lets anyone with its access details control the PC). Use it only on test/admin PCs.
- Startup grace (accepted trade-off): from service start until the first shell has connected and
  reported (its first snapshot or alive) or 30 s have passed, whichever comes first, the name-only
  fallback kills and closes nothing; the shell is still launched as usual. Without it every boot or
  restart killed all non-allowlisted user programs before the sign-in screen could appear (seen on
  a real PC). So for up to 30 s after a service start a locked PC is not enforced until the shell
  connects; the sign-in screen and window-aware enforcement start as soon as it does. Pure logic in
  Core (`StartupGrace`, monotonic clock, latched: it never comes back once over). It covers only
  "no shell ever connected since this service process started": a shell that connected once and is
  then killed, hung or stale gets no grace, so attacking the shell gains no time. A standard user
  cannot restart the service to renew it.

## 8. Privacy

Recorded and sent to the backend: app (exe) names, start and end times, lock state, sign-in
and sign-out times. Not recorded: screenshots, keystrokes, window titles, page contents,
URLs. The browser host is read in the shell, checked by the service, and never stored or
sent. Logs: the shell log (per student, about 512 KB, rotated) holds exception type names and
stack traces only. The service writes to the Windows Application event log: names of killed
executables ("Terminated <exe>"), and some error entries that include exception messages
(pipe, shell-launch and data-folder errors). No log call writes passwords, tokens, URLs or
window titles (checked by reading the log calls); checklist test 87 verifies it on a PC.
Maintenance mode adds audit entries (start with minutes and end time, end with reason,
rejected-code count, lockout, http refusal); the maintenance code is never logged or written to disk
(checklist test 132). Local data in
`%ProgramData%\PcGuard` (machine key, rule cache, usage queue; the queue is purged at service start) is readable only by SYSTEM and
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
- Maintenance code: wrong, expired or used codes show one message; the backend unreachable
  (or no answer within 10 s) shows "no connection" and the PC stays locked (the recovery code,
  if set, Safe Mode or the Cleanup tool is then the only way out); backend 429 and the local lockout show "too many
  attempts" (the local one with a countdown).

## 10. Testing

- Backend: pytest for lock decision (precedence, rest days, no student, expiry, session
  binding), device-token scoping, WebSocket flow, usage rules, allowlist, commands, scoping
  and report.
- Agent: unit tests of the pure logic in `PcGuard.Core` (matcher, rule cache, usage tracker
  and queue, planner, pipe protocol, browser rule, ownership, shell startup and UI fallback rules, shell token
  object descriptor, UI strings).
  The Windows service, shell and scripts are only compile-checked.
- Frontend: component tests for the console tabs, in `frontend/src/__tests__/`.
- Manual: the 194-test Windows VM checklist in `pc-agent/README.md` (tests 120 to 137 cover
  maintenance mode, 144 to 154 and 158 to 168 the recovery code, 155 to 157 the startup grace,
  39 to 43 and 189 to 193 the ordinary shell token and ending the shell).

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
(49 suites, 292 tests: the whole frontend suite, not only the PC console; also run under
other time zones). Since then the agent Core suite has grown to 712 tests, including
maintenance mode (code shape, limiter, gate, monotonic deadline, request ids, https-only
redeem, redeem protocol, pipe messages, strings, rules); with extra allowed apps and the
recovery code (validation, PBKDF2 vector, verify, gate, prompt, hidden input, pipe messages,
Setup arguments) it is 872; with the startup grace 892; with the recovery-code hardening
(stricter code rules, persistent escalating limiter, hash-file hand-off, shell server check,
Setup confirmation) 965.

Never run: the Windows service, the shell and the installer scripts (`install.ps1`,
`uninstall.ps1`, `publish.ps1`). They compile (0-warning build) but nothing has executed on
Windows. The 194-test VM checklist in `pc-agent/README.md` must be run before any rollout;
treat enforcement, shell protection, the Safe Mode registration, browser address-bar reading
and the installer rollback as unverified until then.

Accepted or parked risks:
- A renamed copy of an allowlisted exe name passes the name match (no signature check); a
  publisher entry is a spoofable metadata match.
- Allowlisted interpreters (`python.exe`, `node.exe`) own any windows they open (pygame,
  Electron), so those windows are not closed.
- WSL, Docker and VM guests are not seen; only the host-side window is checked.
- The student can end, suspend or inject into the shell (ordinary token since 2026-11-05); the
  service relaunches it and the name-only fallback applies meanwhile (inbox apps spared, see 7); a
  compromised shell could under-report windows.
- An administrator can stop the service; Safe Mode behaviour is untested.
- Maintenance mode needs the backend and a device the console knows with its current machine
  key: otherwise a locked PC can only be freed through the recovery code (if set), Safe Mode or
  the Cleanup tool.
- The recovery code switches PC Guard off on that PC for anyone who knows it, until it is
  installed again with a new code; it is single use, but typed in the student's session (keylogger,
  shoulder surfing); a release is visible only in the PC's event log. Its service, shell dialog,
  Setup prompt and install.ps1 handling are only compile-checked / unrun. A window
  lasts up to 4 hours and cannot be ended remotely yet (recommend 15 minutes). The maintenance service, shell dialog and banner are only
  compile-checked.
- Violators are killed with no chance to save work.
- Browser rule gaps: pages with a non-http(s) scheme or a dotless address read as no host
  and are allowed; subdomains of a listed host are allowed; only Chrome and Edge are covered.
- Usage buffered offline is lost on a service restart or reboot (reports undercount).
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
empty value silently disables the browser rule. The workflow does not run Alembic (it pulls,
installs requirements and restarts); missing tables are created by `create_all` at startup. Nothing has been pushed.
