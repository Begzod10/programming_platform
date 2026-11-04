# PC Guard (Windows agent)

PC Guard is a Windows service plus a small sign-in/overlay application for computers in a learning center. A student signs in with the same username and password as on the platform; the platform then decides whether that PC is locked (the student still owes lessons or has no session) or unlocked. While locked, programs that are not on the allowlist are closed within seconds and, if configured, browser windows on non-platform hosts are closed. Teachers can lock a PC or send it a message from the teacher console, and the PC reports which apps were used and for how long.

**Status: nothing in this folder has been run on Windows yet.** The code compiles and its pure logic is unit-tested (`dotnet test`), but the Windows-specific parts and the scripts in `scripts/` are untested. Use the manual checklist at the end on a Windows VM before any rollout.

## Architecture

- **Service (`PcGuard.Service.exe`)**: runs as LocalSystem in session 0 and is the only authority on the PC. It signs in against the backend, holds the session token in memory only, enforces every 2 s, keeps the rule cache, queues usage events on disk and talks to the backend over HTTPS and a WebSocket.
- **Shell (`PcGuard.Shell.exe`)**: runs as the student in the console session and acts as the service's eyes and face: sign-in screen, lock banner, message popup, and a snapshot of visible windows (exe names, browser hosts) every 2 s.
- **Pipe**: the shell talks to the service over the local named pipe `PcGuard.Pipe`. The service launches the shell itself (suspended, pins its pid and creation time, then resumes) and accepts only that exact instance.
- **Backend**: the existing platform API (`/api/v1/pc/*`). **The server decides the lock state.** The agent never unlocks by itself; it applies the rules the server sends. If the server cannot be reached the cached rules stay for 10 minutes, then the PC locks. The one exception is maintenance mode, and it also needs the server: a teacher issues a one-time code in the console and the backend confirms it (see "Maintenance mode (teacher code)").
- **Install folder**: both exes live in the same folder (`C:\Program Files\PcGuard`), writable only by SYSTEM and Administrators.
- **Fallback**: without fresh snapshots (shell missing, hung, other desktop or session) the service enforces by process name only. This is stricter for third-party apps (background apps are killed too) but exempts Windows inbox apps; see the never-kill rule under Known limitations.

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

Parameters: `-BackendBaseUrl` (required; includes the `/api/v1` prefix; must be https unless the host is localhost), `-DistDir` (default `..\dist`), `-InstallDir` (default `C:\Program Files\PcGuard`), `-ExtraAllowedApps` (optional; see "Extra allowed apps on one PC" below).

The script: stops and removes an existing PcGuard service (upgrade), kills leftover shells, copies the files, writes the URL into the installed `appsettings.json`, removes inheritance from the install folder and grants SYSTEM and Administrators full control and Users read/execute only, creates the service (`LocalSystem`, automatic start, quoted binary path verified by reading `ImagePath` back; a wrong path aborts and removes the service), sets the description, sets recovery to restart after 5 s on every failure (`sc.exe failure PcGuard reset= 0 actions= restart/5000/restart/5000/restart/5000` plus `failureflag 1`) and starts it. It deliberately does NOT register a Run key, scheduled task or Startup shortcut for the shell: only the service starts the shell. Running it again upgrades: the old folder is renamed to `PcGuard.old-<timestamp>`, and if any step fails the new files and service are removed and the old version is restored; the old folder is deleted only after the new service started. `%ProgramData%\PcGuard` is kept.

## Uninstall

```powershell
.\scripts\uninstall.ps1          # removes the service and the install folder, keeps the machine key and data
.\scripts\uninstall.ps1 -Purge   # also deletes %ProgramData%\PcGuard
```

## Setup-PcGuard.exe (one-click install)

`Setup-PcGuard.exe` sits in the root of the package folder, next to `dist\` and `scripts\`:

```
PcGuard\
  Setup-PcGuard.exe
  dist\        (PcGuard.Service.exe, PcGuard.Shell.exe, appsettings.json, runtime files)
  scripts\     (install.ps1, uninstall.ps1, publish.ps1)
  README.md
```

Double-click it (Windows shows the UAC prompt; it needs Administrator) and choose `[1] Install or upgrade`, `[2] Uninstall` or `[3] Quit`. For install it asks for the backend URL (`https://host/api/v1`; http is accepted only for localhost, 127.0.0.1 and [::1]; a URL not ending in `/api/v1` gives a warning only), shows a summary and waits for you to type `YES`. Then it runs `install.ps1` / `uninstall.ps1` with Windows PowerShell, shows the script output live, reports the exit code and waits for Enter. The exit code of the script is the exit code of the exe.

- The two scripts are EMBEDDED in the exe. At run time they are written to a new folder `%ProgramData%\PcGuard-setup-<guid>` that only SYSTEM and Administrators can access (ACL applied when the folder is created, inheritance removed), checked by SHA-256 against the embedded bytes, run, and the folder is deleted afterwards (also after errors and Ctrl+C). The loose `scripts\` folder is never executed by the exe (so a changed file there has no effect on it). The app files are taken from `dist\` next to the exe, so keep the folder together; if `dist\PcGuard.Service.exe`, `dist\PcGuard.Shell.exe` or `dist\appsettings.json` is missing it stops with a clear error.
- Extra apps: after the backend URL the interactive install asks `Extra apps to keep running on this PC (comma separated exe names, e.g. anydesk.exe; empty for none):` and shows the answer in the summary before YES (an invalid name or more than 16 repeats the question). Silent: add `--allow-app anydesk.exe` (repeatable; only with `--install`; an invalid name or more than 16 is a usage error, exit code 2, before anything runs). See "Extra allowed apps on one PC".
- Silent use: `Setup-PcGuard.exe --install --backend-url https://host/api/v1 --no-pause` (no questions), `Setup-PcGuard.exe --uninstall --no-pause`, `--uninstall --purge` (also deletes `%ProgramData%\PcGuard`), `--help`. `--backend-url` works only with `--install`, and `--purge` only as `--uninstall --purge`.
- **Copy the PcGuard folder to an admin-only location such as `C:\PcGuardSetup` and lock it before running the install.** The installer turns `dist\PcGuard.Service.exe` (and every DLL in `dist\`) into a service that runs as SYSTEM, so it refuses a package folder that standard users can modify: before doing anything it reads the permissions of the package folder and of EVERY folder and file under `dist\` (at most 5000 entries; links or junctions inside `dist\` and a bigger tree are refused too) and stops with exit code 4 if Users, Authenticated Users, Everyone or INTERACTIVE can write, append, delete or change permissions. Typical offenders: `C:\Users\Public`, a USB stick or FAT/exFAT drive, a non-system drive root, shared folders, and a folder copied under the `C:\` root, because on a default Windows `C:\` gives Authenticated Users Modify and a plain copy inherits it. A default user-profile folder such as the administrator's own Downloads or Desktop passes. So after copying to `C:\PcGuardSetup`, run this from an elevated prompt (it removes the inherited permissions and gives only Administrators and SYSTEM access):

  ```
  icacls C:\PcGuardSetup /inheritance:r /grant:r "*S-1-5-32-544:(OI)(CI)F" "*S-1-5-18:(OI)(CI)F"
  ```

  Alternatively run the package from the administrator's own profile folder (Desktop or Downloads). `--allow-writable-package` overrides the check with a loud warning; use it only if you accept the risk. The exe prints the package path at every install, and the refusal message repeats these commands.
- It is NOT code-signed, so Windows SmartScreen may show "Windows protected your PC" (More info, Run anyway), and a downloaded zip may need Unblock in the file properties.
- It has NEVER been run on Windows. Run tests 93-107 and 138-143 below before relying on it.
- Build: `dotnet publish src/PcGuard.Setup/PcGuard.Setup.csproj -c Release -r win-x64 --self-contained true -p:PublishSingleFile=true -p:EnableCompressionInSingleFile=true -p:IncludeNativeLibrariesForSelfExtract=true -o dist-setup` (works on macOS too).

## Cleanup-PcGuard.exe (no terminal needed)

`Cleanup-PcGuard.exe` is a double-click wrapper around `scripts\cleanup.ps1` (see `scripts\CLEANUP.md`) for removing PC Guard from a PC when the normal uninstall is not possible. It is a single file: it needs no `dist\` or `scripts\` folder, so it also runs from a USB stick.

Double-click it (UAC asks for Administrator rights). It then does, without any menu:

1. Extracts the embedded `cleanup.ps1` to a new admin-only folder `%ProgramData%\PcGuard-cleanup-<guid>` (SHA-256 checked against the embedded bytes; deleted afterwards, also after errors and Ctrl+C).
2. Lists busy script processes (`-FindBusyScripts`). It never closes busy scripts.
3. Shows a preview of the removal (`-RemovePcGuard -WhatIf`); nothing is changed. The data purge is not part of the preview (it removes only `%ProgramData%\PcGuard`, after the same checks). If the preview exits with 2 (it reports steps that would FAIL or be SKIPPED, for example a user-writable install folder), a warning is printed and you are STILL asked; only exit code 1 or an unexpected code stops the program.
4. Asks `Type YES to remove PC Guard (anything else exits)`. Anything but YES (any case) prints "Nothing was changed." and exits with code 0.
5. Asks `Also delete PC Guard's data (machine key, rules)? [y/N]` (default No).
6. Runs the real removal (`-RemovePcGuard -Force`, plus `-Purge` if you said yes). It never passes `-Kill`, `-IgnoreAcl` or `-InstallDir`; the removal itself ends PC Guard's own service and shell (busy scripts are never closed). It prints what the exit code means (0 ok, 1 error or not elevated, 2 at least one step FAILED) and waits for Enter; the exit code of the removal is the exit code of the exe (a preview that exited with 2 does not matter if the removal ends with 0). Bad command line: exit code 64.

Switches: `--list-only` (steps 1-2 only), `--preview-only` (steps 1-3 only; cannot be combined with `--list-only` or `--purge`), `--purge` (answers step 5 with yes; the YES question is still asked), `--no-pause` (no "Press Enter"), `--help`. There is deliberately no silent mode.

- It is a tool for administrators. Although it needs Administrator rights to run, do not leave it on a PC, share or USB stick where students can get at it: anyone who can approve a UAC prompt can use it to remove PC Guard.
- It is NOT code-signed, so Windows SmartScreen may show "Windows protected your PC" (More info, Run anyway), and a downloaded zip may need Unblock in the file properties.
- It has NEVER been run on Windows. Run tests 108-119 below before relying on it.
- Build: `dotnet publish src/PcGuard.Cleanup/PcGuard.Cleanup.csproj -c Release -r win-x64 --self-contained true -p:PublishSingleFile=true -p:EnableCompressionInSingleFile=true -p:IncludeNativeLibrariesForSelfExtract=true -o dist-cleanup` (works on macOS too).

## Configuration

- **PC side**: `Backend:BaseUrl` in `appsettings.json` next to the exes (written by `install.ps1`). Edit it only as administrator and restart the service (`Restart-Service PcGuard`).
- **Backend side**: `PC_PLATFORM_HOSTS` (setting in `backend/app/config.py`, default empty) is a comma-separated list of platform hosts (for example `example.uz,www.example.uz`). While a PC is locked, browser windows are allowed only on these hosts. **If it is empty the browser host rule is DISABLED and browsers run unrestricted while locked, so it must be set before rollout.** Set it in the SERVER's own `.env` file (a server-local file, not part of the repository); it takes effect after the backend restarts. Pushing backend changes to the `server` branch auto-deploys: the workflow `.github/workflows/deploy-backend.yml` triggers on pushes to `server` that touch `backend/**` (or the workflow file) and restarts the backend service. That deploy does not change `.env`, so edit it on the server and restart the backend.
- The default app allowlist comes from the server. Publisher entries in the allowlist are not used by default.
- **PC side, optional**: `Allowlist:ExtraApps` in the same `appsettings.json` (see the next section).

## Extra allowed apps on one PC

For test and admin PCs only: a way to keep chosen programs (for example `anydesk.exe`, so a developer keeps remote access while testing) running on ONE PC although they are not on the server's allowlist.

- **Where**: `Allowlist:ExtraApps` in the installed `appsettings.json` next to the exes, an array of exe file names, for example `"Allowlist": { "ExtraApps": ["anydesk.exe"] }`. Default: empty. The install folder is writable by administrators only, so only an administrator can set it. It is read when the service starts: after editing it by hand, run `Restart-Service PcGuard`.
- **How to set it**: `install.ps1 -ExtraAllowedApps anydesk.exe` (an array, or one comma separated string such as `"anydesk.exe,rustdesk.exe"`), `Setup-PcGuard.exe --install --backend-url https://host/api/v1 --allow-app anydesk.exe --no-pause` (repeat `--allow-app` for more), or the question in the interactive Setup install. An upgrade without the parameter keeps the extra apps of the existing install; `install.ps1 -ExtraAllowedApps ''` clears them. (Setup-PcGuard.exe never clears them: with no extra apps given it omits the parameter, so they are kept.)
- **Name rule**: a bare file name ending in `.exe`, 5-64 characters, only letters A-Z, digits, `.`, `-` and `_`; no path, no spaces, no wildcards; at most 16 entries; matched case-insensitively. `install.ps1` and Setup refuse an invalid value or more than 16 with a clear message before anything is changed (install.ps1 exit code 1, Setup exit code 2). If the file is edited by hand, the service ignores each invalid entry, and every entry beyond the 16th, with a warning in the event log (the name only); valid entries are logged at start as a warning too.
- **What it does**: the service adds these names (without publisher) to the EFFECTIVE allowlist in every state: signed out, default allowlist, signed-in student rules, offline cache and fail-closed. They are added locally at enforcement time only: never written into the rule cache (`rules.json`) and never sent to the backend. An extra app is treated exactly like an allowlisted app: it is not closed while locked, also not in fallback mode, and its use is recorded in usage like any other app. The protected-process rule and the browser host rule are unchanged (an extra browser is still subject to the host rule).
- **Security**: extra apps are local, administrator-configured and bypass the lock for that PC only. **Adding remote-control software (AnyDesk, TeamViewer, RustDesk ...) lets someone at the PC use it while the PC is locked** (for example to reach another computer where nothing is blocked), and anyone who knows its access details can control the PC from outside. Use it only on test/admin PCs, never on student PCs.

## Data locations and what is recorded

- `%ProgramData%\PcGuard` (SYSTEM and Administrators only): `machine.key` (random per-PC key), `rules.json` (cached rules), `usage.queue` (usage events waiting for upload).
- `%LocalAppData%\PcGuard\shell.log` (per student, about 512 KB, rotated): exception type names and stack traces only; never messages, titles, URLs or passwords.
- Recorded and sent to the backend: app (exe) names, start and end times, durations, lock state, sign-in and sign-out times.
- NOT recorded: screenshots, keystrokes, window titles, URLs, page contents. The browser host is read from the address bar by the shell, checked locally by the service against the host list, and never stored or sent to the backend. Student passwords are never stored on the PC.
- **Privacy notice**: many students are minors. The learning center must inform parents. The sign-in screen shows a notice in Uzbek and Russian.

## Maintenance mode (teacher code)

An emergency way to use a locked PC (for example to repair it) without stopping PC Guard. No Windows account or password is involved.

- **Precondition: the PC must already appear in the teacher console**, that is, a student has signed in on it at least once with its current `machine.key`. A code can only be issued for a device the console lists, and the backend only accepts it from the machine key that device row holds. So a code can NOT unlock: a freshly installed PC on which no student has signed in yet; a PC whose `machine.key` was regenerated (for example after a read error or after an untrusted data folder was quarantined; the console may still show the old row with the same hostname, and a code issued for it is always rejected); and a PC running fail-closed with a temporary key (data folder could not be secured; the key changes at every start). **For those PCs the only recovery is Safe Mode or the Cleanup tool (`Cleanup-PcGuard.exe`), both of which need a Windows administrator.**
- **How**: a teacher opens the device in the teacher console and creates a maintenance code for that one PC, choosing 15 minutes, 1 hour or 4 hours. **Choose 15 minutes** unless the repair really needs longer: once redeemed, the teacher has no way to end maintenance remotely (see below). The console shows a 6-digit code. On the PC, click **Texnik kod / Код обслуживания** (bottom left of the sign-in screen, or next to Sign out in the name banner while a student is signed in), type the code and press **Ochish / Открыть**. The PC sends the code with its machine key to the backend (`POST /api/v1/pc/maintenance/redeem`, **https only**: with an `http://` backend URL the service refuses to send the code and the dialog shows the generic error); only if the backend accepts it does the service stop enforcing.
- **The code**: 6 digits, valid for 5 minutes, single use (consumed on success), only for the PC it was issued for. A new code for the same PC replaces the older one; if two were somehow active at once (a race), the backend accepts either and retires both. The duration comes from the server (exactly 15, 60 or 240 minutes; any other answer is refused); it is not chosen on the PC.
- **While it is active**: the sign-in screen is hidden and a small banner at the top right shows "Texnik rejim HH:mm gacha" / "Режим обслуживания до HH:mm" (local time) with a **Tugatish / Завершить** button. Nothing is killed and no browser window is closed. **Nobody can sign in during maintenance**: the sign-in screen is hidden. A student who was already signed in stays signed in and keeps working (the name banner stays); on a signed-out PC the PC is simply open and nobody signs in until maintenance ends. Rules from the server (a teacher's "lock now" included) and usage tracking keep arriving, but they cannot re-lock the PC until maintenance ends; then the current rules apply at once.
- **It ends**: at the end time; when someone at the PC presses Tugatish / Завершить (no code needed, ending only re-locks); and when the service stops or restarts (maintenance is kept in memory only, nothing is written to disk, so a restart or reboot always re-locks). The end time is measured on a monotonic clock, so changing the PC clock (or an NTP correction) neither ends it early nor extends it; the clock time shown on the banner is for display only. **A window can last up to 4 hours, and the teacher has no remote "end maintenance" action yet**: the console keeps showing the server state (for example "locked") and, after a redeem, a "Maintenance until HH:mm" badge on the device card. The badge shows the window that was granted: it does NOT clear if the PC ends maintenance early (Tugatish or a service restart) and stays until the time passes. Prefer 15 minutes, and press Tugatish / Завершить when the work is done.
- **Wrong codes**: every failure looks the same ("Kod noto'g'ri yoki muddati o'tgan" / "Неверный код или срок действия истёк"). The PC allows one attempt per second and locks code entry for 10 minutes after 5 wrong codes in a row (a valid code is refused during that time too). The backend burns a code after 5 wrong guesses (per-code limit of 5, stored in the database) and blocks the device's machine key for 10 minutes after 5 failures (shown as "too many attempts, try later"). Failures are counted only for machine keys of known devices (an unknown key creates no state). **The backend does NOT block by IP on failures**: all lab PCs share one public IP, so an IP block would let one student turn the codes off for the whole lab. There is only a generous flood limit on the redeem endpoint, 120 requests per minute per client IP (answer 429, also shown as "too many attempts"). The IP is the first `X-Forwarded-For` entry, as for login, so it can be shared by the lab or dodged by a spoofed header: it is a coarse guard only, not a security control; the per-code limit is what bounds guessing.
- **Lost answer**: if the backend accepted the code but its answer did not reach the PC (timeout, network drop), the PC shows "Serverga ulanib bo'lmadi" / "Нет связи с сервером" and stays locked, and the code is used up. Create a new code.
- **Audit**: the audit is log lines only. The service writes to the Windows Application event log (source PcGuard): `Maintenance mode started for N minutes (until <UTC>), redeemed with teacher code`, `Maintenance mode ended (expired|ended on the PC|service stopped)`, `Maintenance code rejected (n of 5 consecutive failures)`, a lockout notice, and `Maintenance code not sent: the backend URL is not https ...` for the http refusal. The backend writes log lines for which teacher issued a code for which device and for a redemption (device, minutes). There is no durable audit table: the code rows in the database do not record why a code was consumed and are deleted after 7 days. The code itself is never logged or stored on the PC.
- **Accepted limitation: it needs the backend.** The code is checked by the server, so if the backend cannot be reached the PC shows "Serverga ulanib bo'lmadi" / "Нет связи с сервером" and stays locked. **If the backend is down, the only way out is Safe Mode or the Cleanup tool (`Cleanup-PcGuard.exe`), both of which need a Windows administrator.**
- **The code is often read out loud.** Anyone who hears it within the 5 minutes can use it on that PC, so give it only to the person sitting at that PC, and create it only when they are ready to type it.

## Known limitations and accepted risks

- **Publisher entries are spoofable.** An allowlist entry with a publisher matches the exe's `CompanyName` file metadata, which anyone can forge. A renamed game can pass an entry that has no publisher (the default allowlist has none, so such entries match by exe name only). There is no Authenticode check.
- **Same-user code injection into the shell is only partly mitigated.** The shell is protected by a process security descriptor, a restricted token default DACL, a startup-hook-free build and a cleaned environment, and the pipe accepts only the launched instance. Other same-user vectors are not covered; a compromised shell could under-report windows.
- **An administrator can stop the service** (and so can anyone with administrator rights). Standard accounts are required.
- **Violators are killed at once** with no chance to save their work (no graceful close from session 0).
- **Never-kill rule.** While locked, a console-session process is never killed if its exe name is in the protected set (explorer, dwm, csrss, winlogon, ctfmon, sihost, taskhostw, runtimebroker, shellexperiencehost, searchhost, startmenuexperiencehost, textinputhost, conhost, applicationframehost, searchapp, searchui, lockapp, shellhost, widgets, and the PC Guard shell and service), or if it is allowlisted, or if it counts as service-owned. Service-owned means: its process token belongs to SYSTEM, LOCAL SERVICE or NETWORK SERVICE; or its token owner cannot be read AND its image is under %SystemRoot% and owned by TrustedInstaller, SYSTEM or Administrators; or even its image path cannot be read (the service cannot open the process at all, despite SeDebugPrivilege, for example protected system processes). A process whose token owner cannot be read but whose image is anywhere else (for example a user-writable folder) counts as the student's and is killed. That is the whole rule in normal (fresh) mode. In fallback mode (no fresh snapshot from the shell) processes whose image is under %SystemRoot% and owned by TrustedInstaller, SYSTEM or Administrators are also spared.
- **Inbox apps in fallback mode (accepted).** Notepad, Paint and other Windows inbox apps run under the student's own account, so in fresh mode they are killed when locked like any other non-allowlisted app. In fallback mode they survive until the shell is back (about 6-15 s), because without window information the service cannot tell them from background OS processes.
- **Allowlisted interpreters can open other windows (by design).** A window opened by `python.exe` (for example pygame) or `node.exe` (for example Electron run through node) belongs to the allowlisted process and is not killed. Remove those entries from the allowlist if this matters.
- **WSL, Docker and virtual machine guests are out of reach.** Only host-side windowed processes are checked. The host process (wsl.exe, a VM window, Docker Desktop) is killed when it is not allowlisted, but programs inside a running guest are not seen.
- **Safe Mode support is untested.** The installer registers the service for Safe Mode (Minimal and Network) on a best-effort basis; whether the service, the shell and enforcement work there has not been checked (see the Safe Mode test).
- **Fallback mode is stricter** and can kill autostart and background apps (OneDrive, Teams) for a few seconds, for example right after Windows sign-in.
- **Browser address-bar reading depends on Chrome/Edge UI Automation** (omnibox class `OmniboxViewViews`) and may break after a browser update. If the address bar cannot be read the host counts as unknown and is allowed, except for windows with no address bar at all (app-mode, PWA, popup windows), which are closed while a host list is active. Only Chrome and Edge are covered; other browsers are not restricted by the host rule.
- **UWP edge cases**: UWP windows are hosted by ApplicationFrameHost; the real app pid is resolved from the CoreWindow child, and edge cases remain (suspended apps, Store/Settings).
- **Fast user switching**: only the console session is enforced; a snapshot from another session is ignored and the service falls back until a new shell runs in the new console session.
- The secure desktop (UAC, Ctrl+Alt+Del, lock screen) is outside the shell's reach.
- After a service restart, usage that was waiting for upload and belonged to a session whose token is gone is dropped on purpose, so it is never filed under another student.
- A student typing a full non-platform host into the address bar may have the window closed before pressing Enter.
- The password travels from the shell to the service as a .NET string and cannot be zeroed in memory. The same applies to a maintenance code.
- **Extra allowed apps bypass the lock on that PC** (`Allowlist:ExtraApps`, see "Extra allowed apps on one PC"). They are set by an administrator on the PC itself, are not visible in the teacher console, and remote-control software kept this way can be used by anyone at the locked PC. Test/admin PCs only.
- **Maintenance mode needs the backend and a known device** (see "Maintenance mode (teacher code)"): with the backend down, on a PC the console does not list yet, or after its `machine.key` changed, the only way out of a locked PC is Safe Mode or the Cleanup tool. Maintenance can last up to 4 hours and cannot be ended remotely yet.

## Manual Windows VM test checklist

Nothing below has been run yet. Use a Windows 10 or 11 VM with snapshots: one standard-account student user, one separate administrator account, a reachable backend (staging) with a student, a teacher account, `PC_PLATFORM_HOSTS` set, and a required lesson quota. Install with `install.ps1` first. Mark each test Pass or Fail and write failures in the Notes line.

### 1. Core acceptance tests

**Test 1. Locked student cannot keep a non-allowlisted app open**

1. Sign in on the PC as a student whose lesson quota is NOT complete (PC is locked).
2. Open Notepad (or any app that is not on the allowlist).
3. Watch the window.

- Expected: Notepad closes within about 5 s and the lock banner stays visible. Allowlisted apps keep working. This test is in normal (fresh) mode, with the shell running.
- Note: if the shell has been killed (fallback mode), Notepad and other inbox apps survive until the shell is relaunched (about 6-15 s). That is accepted; see Test 49.
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

**Test 15.** Session filtering and the never-kill rule: only console-session processes are listed. In normal (fresh) mode the only processes never killed are the protected set (explorer, dwm, sihost, ctfmon, SearchHost, SearchApp, SearchUI, StartMenuExperienceHost, ShellExperienceHost, ApplicationFrameHost, LockApp, ShellHost, Widgets and the rest listed under Known limitations), allowlisted apps, and service-owned processes: token of SYSTEM, LOCAL SERVICE or NETWORK SERVICE (for example svchost), or an unreadable token owner on a system image, or an unreadable image path. In fallback mode, processes whose image is under C:\Windows and owned by TrustedInstaller, SYSTEM or Administrators are also spared.

- Expected: While locked, the desktop, Start menu, Windows 10 Search (SearchApp/SearchUI) and Windows 11 Search (SearchHost) keep working; locking the PC shows the lock screen (LockApp) normally, and on Windows 11 the widgets panel does not crash the session. With the shell running, Notepad, Paint (mspaint) and Character Map started by the student close within about 5 s. With the shell ended by an admin (fallback), the same apps stay open until the shell is back, and svchost and other service-account processes are never killed in either mode.
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

- Expected: The service kills a violator that was started with a restrictive process ACL; record the result. The Application event log (source PcGuard) shows "SeDebugPrivilege enabled" at service start; an error entry there instead is a Fail.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 24a.** A program that locks down its own process and token DACL is still closed while locked.

- Steps (untested snippet): powershell.exe itself is allowlisted and lives in System32, so use a copy outside C:\Windows. As the student, copy `C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe` to `Downloads\ps2.exe`, save the PowerShell below as `Downloads\deny.ps1`, and while the PC is locked run `Downloads\ps2.exe -ExecutionPolicy Bypass -File Downloads\deny.ps1`. It replaces its own process and token DACL with an empty one (no access for anyone), then opens a window.

```powershell
Add-Type -Namespace W -Name A -MemberDefinition @'
[DllImport("advapi32.dll")] public static extern uint SetSecurityInfo(IntPtr h, int type, uint info, IntPtr owner, IntPtr group, IntPtr dacl, IntPtr sacl);
[DllImport("advapi32.dll")] public static extern bool InitializeAcl(byte[] acl, int len, int rev);
[DllImport("advapi32.dll")] public static extern bool OpenProcessToken(IntPtr p, uint access, out IntPtr t);
'@
$acl = New-Object byte[] 64; [W.A]::InitializeAcl($acl, 64, 2) | Out-Null
$h = [Runtime.InteropServices.GCHandle]::Alloc($acl, 'Pinned'); $p = $h.AddrOfPinnedObject()
$proc = [Diagnostics.Process]::GetCurrentProcess().Handle
[W.A]::SetSecurityInfo($proc, 6, 4, [IntPtr]::Zero, [IntPtr]::Zero, $p, [IntPtr]::Zero)   # 6 = kernel object, 4 = DACL
$tok = [IntPtr]::Zero; [W.A]::OpenProcessToken($proc, 0x60000, [ref]$tok) | Out-Null       # READ_CONTROL | WRITE_DAC
[W.A]::SetSecurityInfo($tok, 6, 4, [IntPtr]::Zero, [IntPtr]::Zero, $p, [IntPtr]::Zero)
Add-Type -AssemblyName System.Windows.Forms; [Windows.Forms.MessageBox]::Show('still open?') | Out-Null
```

- Expected: ps2.exe and its window are closed within about 5 s. Both SetSecurityInfo calls should print 0 (success); record what they print. If they print 0 and the window stays open, that is a Fail.
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

- Expected: `PcGuard.Shell.runtimeconfig.json` in the install folder has `System.StartupHookProvider.IsSupported` set to false.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 48.** The student cannot plant files beside the shell.

- Expected: Copying a file or DLL into the install folder as a standard user is denied (see section K).
- Result: [ ] Pass  [ ] Fail   Notes: ______

#### F. Fallback mode

**Test 49.** With no fresh snapshot for more than 6 s (end the shell as admin), enforcement is name-only: every non-allowlisted user process in the console session is killed, including background apps such as OneDrive or Teams autostart, except protected names, service-account processes and Windows inbox apps (image under C:\Windows owned by TrustedInstaller, SYSTEM or Administrators).

- Expected: Third-party apps are killed until the shell is back (about 6-15 s). Notepad and Paint stay open during fallback (accepted). Judge how disruptive this is right after Windows sign-in and record it.
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

- Expected: Files copied; appsettings.json has the URL under Backend:BaseUrl; service Running; `sc.exe qfailure PcGuard` shows three restarts at 5000 ms, reset 0, and the failure flag on. RAW IMAGEPATH CHECK: `reg query HKLM\SYSTEM\CurrentControlSet\Services\PcGuard /v ImagePath` must show the path WITH double quotes around it. Run the install once from Windows PowerShell 5.1 and once from PowerShell 7 (uninstall in between); both must show the quoted string (an unquoted path with a space in a SYSTEM service is a privilege-escalation hole: Fail). SAFE MODE KEYS: `reg query HKLM\SYSTEM\CurrentControlSet\Control\SafeBoot\Minimal\PcGuard` and `...\SafeBoot\Network\PcGuard` each show a (Default) REG_SZ value `Service`.
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

- Expected: Service and install folder removed; both SafeBoot\Minimal\PcGuard and SafeBoot\Network\PcGuard keys removed; %ProgramData%\PcGuard kept; reinstalling reuses the machine key. After a failed install that rolled back (Test 75), the SafeBoot keys match the state before the install.
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

#### N. Host-list changes, escape paths and Safe Mode

**Test 89.** An intentionally empty host list disables the browser host rule, and a populated one turns it back on.

- Expected: While a locked student has a Chrome window open on a non-platform host, set `PC_PLATFORM_HOSTS` on the backend to empty and restart the backend: within one state frame or heartbeat (about 30 s) the window is no longer closed. Set it back to the platform host: within about 30 s the non-platform window is closed again. The PC stays locked throughout.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 90.** A changed `PC_PLATFORM_HOSTS` reaches a connected agent without a reconnect.

- Expected: Keep the student signed in and watch that the WebSocket does not drop (no reconnect in the service log). Change the host list on the backend (for example add a second host) and restart the backend workers if needed. Within about 30 s (the next heartbeat) a window on the new host is allowed while locked.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 91.** Known escape paths behave as documented.

- Expected: (1) While locked, a pygame window started with an allowlisted `python.exe` stays open (allowed by design; remove python.exe from the allowlist to block it). (2) If WSL or a VM is installed, the host-side window (wsl.exe terminal, VM window) is killed when not allowlisted; programs inside a guest that is already running are not seen. Record what you observe.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 92.** Safe Mode with Networking (UNTESTED feature, best effort).

- Expected: Boot into Safe Mode with Networking and sign in as the standard student. Check and record each: (a) the PcGuard service is running (`sc query PcGuard`); (b) the shell sign-in screen appears; (c) a locked student's Notepad is closed. Also note whether a standard user could reach Safe Mode at all. Repeat once for plain Safe Mode (no networking): the PC should stay locked with cached or default rules.
- Result: [ ] Pass  [ ] Fail   Notes: ______

#### O. Setup-PcGuard.exe

**Test 93.** Double-click `Setup-PcGuard.exe` as a standard or administrator user.

- Expected: The UAC prompt appears (shield icon on the exe); after approval the console menu shows `[1] Install or upgrade`, `[2] Uninstall`, `[3] Quit`. Declining UAC starts nothing.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 94.** Enter a wrong URL (`abc`, empty, `https://a@b/api/v1`, `https://x/api/v1?x=1`).

- Expected: Each is rejected with a clear message and the prompt repeats. `https://example.uz/api` is accepted with a warning only.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 95.** Enter `http://example.uz/api/v1`; then `http://localhost:8000/api/v1`.

- Expected: The remote http URL is rejected; the localhost one is accepted.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 96.** Install with a real https URL, answer YES.

- Expected: Script output streams live; "finished successfully (exit code 0)"; service Running; `reg query HKLM\SYSTEM\CurrentControlSet\Services\PcGuard /v ImagePath` shows the path WITH double quotes (same checks as Test 70). Typing anything but YES changes nothing.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 97.** Copy only `Setup-PcGuard.exe` to an empty folder (no `dist`) and run it, choose Install.

- Expected: Clear error naming the missing `dist\...` files; nothing changed; Enter closes it; exit code 2.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 98.** Choose Uninstall, answer N to purge, then run again with purge Y.

- Expected: As Tests 76 and 77: first run keeps `%ProgramData%\PcGuard`, the purge run removes it.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 99.** Silent mode: `Setup-PcGuard.exe --install --backend-url https://example.uz/api/v1 --no-pause` from an elevated prompt; then `--uninstall --no-pause`.

- Expected: No questions, no "Press Enter"; installs, then uninstalls; `echo %ERRORLEVEL%` is 0. With an invalid URL it prints the error and returns 2.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 100.** Edit `scripts\install.ps1` in the package (for example add `Write-Host TAMPERED` at the top, or make it `exit 99`), then run Setup-PcGuard.exe install.

- Expected: The edit has NO effect: the embedded copy runs (no TAMPERED line, install behaves normally).
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 101.** After an install or uninstall (and after pressing Ctrl+C during a run) look in `%ProgramData%`.

- Expected: No `PcGuard-setup-*` folder remains (exception: closing the console window with the X button, or killing the exe, may leave a `PcGuard-setup-<guid>` folder behind; it is admin-only and harmless and can be deleted). A second Ctrl+C kills the script and can leave a half-done upgrade: re-run the install. No `PcGuard-setup-*` folder remains in the normal cases. While a run is in progress, `icacls %ProgramData%\PcGuard-setup-*` shows only SYSTEM and Administrators, no inherited entries. A first Ctrl+C waits for the script, a second one stops it.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 102.** Exit code propagation: make the install fail (for example `--install --backend-url https://example.uz/api/v1` with a `dist\appsettings.json` that is invalid JSON, as in Test 75), run silently.

- Expected: The output says FAILED with the script's exit code, and `%ERRORLEVEL%` equals that non-zero code.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 103.** Run the install from a package folder that standard users can write to (for example copy `PcGuard` to `C:\Users\Public\PcGuard`), and also from a plain copy at `C:\PcGuardSetup` (inherits Authenticated Users Modify from `C:\`).

- Expected: The exe prints the package path, names up to 5 paths and the group (for example "Users can modify: C:\Users\Public\PcGuard\dist"), refuses with "Refusing to install" and the icacls commands, exit code 4, nothing changed and no `PcGuard-setup-*` folder. Uninstall still works from there.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 104.** Copy the package to `C:\PcGuardSetup`, then (elevated) `icacls C:\PcGuardSetup /inheritance:r /grant:r "*S-1-5-32-544:(OI)(CI)F" "*S-1-5-18:(OI)(CI)F"` and run the install from there. Also try the package in the administrator's own Desktop or Downloads folder.

- Expected: The check passes silently (only the package path line is printed) and the install proceeds. Re-grant `*S-1-5-32-545:(OI)(CI)M` (Users modify) and it is refused again.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 105.** From the writable folder of Test 103 run `Setup-PcGuard.exe --install --backend-url https://example.uz/api/v1 --allow-writable-package --no-pause`.

- Expected: A loud WARNING that the package folder is not safe, then the install proceeds and succeeds. Without `--allow-writable-package` the same command returns 4.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 106.** In a correctly locked package (Test 104 passes) grant Users Modify on one nested file only, for example `icacls C:\PcGuardSetup\dist\System.Private.CoreLib.dll /grant "*S-1-5-32-545:M"`, or create a subfolder in `dist` that Users can write to; run the install.

- Expected: Refused with exit code 4, naming that file or folder (the check covers everything under `dist\`, not only the three exes).
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 107.** In a locked package create a junction inside `dist` (`mklink /J C:\PcGuardSetup\dist\link C:\Windows\Temp`) and run the install.

- Expected: Refused with exit code 4 ("Link or junction inside the package"); the junction is not followed. Remove it and the install is accepted again.
- Result: [ ] Pass  [ ] Fail   Notes: ______

#### P. Cleanup-PcGuard.exe

**Test 108.** Double-click `Cleanup-PcGuard.exe` as a standard or administrator user.

- Expected: The UAC prompt appears (shield icon on the exe); after approval the list of busy scripts is shown and the flow continues without a menu. Declining UAC starts nothing.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 109.** Run `Cleanup-PcGuard.exe --list-only` (elevated prompt) while a CPU burner script runs.

- Expected: Busy script list is shown, the burner keeps running, the exe exits (no preview, no YES question); `%ERRORLEVEL%` is 0.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 110.** Run `Cleanup-PcGuard.exe --preview-only` on a PC with PC Guard installed.

- Expected: The list and then the "What if" preview of the removal are shown; service, shell, install folder and data are unchanged afterwards; no YES question.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 111.** Run the full flow and answer anything but YES (Enter, `y`, `yes please`, `no`; also close stdin).

- Expected: "Nothing was changed.", exit code 0, PC Guard still installed and running. `yes` or ` YES ` (any case, spaces) continues.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 112.** Run the full flow, type `YES`, answer `n` (or Enter) to the data question.

- Expected: Service, shell and install folder removed, Safe Mode keys gone; `%ProgramData%\PcGuard\machine.key` still present; exit code 0.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 113.** Install again, run the full flow, type `YES`, answer `y` to the data question (also try `--purge`).

- Expected: `%ProgramData%\PcGuard` is gone as well. With `--purge` the data question is not asked, but YES still is.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 114.** Run `Cleanup-PcGuard.exe` on a PC without PC Guard.

- Expected: The preview and the removal say nothing is there to remove (steps SKIPPED); it exits cleanly with code 0.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 115.** Press Ctrl+C during the list step and during the removal.

- Expected: The first Ctrl+C waits for the running step, a second one stops it; the exe prints that the step may be incomplete and removes its folder; a console with no step running just ends the program.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 116.** Look in `%ProgramData%` after each run (also after Ctrl+C), and with `icacls` while a step is running.

- Expected: No `PcGuard-cleanup-*` folder remains (closing the console with X or killing the exe may leave one; it is admin-only and can be deleted). While running only SYSTEM and Administrators have access, no inherited entries.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 117.** Make the removal fail partly (for example keep services.msc open on PcGuard, as in CLEANUP.md test 22/32) and check `%ERRORLEVEL%` with `--no-pause`. Then simulate a non-elevated run: as a STANDARD user open cmd, run `set __COMPAT_LAYER=RunAsInvoker` and start `Cleanup-PcGuard.exe` from that window (the manifest would otherwise always show UAC). Also try a wrong switch (`--foo`).

- Expected: Partial failure: the output explains exit code 2 and `%ERRORLEVEL%` is 2. Non-elevated: the "must run as Administrator" message and exit code 1, nothing changed, no extraction folder left. Wrong switch: the error and usage, exit code 64.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 118.** Copy only `Cleanup-PcGuard.exe` to a USB stick (no `dist\`, no `scripts\`), edit/delete nothing, run it from there on a PC with PC Guard.

- Expected: It works without any package; placing a modified `cleanup.ps1` next to it has no effect (the embedded copy runs). Also run it with the stick as the current directory: nothing is read from there.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 119.** Preview exit 2 must not block the removal: create `C:\ProgramData\PcGuard-setup-planted` as a junction (`mklink /J`) to an empty scratch folder (or grant Users Modify on the PC Guard install folder), then run the full flow.

- Expected: The preview shows FAILED/SKIPPED lines and the warning "The preview reported steps that would FAIL or be SKIPPED ..."; the YES question is STILL asked; after YES the service and shell are removed, the planted entry is reported by the removal (FAILED/SKIPPED) and the junction target is untouched. Exit code is that of the real removal.
- Result: [ ] Pass  [ ] Fail   Notes: ______

#### Q. Maintenance mode (teacher code)

Needs a teacher account that can create maintenance codes for the test PC in the console, and the backend reachable unless a test says otherwise.

**Test 120.** Look at the sign-in screen in both languages; sign in as a student and look at the name banner.

- Expected: A "Texnik kod" / "Код обслуживания" link (no "Administrator" anywhere) at the bottom left of the sign-in screen and next to Sign out in the name banner. Clicking it opens a small dialog on top of the sign-in screen: title, "Texnik kod (6 raqam)" / "Код обслуживания (6 цифр)", one input, Ochish / Bekor qilish. The sign-in screen does not take the focus back while the dialog is open; Escape and Cancel close it; only digits can be typed or pasted (at most 6).
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 121.** Type a wrong 6-digit code (and also 5 digits) and press Ochish.

- Expected: "Kod noto'g'ri yoki muddati o'tgan" / "Неверный код или срок действия истёк"; the field is empty again; the PC stays locked.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 122.** Create a 15-minute code for this PC in the console and enter it on the PC.

- Expected: The dialog closes, the sign-in screen disappears and a banner at the top right says "Texnik rejim HH:mm gacha" / "Режим обслуживания до HH:mm" with the local time 15 minutes from now. Event log: "Maintenance mode started for 15 minutes (until ... UTC), redeemed with teacher code".
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 123.** During maintenance start apps that are blocked when locked (Notepad, a game, a browser on a non-platform host); also kill the shell once.

- Expected: Nothing is closed for the whole period, also while the shell is missing (no name-only kills).
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 124.** During maintenance press Tugatish / Завершить on the banner.

- Expected: The banner disappears and the sign-in screen is back at once; within about 2 s the blocked apps from Test 123 are closed. Event log: "Maintenance mode ended (ended on the PC)".
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 125.** Redeem a new 15-minute code and wait until the end time. During another 15-minute period, as administrator set the clock back by an hour; during a third one set it forward by an hour.

- Expected: At the end time the PC re-locks by itself; event log "Maintenance mode ended (expired)". Changing the clock neither ends maintenance early nor extends it: in both runs the PC re-locks 15 minutes after the code was redeemed (by a stopwatch), although the banner's HH:mm no longer matches the new clock.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 126.** Redeem a 60-minute code, then restart the service as administrator (`Restart-Service PcGuard`), and in another run reboot the PC.

- Expected: The PC is locked again after the restart and after the reboot; event log "Maintenance mode ended (service stopped)". Nothing about maintenance is in `%ProgramData%\PcGuard`.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 127.** Enter the code from Test 122 or 126 again (already used).

- Expected: Rejected with the invalid-code message; the PC stays locked.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 128.** Enter 5 wrong codes in a row, then create a new valid code in the console and enter it within 10 minutes; enter it again after the 10 minutes (create another one if it expired).

- Expected: The 5th wrong code shows "Juda ko'p urinish. N soniyadan so'ng ..." with a countdown and the input disabled; the valid code is refused during the 10 minutes (it never reaches the backend: it stays usable); after the lockout a valid code works. Event log: "Maintenance code rejected (n of 5 ...)" entries and "Maintenance code attempts locked out for 10 minutes after 5 consecutive failures". (The backend may also answer "Juda ko'p urinish, keyinroq urinib ko'ring" for its own 10-minute block.)
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 129.** Disconnect the network (or stop the backend), create a code (on the console from another network) and enter it on the PC.

- Expected: "Serverga ulanib bo'lmadi" / "Нет связи с сервером" within about 10 s; the PC stays locked; the failure does not count toward the lockout. Confirm that Safe Mode or Cleanup-PcGuard.exe is the documented way out in this case.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 130.** Sign in as a student (locked), click Texnik kod / Код обслуживания in the name banner and enter a valid code.

- Expected: The name banner stays (no remaining-lessons line), the maintenance banner appears, nothing is closed. After Tugatish the student's normal locked state applies again at once.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 131.** Create a code and wait more than 5 minutes before entering it.

- Expected: Rejected with the invalid-code message.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 132.** After Tests 121 to 131 search the Application event log (source PcGuard), shell.log and `%ProgramData%\PcGuard` for every code you typed.

- Expected: The started, ended and rejected/lockout entries are present; no code appears anywhere.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 133.** As the student, run a fake shell (a copy of PcGuard.Shell.exe, or a script opening `\\.\pipe\PcGuard.Pipe`) that sends `{"t":"maintenance_redeem","code":"<valid code>"}` and `{"t":"admin_end"}`.

- Expected: The connection is rejected ("Rejected pipe client ... not the shell instance this service launched" in the event log); the code is not redeemed (it still works from the real shell) and maintenance does not start or end.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 134.** Request ids: block the backend with a delay of more than 15 s (for example a firewall rule that drops, not rejects, traffic to it, or a proxy that holds the request), enter a valid code, wait for the dialog's "Serverga ulanib bo'lmadi" after 15 s, close the dialog, open it again and leave it empty. Then remove the delay.

- Expected: A late answer to the first attempt never appears as an error or result in the reopened dialog. If the late answer was a success, maintenance starts and the dialog closes (because maintenance started), not because of a result. shell.log has no error. (A code replaced in the service by a newer one before it was checked gets ok=false "error"; the real shell cannot send a second code while one is pending, so this part is covered by unit tests only.)
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 135.** As administrator set `Backend:BaseUrl` in the installed `appsettings.json` to the `http://` form of a staging backend that also serves plain http (restart the service), sign in once if needed, create a code and enter it. Restore the https URL afterwards.

- Expected: The dialog shows the generic error ("Xatolik yuz berdi" / "Произошла ошибка"); the PC stays locked; the backend receives no `/pc/maintenance/redeem` request (check its access log); the code is still unused (it works after restoring https). Event log: a warning "Maintenance code not sent: the backend URL is not https ..." without the code; sign-in over http still works as before (with the existing plain-http warning at service start).
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 136.** Type a code, press Ochish while the backend is unreachable (or a wrong code), then click into the empty box and press Ctrl+Z (also right-click: Undo).

- Expected: Nothing comes back: the box stays empty and Undo is unavailable.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 137.** Precondition: on a freshly installed PC where no student has signed in yet, check the teacher console; then on a PC that is listed, as administrator delete `%ProgramData%\PcGuard\machine.key` and restart the service, create a code for the (old) row in the console and enter it.

- Expected: The fresh PC is not listed, so no code can be created for it. The code for the old row is rejected with the invalid-code message (the key changed). Recovery for both is Safe Mode or Cleanup-PcGuard.exe, as the README says. After a student signs in once, the PC is listed (again) with its new key and a new code works.
- Result: [ ] Pass  [ ] Fail   Notes: ______

#### R. Extra allowed apps (Allowlist:ExtraApps)

Needs AnyDesk (or another app that is not on the allowlist) installed on the test PC.

**Test 138.** Install with `Setup-PcGuard.exe --install --backend-url https://example.uz/api/v1 --allow-app anydesk.exe --no-pause` (and once interactively: answer `anydesk.exe` to the extra apps question; the summary before YES shows it). Start AnyDesk, then sign a student in on a locked account, sign out, and lock the PC from the teacher console.

- Expected: The installed `appsettings.json` has `"Allowlist": { "ExtraApps": [ "anydesk.exe" ] }` (a JSON array, also with Windows PowerShell 5.1); install.ps1 prints `Extra apps : anydesk.exe` and the security warning; the event log shows the extra-apps warning at service start. AnyDesk stays open (and a remote session through it keeps working) while signed out, while locked with a student signed in, after "lock now", and during fallback (kill the shell as administrator); Notepad and other non-allowlisted apps are still closed. `%ProgramData%\PcGuard\rules.json` does not contain anydesk.exe.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 139.** Invalid names: `install.ps1 -BackendBaseUrl https://example.uz/api/v1 -ExtraAllowedApps "C:\Tools\anydesk.exe"`, then `-ExtraAllowedApps "any desk.exe"`, `"*.exe"` and `"anydesk"`; and `Setup-PcGuard.exe --install --backend-url https://example.uz/api/v1 --allow-app "C:\Tools\anydesk.exe" --no-pause`; over an existing install.

- Expected: install.ps1 prints `Invalid -ExtraAllowedApps value ...` with the rule and "Nothing was changed.", exit code 1; Setup prints the error and usage, exit code 2. In both cases the service was not stopped, the install folder and its `appsettings.json` are unchanged (compare the file hash before and after) and no `PcGuard.old-*` folder exists.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 140.** 17 entries: `install.ps1 ... -ExtraAllowedApps "a1.exe,a2.exe,...,a17.exe"` and Setup with 17 `--allow-app`; then, as administrator, edit the installed `appsettings.json` by hand to hold 17 valid names plus one invalid entry (`"bad name.exe"`) and run `Restart-Service PcGuard`.

- Expected: install.ps1 refuses ("Too many ... at most 16", exit code 1, nothing changed); Setup refuses (exit code 2). With the hand-edited file the service starts, logs one warning per ignored entry (`bad name.exe` and the 17th name, names only) and keeps the first 16 valid names as extra apps; the 17th name is not allowed (an app with that name is closed while locked).
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 141.** Upgrade keeps extras: with anydesk.exe configured (Test 138), run `Setup-PcGuard.exe --install --backend-url https://example.uz/api/v1 --no-pause` (no `--allow-app`), then `install.ps1 -BackendBaseUrl ... -ExtraAllowedApps rustdesk.exe`, then `install.ps1 -BackendBaseUrl ... -ExtraAllowedApps ''`.

- Expected: After the first upgrade `appsettings.json` still lists anydesk.exe (the script prints "Keeping the extra apps of the existing install"); after the second only rustdesk.exe; after the third the list is empty (`[]`) and AnyDesk is closed while locked again.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 142.** Extras survive a service restart and a reboot: with anydesk.exe configured and AnyDesk open on a locked PC, run `Restart-Service PcGuard` as administrator, then reboot and start AnyDesk again before and after a student signs in.

- Expected: AnyDesk is never closed (during and after the restart, after the reboot before anyone signs in, and with a student signed in); the same extra-apps warning is in the event log after every start.
- Result: [ ] Pass  [ ] Fail   Notes: ______

**Test 143.** Everything else is still allowlist-bound: with anydesk.exe configured, sign in a student whose PC is locked, open Notepad, a game and a Chrome window on a non-platform host; then disconnect the network until the cache is too old (offline_timeout).

- Expected: Notepad and the game are closed and the non-platform Chrome window is closed (host rule unchanged) while AnyDesk stays open; the same holds offline. The teacher console allowlist does not show anydesk.exe, and the usage report lists AnyDesk time like any other app.
- Result: [ ] Pass  [ ] Fail   Notes: ______

### 3. Results

Fill in after each run. Total tests: 144 (7 core, 137 additional).

| Date | Tester | Windows build (winver) | Agent commit | Passed | Failed | Not run | Notes |
|------|--------|------------------------|--------------|--------|--------|---------|-------|
|      |        |                        |              |        |        |         |       |
|      |        |                        |              |        |        |         |       |
