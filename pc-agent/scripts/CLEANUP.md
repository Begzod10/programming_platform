# cleanup.ps1

Run BY HAND, in an elevated PowerShell, on one Windows PC at a time (no remote execution, no network, writes no files).
Works in Windows PowerShell 5.1 and PowerShell 7. Exit codes: 0 ok, 1 error / not elevated, 2 some step FAILED.

## What it does

1. **List busy scripts (default, `-FindBusyScripts`).** Samples CPU for `-SampleSeconds` (2-60, default 5) and lists
   script-type processes using at least `-MinCpuPercent` (default 10) of the TOTAL machine CPU
   (delta CPU time / (interval x logical cores)). Script-type = image `powershell, pwsh, powershell_ise, cmd, wscript,
   cscript, mshta, python, pythonw, node, ruby, perl, bash, wsl`, plus any process whose command line contains
   `.ps1 .vbs .vbe .js .jse .wsf .bat .cmd .py` and whose parent is one of those hosts. Shows PID, name, CPU %, owner,
   start time, parent, command line (display truncated to 300 chars). Also prints the top 10 CPU processes
   overall for information only (never offered for closing). Nothing is closed.
2. **Close them (`-Kill`).** Asks per process: `Close PID 1234 (powershell.exe, 38% CPU)? [y/N/a=all remaining/q=quit]`.
   Default is No. `a` applies to the rest of the list but protected processes are still skipped.
3. **Remove PC Guard (`-RemovePcGuard`).** Forced removal that works on damaged installs: disables and stops the
   service, ends `PcGuard.Service.exe` and `PcGuard.Shell.exe`, deletes the service, removes both Safe Mode keys,
   deletes the install folder (found from the service `ImagePath`, override `-InstallDir`, fallback
   `%ProgramW6432%\PcGuard`) and leftover `%ProgramData%\PcGuard-setup-*` folders. `%ProgramData%\PcGuard`
   (machine key, rules, queue) is deleted only with `-Purge`. Nothing else is removed (`PcGuard.old-*` backup
   folders are only mentioned). Asks you to type `YES` unless `-Force` is given. Each step reports OK / SKIPPED / FAILED.

## Examples

```powershell
.\cleanup.ps1                                          # list busy scripts, close nothing
.\cleanup.ps1 -MinCpuPercent 25 -SampleSeconds 10
.\cleanup.ps1 -Kill                                    # list, then ask per process
.\cleanup.ps1 -RemovePcGuard -Purge -WhatIf            # show what removal would do, change nothing
.\cleanup.ps1 -RemovePcGuard                           # remove PC Guard, keep machine key
```

`-WhatIf` works for every action. `-RemovePcGuard` and `-Kill` need Administrator (refused with exit 1 otherwise);
listing alone may run unelevated but other users' processes and command lines can then be hidden.

## What is protected (never closed by -Kill)

PID 0 and 4; this PowerShell and its whole parent chain; `System, Idle, Registry, smss, csrss, wininit, winlogon,
services, lsass, svchost, dwm, explorer, fontdrvhost, sihost, ctfmon, taskhostw, RuntimeBroker, SearchHost, SearchApp,
StartMenuExperienceHost, ShellExperienceHost, TextInputHost, audiodg, MsMpEng, SecurityHealthService, spoolsv,
WmiPrvSE, conhost`; and anything named `PcGuard*` (removed only via `-RemovePcGuard`). Protected busy script hosts are
listed with `[protected]` and get no prompt. The check is repeated right before closing (same name and start time).
`-RemovePcGuard` refuses to delete a drive root, the Windows folder, Program Files, ProgramData, the user profile
folder, or a folder that is not named `PcGuard` and holds no PC Guard exe.

## Honest limits

- NEVER executed on Windows (written without PowerShell available). Run the checklist below on a VM first.
- CPU % is one short sample, not an average; a process can spike or sleep just outside the window.
- Processes of other users (and their command lines) need elevation to be seen.
- The shell is protected by a deny-terminate DACL. An elevated admin should still end it, but if not, the step
  FAILS with a hint: reboot into Safe Mode / see README, then run the script again.
- A service still "marked for deletion" (open Services / Event Viewer window) needs a reboot.
- "Script" detection is by host name and command line, never by file content. A malicious program renamed to
  `notepad.exe` is not found; a legitimate `python` job is listed. Command lines are shown as-is and may contain
  secrets: do not paste the output publicly.

## VM test checklist

Use a disposable Windows VM with PC Guard installed (via install.ps1). Run each test in both Windows PowerShell 5.1
and PowerShell 7 at least once (test 14).

CPU burner (save as `burn.ps1`, run `powershell -File burn.ps1` in a normal window):

```powershell
$x = 0
while ($true) { $x++ }
```

| # | Test | Expected | Pass/Fail |
|---|------|----------|-----------|
| 1 | Elevated: `.\cleanup.ps1` with the burner running | Burner listed with CPU above 10%, owner, parent, command line `burn.ps1`; top-10 list labelled informational; nothing closed | [ ] Pass [ ] Fail |
| 2 | Same with `-MinCpuPercent 95 -SampleSeconds 2` on a multi-core VM | Burner (about 100/cores %) not listed; "None found." | [ ] Pass [ ] Fail |
| 3 | `.\cleanup.ps1 -Kill -WhatIf` with burner running | "What if: ... Stop process" printed, no prompt, burner keeps running | [ ] Pass [ ] Fail |
| 4 | `.\cleanup.ps1 -Kill`, answer `N` (or just Enter) | Burner still running afterwards | [ ] Pass [ ] Fail |
| 5 | `.\cleanup.ps1 -Kill`, answer `y` | Burner closed, message "closed"; exit code 0 | [ ] Pass [ ] Fail |
| 6 | Start two burners, `-Kill`, answer `a` on the first | Both closed; protected ones (if any listed) still skipped | [ ] Pass [ ] Fail |
| 7 | Answer `q` at the first prompt | Loop ends, nothing closed | [ ] Pass [ ] Fail |
| 8 | Run cleanup from the burner's parent: start `powershell` window A (burner inside), run `.\cleanup.ps1 -Kill` from a child console of A | A is shown as `[protected: this PowerShell or its parent chain]`, no prompt, not closed | [ ] Pass [ ] Fail |
| 9 | While heavy load runs from explorer/svchost/MsMpEng (e.g. a full Defender scan) | They appear only in the top-10 informational list, never in the candidate list or any prompt | [ ] Pass [ ] Fail |
| 10 | With PC Guard running, `.\cleanup.ps1 -Kill` | PcGuard.* processes never listed for closing or prompted | [ ] Pass [ ] Fail |
| 11 | Unelevated: `.\cleanup.ps1` | Lists, with a warning about hidden processes; exit 0 | [ ] Pass [ ] Fail |
| 12 | Unelevated: `.\cleanup.ps1 -Kill` and `-RemovePcGuard` | Clear "needs Administrator" message, exit code 1, nothing changed | [ ] Pass [ ] Fail |
| 13 | `.\cleanup.ps1 -RemovePcGuard -Purge -WhatIf` | Plan and "What if" lines printed; service, shell, folders, registry keys, `%ProgramData%\PcGuard` all unchanged | [ ] Pass [ ] Fail |
| 14 | Run test 1 and test 15 once in Windows PowerShell 5.1 and once in PowerShell 7 | Same behaviour, no parse or runtime errors | [ ] Pass [ ] Fail |
| 15 | `.\cleanup.ps1 -RemovePcGuard`, type `YES` on a normal install | Service stopped and deleted, shell ended, install folder gone, both SafeBoot keys gone, `PcGuard-setup-*` gone; `sc.exe query PcGuard` says not found; exit 0 | [ ] Pass [ ] Fail |
| 16 | Same test, answer anything but `YES` | "Cancelled", nothing changed | [ ] Pass [ ] Fail |
| 17 | Without `-Purge`: check `%ProgramData%\PcGuard\machine.key` afterwards | Still present; Data folder step says SKIPPED (kept) | [ ] Pass [ ] Fail |
| 18 | With `-Purge` (fresh install first) | `%ProgramData%\PcGuard` gone | [ ] Pass [ ] Fail |
| 19 | Damaged install: delete `PcGuard.Service.exe` from the install folder first (stop the service first), then `-RemovePcGuard -Force` | Still removes everything (install dir found via ImagePath or default); exit 0 | [ ] Pass [ ] Fail |
| 20 | Custom location: install to another folder, run `-RemovePcGuard` with and without `-InstallDir` | Folder found automatically from ImagePath; with the override the given folder is used | [ ] Pass [ ] Fail |
| 21 | `-RemovePcGuard -InstallDir C:\Windows` / `C:\` / `C:\Program Files` | Step Install folder FAILED with "refusing to delete"; nothing deleted; exit 2 | [ ] Pass [ ] Fail |
| 22 | Open services.msc during removal | Either "marked for deletion" FAILED message asking for a reboot, or OK; script finishes with a summary either way | [ ] Pass [ ] Fail |
| 23 | Shell cannot be ended (if it resists as admin) | Step FAILED with the Safe Mode / README hint, exit 2; rerun after reboot succeeds | [ ] Pass [ ] Fail |
| 24 | Run `-RemovePcGuard` again on a clean PC | All steps SKIPPED, exit 0 | [ ] Pass [ ] Fail |
