# PC Guard self-test (`selftest.ps1`)

An automated, read-only check of an installed PC Guard, run on the PC itself. It covers the parts of the
README VM checklist that need no human, no second account and no backend. **It has not been run on
Windows yet** (written and parse-checked on macOS); treat its first runs as a test of the script too.

## How to run

Open **Windows PowerShell as Administrator** (powershell.exe, not PowerShell 7: `pwsh.exe` is not on
the allowlist and is closed while the PC is locked) in the console session of the PC (at the PC or
through AnyDesk; from an RDP session the enforcement probes are skipped), then:

```powershell
cd <package>\scripts
powershell -NoProfile -ExecutionPolicy Bypass -File .\selftest.ps1
```

Options: `-Quiet` (console shows only FAIL lines and the summary), `-NoProbes` (skip section D: nothing
is started), `-OutFile <path>`, `-ExpectedBaseUrl <url>` and `-ExpectedExtraApps <names>` (compare the
installed `appsettings.json` with what you installed), `-InstallDir`, `-LogHours` (default 2).

Output: one line per check, `[PASS] id title` (details on the next line), `[FAIL] id title - detail`
or `[SKIP] id title - reason`, then a summary. The same lines plus environment information (Windows
build, PowerShell version, install folder listing hash and SHA-256 of every exe, `sc.exe qc` /
`qfailure` / `qfailureflag` / `sdshow`, the last 300 PC Guard event log lines) go to
`%USERPROFILE%\Desktop\pcguard-selftest-<yyyyMMdd-HHmmss>.txt`. Exit code 0 = no FAIL, 1 = at least one
FAIL, 2 = not elevated.

It never prints or writes secrets (for `recovery.hash` only "present, format ok, N bytes"; for
`machine.key` only "GUID ok"), never attempts a recovery release and changes nothing. The event log
checks need a recent service start: if the service has run longer than `-LogHours`, run
`Restart-Service PcGuard`, wait about 45 s and run the self-test again.

## What it checks

| Id | Check | README VM tests |
|----|-------|-----------------|
| A01-A04 | Service `PcGuard` exists, LocalSystem, Automatic (Disabled = released or switched off: FAIL with hint), Running | 8, 70 |
| A05 | `ImagePath` / `sc.exe qc` BINARY_PATH_NAME quoted and in the install folder | 8, 70 |
| A06-A07 | `sc.exe qfailure` 3 x restart/5000 ms, reset 0; `qfailureflag` TRUE (registry as fallback) | 3, 70 |
| A08 | `SafeBoot\Minimal\PcGuard` and `SafeBoot\Network\PcGuard` (Default) = `Service` | 70 |
| A09 | Install folder: inheritance removed, no write/modify/full for Users, Authenticated Users, Everyone, INTERACTIVE on any entry, no links inside | 48, 71 |
| A10 | Every exe/dll owned by SYSTEM, Administrators or TrustedInstaller | 71 |
| A11 | Required files present; `PcGuard.Shell.runtimeconfig.json` has `System.StartupHookProvider.IsSupported: false` | 47 |
| A12-A13 | `appsettings.json` parses; `Backend:BaseUrl` valid (not CHANGE-ME); `Allowlist:ExtraApps` a JSON array of valid names | 70, 138, 140 |
| A14-A15 | `%ProgramData%\PcGuard` SYSTEM/Administrators only, inheritance removed; `machine.key` is a GUID | 22 |
| A16 | No Run key, scheduled task or Startup shortcut for PC Guard | 72 |
| A17 | `rules.json` does not contain the extra apps | 138 |
| F01 | `recovery.hash` absent, or well formed (pbkdf2-sha256, 310000-5000000 iterations, 16/32-byte parts), <= 136 bytes, admin-only | 145 |
| F02 | `recovery.attempts` absent, or admin-only, <= 256 bytes, `v1;failures=..;lockouts=..;until=..` (shows the lockout state) | 160, 161 |
| E01-E03 | BaseUrl scheme (http only for localhost, with a warning); no secret-like keys/values in `appsettings.json`; `machine.key` not readable by standard users | 22, 69, 135 |
| B01-B02 | `PcGuard.Service.exe` as SYSTEM in session 0; one `PcGuard.Shell.exe` in the console session as the console user | 8, 10, 86 |
| B03 | Pipe `\\.\pipe\PcGuard.Pipe` exists (it is not connected to) | 34 (indirect) |
| B04-B05 | Process DACLs read with READ_CONTROL: shell owner Administrators, first ACE denies 0x82B to the user, no terminate/suspend grant; service grants standard users no terminate | 3, 39, 41 (structure only) |
| C01-C09 | Application log (provider `PcGuard.Service`, last `-LogHours`): service start, `SeDebugPrivilege enabled`, shell launched + connected, startup grace lines with no kills before the shell connected, window-aware mode (`Shell snapshots resumed` is logged only after a fallback period, so its absence is not a failure), no Error/Critical entries, warnings listed, extra-apps warning; privacy scan for `pbkdf2`, the recovery hash parts, the machine key and `?token=` (counts only) | 9, 10, 24, 31, 41, 87, 138, 155 |
| D01-D03 | `notepad.exe`, `mspaint.exe`, `taskmgr.exe` started from this elevated window are gone within 20 s and the log shows `Terminated <exe>` | 1, 15, 19 |
| D04-D07 | An allowlisted `cmd.exe` window started by the test, `explorer.exe`, this `powershell.exe` and AnyDesk (if it is an extra app and running) survive the 20 s | 15, 138 |

Section D runs only when the service is Running, a shell is connected in the console session, the
script runs in that session, the log shows no signed-in student, no active maintenance, no release and
no current name-only fallback. Processes are started with plain `Start-Process` from the elevated
window: the service treats an elevated administrator's processes in the console session like any
student process (their token owner is Administrators, not a service account). Afterwards the script
closes only the test processes it started (new instances since the probe began, and its cmd.exe).
`Add-Type` compiles a small helper (console session id, process security descriptors) with csc.exe,
which runs without a window and is not affected by PC Guard.

## Expected results on the dummy-backend test setup

Installed with `Setup-PcGuard.exe --install --backend-url http://localhost:8001/api/v1 --allow-app anydesk.exe`,
no backend running, nobody signed in to PC Guard (locked, `no_student`), sign-in screen up, service
started within the last 2 hours:

- All A, B, E and F checks PASS. E01 passes with the plain-http WARNING. A13 shows `[anydesk.exe]`.
  A17 is SKIP (no `rules.json` without a backend) or PASS. F01/F02 PASS as "absent" or "present, format ok".
- C01-C06, C08, C09 PASS; C07 lists the warnings, at least `Backend:BaseUrl uses plain http ...` and
  `Extra allowed apps configured on this PC ...`. If the service started at the Windows logon screen,
  C04 shows the "expired without a shell" variant (PASS) and C05 should show `Shell snapshots resumed`.
- D01-D06 PASS; D07 PASS when AnyDesk is running, otherwise SKIP. The kills appear as
  `Terminated <exe> (pid N)` in the event log.

## What still needs a human or the VM

Reboot behaviour (8, 78, 142, 153, 155 reboot part, 160), anything as a standard user (3, 22 `type`,
39-41, 48, 71 replace/delete attempts, 158), Safe Mode (92), backend sign-in and everything that
depends on it (2, 4-7, 25-30, 52-54, 120-137), lesson quota (1 and 2 with a real student), the browser
host rule (55-61, 89-90), UWP / desktops / fast user switching (62-67), the shell UI (79-86), Setup and
Cleanup (93-119, 144, 150, 167, 168), fake shells and pipe squatting (32-37, 133, 149, 164), and the
recovery code use: wrong codes, release, re-install (146-154, 159-166). The self-test never attempts a
release; check F01/F02 again after those tests.
