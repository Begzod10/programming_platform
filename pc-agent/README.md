# PC Guard (Windows agent)

PC Guard is a Windows service plus a small sign-in/overlay application for computers in a learning center. A student signs in with the same username and password as on the platform; the platform then decides whether that PC is locked (the student still owes lessons or has no session) or unlocked. While locked, programs that are not on the allowlist are closed within seconds and, if configured, browser windows on non-platform hosts are closed. Teachers can lock a PC or send it a message from the teacher console, and the PC reports which apps were used and for how long.

**Status: nothing in this folder has been run on Windows yet.** The code compiles and its pure logic is unit-tested (`dotnet test`), but the Windows-specific parts and the scripts in `scripts/` are untested. Use the manual checklist at the end on a Windows VM before any rollout.

## Architecture

- **Service (`PcGuard.Service.exe`)**: runs as LocalSystem in session 0 and is the only authority on the PC. It signs in against the backend, holds the session token in memory only, enforces every 2 s, keeps the rule cache, queues usage events on disk and talks to the backend over HTTPS and a WebSocket.
- **Shell (`PcGuard.Shell.exe`)**: runs as the student in the console session and acts as the service's eyes and face: sign-in screen, lock banner, message popup, and a snapshot of visible windows (exe names, browser hosts) every 2 s.
- **Pipe**: the shell talks to the service over the local named pipe `PcGuard.Pipe`. The service launches the shell itself (suspended, pins its pid and creation time, then resumes) and accepts only that exact instance.
- **Backend**: the existing platform API (`/api/v1/pc/*`). **The server decides the lock state.** The agent never unlocks by itself; it applies the rules the server sends. If the server cannot be reached the cached rules stay for 10 minutes, then the PC locks.
- **Install folder**: both exes live in the same folder (`C:\Program Files\PcGuard`), writable only by SYSTEM and Administrators.
- **Fallback**: without fresh snapshots (shell missing, hung, other desktop or session) the service enforces by process name only, which is stricter.

## Requirements

- Windows 10 or 11, x64.
- Students use **standard (non-administrator) Windows accounts**. An administrator can stop the service and bypass the whole system; the installer prints a BEST-EFFORT warning when the signed-in user looks like an administrator (domain, Azure AD and nested-group administrators and RDP sessions may be missed), so verify yourself that student accounts are standard users.
- Outbound HTTPS from the PCs to the backend (including WebSocket `wss`).
- A build machine with the .NET 8 SDK (Windows, because the shell uses WPF). Target PCs need no .NET installed: the build is self-contained.
- On the backend: `PC_PLATFORM_HOSTS` set (see Configuration).

## Build

On the build machine, in PowerShell from the `pc-agent` folder:

```powershell
.\scripts\publish.ps1
```

This runs `dotnet publish` for the service and the shell (self-contained, win-x64) into one folder, `pc-agent\dist`, so `PcGuard.Service.exe` and `PcGuard.Shell.exe` sit side by side. It is a plain folder (no single-file, no trimming), which keeps WPF working and `StartupHookSupport=false` in effect. Use `-OutputDir` to choose another folder.

## Install

Copy `dist` and `scripts` to the PC (for example to a USB stick), open PowerShell **as Administrator** and run:

```powershell
.\scripts\install.ps1 -BackendBaseUrl https://example.uz/api/v1
```

Parameters: `-BackendBaseUrl` (required; includes the `/api/v1` prefix; must be https unless the host is localhost), `-DistDir` (default `..\dist`), `-InstallDir` (default `C:\Program Files\PcGuard`).

The script: stops and removes an existing PcGuard service (upgrade), kills leftover shells, copies the files, writes the URL into the installed `appsettings.json`, removes inheritance from the install folder and grants SYSTEM and Administrators full control and Users read/execute only, creates the service (`LocalSystem`, automatic start, quoted binary path verified by reading `ImagePath` back; a wrong path aborts and removes the service), sets the description, sets recovery to restart after 5 s on every failure (`sc.exe failure PcGuard reset= 0 actions= restart/5000/restart/5000/restart/5000` plus `failureflag 1`) and starts it. It deliberately does NOT register a Run key, scheduled task or Startup shortcut for the shell: only the service starts the shell. Running it again upgrades: the old folder is renamed to `PcGuard.old-<timestamp>`, and if any step fails the new files and service are removed and the old version is restored; the old folder is deleted only after the new service started. `%ProgramData%\PcGuard` is kept.

## Uninstall

```powershell
.\scripts\uninstall.ps1          # removes the service and the install folder, keeps the machine key and data
.\scripts\uninstall.ps1 -Purge   # also deletes %ProgramData%\PcGuard
```

## Configuration

- **PC side**: `Backend:BaseUrl` in `appsettings.json` next to the exes (written by `install.ps1`). Edit it only as administrator and restart the service (`Restart-Service PcGuard`).
- **Backend side**: `PC_PLATFORM_HOSTS` (setting in `backend/app/config.py`, default empty) is a comma-separated list of platform hosts (for example `example.uz,www.example.uz`). While a PC is locked, browser windows are allowed only on these hosts. **If it is empty the browser host rule is DISABLED and browsers run unrestricted while locked, so it must be set before rollout.** Set it in the SERVER's own `.env` file (a server-local file, not part of the repository); it takes effect after the backend restarts. Pushing backend changes to the `server` branch auto-deploys: the workflow `.github/workflows/deploy-backend.yml` triggers on pushes to `server` that touch `backend/**` (or the workflow file) and restarts the backend service. That deploy does not change `.env`, so edit it on the server and restart the backend.
- The default app allowlist comes from the server. Publisher entries in the allowlist are not used by default.

## Data locations and what is recorded

- `%ProgramData%\PcGuard` (SYSTEM and Administrators only): `machine.key` (random per-PC key), `rules.json` (cached rules), `usage.queue` (usage events waiting for upload).
- `%LocalAppData%\PcGuard\shell.log` (per student, about 512 KB, rotated): exception type names and stack traces only; never messages, titles, URLs or passwords.
- Recorded and sent to the backend: app (exe) names, start and end times, durations, lock state, sign-in and sign-out times.
- NOT recorded: screenshots, keystrokes, window titles, URLs, page contents. The browser host is read from the address bar by the shell, checked locally by the service against the host list, and never stored or sent to the backend. Student passwords are never stored on the PC.
- **Privacy notice**: many students are minors. The learning center must inform parents. The sign-in screen shows a notice in Uzbek and Russian.

## Known limitations and accepted risks

- **Publisher entries are spoofable.** An allowlist entry with a publisher matches the exe's `CompanyName` file metadata, which anyone can forge. A renamed game can pass an entry that has no publisher (the default allowlist has none, so such entries match by exe name only). There is no Authenticode check.
- **Same-user code injection into the shell is only partly mitigated.** The shell is protected by a process security descriptor, a restricted token default DACL, a startup-hook-free build and a cleaned environment, and the pipe accepts only the launched instance. Other same-user vectors are not covered; a compromised shell could under-report windows.
- **An administrator can stop the service** (and so can anyone with administrator rights). Standard accounts are required.
- **Violators are killed at once** with no chance to save their work (no graceful close from session 0).
- **Fallback mode is stricter** and can kill autostart and background apps (OneDrive, Teams) for a few seconds, for example right after Windows sign-in.
- **Browser address-bar reading depends on Chrome/Edge UI Automation** (omnibox class `OmniboxViewViews`) and may break after a browser update. If the address bar cannot be read the host counts as unknown and is allowed, except for windows with no address bar at all (app-mode, PWA, popup windows), which are closed while a host list is active. Only Chrome and Edge are covered; other browsers are not restricted by the host rule.
- **UWP edge cases**: UWP windows are hosted by ApplicationFrameHost; the real app pid is resolved from the CoreWindow child, and edge cases remain (suspended apps, Store/Settings).
- **Fast user switching**: only the console session is enforced; a snapshot from another session is ignored and the service falls back until a new shell runs in the new console session.
- The secure desktop (UAC, Ctrl+Alt+Del, lock screen) is outside the shell's reach.
- After a service restart, usage that was waiting for upload and belonged to a session whose token is gone is dropped on purpose, so it is never filed under another student.
- A student typing a full non-platform host into the address bar may have the window closed before pressing Enter.
- The password travels from the shell to the service as a .NET string and cannot be zeroed in memory.

## Manual Windows VM test checklist

Nothing below has been run yet. Use a Windows 10 or 11 VM with snapshots: one standard-account student user, one separate administrator account, a reachable backend (staging) with a student, a teacher account, `PC_PLATFORM_HOSTS` set, and a required lesson quota. Install with `install.ps1` first. Mark each test Pass or Fail and write failures in the Notes line.

### 1. Core acceptance tests

**Test 1. Locked student cannot keep a non-allowlisted app open**

1. Sign in on the PC as a student whose lesson quota is NOT complete (PC is locked).
2. Open Notepad (or any app that is not on the allowlist).
3. Watch the window.

- Expected: Notepad closes within about 5 s and the lock banner stays visible. Allowlisted apps keep working.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 2. Completing the quota unlocks the PC**

1. With the student from test 1 signed in and locked, complete the required quota on the platform (from a browser on another device or the allowed browser).
2. Within about 10 s open Notepad.

- Expected: The banner changes to unlocked (name and Sign out only) within about 10 s and Notepad stays open.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 3. A standard user cannot stop the service; an admin kill restarts it**

1. As the standard student user run `taskkill /f /im PcGuard.Service.exe` and `sc.exe stop PcGuard`.
2. Confirm both fail with access denied and the service keeps running.
3. In an elevated prompt run `taskkill /f /im PcGuard.Service.exe`.
4. Run `Get-Service PcGuard` every second for 10 s.

- Expected: Steps 1-2 are denied. After the admin kill the service is Running again within 5 s (recovery action restart/5000) and a shell appears again for the signed-in user.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 4. Network loss keeps rules for 10 minutes, then locks**

1. Sign in as a student whose PC is UNLOCKED. Note the time.
2. Disconnect the network (disable the adapter or unplug).
3. After 5 min open Notepad.
4. About 10 min after the last server contact open Notepad again.

- Expected: Until 10 min the unlocked state holds and Notepad works. After 10 min the PC locks (offline timeout) and Notepad closes within about 5 s. After reconnecting, the server state is restored within about 1 min.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 5. Teacher `lock` command locks an unlocked PC**

1. Student signed in and unlocked.
2. In the teacher console send the lock command for that PC.
3. Open Notepad.

- Expected: The banner shows locked within a few seconds and Notepad closes within about 5 s.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 6. Teacher `message` shows the popup**

1. Student signed in.
2. In the teacher console send a short message to that PC.
3. While it appears, keep typing in an allowed app.

- Expected: A popup appears bottom right within a few seconds, does not steal keyboard focus, and disappears after about 10 s. Two messages in a row show one after the other.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 7. Usage appears in the report**

1. Student signed in; use two allowlisted apps for about 2 minutes each, switching between them.
2. Sign out and wait 1 minute.
3. Open the teacher usage report for that student and day.

- Expected: Both app names appear with durations close to real use and the lock state. Nothing else (no titles, no URLs) is shown.
- Result: [ ] Pass  [ ] Fail   Notes: ______

### 2. Additional tests from the service and shell reviews

Each test says what to do, then what must happen.

#### A. Service and session-0 behaviour

**Test 8.** Service installed as LocalSystem, automatic start, reads appsettings.json from the install folder.

- Expected: `sc.exe qc PcGuard` shows SERVICE_START_NAME LocalSystem, START_TYPE AUTO_START and a quoted BINARY_PATH_NAME. After a reboot the service is Running before anyone signs in.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 9.** Logon screen (nobody signed in): service runs, nothing is launched; ERROR_NO_TOKEN (1008) is logged only at Debug.

- Expected: No PcGuard.Shell.exe at the logon screen; no crash; no error flood in Event Viewer.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 10.** Shell is launched visibly into the console user's session with the user's environment (PATH, APPDATA present) and working directory = install folder.

- Expected: After Windows sign-in the PC Guard sign-in window appears within about 10 s. Process Explorer shows PcGuard.Shell.exe in the student's session.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 11.** Shell is relaunched about 6 s after snapshots stop, at most once per 15 s.

- Expected: End the shell as admin: a new one starts within about 6-15 s and never more often than every 15 s.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 12.** Hung shell: killed after about 30 s and relaunched. A slow shell that still sends alive frames is not killed.

- Expected: As admin suspend PcGuard.Shell.exe (Process Explorer). After about 30 s it is killed and a new one starts.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 13.** Secure desktop (UAC prompt, Ctrl+Alt+Del, lock screen): nothing launched, name-only enforcement after about 6 s, shell not killed.

- Expected: Stay on a UAC prompt for 30 s and on Ctrl+Alt+Del for 30 s: no relaunch storm, no crash; window-aware enforcement resumes afterwards.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 14.** Missing shell exe is logged as an error and does not crash the service.

- Expected: In a test install rename PcGuard.Shell.exe: Event Log has an error naming the path; service stays Running. Restore the name.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 15.** Session filtering and system-owned processes: only console-session processes are listed; explorer, dwm, sihost, ctfmon, SearchHost, StartMenuExperienceHost, svchost are never killed; a process whose image path cannot be read is never killed.

- Expected: While locked the desktop, Start menu and search keep working.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 16.** A copy of an exe in C:\Windows\Temp or renamed to explorer.exe is NOT trusted (reported as unverified:name) and is killed when locked.

- Expected: As student copy notepad.exe to C:\Windows\Temp\x.exe and another copy named explorer.exe to Downloads; start both while locked: both close within about 5 s.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 17.** Publisher metadata (FileVersionInfo.CompanyName) reads correctly. CPU and memory cost of the 2 s enumeration with about 150 processes is low; image cache stays bounded.

- Expected: Task Manager: PcGuard.Service.exe idle CPU stays low and memory flat over 1 hour.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 18.** Killing: violators are killed at once (MainWindowHandle is 0 from session 0, so no graceful close). Process trees die; access-denied and already-exited cases are silent; pid-reuse check does not block normal kills.

- Expected: Type text in Notepad while locked: it closes without a save prompt (accepted). No error spam in the Event Log.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 19.** Signed-out state: the PC is locked (no_student) and the allowlist still applies.

- Expected: Before anyone signs in to PC Guard, Notepad closes within about 5 s; allowlisted apps work.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 20.** Stop and start the service while locked.

- Expected: `Restart-Service PcGuard` as admin: the PC is locked again within seconds (the sign-in is memory-only, so the student signs in again). Queued usage behaves as in section G.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 21.** Fail-closed data folder: if %ProgramData%\PcGuard cannot be secured (pre-create it owned by a standard user and make the move fail), the service runs locked with the default allowlist and writes nothing to disk.

- Expected: Log says memory-only mode; no machine.key, rules.json or usage.queue is written to the unsafe folder.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 22.** Fresh data folder ACL and machine key.

- Expected: `icacls %ProgramData%\PcGuard` lists only SYSTEM and Administrators, no inheritance. As a standard user `type machine.key` is denied. The key is identical after restarts.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 23.** Login flood from a compromised shell does not grow memory; only the latest login is processed (optional stress test: a script writing many login frames, run as admin with a test shell).

- Expected: Service memory stays flat; Logout and token-death commands are never lost.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 24.** SeDebugPrivilege: LocalSystem can terminate processes whose own security descriptor denies everyone else. If the service ever runs under a non-SYSTEM account it needs this privilege.

- Expected: The service kills a violator that was started with a restrictive process ACL; record the result.
- Result: [ ] Pass  [ ] Fail   Notes: ______

#### B. Backend client

**Test 25.** Login results: correct password signs in; wrong password, 403, 429 and an offline backend each give their own message.

- Expected: Each case shows the matching text in Uzbek and Russian.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 26.** WebSocket connects over wss with the device token; first frame is `state`; heartbeat every 30 s gets a pong; the pong refreshes the rule cache so an online PC does not lock as offline after 10 minutes.

- Expected: Teacher console shows the PC online; an unlocked student stays unlocked for over 15 minutes with the network up.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 27.** Second login on the same machine, or logout, closes the old socket (code 4001) and signs the old session out.

- Expected: Sign in as student A, sign out, sign in as student B: A is gone from the teacher console.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 28.** Dead or revoked token (403 on the handshake, or on `GET /pc/state` while the socket is down) signs the student out.

- Expected: Revoke the session: the PC returns to the sign-in window.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 29.** Network pulled: reconnect backoff 1/2/5/10/30 s; a fresh `state` arrives after reconnect; a half-open socket is detected by the silence watchdog after about 75 s.

- Expected: Event log shows retries at roughly those intervals.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 30.** Usage upload errors: 422 drops the batch, 5xx or offline keeps events on disk and retries; timestamps are accepted by the server.

- Expected: Stop the backend for a few minutes during use, start it again: usage appears afterwards.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 31.** Secret hygiene: search the Application event log (source PcGuard) and shell.log for the password, the device token and the text `?token=`.

- Expected: No matches.
- Result: [ ] Pass  [ ] Fail   Notes: ______

#### C. Pipe pinning and fake shell attempts

**Test 32.** Only the exact shell instance launched by the service is accepted (pid + creation time pin).

- Expected: As the student start PcGuard.Shell.exe by hand from the install folder while the real one runs: it is rejected (service logs a warning); the real one stays connected.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 33.** A copy of the exe elsewhere, or another program speaking the protocol, is rejected before any message is read.

- Expected: Copy the install folder to the Desktop and run its PcGuard.Shell.exe: rejected. A PowerShell script connecting to the pipe `PcGuard.Pipe` and sending a login frame: rejected.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 34.** Pipe squatting: a rogue process creates the pipe before the service starts.

- Expected: Stop the service, start a rogue pipe server, start the service: it logs that it could not create the first pipe instance and does not trust the rogue. Remove the rogue afterwards.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 35.** A standard user can connect read/write but cannot create a second pipe instance; remote (SMB) clients are denied.

- Expected: From another PC the path `\\target\pipe\PcGuard.Pipe` cannot be used.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 36.** A new client replaces the old one; a client in a non-console session (RDP, second user) is rejected; same pid with a different creation time is rejected.

- Expected: RDP in with another account and run the shell: rejected; the console shell is unaffected.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 37.** All message types flow: login, logout, snapshot, state, login_result, message, close_window, alive. A 2 MiB line is skipped and the connection survives; a shell that stops reading is dropped after 2 s.

- Expected: Normal use shows all of them working; no reconnect loops.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 38.** First connect: the shell is created suspended, pinned, then resumed, so its first connect is accepted. The shell retries with backoff after a service stop/restart and shows the connecting text.

- Expected: `Restart-Service PcGuard` while the shell runs: the shell reconnects within seconds.
- Result: [ ] Pass  [ ] Fail   Notes: ______

#### D. Shell protection (process DACL, thread kill attempts, token default DACL)

**Test 39.** As the standard student: `taskkill /f /pid <shell pid>`, Process Explorer Kill, Task Manager End task, and a suspend attempt on PcGuard.Shell.exe.

- Expected: All four fail with access denied. An elevated admin or SYSTEM can still terminate it, and the service relaunches it.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 40.** As the student: suspend or kill the shell's individual threads (Process Explorer, Threads, Kill; or OpenThread with THREAD_TERMINATE).

- Expected: All denied.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 41.** As the student: open the shell with WRITE_DAC and try to rewrite its DACL, then terminate or suspend (owner-rights ACE).

- Expected: The DACL rewrite is denied, so terminate/suspend stay denied. The service log has NO error about the restricted default DACL or process security descriptor. If it has one (for example the `OW` alias in `(A;;0x0;;;OW)` was rejected), the shell started unprotected: change `ShellSecurity.DefaultDaclSddl` to the literal `S-1-3-4` form.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 42.** The shell works normally under the restricted process SD and token default DACL (WPF, GDI, pipe client, single-instance mutex).

- Expected: Sign-in, banner, popup and snapshots work through a full session; no access-denied on its own objects.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 43.** Windows Error Reporting for a crashed shell: force a crash of the shell as the student (for example with an admin tool that injects a crash) and check Reliability Monitor / %LocalAppData%\CrashDumps.

- Expected: A WER entry for PcGuard.Shell.exe exists. If none exists, mark Fail and note it as an accepted loss caused by the deny ACE.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 44.** Failure paths of the suspended launch: a failing pin callback or GetProcessTimes must leave no orphaned suspended PcGuard.Shell.exe (review or force if feasible).

- Expected: Process Explorer never shows a suspended PcGuard.Shell.exe after many relaunches.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 45.** Many launches do not leak handles (security descriptor LocalFree, token, environment block).

- Expected: End the shell as admin 50 times: the handle count of PcGuard.Service.exe stays flat.
- Result: [ ] Pass  [ ] Fail   Notes: ______

#### E. Environment-variable startup-hook attempt

**Test 46.** As the student set user environment variables `DOTNET_STARTUP_HOOKS` (a harmless test DLL that writes a marker file), `CORECLR_ENABLE_PROFILING=1` with `CORECLR_PROFILER` / `CORECLR_PROFILER_PATH`, and a `COMPlus_*` variable. Sign out and in so the service relaunches the shell.

- Expected: The hook/profiler is NOT loaded (no marker file; no extra DLL in Process Explorer). The shell still starts with PATH and APPDATA set.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 47.** The published shell has startup hook support disabled.

- Expected: `PcGuard.Shell.runtimeconfig.json` in the install folder has `System.Runtime.EnableStartupHookSupport` set to false.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 48.** The student cannot plant files beside the shell.

- Expected: Copying a file or DLL into the install folder as a standard user is denied (see section K).
- Result: [ ] Pass  [ ] Fail   Notes: ______

#### F. Fallback mode

**Test 49.** With no fresh snapshot for more than 6 s (end the shell as admin), enforcement is name-only and strict: every non-system, non-allowlisted user process in the console session is killed, including background apps such as OneDrive or Teams autostart.

- Expected: Those apps are killed until the shell is back (about 6-15 s). Judge how disruptive this is right after Windows sign-in and record it.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 50.** Fallback with an active browser host list: allowlisted browsers are also killed.

- Expected: While in fallback and locked with a host list, Chrome/Edge close; with an empty host list they do not.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 51.** A snapshot older than 6 s, or from another session, is not trusted.

- Expected: Steps: (1) as admin suspend PcGuard.Shell.exe (Process Explorer) and watch Notepad as a locked student; (2) after about 6 s a non-allowlisted app opened now is killed by name even though the shell is still alive; (3) resume the shell. For the other-session case run test 'Fast user switching' in section J. Expected: step 2 kills Notepad within about 5 s after the 6 s staleness window, and enforcement is window-aware again after step 3.
- Result: [ ] Pass  [ ] Fail   Notes: ______

#### G. Usage upload attribution across sign-outs

**Test 52.** Student A's buffered usage uploads under A's session even after B signs in.

- Expected: Pull the network during A's session, sign A out, sign B in, restore the network. A's events appear in A's report and none in B's (closed token is valid up to 24 h).
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 53.** Service restart before the upload: A's un-uploaded events are dropped, not mis-filed (accepted trade-off).

- Expected: Repeat with `Restart-Service PcGuard` before restoring the network: A's report lacks that tail; B's report contains none of it.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 54.** Usage rows reach the backend after a normal session.

- Expected: Rows are present in `pc_usage_events` with plausible durations.
- Result: [ ] Pass  [ ] Fail   Notes: ______

#### H. Browser host rule (needs PC_PLATFORM_HOSTS on the backend)

**Test 55.** While locked, a Chrome/Edge window on a platform host is allowed; a window on any other host is closed within about 4 s.

- Expected: Platform page stays; a google.com window closes. With PC_PLATFORM_HOSTS empty nothing is closed: confirm this too.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 56.** App-mode and PWA windows (`msedge --app=https://example.com`, Chrome install-as-app) have no omnibox and are closed within about 4 s while a host list is active. Normal windows are never reported unreadable on a cold browser start.

- Expected: App-mode window closes; a freshly started normal window on a platform page does not.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 57.** Typing in the omnibox does not close the window; a bare word is ignored.

- Expected: Type `goo`, then `google` without Enter: the window stays. Record what happens when `google.com` is typed without Enter (it may close on the next tick; accepted).
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 58.** Omnibox dropdown, app menu, permission and extension bubbles are not closed.

- Expected: Open each while locked with a host list: the browser stays.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 59.** Undocked DevTools and Picture-in-Picture windows are closed when locked with a host list (accepted).

- Expected: Observed and recorded.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 60.** UI Automation omnibox read works on current Chrome and Edge (ClassName `OmniboxViewViews`), with several windows and profiles; a hung browser keeps its last host; the cost every 2 s is acceptable.

- Expected: Record the browser versions tested; repeat after browser updates.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 61.** close_window closes only top-level Chrome/Edge windows and never other apps.

- Expected: Observed during the tests above.
- Result: [ ] Pass  [ ] Fail   Notes: ______

#### I. UWP apps and window filtering

**Test 62.** UWP apps (Calculator, Store games, Settings) report the real app pid and are killed when not allowlisted; ApplicationFrameHost itself is never killed.

- Expected: Calculator closes within about 5 s while locked; taskbar and shell keep working.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 63.** Suspended (cloaked) UWP windows cause no false positives; tool windows of at least 100x100 and title-less windows count; helper processes without windows are not killed as windowed.

- Expected: No unexpected kills of background helpers while idle.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 64.** The window list matches the taskbar; elevated or other-user processes appear as `?` and the foreground app is correct.

- Expected: Spot-check with several apps.
- Result: [ ] Pass  [ ] Fail   Notes: ______

#### J. Second desktop and fast user switching

**Test 65.** Stay on a second desktop (Sysinternals Desktops) for more than 1 minute: no snapshots are sent, the service falls back to name-only after 6 s, the shell is NOT killed or relaunched. Back on Default, window-aware enforcement resumes.

- Expected: Shell pid unchanged; service log shows fallback, then recovery.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 66.** On the UAC prompt and lock screen the input-desktop check fails open (keeps sending).

- Expected: No relaunch storm.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 67.** Fast user switching: switch to another Windows user, lock and unlock, RDP versus console.

- Expected: The service drops the old session's snapshots (fallback), rejects the stranded shell, launches a new shell in the new console session and pins it. No snapshot from a background session is treated as fresh.
- Result: [ ] Pass  [ ] Fail   Notes: ______

#### K. Installer, upgrade and uninstall

**Test 68.** Not elevated: install.ps1 stops at once.

- Expected: Clear message to run as administrator, exit code 1, nothing changed.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 69.** URL validation.

- Expected: `http://example.uz/api/v1` is rejected; `http://localhost:8000/api/v1` is accepted; a missing -BackendBaseUrl prompts.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 70.** Fresh install with a real https URL.

- Expected: Files copied; appsettings.json has the URL under Backend:BaseUrl; service Running; `sc.exe qfailure PcGuard` shows three restarts at 5000 ms, reset 0, and the failure flag on. RAW IMAGEPATH CHECK: `reg query HKLM\SYSTEM\CurrentControlSet\Services\PcGuard /v ImagePath` must show the path WITH double quotes around it. Run the install once from Windows PowerShell 5.1 and once from PowerShell 7 (uninstall in between); both must show the quoted string (an unquoted path with a space in a SYSTEM service is a privilege-escalation hole: Fail).
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 71.** Folder ACL: `icacls "C:\Program Files\PcGuard"`.

- Expected: No inherited entries; SYSTEM and Administrators full; Users read & execute only. As a standard user replacing or deleting PcGuard.Shell.exe or PcGuard.Service.exe is denied.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 72.** No Run key, scheduled task or Startup shortcut exists for the shell.

- Expected: `reg query HKLM\Software\Microsoft\Windows\CurrentVersion\Run`, `schtasks /query` and the Startup folders show nothing from PC Guard.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 73.** Administrator warning: run the installer while signed in as an administrator account, then as a standard user (elevating with another admin).

- Expected: With an admin console user the warning and fix steps are printed and the install still succeeds; with a standard user no warning. The check is best-effort (domain, Azure AD, nested-group admins and RDP sessions may be missed): independently verify in Computer Management that every student account is a standard user.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 74.** Upgrade: run install.ps1 again over a running install.

- Expected: Old service stopped and removed, shell killed, files replaced, service recreated and Running; the `PcGuard.old-*` folder is gone; %ProgramData%\PcGuard is kept; the same machine appears in the teacher console.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 75.** Rollback: run install.ps1 over a working install with a dist folder whose appsettings.json is invalid JSON (for example truncated), so a step after the file copy fails.

- Expected: The script exits non-zero, the new folder and service are removed, the previous version is restored and its service is running again, no `.old-*` folder is left.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 76.** Uninstall without -Purge.

- Expected: Service and install folder removed; %ProgramData%\PcGuard kept; reinstalling reuses the machine key.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 77.** Uninstall with -Purge.

- Expected: %ProgramData%\PcGuard is also removed.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 78.** Reboot after install.

- Expected: Service is Running before anyone signs in.
- Result: [ ] Pass  [ ] Fail   Notes: ______

#### L. Shell UI, multi-monitor and sign-in errors

**Test 79.** Sign-in screen covers the whole virtual screen on multi-monitor setups with mixed DPI or different layouts, and after hot-plug or resolution changes; a resolution change while signed in does not re-show it.

- Expected: All monitors covered and resized correctly.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 80.** Sign-in screen stays on top of other topmost windows; Alt+F4, Win key and Alt+Tab do not dismiss it; visible on all virtual desktops; no taskbar button; keyboard focus in the username box. Ctrl+Alt+Del is outside its reach.

- Expected: Cannot be closed from the keyboard. Document what a student can do on the Ctrl+Alt+Del screen.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 81.** Enter submits; the UZ/RU toggle works and resets to Uzbek at each shell start; Uzbek and Russian glyphs render correctly.

- Expected: Visual check.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 82.** Login errors in both languages: wrong password, forbidden account, too many attempts (429), backend unreachable, 20 s busy timeout, empty fields.

- Expected: Each shows a distinct, correctly translated message in Uzbek and Russian; the password box is cleared after submit; a failed login has about 1 s delay.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 83.** The privacy notice is shown at the bottom of the sign-in screen in Uzbek and Russian.

- Expected: Text present and readable.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 84.** Banner (top centre of the primary monitor): name and lessons left when locked, name and Sign out only when unlocked; Sign out returns to the sign-in screen; it never steals focus; topmost is re-asserted every 2 s.

- Expected: As described, also on multi-monitor.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 85.** Message popup: bottom right, non-activating, 10 s, one at a time (queue up to 20).

- Expected: As described.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 86.** Single instance and robustness: a second shell exits at once; unhandled exceptions go to shell.log and the shell keeps running; state changes (service restart, token death, sign-out) show the right window.

- Expected: As described.
- Result: [ ] Pass  [ ] Fail   Notes: ______

#### M. Privacy

**Test 87.** Browse several sites and open documents with revealing titles for 30 minutes while signed in, then search everything the agent wrote: %ProgramData%\PcGuard\*, %LocalAppData%\PcGuard\shell.log, the Application event log (PcGuard source) and the backend table pc_usage_events.

- Expected: No URLs, visited host names, window titles, keystrokes or passwords anywhere. Only app names, durations and lock state. shell.log contains only exception type names and stack traces.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 88.** Capture the PC's network traffic (or read backend logs) during a session.

- Expected: Only login, heartbeat/state and usage events. The browser host and window titles are never sent to the backend.
- Result: [ ] Pass  [ ] Fail   Notes: ______

### 3. Results

Fill in after each run. Total tests: 88 (7 core, 81 additional).

| Date | Tester | Windows build (winver) | Agent commit | Passed | Failed | Not run | Notes |
|------|--------|------------------------|--------------|--------|--------|---------|-------|
|      |        |                        |              |        |        |         |       |
|      |        |                        |              |        |        |         |       |
