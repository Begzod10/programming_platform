<#
.SYNOPSIS
  Lists busy script processes (and optionally closes them), and/or force-removes PC Guard.
  Run BY HAND in an elevated PowerShell, one PC at a time.
.DESCRIPTION
  Default (-FindBusyScripts): samples CPU for -SampleSeconds and lists script-type processes (powershell, cmd,
  wscript, python, node ...) using at least -MinCpuPercent of the TOTAL machine CPU. Nothing is closed.
  -Kill: asks for each listed, non-protected process whether to close it (default answer is No).
  -RemovePcGuard: forced removal of PC Guard (service, shell, install folder, Safe Mode keys, setup temp
  folders) even when the install is damaged. %ProgramData%\PcGuard (machine key) is deleted only with -Purge.
  Use -WhatIf to print what would be done without changing anything.
  Never touched: system processes, explorer, this PowerShell and its parent chain, and anything named PcGuard*
  (PC Guard is removed only through -RemovePcGuard, never through -Kill).
  Command lines are shown as-is and may contain secrets: do not paste the output publicly.
  NOT TESTED: written without PowerShell available; run the VM checklist in CLEANUP.md.
  Compatible with Windows PowerShell 5.1 and PowerShell 7 (no ternary, no && / ||).
  Exit codes: 0 ok, 1 error or not elevated, 2 partial failure (some step FAILED).
.PARAMETER FindBusyScripts
  List busy script processes (default when no other switch is given).
.PARAMETER SampleSeconds
  CPU sampling interval, 2-60 seconds (default 5).
.PARAMETER MinCpuPercent
  Minimum percent of total machine CPU for a process to be listed (default 10).
.PARAMETER Kill
  Ask, per listed process, whether to close it. Requires Administrator.
.PARAMETER RemovePcGuard
  Force-remove PC Guard. Requires Administrator.
.PARAMETER InstallDir
  Override of the PC Guard install folder (default: taken from the service ImagePath, else Program Files\PcGuard).
.PARAMETER Purge
  With -RemovePcGuard: also delete %ProgramData%\PcGuard (machine key, rules, usage queue).
.PARAMETER Force
  With -RemovePcGuard: do not ask to type YES.
.EXAMPLE
  .\cleanup.ps1
.EXAMPLE
  .\cleanup.ps1 -MinCpuPercent 25 -SampleSeconds 10
.EXAMPLE
  .\cleanup.ps1 -Kill
.EXAMPLE
  .\cleanup.ps1 -RemovePcGuard -Purge -WhatIf
#>
[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [switch]$FindBusyScripts,
    [ValidateRange(2, 60)][int]$SampleSeconds = 5,
    [ValidateRange(0, 100)][double]$MinCpuPercent = 10,
    [switch]$Kill,
    [switch]$RemovePcGuard,
    [string]$InstallDir,
    [switch]$Purge,
    [switch]$Force
)

$ErrorActionPreference = 'Stop'
$ServiceName = 'PcGuard'
$ServiceKey = 'HKLM:\SYSTEM\CurrentControlSet\Services\PcGuard'
$script:Cmdlet = $PSCmdlet
$script:DryRun = [bool]$WhatIfPreference
$script:NativeExit = 0
$script:Results = New-Object System.Collections.ArrayList
$script:KillFailures = 0

# Script hosts (image name without .exe, lower case).
$ScriptHosts = @('powershell', 'pwsh', 'powershell_ise', 'cmd', 'wscript', 'cscript', 'mshta', 'python', 'pythonw', 'node', 'ruby', 'perl', 'bash', 'wsl')
# Never touched by -Kill (lower case, no .exe). Anything starting with pcguard is protected as well.
$ProtectedNames = @('system', 'idle', 'registry', 'smss', 'csrss', 'wininit', 'winlogon', 'services', 'lsass', 'svchost', 'dwm', 'explorer',
    'fontdrvhost', 'sihost', 'ctfmon', 'taskhostw', 'runtimebroker', 'searchhost', 'searchapp', 'startmenuexperiencehost',
    'shellexperiencehost', 'textinputhost', 'audiodg', 'msmpeng', 'securityhealthservice', 'spoolsv', 'wmiprvse', 'conhost')
$ScriptCmdRegex = '(?i)\.(ps1|vbs|vbe|jse|js|wsf|bat|cmd|py)(?=["''\s]|$)'

# ---------------------------------------------------------------- helpers

function Invoke-Native {
    # Runs a native program without letting stderr text become a terminating error (Windows PowerShell 5.1).
    param([string]$Exe, [string[]]$ExeArgs)
    $old = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try {
        $out = & $Exe @ExeArgs 2>&1
        $script:NativeExit = $LASTEXITCODE
    }
    finally {
        $ErrorActionPreference = $old
    }
    return $out
}

function Test-IsAdmin {
    $principal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Confirm-Action {
    # Honors -WhatIf / -Confirm of the script.
    param([string]$Target, [string]$Action)
    return $script:Cmdlet.ShouldProcess($Target, $Action)
}

function Add-Result {
    param([string]$Step, [string]$Status, [string]$Detail)
    [void]$script:Results.Add([pscustomobject]@{ Step = $Step; Status = $Status; Detail = $Detail })
    $color = 'Gray'
    if ($Status -eq 'OK') { $color = 'Green' }
    if ($Status -eq 'FAILED') { $color = 'Red' }
    Write-Host ('  [{0}] {1}: {2}' -f $Status, $Step, $Detail) -ForegroundColor $color
}

function Invoke-Step {
    param([string]$Name, [scriptblock]$Action)
    try {
        & $Action
    }
    catch {
        Add-Result $Name 'FAILED' $_.Exception.Message
    }
}

function Get-ImageName {
    # "Powershell.EXE" -> "powershell"
    param([string]$Name)
    if (-not $Name) { return '' }
    return ($Name -replace '(?i)\.exe$', '').ToLowerInvariant()
}

function Get-CimProcessMap {
    # pid (int) -> Win32_Process instance
    $map = @{}
    foreach ($p in (Get-CimInstance -ClassName Win32_Process -ErrorAction Stop)) {
        $map[[int]$p.ProcessId] = $p
    }
    return $map
}

function Get-OwnChain {
    # PIDs of this PowerShell process and all its ancestors.
    param($CimMap)
    $set = @{}
    $cur = [int]$PID
    $guard = 0
    while ($cur -gt 0 -and (-not $set.ContainsKey($cur)) -and $guard -lt 64) {
        $set[$cur] = $true
        $p = $CimMap[$cur]
        if ($p) { $cur = [int]$p.ParentProcessId } else { $cur = 0 }
        $guard++
    }
    return $set
}

function Get-ProtectionReason {
    # Returns a reason string when the process must never be closed, otherwise $null.
    param([int]$ProcId, [string]$ImgName, $Chain)
    if ($ProcId -le 4) { return 'system process id' }
    if ($Chain.ContainsKey($ProcId)) { return 'this PowerShell or its parent chain' }
    if ($ProtectedNames -contains $ImgName) { return 'system / shell process' }
    if ($ImgName -like 'pcguard*') { return 'PC Guard (use -RemovePcGuard)' }
    return $null
}

function Get-OwnerText {
    param($CimProc)
    try {
        $r = Invoke-CimMethod -InputObject $CimProc -MethodName GetOwner -ErrorAction Stop
        if ($r -and $r.User) { return ('{0}\{1}' -f $r.Domain, $r.User) }
    }
    catch { }
    return '(unknown)'
}

function Get-CpuSample {
    # pid (int) -> total processor seconds
    $h = @{}
    foreach ($p in (Get-Process -ErrorAction SilentlyContinue)) {
        try { $h[[int]$p.Id] = $p.TotalProcessorTime.TotalSeconds } catch { }
    }
    return $h
}

function Format-Cmd {
    param([string]$Cmd)
    if (-not $Cmd) { return '(not available; run elevated to see other users'' command lines)' }
    if ($Cmd.Length -gt 300) { return ($Cmd.Substring(0, 300) + ' ...[truncated for display, ' + $Cmd.Length + ' chars]') }
    return $Cmd
}

function Read-Answer {
    param([string]$Prompt)
    try {
        $a = Read-Host $Prompt
    }
    catch {
        return 'q'
    }
    if ($null -eq $a) { return 'n' }
    return $a.Trim().ToLowerInvariant()
}

# ---------------------------------------------------------------- find / kill busy scripts

function Invoke-FindBusyScripts {
    Write-Host ''
    Write-Host ('Sampling CPU for {0} s (threshold {1}% of total machine CPU) ...' -f $SampleSeconds, $MinCpuPercent)
    $cores = [Environment]::ProcessorCount
    if ($cores -lt 1) { $cores = 1 }

    $s1 = Get-CpuSample
    $t1 = [Diagnostics.Stopwatch]::GetTimestamp()
    Start-Sleep -Seconds $SampleSeconds
    $s2 = Get-CpuSample
    $t2 = [Diagnostics.Stopwatch]::GetTimestamp()
    $elapsed = ($t2 - $t1) / [double][Diagnostics.Stopwatch]::Frequency
    if ($elapsed -le 0) { $elapsed = [double]$SampleSeconds }

    $cim = Get-CimProcessMap
    $chain = Get-OwnChain $cim

    $rows = New-Object System.Collections.ArrayList
    foreach ($procId in $s2.Keys) {
        if (-not $s1.ContainsKey($procId)) { continue }
        $delta = $s2[$procId] - $s1[$procId]
        if ($delta -lt 0) { $delta = 0 }
        $pct = ($delta / ($elapsed * $cores)) * 100
        $c = $cim[$procId]
        if (-not $c) { continue }
        [void]$rows.Add([pscustomobject]@{ ProcId = [int]$procId; Cpu = [math]::Round($pct, 1); Cim = $c })
    }

    # Candidates: script hosts, or script-looking command lines whose parent is a script host.
    $cands = New-Object System.Collections.ArrayList
    foreach ($r in $rows) {
        if ($r.Cpu -lt $MinCpuPercent) { continue }
        if ($r.ProcId -eq 0) { continue }
        $c = $r.Cim
        $img = Get-ImageName $c.Name
        $cmd = [string]$c.CommandLine
        $parent = $cim[[int]$c.ParentProcessId]
        $parentOk = $false
        $parentName = '(exited)'
        if ($parent) {
            if ($parent.CreationDate -and $c.CreationDate -and ($parent.CreationDate -gt $c.CreationDate)) {
                $parentOk = $false   # PID was reused after the real parent exited
            }
            else {
                $parentOk = $true
                $parentName = [string]$parent.Name
            }
        }
        $isHost = ($ScriptHosts -contains $img)
        $childOfHost = $false
        if ($parentOk -and $cmd -match $ScriptCmdRegex) {
            if ($ScriptHosts -contains (Get-ImageName $parentName)) { $childOfHost = $true }
        }
        if (-not ($isHost -or $childOfHost)) { continue }
        $reason = Get-ProtectionReason $r.ProcId $img $chain
        [void]$cands.Add([pscustomobject]@{
                ProcId     = $r.ProcId
                Name       = [string]$c.Name
                Image      = $img
                Cpu        = $r.Cpu
                Owner      = (Get-OwnerText $c)
                Started    = $c.CreationDate
                ParentId   = [int]$c.ParentProcessId
                ParentName = $parentName
                CmdLine    = $cmd
                Protected  = $reason
            })
    }
    $sorted = @($cands | Sort-Object -Property Cpu -Descending)

    Write-Host ''
    Write-Host ('=== Busy script processes (>= {0}% of total CPU, sampled {1:N1} s, {2} logical cores) ===' -f $MinCpuPercent, $elapsed, $cores) -ForegroundColor Cyan
    Write-Host 'WARNING: command lines are shown as-is and may contain secrets. Do not paste this output publicly.' -ForegroundColor Yellow
    if (-not (Test-IsAdmin)) {
        Write-Host 'WARNING: not elevated: other users'' processes and command lines may be hidden or missing.' -ForegroundColor Yellow
    }
    if ($sorted.Count -eq 0) {
        Write-Host 'None found.'
    }
    foreach ($x in $sorted) {
        Write-Host ''
        $note = ''
        if ($x.Protected) { $note = '   [protected: ' + $x.Protected + ']' }
        Write-Host ('PID {0}  {1}  {2}% CPU{3}' -f $x.ProcId, $x.Name, $x.Cpu, $note) -ForegroundColor White
        Write-Host ('   owner:   {0}' -f $x.Owner)
        Write-Host ('   started: {0}' -f $x.Started)
        Write-Host ('   parent:  {0} ({1})' -f $x.ParentId, $x.ParentName)
        Write-Host ('   command: {0}' -f (Format-Cmd $x.CmdLine))
    }

    # Informational top 10 (never offered for killing).
    Write-Host ''
    Write-Host '=== Top 10 CPU processes overall (informational only, never offered for closing) ===' -ForegroundColor Cyan
    $top = @($rows | Where-Object { $_.ProcId -ne 0 } | Sort-Object -Property Cpu -Descending | Select-Object -First 10)
    foreach ($t in $top) {
        Write-Host ('   {0,5}%  PID {1,-6} {2}  ({3})' -f $t.Cpu, $t.ProcId, $t.Cim.Name, (Get-OwnerText $t.Cim))
    }

    if (-not $Kill) { return }

    # ---- -Kill: per-process confirmation
    $killable = @($sorted | Where-Object { -not $_.Protected })
    Write-Host ''
    if ($killable.Count -eq 0) {
        Write-Host 'Nothing to close (no unprotected busy script processes).'
        return
    }
    Write-Host ('--- Close processes ({0} candidate(s); default answer is No) ---' -f $killable.Count) -ForegroundColor Cyan
    $all = $false
    foreach ($x in $killable) {
        # Re-check right before acting: same process (name + start time) and still not protected.
        $fresh = $null
        try { $fresh = Get-CimInstance -ClassName Win32_Process -Filter ('ProcessId=' + $x.ProcId) -ErrorAction Stop } catch { }
        if (-not $fresh) {
            Write-Host ('PID {0} ({1}) no longer running; skipped.' -f $x.ProcId, $x.Name)
            continue
        }
        if (([string]$fresh.Name -ne $x.Name) -or ($fresh.CreationDate -ne $x.Started)) {
            Write-Host ('PID {0}: a different process now uses this id; skipped.' -f $x.ProcId)
            continue
        }
        $freshMap = Get-CimProcessMap
        $freshChain = Get-OwnChain $freshMap
        $why = Get-ProtectionReason $x.ProcId (Get-ImageName $fresh.Name) $freshChain
        if ($why) {
            Write-Host ('PID {0} ({1}) is protected ({2}); skipped.' -f $x.ProcId, $x.Name, $why)
            continue
        }

        if (-not $script:DryRun) {
            if (-not $all) {
                $ans = Read-Answer ('Close PID {0} ({1}, {2}% CPU)? [y/N/a=all remaining/q=quit]' -f $x.ProcId, $x.Name, $x.Cpu)
                if ($ans -eq 'q') { Write-Host 'Quit.'; break }
                if ($ans -eq 'a') { $all = $true }
                elseif ($ans -ne 'y') { Write-Host '   left running.'; continue }
            }
        }
        if (Confirm-Action ('PID {0} ({1})' -f $x.ProcId, $x.Name) 'Stop process') {
            try {
                Stop-Process -Id $x.ProcId -Force -ErrorAction Stop
                Start-Sleep -Milliseconds 700
                if (Get-Process -Id $x.ProcId -ErrorAction SilentlyContinue) {
                    Write-Host ('   PID {0}: still running after Stop-Process.' -f $x.ProcId) -ForegroundColor Red
                    $script:KillFailures++
                }
                else {
                    Write-Host ('   PID {0}: closed.' -f $x.ProcId) -ForegroundColor Green
                }
            }
            catch {
                Write-Host ('   PID {0}: FAILED: {1}' -f $x.ProcId, $_.Exception.Message) -ForegroundColor Red
                $script:KillFailures++
            }
        }
    }
}

# ---------------------------------------------------------------- PC Guard removal

function Get-ServiceImageDir {
    # Install folder according to the service registration, or $null.
    try {
        if (-not (Test-Path -LiteralPath $ServiceKey)) { return $null }
        $ip = [string](Get-ItemProperty -LiteralPath $ServiceKey -Name ImagePath -ErrorAction Stop).ImagePath
        $ip = [Environment]::ExpandEnvironmentVariables($ip).Trim()
        $exe = $ip
        if ($ip -match '^"([^"]+)"') { $exe = $Matches[1] }
        elseif ($ip -match '^(.+?\.exe)') { $exe = $Matches[1] }
        $exe = $exe -replace '^\\\?\?\\', ''
        return (Split-Path -Parent $exe)
    }
    catch {
        return $null
    }
}

function Get-DefaultInstallDir {
    $pf = $env:ProgramW6432
    if (-not $pf) { $pf = $env:ProgramFiles }
    return (Join-Path $pf 'PcGuard')
}

function Get-DeleteRefusal {
    # Returns a reason when the folder must NOT be deleted, otherwise $null.
    param([string]$Path)
    $full = [System.IO.Path]::GetFullPath($Path).TrimEnd('\')
    if ($full.StartsWith('\\')) { return 'network (UNC) path' }
    $root = [System.IO.Path]::GetPathRoot($full).TrimEnd('\')
    if ($full -eq $root) { return 'drive root' }
    $forbidden = @($env:windir, $env:SystemRoot, $env:ProgramFiles, $env:ProgramW6432, ${env:ProgramFiles(x86)},
        $env:ProgramData, $env:SystemDrive, $env:USERPROFILE, (Join-Path $env:SystemRoot 'System32'))
    foreach ($f in $forbidden) {
        if ($f -and ($full -eq $f.TrimEnd('\'))) { return ('protected system folder (' + $f + ')') }
    }
    if ($env:windir -and $full.StartsWith(($env:windir.TrimEnd('\') + '\'), [StringComparison]::OrdinalIgnoreCase)) {
        return 'inside the Windows folder'
    }
    $leaf = Split-Path -Leaf $full
    $hasFiles = (Test-Path -LiteralPath (Join-Path $full 'PcGuard.Service.exe')) -or (Test-Path -LiteralPath (Join-Path $full 'PcGuard.Shell.exe'))
    if ((-not $hasFiles) -and ($leaf -ne 'PcGuard')) {
        return 'folder is not named PcGuard and contains no PcGuard.Service.exe / PcGuard.Shell.exe'
    }
    return $null
}

function Remove-DirForced {
    # Resets ACLs, deletes; if that fails takes ownership and retries. Throws when the folder remains.
    param([string]$Path)
    Invoke-Native 'icacls.exe' @($Path, '/reset', '/T', '/C', '/Q') | Out-Null
    try {
        Remove-Item -LiteralPath $Path -Recurse -Force -ErrorAction Stop
    }
    catch { }
    if (-not (Test-Path -LiteralPath $Path)) { return }
    Invoke-Native 'takeown.exe' @('/F', $Path, '/R', '/D', 'Y') | Out-Null
    Invoke-Native 'icacls.exe' @($Path, '/reset', '/T', '/C', '/Q') | Out-Null
    try {
        Remove-Item -LiteralPath $Path -Recurse -Force -ErrorAction Stop
    }
    catch {
        throw ('could not delete ''' + $Path + ''': ' + $_.Exception.Message)
    }
    if (Test-Path -LiteralPath $Path) { throw ('''' + $Path + ''' still exists after deletion attempt.') }
}

function Stop-ProcessesByBaseName {
    # Returns the number of processes still running. Stop-Process first, taskkill /f as fallback.
    param([string]$BaseName)
    $procs = @(Get-Process -Name $BaseName -ErrorAction SilentlyContinue)
    foreach ($p in $procs) {
        try { Stop-Process -Id $p.Id -Force -ErrorAction Stop } catch { }
    }
    Start-Sleep -Milliseconds 800
    $left = @(Get-Process -Name $BaseName -ErrorAction SilentlyContinue)
    if ($left.Count -gt 0) {
        Invoke-Native 'taskkill.exe' @('/f', '/im', ($BaseName + '.exe')) | Out-Null
        Start-Sleep -Seconds 1
        $left = @(Get-Process -Name $BaseName -ErrorAction SilentlyContinue)
    }
    return $left.Count
}

function Test-ServiceExists {
    return [bool](Get-Service -Name $ServiceName -ErrorAction SilentlyContinue)
}

function Invoke-RemovePcGuard {
    # ---- resolve the install folder BEFORE the service is deleted
    $dirSource = ''
    $candidates = New-Object System.Collections.ArrayList
    if ($InstallDir) {
        [void]$candidates.Add($InstallDir)
        $dirSource = 'from -InstallDir'
    }
    else {
        $fromSvc = Get-ServiceImageDir
        if ($fromSvc) { [void]$candidates.Add($fromSvc) }
        [void]$candidates.Add((Get-DefaultInstallDir))
    }
    $resolved = $null
    foreach ($c in $candidates) {
        if ($c -and (Test-Path -LiteralPath $c)) { $resolved = $c; break }
    }
    if (-not $resolved) { $resolved = $candidates[0] }
    if (-not $dirSource) {
        if ($resolved -eq (Get-DefaultInstallDir)) { $dirSource = 'default location' } else { $dirSource = 'from the service ImagePath' }
    }
    $script:TargetDir = $resolved
    $dataDir = Join-Path $env:ProgramData 'PcGuard'
    $setupDirs = @()
    try { $setupDirs = @(Get-ChildItem -LiteralPath $env:ProgramData -Directory -Filter 'PcGuard-setup-*' -Force -ErrorAction SilentlyContinue) } catch { }

    Write-Host ''
    Write-Host '=== Remove PC Guard (forced) ===' -ForegroundColor Cyan
    Write-Host 'This will:'
    Write-Host '  - disable and stop the PcGuard service, end PcGuard.Service.exe and PcGuard.Shell.exe'
    Write-Host '  - delete the PcGuard service and its Safe Mode registry keys'
    Write-Host ('  - delete the install folder: {0} ({1})' -f $resolved, $dirSource)
    Write-Host ('  - delete {0} leftover PcGuard-setup-* folder(s) in {1}' -f $setupDirs.Count, $env:ProgramData)
    if ($Purge) {
        Write-Host ('  - DELETE {0} (machine key, rules, usage queue)' -f $dataDir) -ForegroundColor Yellow
    }
    else {
        Write-Host ('  - keep {0} (use -Purge to delete it)' -f $dataDir)
    }
    if ($script:DryRun) {
        Write-Host '(-WhatIf: nothing will be changed)' -ForegroundColor Yellow
    }
    elseif (-not $Force) {
        $ans = Read-Answer 'Type YES to continue'
        if ($ans -ne 'yes') {
            Write-Host 'Cancelled. Nothing was changed.'
            return
        }
    }
    Write-Host ''
    Write-Host 'Steps:'

    # 1. Stop recovery from restarting the service, then stop it.
    Invoke-Step 'Disable service' {
        if (-not (Test-ServiceExists)) { Add-Result $Name 'SKIPPED' 'service not registered'; return }
        if (-not (Confirm-Action $ServiceName 'sc.exe config start= disabled; failureflag 0')) { Add-Result $Name 'SKIPPED' 'WhatIf'; return }
        $o1 = Invoke-Native 'sc.exe' @('config', $ServiceName, 'start=', 'disabled')
        $e1 = $script:NativeExit
        $o2 = Invoke-Native 'sc.exe' @('failureflag', $ServiceName, '0')
        $e2 = $script:NativeExit
        if ($e1 -ne 0) { Add-Result $Name 'SKIPPED' ('could not disable (exit ' + $e1 + '); continuing: ' + ($o1 -join ' ')); return }
        Add-Result $Name 'OK' ('start type disabled; failureflag exit ' + $e2)
    }

    Invoke-Step 'Stop service' {
        if (-not (Test-ServiceExists)) { Add-Result $Name 'SKIPPED' 'service not registered'; return }
        $svc = Get-Service -Name $ServiceName
        if ($svc.Status -eq 'Stopped') { Add-Result $Name 'SKIPPED' 'already stopped'; return }
        if (-not (Confirm-Action $ServiceName 'Stop service')) { Add-Result $Name 'SKIPPED' 'WhatIf'; return }
        try { Stop-Service -Name $ServiceName -Force -ErrorAction Stop } catch { }
        try { $svc.WaitForStatus('Stopped', [TimeSpan]::FromSeconds(30)) } catch { }
        $svc.Refresh()
        if ($svc.Status -eq 'Stopped') { Add-Result $Name 'OK' 'stopped' }
        else { Add-Result $Name 'SKIPPED' ('status is ' + $svc.Status + ' after 30 s; the process is ended in the next step') }
    }

    Invoke-Step 'End PcGuard.Service.exe' {
        $present = @(Get-Process -Name 'PcGuard.Service' -ErrorAction SilentlyContinue)
        if ($present.Count -eq 0) { Add-Result $Name 'SKIPPED' 'not running'; return }
        if (-not (Confirm-Action 'PcGuard.Service.exe' 'Stop process')) { Add-Result $Name 'SKIPPED' 'WhatIf'; return }
        $left = Stop-ProcessesByBaseName 'PcGuard.Service'
        if ($left -eq 0) { Add-Result $Name 'OK' ('ended ' + $present.Count + ' process(es)') }
        else { Add-Result $Name 'FAILED' ($left.ToString() + ' process(es) still running. Reboot (or boot into Safe Mode) and run this script again.') }
    }

    Invoke-Step 'End PcGuard.Shell.exe' {
        $present = @(Get-Process -Name 'PcGuard.Shell' -ErrorAction SilentlyContinue)
        if ($present.Count -eq 0) { Add-Result $Name 'SKIPPED' 'not running'; return }
        if (-not (Confirm-Action 'PcGuard.Shell.exe' 'Stop process')) { Add-Result $Name 'SKIPPED' 'WhatIf'; return }
        $left = Stop-ProcessesByBaseName 'PcGuard.Shell'
        if ($left -eq 0) { Add-Result $Name 'OK' ('ended ' + $present.Count + ' process(es)') }
        else { Add-Result $Name 'FAILED' ($left.ToString() + ' process(es) still running (the shell is protected). Reboot into Safe Mode / see README, then run this script again.') }
    }

    # 2. Delete the service.
    Invoke-Step 'Delete service' {
        if (-not (Test-ServiceExists)) { Add-Result $Name 'SKIPPED' 'service not registered'; return }
        if (-not (Confirm-Action $ServiceName 'sc.exe delete')) { Add-Result $Name 'SKIPPED' 'WhatIf'; return }
        $out = Invoke-Native 'sc.exe' @('delete', $ServiceName)
        if ($script:NativeExit -ne 0) {
            Add-Result $Name 'FAILED' ('sc.exe delete exit code ' + $script:NativeExit + ': ' + ($out -join ' '))
            return
        }
        $deadline = (Get-Date).AddSeconds(30)
        while ((Test-ServiceExists) -and (Get-Date) -lt $deadline) { Start-Sleep -Milliseconds 500 }
        if (Test-ServiceExists) {
            Add-Result $Name 'FAILED' 'still registered (marked for deletion; something holds a handle, for example a Services or Event Viewer window). A reboot is needed; then run this script again.'
        }
        else {
            Add-Result $Name 'OK' 'deleted'
        }
    }

    # 3. Safe Mode keys.
    foreach ($mode in @('Minimal', 'Network')) {
        $key = 'HKLM:\SYSTEM\CurrentControlSet\Control\SafeBoot\' + $mode + '\PcGuard'
        $stepName = 'Safe Mode key ' + $mode
        Invoke-Step $stepName {
            if (-not (Test-Path -LiteralPath $key)) { Add-Result $Name 'SKIPPED' 'not present'; return }
            if (-not (Confirm-Action $key 'Remove registry key')) { Add-Result $Name 'SKIPPED' 'WhatIf'; return }
            Remove-Item -LiteralPath $key -Recurse -Force -ErrorAction Stop
            Add-Result $Name 'OK' 'removed'
        }
    }

    # 4. Install folder.
    Invoke-Step 'Install folder' {
        $dir = $script:TargetDir
        if (-not (Test-Path -LiteralPath $dir)) { Add-Result $Name 'SKIPPED' ($dir + ' does not exist'); return }
        $refusal = Get-DeleteRefusal $dir
        if ($refusal) { Add-Result $Name 'FAILED' ('refusing to delete ''' + $dir + ''': ' + $refusal); return }
        if (-not (Confirm-Action $dir 'Delete folder recursively')) { Add-Result $Name 'SKIPPED' 'WhatIf'; return }
        Remove-DirForced $dir
        Add-Result $Name 'OK' ('deleted ' + $dir)
    }

    # 5. Leftover setup temp folders.
    Invoke-Step 'Setup temp folders' {
        $list = @()
        try { $list = @(Get-ChildItem -LiteralPath $env:ProgramData -Directory -Filter 'PcGuard-setup-*' -Force -ErrorAction SilentlyContinue) } catch { }
        if ($list.Count -eq 0) { Add-Result $Name 'SKIPPED' 'none found'; return }
        $done = 0
        $bad = @()
        foreach ($d in $list) {
            if ($d.Name -notlike 'PcGuard-setup-*') { continue }
            if (($d.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { $bad += ($d.FullName + ' (reparse point, skipped)'); continue }
            if (-not (Confirm-Action $d.FullName 'Delete folder recursively')) { continue }
            try { Remove-DirForced $d.FullName; $done++ } catch { $bad += ($d.FullName + ': ' + $_.Exception.Message) }
        }
        if ($bad.Count -gt 0) { Add-Result $Name 'FAILED' ($bad -join '; ') }
        elseif ($script:DryRun) { Add-Result $Name 'SKIPPED' 'WhatIf' }
        else { Add-Result $Name 'OK' ('deleted ' + $done + ' folder(s)') }
    }

    # 6. Data folder (machine key) only with -Purge.
    Invoke-Step 'Data folder' {
        $data = Join-Path $env:ProgramData 'PcGuard'
        if (-not $Purge) {
            if (Test-Path -LiteralPath $data) { Add-Result $Name 'SKIPPED' ('kept ' + $data + ' (machine key, rules, usage queue); use -Purge to delete') }
            else { Add-Result $Name 'SKIPPED' 'not present' }
            return
        }
        if (-not (Test-Path -LiteralPath $data)) { Add-Result $Name 'SKIPPED' 'not present'; return }
        if (-not (Confirm-Action $data 'Delete folder recursively (-Purge)')) { Add-Result $Name 'SKIPPED' 'WhatIf'; return }
        # No "icacls /reset": it would briefly expose machine.key through inherited rights.
        Remove-Item -LiteralPath $data -Recurse -Force -ErrorAction Stop
        if (Test-Path -LiteralPath $data) { throw ('''' + $data + ''' still exists after deletion.') }
        Add-Result $Name 'OK' ('deleted ' + $data)
    }

    $old = @()
    try { $old = @(Get-ChildItem -LiteralPath (Split-Path -Parent $resolved) -Directory -Filter ((Split-Path -Leaf $resolved) + '.old-*') -ErrorAction SilentlyContinue) } catch { }
    if ($old.Count -gt 0) {
        Write-Host ''
        Write-Host 'Note: these backup folders from earlier upgrades were NOT touched (delete them by hand if wanted):'
        foreach ($o in $old) { Write-Host ('   ' + $o.FullName) }
    }
}

# ---------------------------------------------------------------- main

try {
    $doFind = ($FindBusyScripts -or $Kill -or (-not $RemovePcGuard))

    if ($Purge -and -not $RemovePcGuard) { throw '-Purge only makes sense together with -RemovePcGuard.' }
    if ($InstallDir -and -not $RemovePcGuard) { throw '-InstallDir only makes sense together with -RemovePcGuard.' }

    if (($RemovePcGuard -or $Kill) -and -not (Test-IsAdmin)) {
        throw 'This needs Administrator rights (-RemovePcGuard and -Kill). Right-click PowerShell, choose "Run as administrator", and run it again.'
    }

    Write-Host 'PC Guard cleanup' -ForegroundColor Cyan
    Write-Host 'Command lines in the report are shown as-is and may contain secrets: do not paste the output publicly.' -ForegroundColor Yellow
    if ($script:DryRun) { Write-Host '-WhatIf: nothing will be closed, stopped or deleted.' -ForegroundColor Yellow }

    if ($doFind) { Invoke-FindBusyScripts }
    if ($RemovePcGuard) { Invoke-RemovePcGuard }

    $failed = @($script:Results | Where-Object { $_.Status -eq 'FAILED' }).Count + $script:KillFailures
    if ($script:Results.Count -gt 0) {
        Write-Host ''
        Write-Host '=== Summary ===' -ForegroundColor Cyan
        foreach ($r in $script:Results) {
            Write-Host ('  {0,-8} {1}' -f $r.Status, $r.Step)
        }
    }
    if ($failed -gt 0) {
        Write-Host ''
        Write-Host ('{0} step(s) FAILED. See the messages above.' -f $failed) -ForegroundColor Red
        exit 2
    }
    Write-Host ''
    Write-Host 'Done.' -ForegroundColor Green
    exit 0
}
catch {
    Write-Host ('ERROR: ' + $_.Exception.Message) -ForegroundColor Red
    exit 1
}
