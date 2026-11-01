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
  Never touched: system processes, explorer, this PowerShell and its parent chain, anything named PcGuard*, and
  script hosts started by PcGuard / Setup-PcGuard (PC Guard is removed only through -RemovePcGuard).
  Folder deletion never follows junctions or symlinks (reparse points are removed as links only).
  Command lines are shown as-is and may contain secrets: do not paste the output publicly.
  NOT TESTED: written without PowerShell available; run the VM checklist in CLEANUP.md.
  Compatible with Windows PowerShell 5.1 and PowerShell 7 (no ternary, no pipeline chain operators).
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
  A folder whose name is not PcGuard is deleted only together with -Force.
.PARAMETER Purge
  With -RemovePcGuard: also delete %ProgramData%\PcGuard (machine key, rules, usage queue).
.PARAMETER Force
  With -RemovePcGuard: do not ask to type YES (and allow an explicit -InstallDir not named PcGuard).
  It does NOT override the install-folder ACL safety check (see -IgnoreAcl).
.PARAMETER IgnoreAcl
  With -RemovePcGuard: delete the install folder even though Users / Everyone / Authenticated Users / INTERACTIVE can write
  to it. DANGEROUS: in a user-writable folder a directory can be swapped for a junction while it is being deleted.
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
    [switch]$Force,
    [switch]$IgnoreAcl
)

$ErrorActionPreference = 'Stop'
$ServiceName = 'PcGuard'
$ServiceKey = 'HKLM:\SYSTEM\CurrentControlSet\Services\PcGuard'
$script:Cmdlet = $PSCmdlet
$script:DryRun = [bool]$WhatIfPreference
$script:NativeExit = 0
$script:Results = New-Object System.Collections.ArrayList
$script:KillFailures = 0
$script:ProcEndFailed = $false
$script:ServiceTouched = $false
$script:OrigStart = $null
$script:TargetDir = $null
$script:DirExplicit = $false
$script:RemovalRan = $false
$script:SvcDisabled = $false

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

function Get-NotDoneText {
    if ($script:DryRun) { return 'WhatIf: not performed' }
    return 'not performed (declined at the -Confirm prompt)'
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
    # pid (int) -> Win32_Process instance (read-only query)
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
    param([int]$ProcId, [string]$ImgName, $Chain, $CimMap)
    if ($ProcId -le 4) { return 'system process id' }
    if ($Chain.ContainsKey($ProcId)) { return 'this PowerShell or its parent chain' }
    if ($ProtectedNames -contains $ImgName) { return 'system / shell process' }
    if ($ImgName -like 'pcguard*') { return 'PC Guard (use -RemovePcGuard)' }
    # Anything started (directly or indirectly) by PcGuard or Setup-PcGuard is protected.
    $cur = $CimMap[$ProcId]
    $guard = 0
    while ($cur -and $guard -lt 32) {
        $pp = [int]$cur.ParentProcessId
        if ($pp -le 0) { break }
        $par = $CimMap[$pp]
        if (-not $par) { break }
        $pn = Get-ImageName ([string]$par.Name)
        if (($pn -like 'pcguard*') -or ($pn -like 'setup-pcguard*')) { return 'started by PC Guard / Setup-PcGuard' }
        $cur = $par
        $guard++
    }
    return $null
}

function Get-OwnerText {
    param($CimProc)
    try {
        $r = Invoke-CimMethod -InputObject $CimProc -MethodName GetOwner -WhatIf:$false -Confirm:$false -ErrorAction Stop
        if ($r -and $r.User) { return ('{0}\{1}' -f $r.Domain, $r.User) }
    }
    catch { }
    return '(unknown)'
}

function Get-CpuSample {
    # pid (int) -> @{ Cpu = total processor seconds; Start = StartTime or $null }
    $h = @{}
    foreach ($p in (Get-Process -ErrorAction SilentlyContinue)) {
        $cpu = $null
        try { $cpu = $p.TotalProcessorTime.TotalSeconds } catch { $cpu = $null }
        if ($null -eq $cpu) { continue }
        $st = $null
        try { $st = $p.StartTime } catch { $st = $null }
        $h[[int]$p.Id] = [pscustomobject]@{ Cpu = $cpu; Start = $st }
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
    # Enter, EOF or a non-interactive host never count as yes: Read-Host failing returns 'q'.
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
        $a = $s1[$procId]
        $b = $s2[$procId]
        # Same PID but a different start time means the PID was reused: skip.
        if ($a.Start -and $b.Start -and ($a.Start -ne $b.Start)) { continue }
        $delta = $b.Cpu - $a.Cpu
        if ($delta -lt 0) { $delta = 0 }
        $pct = ($delta / ($elapsed * $cores)) * 100
        $c = $cim[$procId]
        if (-not $c) { continue }
        $startOk = [bool]($a.Start -and $b.Start)
        [void]$rows.Add([pscustomobject]@{ ProcId = [int]$procId; Cpu = [math]::Round($pct, 1); CpuRaw = $pct; StartOk = $startOk; Cim = $c })
    }

    # Candidates: script hosts, or script-looking command lines whose parent is a script host.
    $cands = New-Object System.Collections.ArrayList
    foreach ($r in $rows) {
        if ($r.CpuRaw -lt $MinCpuPercent) { continue }   # compare the UNROUNDED value; Cpu is for display only
        if ($r.ProcId -eq 0) { continue }
        if (-not $r.StartOk) { continue }   # fail closed: no start time in both samples => PID reuse cannot be excluded
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
        $reason = Get-ProtectionReason $r.ProcId $img $chain $cim
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
        if (-not $script:DryRun) {
            if (-not $all) {
                $ans = Read-Answer ('Close PID {0} ({1}, {2}% CPU)? [y/N/a=all remaining/q=quit]' -f $x.ProcId, $x.Name, $x.Cpu)
                if ($ans -eq 'q') { Write-Host 'Quit.'; break }
                if ($ans -eq 'a') { $all = $true }
                elseif ($ans -ne 'y') { Write-Host '   not closed (answered No); still running.'; continue }
            }
        }

        # Re-check AFTER the answer: the PID may have been reused while the prompt waited.
        $p = $null
        try { $p = Get-Process -Id $x.ProcId -ErrorAction Stop } catch { $p = $null }
        if (-not $p) {
            Write-Host ('   PID {0} ({1}) is no longer running; skipped.' -f $x.ProcId, $x.Name)
            continue
        }
        $pStart = $null
        try { $pStart = $p.StartTime } catch { $pStart = $null }
        $sameStart = $false
        if ($pStart -and $x.Started) {
            if ([math]::Abs(($pStart - $x.Started).TotalSeconds) -le 2) { $sameStart = $true }
        }
        $freshMap = Get-CimProcessMap
        $freshCim = $freshMap[[int]$x.ProcId]
        $sameName = $false
        if ($freshCim) {
            if ((Get-ImageName ([string]$freshCim.Name)) -eq $x.Image) { $sameName = $true }
        }
        if ((-not $sameStart) -or (-not $sameName) -or ((Get-ImageName $p.ProcessName) -ne $x.Image)) {
            Write-Host ('   PID {0}: PID was reused (or could not be verified); skipped.' -f $x.ProcId) -ForegroundColor Yellow
            continue
        }
        $freshChain = Get-OwnChain $freshMap
        $why = Get-ProtectionReason $x.ProcId $x.Image $freshChain $freshMap
        if ($why) {
            Write-Host ('   PID {0} ({1}) is protected ({2}); skipped.' -f $x.ProcId, $x.Name, $why)
            continue
        }

        if (Confirm-Action ('PID {0} ({1})' -f $x.ProcId, $x.Name) 'Stop process') {
            try {
                # Kill through the very object that was verified above, not through the bare PID.
                Stop-Process -InputObject $p -Force -WhatIf:$false -Confirm:$false -ErrorAction Stop
                Start-Sleep -Milliseconds 700
                $gone = $false
                try { $p.Refresh(); $gone = $p.HasExited } catch { $gone = $false }
                if ($gone) {
                    Write-Host ('   PID {0}: closed.' -f $x.ProcId) -ForegroundColor Green
                }
                else {
                    Write-Host ('   PID {0}: not confirmed closed (still running or state unreadable).' -f $x.ProcId) -ForegroundColor Red
                    $script:KillFailures++
                }
            }
            catch {
                $killMsg = $_.Exception.Message
                $exitedNow = $false
                try { $p.Refresh(); $exitedNow = $p.HasExited } catch { $exitedNow = $false }
                if ($exitedNow) {
                    Write-Host ('   PID {0}: already gone.' -f $x.ProcId) -ForegroundColor Green
                }
                else {
                    Write-Host ('   PID {0}: FAILED: {1}' -f $x.ProcId, $killMsg) -ForegroundColor Red
                    $script:KillFailures++
                }
            }
        }
        else {
            Write-Host ('   PID {0}: {1}' -f $x.ProcId, (Get-NotDoneText))
        }
    }
}

# ---------------------------------------------------------------- safe folder deletion

function Resolve-FsPath {
    # Resolves a path ONCE (relative to the PowerShell location, not the process directory). FileSystem provider only.
    param([string]$Path)
    if ([string]::IsNullOrWhiteSpace($Path)) { throw 'empty path' }
    $prov = $null
    $drv = $null
    $full = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($Path, [ref]$prov, [ref]$drv)
    if ((-not $prov) -or ($prov.Name -ne 'FileSystem')) { throw ('not a file system path: ' + $Path) }
    if ($full -notmatch '^[A-Za-z]:\\') { throw ('must be an absolute local path with a drive letter: ' + $Path) }
    $full = [System.IO.Path]::GetFullPath($full)
    if ($full.Length -gt 3) { $full = $full.TrimEnd('\') }
    return $full
}

function Test-IsReparse {
    param($Info)
    return ((([int]$Info.Attributes) -band ([int][System.IO.FileAttributes]::ReparsePoint)) -ne 0)
}

function Grant-AdminOnItem {
    # Per ITEM only (never recursive); /L acts on a link itself instead of its target. Locale independent (SID).
    param([string]$Path)
    Invoke-Native 'icacls.exe' @($Path, '/setowner', '*S-1-5-32-544', '/C', '/L', '/Q') | Out-Null
    Invoke-Native 'icacls.exe' @($Path, '/grant', '*S-1-5-32-544:(F)', '/C', '/L', '/Q') | Out-Null
}

function Test-ItemUnchanged {
    # Fresh read of the attributes of the item ITSELF (a link is not followed): still the same kind as when listed?
    param([string]$Path, [bool]$IsDir, [bool]$IsLink)
    try {
        $a = [int][System.IO.File]::GetAttributes($Path)
    }
    catch {
        return $false
    }
    $nowLink = (($a -band ([int][System.IO.FileAttributes]::ReparsePoint)) -ne 0)
    $nowDir = (($a -band ([int][System.IO.FileAttributes]::Directory)) -ne 0)
    return (($nowLink -eq $IsLink) -and ($nowDir -eq $IsDir))
}

function Remove-OneItem {
    # Deletes one file / directory / link. A link is removed as a link only. On failure fixes ACL of that item and retries once.
    # The kind of the item is re-read immediately before deleting (a changed or unreadable state is a failure for that item).
    param([string]$Path, [bool]$IsDir, [bool]$IsLink, $Errors)
    if (-not (Test-ItemUnchanged $Path $IsDir $IsLink)) {
        [void]$Errors.Add($Path + ': changed or unreadable just before deletion; not deleted')
        return
    }
    $lastMsg = ''
    for ($attempt = 0; $attempt -lt 2; $attempt++) {
        try {
            if (-not $IsLink) {
                # Never touch attributes of a link here: that could follow it to the target.
                try { [System.IO.File]::SetAttributes($Path, [System.IO.FileAttributes]::Normal) } catch { }
            }
            if ($IsDir) { [System.IO.Directory]::Delete($Path, $false) }
            else { [System.IO.File]::Delete($Path) }
            return
        }
        catch {
            $lastMsg = $_.Exception.Message
        }
        if ($attempt -eq 0) {
            if ($IsLink -and (-not $IsDir)) {
                # File link: never SetAttributes on it (that can follow the link and strips Hidden/System).
                # Only when the link ITSELF is read-only: attrib /L acts on the link, not on its target.
                $ro = $false
                try { $ro = ((([int][System.IO.File]::GetAttributes($Path)) -band ([int][System.IO.FileAttributes]::ReadOnly)) -ne 0) } catch { $ro = $false }
                if ($ro) { Invoke-Native 'attrib.exe' @('-R', '/L', $Path) | Out-Null }
            }
            Grant-AdminOnItem $Path
        }
    }
    [void]$Errors.Add($Path + ': ' + $lastMsg)
}

function Remove-TreeInner {
    # NOTE ON RACES: the listing is a snapshot. The attributes are re-read right before recursing and right before every
    # delete, but the real protection is that callers only pass folders that Test-TrustedAdminFolder /
    # Test-NoNonAdminWrite accepted: nobody but administrators can create or swap entries there while this runs.
    param([string]$Dir, $Errors)
    $children = @()
    $listed = $false
    for ($attempt = 0; $attempt -lt 2; $attempt++) {
        try {
            $di = New-Object System.IO.DirectoryInfo($Dir)
            $children = @($di.GetFileSystemInfos())
            $listed = $true
            break
        }
        catch {
            if ($attempt -eq 0) { Grant-AdminOnItem $Dir }
            else { [void]$Errors.Add($Dir + ': cannot list: ' + $_.Exception.Message) }
        }
    }
    if (-not $listed) { return }
    foreach ($c in $children) {
        $link = Test-IsReparse $c
        if ($c -is [System.IO.DirectoryInfo]) {
            if (-not $link) {
                if (-not (Test-ItemUnchanged $c.FullName $true $false)) {
                    [void]$Errors.Add($c.FullName + ': changed or unreadable before descending; skipped')
                    continue
                }
                Remove-TreeInner $c.FullName $Errors
            }
            Remove-OneItem $c.FullName $true $link $Errors
        }
        else {
            Remove-OneItem $c.FullName $false $link $Errors
        }
    }
}

function Remove-TreeSafe {
    # Deletes a folder tree WITHOUT following junctions / symlinks. Throws on any problem. Root must not be a link.
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) { return }
    $root = New-Object System.IO.DirectoryInfo($Path)
    if (Test-IsReparse $root) {
        throw ('''' + $Path + ''' is a reparse point (junction or symlink); nothing was deleted.')
    }
    if ((([int]$root.Attributes) -band ([int][System.IO.FileAttributes]::Directory)) -eq 0) {
        throw ('''' + $Path + ''' is not a folder; nothing was deleted.')
    }
    $errs = New-Object System.Collections.ArrayList
    Remove-TreeInner $Path $errs
    Remove-OneItem $Path $true $false $errs
    if ($errs.Count -gt 0) {
        $first = @($errs | Select-Object -First 5) -join ' | '
        throw ('could not delete everything under ''' + $Path + ''' (' + $errs.Count + ' problem(s)): ' + $first)
    }
    if (Test-Path -LiteralPath $Path) { throw ('''' + $Path + ''' still exists after deletion.') }
}

function Get-FolderOwner {
    # @{ Text; Sid } of the folder owner, or $null when it cannot be determined.
    param([string]$Path)
    try {
        $acl = Get-Acl -LiteralPath $Path -ErrorAction Stop
        $text = [string]$acl.Owner
        if (-not $text) { return $null }
        $sid = $null
        if ($text -match '^S-1-') {
            $sid = (New-Object System.Security.Principal.SecurityIdentifier($text)).Value
        }
        else {
            $sid = (New-Object System.Security.Principal.NTAccount($text)).Translate([System.Security.Principal.SecurityIdentifier]).Value
        }
        return [pscustomobject]@{ Text = $text; Sid = $sid }
    }
    catch {
        return $null
    }
}

function Test-TrustedAdminFolder {
    # Fail closed (any error => $false). Sets $script:TrustWhy. Trusted = owner SYSTEM / Administrators / the current elevated
    # user, ACL not inherited, and every Allow ACE belongs to SYSTEM or Administrators (CREATOR OWNER is ignored).
    param([string]$Path)
    $script:TrustWhy = 'could not read the ACL'
    try {
        $owner = Get-FolderOwner $Path
        if (-not $owner) { $script:TrustWhy = 'owner unknown'; return $false }
        $me = [System.Security.Principal.WindowsIdentity]::GetCurrent().User.Value
        $okOwners = @('S-1-5-18', 'S-1-5-32-544', $me)
        if ($okOwners -notcontains $owner.Sid) { $script:TrustWhy = 'owner ' + $owner.Text; return $false }
        $acl = Get-Acl -LiteralPath $Path -ErrorAction Stop
        if (-not $acl.AreAccessRulesProtected) { $script:TrustWhy = 'owner ' + $owner.Text + ', ACL inherits entries from the parent folder'; return $false }
        $okAce = @('S-1-5-18', 'S-1-5-32-544', 'S-1-3-0')
        foreach ($r in $acl.GetAccessRules($true, $true, [System.Security.Principal.SecurityIdentifier])) {
            if ($r.AccessControlType -ne 'Allow') { continue }
            $sid = [string]$r.IdentityReference.Value
            if ($okAce -notcontains $sid) { $script:TrustWhy = 'owner ' + $owner.Text + ', non-admin ACE for ' + $sid; return $false }
        }
        return $true
    }
    catch {
        $script:TrustWhy = 'error while checking: ' + $_.Exception.Message
        return $false
    }
}

function Test-NoNonAdminWrite {
    # Fail closed. For the install folder (Users may legitimately have read/execute). Sets $script:WriteWhy.
    param([string]$Path)
    $script:WriteWhy = 'could not read the ACL'
    try {
        $acl = Get-Acl -LiteralPath $Path -ErrorAction Stop
        # WriteData 2, AppendData 4, DeleteSubdirectoriesAndFiles 64, Delete 0x10000, ChangePermissions 0x40000,
        # TakeOwnership 0x80000, GenericAll 0x10000000, GenericWrite 0x40000000
        $mask = (2 -bor 4 -bor 64 -bor 0x10000 -bor 0x40000 -bor 0x80000 -bor 0x10000000 -bor 0x40000000)
        $names = @{ 'S-1-5-32-545' = 'Users'; 'S-1-5-11' = 'Authenticated Users'; 'S-1-1-0' = 'Everyone'; 'S-1-5-4' = 'INTERACTIVE' }
        foreach ($r in $acl.GetAccessRules($true, $true, [System.Security.Principal.SecurityIdentifier])) {
            if ($r.AccessControlType -ne 'Allow') { continue }
            $sid = [string]$r.IdentityReference.Value
            if (-not $names.ContainsKey($sid)) { continue }
            $rights = [int]$r.FileSystemRights
            if (($rights -band $mask) -ne 0) {
                $script:WriteWhy = $names[$sid] + ' (' + $sid + ') has write-type rights (' + $r.FileSystemRights + ') on the folder'
                return $false
            }
        }
        return $true
    }
    catch {
        $script:WriteWhy = 'error while checking: ' + $_.Exception.Message
        return $false
    }
}

function Test-MarkedForDeletion {
    try {
        $v = (Get-ItemProperty -LiteralPath $ServiceKey -Name DeleteFlag -ErrorAction Stop).DeleteFlag
        return ([int]$v -ne 0)
    }
    catch {
        return $false
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

function Test-AnyFile {
    param([string]$Dir, [string[]]$Names)
    foreach ($n in $Names) {
        if (Test-Path -LiteralPath (Join-Path $Dir $n)) { return $true }
    }
    return $false
}

function Get-DeleteRefusal {
    # $Full must already be resolved with Resolve-FsPath. Returns a reason when the folder must NOT be deleted, else $null.
    param([string]$Full)
    $t = $Full.TrimEnd('\')
    $root = [System.IO.Path]::GetPathRoot($Full).TrimEnd('\')
    if ($t -eq $root) { return 'drive root' }
    $list = New-Object System.Collections.ArrayList
    foreach ($v in @($env:windir, $env:SystemRoot, $env:ProgramFiles, $env:ProgramW6432, ${env:ProgramFiles(x86)},
            $env:CommonProgramFiles, ${env:CommonProgramFiles(x86)}, $env:CommonProgramW6432, $env:ProgramData, $env:USERPROFILE)) {
        if ($v) { [void]$list.Add([string]$v) }
    }
    if ($env:SystemRoot) {
        [void]$list.Add((Join-Path $env:SystemRoot 'System32'))
        [void]$list.Add((Join-Path $env:SystemRoot 'SysWOW64'))
    }
    $profiles = New-Object System.Collections.ArrayList
    if ($env:USERPROFILE) { [void]$profiles.Add([string]$env:USERPROFILE) }
    if ($env:SystemDrive) {
        $users = Join-Path $env:SystemDrive 'Users'
        [void]$list.Add($users)
        try {
            foreach ($d in @(Get-ChildItem -LiteralPath $users -Directory -Force -ErrorAction SilentlyContinue)) {
                [void]$profiles.Add($d.FullName)
            }
        }
        catch { }
    }
    foreach ($pr in $profiles) {
        [void]$list.Add($pr)
        foreach ($sub in @('Desktop', 'Documents', 'Downloads')) { [void]$list.Add((Join-Path $pr $sub)) }
    }
    foreach ($f in $list) {
        if ($t -eq $f.TrimEnd('\')) { return ('protected system or user folder (' + $f + ')') }
    }
    if ($env:windir -and $t.StartsWith(($env:windir.TrimEnd('\') + '\'), [StringComparison]::OrdinalIgnoreCase)) {
        return 'inside the Windows folder'
    }
    return $null
}

function Stop-ProcessesByBaseName {
    # Returns the number of processes still running. Stop-Process first, taskkill /f as fallback.
    param([string]$BaseName)
    $procs = @(Get-Process -Name $BaseName -ErrorAction SilentlyContinue)
    foreach ($p in $procs) {
        try { Stop-Process -Id $p.Id -Force -WhatIf:$false -Confirm:$false -ErrorAction Stop } catch { }
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

function Write-MarkedBlock {
    $running = @(Get-Process -Name 'PcGuard.Service' -ErrorAction SilentlyContinue).Count
    Write-Host ''
    Write-Host 'The PcGuard service is marked for deletion: close Services / Event Viewer / Task Manager windows or reboot,' -ForegroundColor Red
    Write-Host 'then run this script again.' -ForegroundColor Red
    if ($script:SvcDisabled) { Write-Host '  This run set the service start type to disabled.' } else { Write-Host '  This run did not change the service start type.' }
    if ($running -gt 0) {
        Write-Host '  PcGuard.Service.exe is still running, so the PC is currently still guarded.' -ForegroundColor Yellow
        if ($script:SvcDisabled) { Write-Host '  Because the start type is now disabled it will NOT start again after a reboot.' -ForegroundColor Yellow }
    }
    else {
        Write-Host '  PcGuard.Service.exe is not running: this PC is UNGUARDED now.' -ForegroundColor Red
    }
    Write-Host '  When the removal is complete the PC stays unguarded until PC Guard is installed again (install.ps1).' -ForegroundColor Red
}

function Write-RestoreBlock {
    Write-Host ''
    Write-Host 'WARNING: the PcGuard service still exists but this script changed it. The PC is UNGUARDED until you rerun' -ForegroundColor Red
    Write-Host 'this script (after fixing the failed step) or restore the service by hand:' -ForegroundColor Red
    if ($null -ne $script:OrigStart) { Write-Host ('  (original Start value in the registry was {0}; 2 = automatic)' -f $script:OrigStart) }
    Write-Host '  sc.exe config PcGuard start= auto'
    Write-Host '  sc.exe failure PcGuard reset= 0 actions= restart/5000/restart/5000/restart/5000'
    Write-Host '  sc.exe failureflag PcGuard 1'
    Write-Host '  sc.exe start PcGuard'
}

function Invoke-RemovePcGuard {
    $script:RemovalRan = $true
    # ---- resolve the install folder ONCE, BEFORE the service is deleted
    $dirSource = ''
    $candidates = New-Object System.Collections.ArrayList
    if ($InstallDir) {
        [void]$candidates.Add((Resolve-FsPath $InstallDir))
        $script:DirExplicit = $true
        $dirSource = 'from -InstallDir'
    }
    else {
        $fromSvc = Get-ServiceImageDir
        if ($fromSvc) {
            try { [void]$candidates.Add((Resolve-FsPath $fromSvc)) } catch { }
        }
        [void]$candidates.Add((Resolve-FsPath (Get-DefaultInstallDir)))
    }
    $resolved = $null
    foreach ($c in $candidates) {
        if (Test-Path -LiteralPath $c) { $resolved = $c; break }
    }
    if (-not $resolved) { $resolved = $candidates[0] }
    if (-not $dirSource) {
        if ($resolved -eq (Resolve-FsPath (Get-DefaultInstallDir))) { $dirSource = 'default location' } else { $dirSource = 'from the service ImagePath' }
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
    Write-Host ('  - delete the install folder: {0} ({1}); only if it passes the safety checks' -f $resolved, $dirSource)
    Write-Host ('  - delete PcGuard-setup-* folders in {0} that were created by Setup (currently {1})' -f $env:ProgramData, $setupDirs.Count)
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

    # 1. Disable the service (start= disabled is the real guard against a restart by the recovery actions), then stop it.
    Invoke-Step 'Disable service' {
        if (-not (Test-ServiceExists)) { Add-Result $Name 'SKIPPED' 'service not registered'; return }
        try { $script:OrigStart = [int](Get-ItemProperty -LiteralPath $ServiceKey -Name Start -ErrorAction Stop).Start } catch { $script:OrigStart = $null }
        if (-not (Confirm-Action $ServiceName 'sc.exe config start= disabled')) { Add-Result $Name 'SKIPPED' (Get-NotDoneText); return }
        $script:ServiceTouched = $true
        $o1 = Invoke-Native 'sc.exe' @('config', $ServiceName, 'start=', 'disabled')
        if ($script:NativeExit -ne 0) {
            Add-Result $Name 'FAILED' ('sc.exe config exit code ' + $script:NativeExit + ': ' + ($o1 -join ' ') + ' (the recovery actions may restart the service when it is killed)')
            return
        }
        $script:SvcDisabled = $true
        Add-Result $Name 'OK' ('start type set to disabled (original Start value: ' + $script:OrigStart + ')')
    }

    Invoke-Step 'Clear recovery actions' {
        if (-not (Test-ServiceExists)) { Add-Result $Name 'SKIPPED' 'service not registered'; return }
        if (-not (Confirm-Action $ServiceName 'sc.exe failure: clear recovery actions (no restart on failure)')) { Add-Result $Name 'SKIPPED' (Get-NotDoneText); return }
        $script:ServiceTouched = $true
        # One verbatim argument string: an empty "" argument would be dropped or mangled by array passing.
        $code = -1
        try {
            $pr = Start-Process -FilePath 'sc.exe' -ArgumentList 'failure PcGuard reset= 0 actions= ""' -Wait -PassThru -NoNewWindow -WhatIf:$false -Confirm:$false -ErrorAction Stop
            if ($null -eq $pr) { throw 'no process object returned by Start-Process' }
            if ($null -eq $pr.ExitCode) { throw 'sc.exe exit code is not available' }
            $code = [int]$pr.ExitCode
        }
        catch {
            Add-Result $Name 'FAILED' ('could not run sc.exe failure: ' + $_.Exception.Message + ' (the recovery actions may bring the service back when it is killed)')
            return
        }
        if ($code -ne 0) {
            Add-Result $Name 'FAILED' ('sc.exe failure exit code ' + $code + ' (the recovery actions may bring the service back when it is killed)')
            return
        }
        Add-Result $Name 'OK' 'recovery actions cleared'
    }

    Invoke-Step 'Stop service' {
        if (-not (Test-ServiceExists)) { Add-Result $Name 'SKIPPED' 'service not registered'; return }
        $svc = Get-Service -Name $ServiceName
        if ($svc.Status -eq 'Stopped') { Add-Result $Name 'SKIPPED' 'already stopped'; return }
        if (-not (Confirm-Action $ServiceName 'Stop service')) { Add-Result $Name 'SKIPPED' (Get-NotDoneText); return }
        $script:ServiceTouched = $true
        try { Stop-Service -Name $ServiceName -Force -WhatIf:$false -Confirm:$false -ErrorAction Stop } catch { }
        try { $svc.WaitForStatus('Stopped', [TimeSpan]::FromSeconds(30)) } catch { }
        $svc.Refresh()
        if ($svc.Status -eq 'Stopped') { Add-Result $Name 'OK' 'stopped' }
        else { Add-Result $Name 'SKIPPED' ('status is ' + $svc.Status + ' after 30 s; the process is ended in the next step') }
    }

    Invoke-Step 'End PcGuard.Service.exe' {
        $present = @(Get-Process -Name 'PcGuard.Service' -ErrorAction SilentlyContinue)
        if ($present.Count -eq 0) { Add-Result $Name 'SKIPPED' 'not running'; return }
        if (-not (Confirm-Action 'PcGuard.Service.exe' 'Stop process')) {
            if (-not $script:DryRun) { $script:ProcEndFailed = $true }
            Add-Result $Name 'SKIPPED' (Get-NotDoneText)
            return
        }
        $script:ServiceTouched = $true
        $left = Stop-ProcessesByBaseName 'PcGuard.Service'
        if ($left -eq 0) { Add-Result $Name 'OK' ('ended ' + $present.Count + ' process(es)') }
        else {
            $script:ProcEndFailed = $true
            Add-Result $Name 'FAILED' ($left.ToString() + ' process(es) still running. Reboot (or boot into Safe Mode) and run this script again.')
        }
    }

    Invoke-Step 'End PcGuard.Shell.exe' {
        $present = @(Get-Process -Name 'PcGuard.Shell' -ErrorAction SilentlyContinue)
        if ($present.Count -eq 0) { Add-Result $Name 'SKIPPED' 'not running'; return }
        if (-not (Confirm-Action 'PcGuard.Shell.exe' 'Stop process')) {
            if (-not $script:DryRun) { $script:ProcEndFailed = $true }
            Add-Result $Name 'SKIPPED' (Get-NotDoneText)
            return
        }
        $left = Stop-ProcessesByBaseName 'PcGuard.Shell'
        if ($left -eq 0) { Add-Result $Name 'OK' ('ended ' + $present.Count + ' process(es)') }
        else {
            $script:ProcEndFailed = $true
            Add-Result $Name 'FAILED' ($left.ToString() + ' process(es) still running (the shell is protected). Reboot into Safe Mode / see README, then run this script again.')
        }
    }

    # 2. Delete the service.
    Invoke-Step 'Delete service' {
        if (-not (Test-ServiceExists)) { Add-Result $Name 'SKIPPED' 'service not registered'; return }
        if (-not (Confirm-Action $ServiceName 'sc.exe delete')) { Add-Result $Name 'SKIPPED' (Get-NotDoneText); return }
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
            if (-not (Confirm-Action $key 'Remove registry key')) { Add-Result $Name 'SKIPPED' (Get-NotDoneText); return }
            Remove-Item -LiteralPath $key -Recurse -Force -WhatIf:$false -Confirm:$false -ErrorAction Stop
            Add-Result $Name 'OK' 'removed'
        }
    }

    # 4. Install folder (only with safety checks; never while PcGuard processes could not be ended).
    Invoke-Step 'Install folder' {
        $dir = $script:TargetDir
        if (-not $dir) { Add-Result $Name 'SKIPPED' 'no install folder found'; return }
        if (-not (Test-Path -LiteralPath $dir)) { Add-Result $Name 'SKIPPED' ($dir + ' does not exist'); return }
        if ($script:ProcEndFailed) {
            Add-Result $Name 'SKIPPED' ('a PcGuard process could not be ended, so ''' + $dir + ''' was not touched. Reboot into Safe Mode / see README, then run this script again.')
            return
        }
        $refusal = Get-DeleteRefusal $dir
        if ($refusal) { Add-Result $Name 'FAILED' ('refusing to delete ''' + $dir + ''': ' + $refusal); return }
        $leaf = Split-Path -Leaf $dir
        $hasBinary = Test-AnyFile $dir @('PcGuard.Service.exe', 'PcGuard.Shell.exe')
        $hasAny = ($hasBinary -or (Test-AnyFile $dir @('appsettings.json')))
        if ($leaf -eq 'PcGuard') {
            if (-not $hasAny) {
                Add-Result $Name 'SKIPPED' ('''' + $dir + ''' contains none of PcGuard.Service.exe, PcGuard.Shell.exe, appsettings.json; not deleted')
                return
            }
        }
        else {
            if (-not $script:DirExplicit) {
                Add-Result $Name 'SKIPPED' ('the discovered install folder ''' + $dir + ''' is not named PcGuard, so it is not deleted automatically. Rerun with -InstallDir ''' + $dir + ''' -Force if you are sure.')
                return
            }
            if (-not $Force) {
                Add-Result $Name 'SKIPPED' ('-InstallDir ''' + $dir + ''' is not named PcGuard; add -Force if you are sure')
                return
            }
            if (-not $hasBinary) {
                Add-Result $Name 'SKIPPED' ('''' + $dir + ''' contains neither PcGuard.Service.exe nor PcGuard.Shell.exe; not deleted')
                return
            }
        }
        if (-not (Test-NoNonAdminWrite $dir)) {
            if (-not $IgnoreAcl) {
                Add-Result $Name 'FAILED' ('''' + $dir + ''' is not safe to delete automatically (' + $script:WriteWhy + '); nothing deleted. Inspect it; only -IgnoreAcl overrides this check (-Force does not).')
                return
            }
            Write-Host ('  WARNING: -IgnoreAcl given; deleting a user-writable folder although ' + $script:WriteWhy + '. A directory can be swapped for a junction during the delete.') -ForegroundColor Red
        }
        if (-not (Confirm-Action $dir 'Delete folder tree (links are removed, never followed)')) { Add-Result $Name 'SKIPPED' (Get-NotDoneText); return }
        Remove-TreeSafe $dir
        Add-Result $Name 'OK' ('deleted ' + $dir)
    }

    # 5. Leftover setup temp folders created by Setup (admin-only ACL and owner, not a link, direct child of ProgramData).
    Invoke-Step 'Setup temp folders' {
        $list = @()
        try { $list = @(Get-ChildItem -LiteralPath $env:ProgramData -Directory -Filter 'PcGuard-setup-*' -Force -ErrorAction SilentlyContinue) } catch { }
        if ($list.Count -eq 0) { Add-Result $Name 'SKIPPED' 'none found'; return }
        $pdFull = Resolve-FsPath $env:ProgramData
        $done = 0
        $notDone = 0
        $skipped = @()
        $bad = @()
        foreach ($d in $list) {
            if ($d.Name -notlike 'PcGuard-setup-*') { continue }
            if (Test-IsReparse $d) { $bad += ($d.FullName + ' is a reparse point (junction or symlink); nothing deleted'); continue }
            $full = $null
            try { $full = Resolve-FsPath $d.FullName } catch { $bad += ($d.FullName + ': ' + $_.Exception.Message); continue }
            if ((Split-Path -Parent $full) -ne $pdFull) { $bad += ($full + ' is not directly inside ' + $pdFull + '; not deleted'); continue }
            $refusal = Get-DeleteRefusal $full
            if ($refusal) { $bad += ($full + ': refusing to delete: ' + $refusal); continue }
            if (-not (Test-TrustedAdminFolder $full)) {
                $skipped += ($full + ': folder is not admin-only (' + $script:TrustWhy + '); inspect it and delete manually')
                continue
            }
            if (-not (Confirm-Action $full 'Delete folder tree (links are removed, never followed)')) { $notDone++; continue }
            try { Remove-TreeSafe $full; $done++ } catch { $bad += ($full + ': ' + $_.Exception.Message) }
        }
        if ($bad.Count -gt 0) {
            Add-Result $Name 'FAILED' (($bad + $skipped) -join '; ')
        }
        elseif ($skipped.Count -gt 0) {
            Add-Result $Name 'SKIPPED' ('deleted ' + $done + '; ' + ($skipped -join '; '))
        }
        elseif ($notDone -gt 0) {
            Add-Result $Name 'SKIPPED' (Get-NotDoneText)
        }
        else {
            Add-Result $Name 'OK' ('deleted ' + $done + ' folder(s)')
        }
    }

    # 6. Data folder (machine key) only with -Purge; must be exactly <ProgramData>\PcGuard and admin-only.
    Invoke-Step 'Data folder' {
        $data = Join-Path $env:ProgramData 'PcGuard'
        if (-not $Purge) {
            if (Test-Path -LiteralPath $data) { Add-Result $Name 'SKIPPED' ('kept ' + $data + ' (machine key, rules, usage queue); use -Purge to delete') }
            else { Add-Result $Name 'SKIPPED' 'not present' }
            return
        }
        if (-not (Test-Path -LiteralPath $data)) { Add-Result $Name 'SKIPPED' 'not present'; return }
        $full = Resolve-FsPath $data
        $expected = (Resolve-FsPath $env:ProgramData) + '\PcGuard'
        if ($full -ne $expected) { Add-Result $Name 'FAILED' ('refusing to purge ''' + $full + ''': it is not exactly ' + $expected); return }
        $refusal = Get-DeleteRefusal $full
        if ($refusal) { Add-Result $Name 'FAILED' ('refusing to purge ''' + $full + ''': ' + $refusal); return }
        $di = New-Object System.IO.DirectoryInfo($full)
        if (Test-IsReparse $di) { Add-Result $Name 'FAILED' ('''' + $full + ''' is a reparse point (junction or symlink); nothing deleted'); return }
        if (-not (Test-TrustedAdminFolder $full)) {
            Add-Result $Name 'SKIPPED' ('folder is not admin-only (' + $script:TrustWhy + '); inspect it and delete manually')
            return
        }
        if (-not (Confirm-Action $full 'Delete folder tree (-Purge; links are removed, never followed)')) { Add-Result $Name 'SKIPPED' (Get-NotDoneText); return }
        Remove-TreeSafe $full
        Add-Result $Name 'OK' ('deleted ' + $full)
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
        if ($script:RemovalRan -and $script:ServiceTouched -and (Test-ServiceExists)) {
            if (Test-MarkedForDeletion) { Write-MarkedBlock } else { Write-RestoreBlock }
        }
        exit 2
    }
    Write-Host ''
    if ($script:DryRun) { Write-Host 'Done (-WhatIf: nothing was changed).' -ForegroundColor Green }
    else { Write-Host 'Done.' -ForegroundColor Green }
    exit 0
}
catch {
    Write-Host ('ERROR: ' + $_.Exception.Message) -ForegroundColor Red
    exit 1
}
